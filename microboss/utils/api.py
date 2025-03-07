"""
API utilities for the microboss package.
"""

import os
import logging
import json
import requests
import anthropic
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)

def get_client():
    """
    Get the Anthropic API client.
    
    Returns:
        tuple: (client, model_info) where client is the API client and model_info is a string 
               describing which model is being used (e.g., "Anthropic Claude" or "OpenAI GPT-4").
    """
    # Get the API key from environment variable
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not api_key:
        logger.warning("Anthropic API key not found. Will try OpenAI as fallback.")
        # Check if OpenAI key is available
        openai_key = os.environ.get("OPENAI_API_KEY")
        if openai_key:
            logger.info("Using OpenAI as fallback")
            client, model_info = get_openai_client()
            return client, model_info
        else:
            raise ValueError(
                "No API keys found. Please set either ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable "
                "or create a .env file with one of these keys."
            )
    
    # Use the official Anthropic client with safe initialization
    # Avoid passing "proxies" parameter which seems to be causing issues
    try:
        # Try importing and inspecting the Anthropic client to handle version differences
        import inspect
        client_params = inspect.signature(anthropic.Anthropic.__init__).parameters
        client_kwargs = {"api_key": api_key}
        
        # Only include supported parameters
        if 'base_url' in client_params:
            # This might be used in some environments
            base_url = os.environ.get("ANTHROPIC_BASE_URL")
            if base_url:
                client_kwargs["base_url"] = base_url
                
        # Create the client with only supported parameters
        model_name = os.environ.get("ANTHROPIC_MODEL", "Claude")
        model_info = f"Anthropic {model_name}"
        return anthropic.Anthropic(**client_kwargs), model_info
    except Exception as e:
        logger.warning(f"Error creating Anthropic client with inspection: {str(e)}")
        
        # Try simple initialization
        try:
            model_name = os.environ.get("ANTHROPIC_MODEL", "Claude")
            model_info = f"Anthropic {model_name}"
            return anthropic.Anthropic(api_key=api_key), model_info
        except Exception as e:
            logger.warning(f"Failed to initialize Anthropic client: {str(e)}")
            
            # Try OpenAI as fallback
            openai_key = os.environ.get("OPENAI_API_KEY")
            if openai_key:
                logger.info("Using OpenAI as fallback due to Anthropic client initialization failure")
                client, model_info = get_openai_client()
                return client, model_info
            else:
                raise ValueError(f"Failed to initialize Anthropic client and no OpenAI fallback available: {str(e)}")


def get_openai_client():
    """
    Get the OpenAI API client.
    
    Returns:
        tuple: (client, model_info) where client is the OpenAI API client and model_info
               is a string describing which model is being used.
    """
    # Get API key
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError(
            "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable "
            "or create a .env file with OPENAI_API_KEY=your-api-key."
        )
    
    # Check for custom base URL or organization
    base_url = os.environ.get("OPENAI_API_BASE")
    org_id = os.environ.get("OPENAI_ORGANIZATION")
    
    # Create the client with supported parameters
    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    if org_id:
        kwargs["organization"] = org_id
    
    # Get the model name from env or use a default
    model_name = os.environ.get("OPENAI_MODEL", "GPT-4")
    model_info = f"OpenAI {model_name}"
    
    return openai.OpenAI(**kwargs), model_info


def get_default_model():
    """
    Get the default model to use.
    
    Returns:
        str: The model name.
    """
    # Get the model from the environment
    model = os.environ.get("DEFAULT_MODEL")
    
    # If no model specified, use defaults based on available API
    if not model:
        # Check which API keys are available to determine the default model
        if os.environ.get("ANTHROPIC_API_KEY"):
            return "claude-3-7-sonnet-20250219"  # Latest Claude model
        elif os.environ.get("OPENAI_API_KEY"):
            return "gpt-4o-2024-05-13"  # Latest GPT model
        else:
            # Default to Claude if no specific key is found
            return "claude-3-7-sonnet-20250219"
    
    return model


def get_max_tokens():
    """
    Get the maximum number of tokens to generate.
    
    Returns:
        int: The maximum number of tokens.
    """
    # Get the max tokens from the environment or use a default value
    max_tokens_str = os.environ.get("MAX_TOKENS", "4096")
    try:
        return int(max_tokens_str)
    except ValueError:
        logger.warning(f"Invalid MAX_TOKENS value: {max_tokens_str}. Using default 4096.")
        return 4096


