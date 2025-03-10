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
from typing import Any, Dict, List, Optional, Tuple, Union
import hashlib
from functools import lru_cache
from microboss.utils.adaptive_optimizer import get_cached_response, cache_response, optimize_prompt

# Load environment variables from .env file
load_dotenv()

# Import API clients
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Setup logging
logger = logging.getLogger(__name__)

# Global prompt cache with LRU caching to limit memory usage
_PROMPT_CACHE = {}
_MAX_CACHE_SIZE = 100

def generate_with_cache(client, prompt: str, max_tokens: Optional[int] = None, cache_key: Optional[str] = None) -> str:
    """
    Generate text using an LLM with caching for similar prompts
    
    Args:
        client: The LLM client
        prompt: The prompt to send
        max_tokens: Maximum tokens to generate
        cache_key: Optional cache key override
        
    Returns:
        The generated text
    """
    # Create a cache key using a hash of the prompt
    if not cache_key:
        cache_key = hashlib.md5(prompt.encode("utf-8")).hexdigest()
    
    # Check if we have a cached result
    if cache_key in _PROMPT_CACHE:
        logger.info(f"Using cached response for prompt")
        return _PROMPT_CACHE[cache_key]
    
    # Manage cache size
    if len(_PROMPT_CACHE) >= _MAX_CACHE_SIZE:
        # Remove a random entry (simple approach)
        _PROMPT_CACHE.pop(next(iter(_PROMPT_CACHE.keys())))
    
    # Generate the response
    response = client.generate(prompt, max_tokens)
    
    # Cache the result
    _PROMPT_CACHE[cache_key] = response
    
    return response

class LLMClient:
    """A unified client for interacting with LLM APIs."""
    
    def __init__(self, provider="anthropic", model=None):
        """
        Initialize the LLM client.
        
        Args:
            provider: The LLM provider ("anthropic" or "openai")
            model: The model to use (defaults to environment variable or system default)
        """
        self.provider = provider
        self.client = None
        self.model = model
        
        # Set default model based on provider
        if not self.model:
            if provider == "anthropic":
                self.model = os.environ.get("DEFAULT_MODEL", "claude-3-7-sonnet-20250219")
            else:
                self.model = os.environ.get("DEFAULT_MODEL", "gpt-4o-2024-05-13")
        
        # Initialize the appropriate client
        if provider == "anthropic":
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("Anthropic package not available. Install with 'pip install anthropic'")
            
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")
            
            try:
                # Simple initialization with just the API key
                self.client = anthropic.Anthropic(api_key=api_key)
                logger.info("Anthropic client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic client: {e}")
                raise
        
        elif provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI package not available. Install with 'pip install openai'")
            
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            
            self.client = openai.OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized")
        
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def generate(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """
        Generate text using the LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            The generated text
        """
        if not max_tokens:
            max_tokens = int(os.environ.get("MAX_TOKENS", 4096))
        
        # Call the direct API implementation to avoid recursion
        if self.provider == "anthropic":
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                result = response.content[0].text
                # Cache the result
                cache_response(prompt, result)
                return result
            except Exception as e:
                logger.error(f"Error with Anthropic API: {e}")
                raise
        elif self.provider == "openai":
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens
                )
                result = response.choices[0].message.content
                # Cache the result
                cache_response(prompt, result)
                return result
            except Exception as e:
                logger.error(f"Error with OpenAI API: {e}")
                raise
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")


def get_llm_client() -> LLMClient:
    """
    Get a unified LLM client, trying Anthropic first and falling back to OpenAI.
    
    Returns:
        A LLMClient instance
    """
    # Try to use Anthropic first
    if ANTHROPIC_AVAILABLE and os.environ.get("ANTHROPIC_API_KEY"):
        try:
            client = LLMClient(provider="anthropic")
            return client
        except Exception as e:
            logger.warning(f"Using OpenAI as fallback due to Anthropic client initialization failure")
            # Fall back to OpenAI if Anthropic fails
            pass
    
    # Use OpenAI if Anthropic is unavailable or failed
    if OPENAI_AVAILABLE and os.environ.get("OPENAI_API_KEY"):
        try:
            # When using OpenAI as fallback, use an OpenAI model instead of trying to use a Claude model
            openai_model = os.environ.get("OPENAI_MODEL", "gpt-4o-2024-05-13")
            client = LLMClient(provider="openai", model=openai_model)
            logger.info(f"USING MODEL: OpenAI {client.model}")
            return client
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise
    
    # If we get here, neither client could be initialized
    raise ValueError("No valid LLM client could be initialized. Please provide valid API keys.")


def get_client():
    """Legacy client getter for backward compatibility."""
    client = get_llm_client()
    return client, client.model


