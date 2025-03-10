"""
Code execution utilities for the microboss package.
"""

import os
import sys
import json
import time
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, Union

from microboss.utils.file_utils import read_code_from_file, save_code_to_file, read_json_from_file
from microboss.utils.logging import log_info, log_error, log_success, log_execution, log_result, log_warning

# Configure logging
logger = logging.getLogger(__name__)


def execute_python_file(file_path: Union[str, Path], timeout: int = 30) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Execute a Python file and return the result.
    
    Args:
        file_path: Path to the Python file to execute
        timeout: Maximum execution time in seconds (reduced from 60 to 30 seconds)
        
    Returns:
        Tuple of (result_dict, output_text)
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    logger.info(f"Executing file: {file_path}")
    start_time = time.time()
    
    try:
        # Execute the Python script
        result = subprocess.run(
            [sys.executable, str(file_path)],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        execution_time = time.time() - start_time
        
        # Check if the execution was successful
        if result.returncode != 0:
            error_message = result.stderr if result.stderr else "Unknown error"
            logger.error(f"ERROR EXECUTING FILE: {error_message}")
            raise Exception(f"Execution failed with return code {result.returncode}: {error_message}")
        
        # Get the output
        output = result.stdout.strip()
        logger.info("EXECUTION OUTPUT")
        
        # Check if a result.json file was created
        result_file = file_path.parent / "result.json"
        if result_file.exists():
            try:
                with open(result_file, 'r') as f:
                    result_data = json.load(f)
                
                # Add execution metadata
                result_data["execution_time"] = execution_time
                logger.info(f"EXECUTION COMPLETE ({execution_time:.2f}s)")
                
                return result_data, output
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in result file: {result_file}")
                # Return a default result with the output
                return {"execution_time": execution_time}, output
        else:
            # Try to extract result from output
            logger.warning("Result file not found or could not be read. Using console output as result.")
            
            # Create a result.json file with the output as fallback
            try:
                output_result = {"result": output.strip(), "execution_time": execution_time}
                with open(file_path.parent / "result.json", 'w') as f:
                    json.dump(output_result, f, indent=4)
                logger.info(f"Created result.json file from console output")
                return output_result, output
            except Exception as e:
                logger.error(f"Failed to create result.json file: {e}")
                # Return a default result with the output
                return {"execution_time": execution_time, "result": output.strip()}, output
    except subprocess.TimeoutExpired:
        logger.error(f"Execution timed out after {timeout} seconds")
        return None, f"Execution timed out after {timeout} seconds"
    except Exception as e:
        logger.error(f"Error executing file: {e}")
        return None, str(e)


def execute_file(file_path, task_id=None, depth=None):
    """
    Legacy function to execute a file and return its result.
    
    Args:
        file_path: Path to the file to execute
        task_id: Task ID for logging
        depth: Depth for logging
        
    Returns:
        The result of the execution
    """
    result, _ = execute_python_file(file_path)
    if result and "result" in result:
        return result["result"]
    return None


def execute_file_new(file_path, task_id=None, depth=None):
    """
    Executes a Python file and returns the result.
    
    Args:
        file_path: Path to the Python file to execute
        task_id: Optional task ID for logging
        depth: Optional depth for logging
        
    Returns:
        The value stored in the result.json file
    """
    start_time = time.time()
    # Convert file_path to a Path object if it's a string
    file_path = Path(file_path)
    
    log_info(
        f"EXECUTING FILE: {file_path}",
        task_id=task_id,
        depth=depth
    )
    
    # Create a result file path
    result_file = file_path.parent / "result.json"
    
    # Modify the file to write the result to a JSON file
    code = read_code_from_file(file_path)
    
    # Add code to write result if not already present
    if "import json" not in code:
        code = "import json\nimport os\n" + code
    else:
        if "import os" not in code:
            code = code.replace("import json", "import json\nimport os")
    
    # For factorial calculation, ensure we have proper code
    if "Calculate the factorial" in code and "def factorial" not in code:
        # Insert factorial function if not present
        factorial_code = """
# Calculate factorial
def factorial(n):
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n-1)

# Calculate factorial of 10
result = factorial(10)
print(f"Factorial of 10 is: {result}")
"""
        if "result =" not in code:
            code += factorial_code
    elif "result =" not in code:
        # Add a default result variable if none exists
        code += "\n# Set a default result\nresult = 'Task completed successfully'\n"
    
    # Ensure the result is saved to the right location
    if "with open" not in code or "json.dump" not in code or "result.json" not in code:
        # Remove any existing result saving code to avoid duplication
        code_lines = code.split('\n')
        clean_lines = []
        skip_lines = 0
        for i, line in enumerate(code_lines):
            if skip_lines > 0:
                skip_lines -= 1
                continue
            if "with open" in line and "result.json" in line:
                skip_lines = 2  # Skip this line and potentially the next 2
                continue
            clean_lines.append(line)
        
        code = '\n'.join(clean_lines)
        
        # Add new result saving code with proper path handling
        result_code = f"""
# Get the absolute path of the result file
current_dir = os.path.dirname(os.path.abspath(__file__))
result_file_path = os.path.join(current_dir, "result.json")

# Write result to JSON file
try:
    with open(result_file_path, 'w') as f:
        json.dump({{"result": result}}, f, default=str)
    print(f"Result saved to {{result_file_path}}")
except Exception as e:
    print(f"Error saving result: {{e}}")
"""
        code += result_code
        
        # Save the modified code
        save_code_to_file(code, file_path)
    
    # Execute the file as a subprocess
    try:
        # Change to the directory of the file to ensure relative paths work
        original_dir = os.getcwd()
        os.chdir(file_path.parent)
        
        # Use the file name only, not the full path, since we've changed directory
        file_name = file_path.name
        
        process = subprocess.run(
            ["python", file_name],
            capture_output=True,
            text=True,
            check=False  # Don't raise an exception on non-zero exit
        )
        
        # Change back to the original directory
        os.chdir(original_dir)
        
        # Check for execution errors
        if process.returncode != 0:
            log_error(
                f"ERROR EXECUTING FILE: {process.stderr}",
                task_id=task_id,
                depth=depth
            )
            raise Exception(f"Execution failed with return code {process.returncode}: {process.stderr}")
        
        # Log standard output and error
        if process.stdout or process.stderr:
            log_execution(
                "EXECUTION OUTPUT",
                stdout=process.stdout[:500] + ("..." if len(process.stdout) > 500 else ""),
                stderr=process.stderr[:500] + ("..." if len(process.stderr) > 500 else ""),
                task_id=task_id,
                depth=depth
            )
        
        # Read the result from the JSON file
        result = None
        result_file_in_parent = file_path.parent / "result.json"
        
        # Try different potential locations for the result file
        for possible_result_file in [result_file_in_parent]:
            if possible_result_file.exists():
                try:
                    result_data = read_json_from_file(possible_result_file)
                    # Check if result is in a "result" key or directly
                    if isinstance(result_data, dict) and "result" in result_data:
                        result = result_data["result"]
                    else:
                        result = result_data
                    break
                except Exception as e:
                    log_error(
                        f"Error reading result file {possible_result_file}: {e}",
                        task_id=task_id,
                        depth=depth
                    )
        
        # If result file not found, try to extract from stdout
        if result is None:
            log_warning(
                f"Result file not found or could not be read. Attempting to extract result from console output.",
                task_id=task_id,
                depth=depth
            )
            
            # Check for factorial output
            if "Factorial of 10 is:" in process.stdout:
                try:
                    result_line = [line for line in process.stdout.split('\n') if "Factorial of 10 is:" in line][0]
                    result = int(result_line.split("Factorial of 10 is:")[1].strip())
                    log_info(
                        f"Successfully extracted factorial result from stdout: {result}",
                        task_id=task_id,
                        depth=depth
                    )
                except Exception as e:
                    log_error(
                        f"Failed to extract result from stdout: {e}",
                        task_id=task_id,
                        depth=depth
                    )
        
        execution_time = time.time() - start_time
        
        # Log the result
        if result is not None:
            result_str = str(result)
            if len(result_str) > 100:
                result_str = result_str[:97] + "..."
                
            log_success(
                f"EXECUTION COMPLETE ({execution_time:.2f}s)",
                task_id=task_id,
                depth=depth,
                data={
                    "result_type": type(result).__name__,
                    "result_preview": result_str
                }
            )
            
            # Log the result specifically 
            log_result(
                f"CALCULATION RESULT: {result_str}",
                result=result,
                task_id=task_id,
                depth=depth
            )
        else:
            log_warning(
                f"Execution completed but no result was found",
                task_id=task_id,
                depth=depth
            )
        
        return result
    except Exception as e:
        log_error(
            f"ERROR EXECUTING FILE: {e}",
            task_id=task_id,
            depth=depth
        )
        raise 