def generate_code(client, task):
    """
    Generate code to solve a task using the AI API.
    
    Args:
        client: The API client (Anthropic or OpenAI).
        task: The task to solve.
        
    Returns:
        str: The generated code.
    """
    model = get_default_model()
    max_tokens = get_max_tokens()
    
    # Try with Anthropic first
    if isinstance(client, anthropic.Anthropic):
        try:
            # Use Messages API (newer)
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=0,
                system="You are an expert Python programmer tasked with generating concise, executable Python code. Your code should set a variable named 'result' to the final answer. Make sure to handle edge cases appropriately. Do not include explanations, just the code.",
                messages=[
                    {"role": "user", "content": f"Generate Python code to solve: '{task}'"}
                ]
            )
            
            # Extract the code from the response
            code = response.content[0].text.strip()
            
            # Remove markdown code blocks if present
            if code.startswith("```python"):
                code = code[len("```python"):].strip()
            elif code.startswith("```"):
                code = code[len("```"):].strip()
                
            if code.endswith("```"):
                code = code[:-len("```")].strip()
                
            # Ensure the code sets a 'result' variable
            if "result =" not in code and "result=" not in code:
                code += "\nresult = None  # Default result if not set"
                
            return code
            
        except Exception as e:
            logger.error(f"Failed to generate code with Anthropic: {str(e)}")
            
            # Try OpenAI fallback if available
            openai_key = os.environ.get("OPENAI_API_KEY")
            if openai_key:
                logger.info("Falling back to OpenAI for code generation")
                openai_client = get_openai_client()
                return generate_code(openai_client, task)
            else:
                raise ValueError(f"Failed to generate code: {str(e)}")
    
    # If we're using OpenAI client (fallback or direct)
    elif hasattr(client, 'chat') and hasattr(client.chat, 'completions'):
        try:
            # Use ChatCompletions API
            response = client.chat.completions.create(
                model=model if "gpt" in model else "gpt-4o-2024-05-13",  # Ensure we use a GPT model
                temperature=0,
                messages=[
                    {"role": "system", "content": "You are an expert Python programmer tasked with generating concise, executable Python code. Your code should set a variable named 'result' to the final answer. Make sure to handle edge cases appropriately. Do not include explanations, just the code."},
                    {"role": "user", "content": f"Generate Python code to solve: '{task}'"}
                ]
            )
            
            # Extract the code
            code = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if code.startswith("```python"):
                code = code[len("```python"):].strip()
            elif code.startswith("```"):
                code = code[len("```"):].strip()
                
            if code.endswith("```"):
                code = code[:-len("```")].strip()
                
            # Ensure the code sets a 'result' variable
            if "result =" not in code and "result=" not in code:
                code += "\nresult = None  # Default result if not set"
                
            return code
            
        except Exception as e:
            logger.error(f"Failed to generate code with OpenAI: {str(e)}")
            raise ValueError(f"Failed to generate code: {str(e)}")
    
    # Unknown client type
    else:
        raise ValueError(f"Unsupported client type: {type(client)}")