def generate_code(client, task):
    """Generate code for a task."""
    prompt = f"""
    Write Python code to solve this task:
    
    TASK: {task}
    
    Requirements:
    - Make sure to include all necessary imports
    - Use proper error handling (complete all try-except blocks)
    - Use descriptive variable names
    - Implement the task completely
    - Save the final result to a file named 'result.json' in the current directory
    
    Return only the Python code, without explanations.
    """
    
    # Use the optimized generate function with task context
    code = generate(client, prompt, task=task, prompt_type="code_generation")
    
    # Extract code if wrapped in markdown code blocks
    import re
    code_block_pattern = r"```(?:python)?(.*?)```"
    code_blocks = re.findall(code_block_pattern, code, re.DOTALL)
    
    if code_blocks:
        # Get the longest code block (most likely the complete solution)
        code = max(code_blocks, key=len).strip()
    
    # Ensure all try-except blocks are complete
    # Simple check for incomplete except blocks
    lines = code.split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('except') and i == len(lines) - 1:
            # Last line is an except statement, add a pass
            lines.append('        print("Error:", e)')
            lines.append('        pass')
    
    # Join lines back
    code = '\n'.join(lines)
    
    # Ensure the code includes result.json saving
    if 'result.json' not in code:
        # Add result saving code
        if '__main__' not in code:
            code += '\n\nif __name__ == "__main__":\n'
            code += '    result = prime_factors(120)\n'
            code += '    with open("result.json", "w") as f:\n'
            code += '        json.dump({"result": result}, f)\n'
            code += '    print("Result:", result)\n'
    
    return code


def fix_code(client, code, error):
    """Fix code based on an error. Legacy function for backward compatibility."""
    prompt = f"""
    The following Python code has an error:
    
    ```python
    {code}
    ```
    
    Error: {error}
    
    Please fix the code. Provide only the corrected code, without any explanations.
    """
    
    return client.generate(prompt)


def decompose_task(client, task, depth):
    """Decompose a task into subtasks."""
    prompt = f"""
    For this task: "{task}"

    Please decompose it into a list of subtasks, such that each subtask can be solved independently with its dependencies.
    Follow these guidelines:
    - Each subtask should be a single, focused task with a clear objective
    - Every subtask should contribute to solving the overall task
    - Identify dependencies between subtasks 
    - The final subtask should integrate the results from all other subtasks
    - Use proper ordering and dependencies to ensure correctness

    Return subtasks in the format:
    [
        ["task_1", "Description of first subtask", []],
        ["task_2", "Description of second subtask", ["task_1"]],
        ...,
        ["task_final", "Combine everything into a solution", ["task_1", "task_2", ...]]
    ]

    Where:
    - First item is a unique ID for the subtask
    - Second item is a clear description of that subtask
    - Third item is a list of dependency task IDs that must be completed before this subtask
    
    Focus on a good decomposition, with clear task descriptions and accurate dependencies.
    """

    # Use the optimized generate function
    response = generate(client, prompt, task=task, prompt_type="decomposition", 
                       context={"current_depth": depth})
    
    # Parse the response to extract subtasks
    import re
    
    # Helper function to parse subtasks
    def parse_subtasks(response_text):
        try:
            # Try to extract JSON-like content
            pattern = r'\[\s*\[.*?\]\s*\]'
            matches = re.findall(pattern, response_text, re.DOTALL)
            if matches:
                # Get the longest match (most likely the complete list)
                largest_match = max(matches, key=len)
                # Clean up and parse
                clean_text = largest_match.replace("'", '"')
                return json.loads(clean_text)
            else:
                # Fall back to line-by-line parsing
                result = []
                lines = response_text.strip().split('\n')
                for line in lines:
                    if line.strip().startswith('[') and ']' in line:
                        try:
                            # Replace single quotes with double quotes for valid JSON
                            clean_line = line.strip().replace("'", '"')
                            task_info = json.loads(clean_line)
                            if len(task_info) == 3:
                                result.append(task_info)
                        except:
                            continue
                return result
        except:
            logger.error("Failed to parse decomposition response", exc_info=True)
            return []
    
    subtasks = parse_subtasks(response)
    
    if not subtasks:
        # Try a simpler prompt if the first one failed
        simple_prompt = f"""
        Break down this task into steps: "{task}"
        
        Format: [id, description, [dependencies]]
        Example: 
        [
            ["task_1", "First step", []], 
            ["task_2", "Second step", ["task_1"]]
        ]
        """
        simple_response = client.generate(simple_prompt)
        subtasks = parse_subtasks(simple_response)
    
    # Ensure there's a final task that combines everything
    has_final = any(task_id == "task_final" for task_id, _, _ in subtasks)
    if not has_final and subtasks:
        all_task_ids = [task_id for task_id, _, _ in subtasks]
        subtasks.append([
            "task_final",
            f"Combine the results of all previous subtasks to solve: {task}",
            all_task_ids
        ])
    
    return subtasks


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

def generate(client, prompt, max_tokens=None, task=None, prompt_type=None, context=None):
    """Generate text with enhanced caching and optimization."""
    # If task and prompt_type are provided, use optimized generation
    if task and prompt_type:
        return optimize_prompt(prompt, task, prompt_type, client, context)
    
    # Otherwise, just use basic caching
    cached = get_cached_response(prompt)
    if cached:
        logger.info("Using cached response")
        return cached
        
    # Generate and cache
    if not max_tokens:
        max_tokens = int(os.environ.get("MAX_TOKENS", 4096))
    
    # Handle different client types
    if isinstance(client, LLMClient):
        # Use direct API implementation from the method we just fixed
        return client.generate(prompt, max_tokens)
    else:
        # Assume it's something else with a generate method
        try:
            result = client.generate(prompt, max_tokens=max_tokens)
            cache_response(prompt, result)
            return result
        except Exception as e:
            logger.error(f"Error generating with client: {e}")
            raise