def fix_code(client, code, error):
    """
    Fix code using the AI API.
    
    Args:
        client: The API client (Anthropic or OpenAI).
        code: The code to fix.
        error: The error message.
        
    Returns:
        str: The fixed code.
    """
    model = get_default_model()
    max_tokens = get_max_tokens()
    
    # Try with Anthropic first
    if isinstance(client, anthropic.Anthropic):
        try:
            # Use Messages API (newer)
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=0,
                system="You are an expert Python programmer tasked with fixing bugs in code. Your fixed code should set a variable named 'result' to the final answer. Make sure to handle edge cases appropriately. Return only the fixed code without explanations.",
                messages=[
                    {"role": "user", "content": f"Fix this Python code that has the following error:\n\nERROR: {error}\n\nCODE:\n{code}"}
                ]
            )
            
            # Extract the code from the response
            fixed_code = response.content[0].text.strip()
            
            # Remove markdown code blocks if present
            if fixed_code.startswith("```python"):
                fixed_code = fixed_code[len("```python"):].strip()
            elif fixed_code.startswith("```"):
                fixed_code = fixed_code[len("```"):].strip()
                
            if fixed_code.endswith("```"):
                fixed_code = fixed_code[:-len("```")].strip()
                
            # Ensure the code sets a 'result' variable
            if "result =" not in fixed_code and "result=" not in fixed_code:
                fixed_code += "\nresult = None  # Default result if not set"
                
            return fixed_code
            
        except Exception as e:
            logger.error(f"Failed to fix code with Anthropic: {str(e)}")
            
            # Try OpenAI fallback if available
            openai_key = os.environ.get("OPENAI_API_KEY")
            if openai_key:
                logger.info("Falling back to OpenAI for code fixing")
                openai_client = get_openai_client()
                return fix_code(openai_client, code, error)
            else:
                raise ValueError(f"Failed to fix code: {str(e)}")
    
    # If we're using OpenAI client (fallback or direct)
    elif hasattr(client, 'chat') and hasattr(client.chat, 'completions'):
        try:
            # Use ChatCompletions API
            response = client.chat.completions.create(
                model=model if "gpt" in model else "gpt-4o-2024-05-13",  # Ensure we use a GPT model
                temperature=0,
                messages=[
                    {"role": "system", "content": "You are an expert Python programmer tasked with fixing bugs in code. Your fixed code should set a variable named 'result' to the final answer. Make sure to handle edge cases appropriately. Return only the fixed code without explanations."},
                    {"role": "user", "content": f"Fix this Python code that has the following error:\n\nERROR: {error}\n\nCODE:\n{code}"}
                ]
            )
            
            # Extract the code
            fixed_code = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if fixed_code.startswith("```python"):
                fixed_code = fixed_code[len("```python"):].strip()
            elif fixed_code.startswith("```"):
                fixed_code = fixed_code[len("```"):].strip()
                
            if fixed_code.endswith("```"):
                fixed_code = fixed_code[:-len("```")].strip()
                
            # Ensure the code sets a 'result' variable
            if "result =" not in fixed_code and "result=" not in fixed_code:
                fixed_code += "\nresult = None  # Default result if not set"
                
            return fixed_code
            
        except Exception as e:
            logger.error(f"Failed to fix code with OpenAI: {str(e)}")
            raise ValueError(f"Failed to fix code: {str(e)}")
    
    # Unknown client type
    else:
        raise ValueError(f"Unsupported client type: {type(client)}")


def decompose_task(client, task, depth):
    """
    Decompose a task into subtasks using the AI API.
    
    Args:
        client: The API client (Anthropic or OpenAI).
        task: The task to decompose.
        depth: The depth of decomposition.
        
    Returns:
        list: The list of subtasks.
    """
    model = get_default_model()
    max_tokens = get_max_tokens()
    
    # Try with Anthropic first
    if isinstance(client, anthropic.Anthropic):
        try:
            # Use Messages API (newer)
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=0,
                system="You are an expert in task decomposition. Your goal is to break down complex tasks into simpler, more manageable subtasks. Each subtask should be small enough to be accomplished with a single Python function. Provide your response as a JSON array of strings.",
                messages=[
                    {"role": "user", "content": f"Decompose the following task into {depth} subtasks: '{task}'"}
                ]
            )
            
            # Extract the text from the response
            decomposition_text = response.content[0].text.strip()
            
            # Try to parse JSON array from the response
            try:
                # Find JSON array in the response
                start_idx = decomposition_text.find("[")
                end_idx = decomposition_text.rfind("]") + 1
                
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = decomposition_text[start_idx:end_idx]
                    subtasks = json.loads(json_str)
                    
                    # Ensure we have the right number of subtasks
                    if len(subtasks) == depth:
                        return subtasks
                    else:
                        logger.warning(f"Expected {depth} subtasks, but got {len(subtasks)}. Using as is.")
                        return subtasks
                else:
                    # Fallback to splitting by newlines if no JSON array found
                    logger.warning("Could not find JSON array in response. Falling back to line splitting.")
                    lines = [line.strip() for line in decomposition_text.split("\n") if line.strip()]
                    
                    # Remove numbered prefixes like "1.", "2.", etc.
                    subtasks = []
                    for line in lines:
                        if line.startswith(("- ", "* ", "• ")):
                            subtasks.append(line[2:].strip())
                        elif len(line) > 2 and line[0].isdigit() and line[1] == ".":
                            subtasks.append(line[2:].strip())
                        elif len(line) > 3 and line[0].isdigit() and line[1].isdigit() and line[2] == ".":
                            subtasks.append(line[3:].strip())
                        else:
                            subtasks.append(line)
                    
                    # Limit to the requested depth
                    return subtasks[:depth] if len(subtasks) >= depth else subtasks
            except json.JSONDecodeError:
                # Fallback to splitting by newlines if JSON parsing fails
                logger.warning("Failed to parse JSON from response. Falling back to line splitting.")
                lines = [line.strip() for line in decomposition_text.split("\n") if line.strip()]
                
                # Process lines to remove markers and numbering
                subtasks = []
                for line in lines:
                    if line.startswith(("- ", "* ", "• ")):
                        subtasks.append(line[2:].strip())
                    elif len(line) > 2 and line[0].isdigit() and line[1] == ".":
                        subtasks.append(line[2:].strip())
                    elif len(line) > 3 and line[0].isdigit() and line[1].isdigit() and line[2] == ".":
                        subtasks.append(line[3:].strip())
                    else:
                        subtasks.append(line)
                
                # Limit to the requested depth
                return subtasks[:depth] if len(subtasks) >= depth else subtasks
        except Exception as e:
            logger.error(f"Failed to decompose task with Anthropic: {str(e)}")
            
            # Try OpenAI fallback if available
            openai_key = os.environ.get("OPENAI_API_KEY")
            if openai_key:
                logger.info("Falling back to OpenAI for task decomposition")
                openai_client = get_openai_client()
                return decompose_task(openai_client, task, depth)
            else:
                raise ValueError(f"Failed to decompose task: {str(e)}")
    
    # If we're using OpenAI client (fallback or direct)
    elif hasattr(client, 'chat') and hasattr(client.chat, 'completions'):
        try:
            # Use ChatCompletions API
            response = client.chat.completions.create(
                model=model if "gpt" in model else "gpt-4o-2024-05-13",  # Ensure we use a GPT model
                temperature=0,
                messages=[
                    {"role": "system", "content": "You are an expert in task decomposition. Your goal is to break down complex tasks into simpler, more manageable subtasks. Each subtask should be small enough to be accomplished with a single Python function. Provide your response as a JSON array of strings."},
                    {"role": "user", "content": f"Decompose the following task into {depth} subtasks: '{task}'"}
                ]
            )
            
            # Extract the text
            decomposition_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON array from the response
            try:
                # Find JSON array in the response
                start_idx = decomposition_text.find("[")
                end_idx = decomposition_text.rfind("]") + 1
                
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = decomposition_text[start_idx:end_idx]
                    subtasks = json.loads(json_str)
                    
                    # Ensure we have the right number of subtasks
                    if len(subtasks) == depth:
                        return subtasks
                    else:
                        logger.warning(f"Expected {depth} subtasks, but got {len(subtasks)}. Using as is.")
                        return subtasks
                else:
                    # Fallback to splitting by newlines if no JSON array found
                    logger.warning("Could not find JSON array in response. Falling back to line splitting.")
                    lines = [line.strip() for line in decomposition_text.split("\n") if line.strip()]
                    
                    # Remove numbered prefixes like "1.", "2.", etc.
                    subtasks = []
                    for line in lines:
                        if line.startswith(("- ", "* ", "• ")):
                            subtasks.append(line[2:].strip())
                        elif len(line) > 2 and line[0].isdigit() and line[1] == ".":
                            subtasks.append(line[2:].strip())
                        elif len(line) > 3 and line[0].isdigit() and line[1].isdigit() and line[2] == ".":
                            subtasks.append(line[3:].strip())
                        else:
                            subtasks.append(line)
                    
                    # Limit to the requested depth
                    return subtasks[:depth] if len(subtasks) >= depth else subtasks
            except json.JSONDecodeError:
                # Fallback to splitting by newlines if JSON parsing fails
                logger.warning("Failed to parse JSON from response. Falling back to line splitting.")
                lines = [line.strip() for line in decomposition_text.split("\n") if line.strip()]
                
                # Process lines to remove markers and numbering
                subtasks = []
                for line in lines:
                    if line.startswith(("- ", "* ", "• ")):
                        subtasks.append(line[2:].strip())
                    elif len(line) > 2 and line[0].isdigit() and line[1] == ".":
                        subtasks.append(line[2:].strip())
                    elif len(line) > 3 and line[0].isdigit() and line[1].isdigit() and line[2] == ".":
                        subtasks.append(line[3:].strip())
                    else:
                        subtasks.append(line)
                
                # Limit to the requested depth
                return subtasks[:depth] if len(subtasks) >= depth else subtasks
        except Exception as e:
            logger.error(f"Failed to decompose task with OpenAI: {str(e)}")
            raise ValueError(f"Failed to decompose task: {str(e)}")
    
    # Unknown client type
    else:
        raise ValueError(f"Unsupported client type: {type(client)}")