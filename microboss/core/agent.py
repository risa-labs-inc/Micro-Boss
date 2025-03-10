"""
Core agent functionality for the microboss package.
"""

import time
import uuid
from datetime import datetime
from pathlib import Path
import os
import re
import json
import logging
from typing import Any, Dict, List, Optional, Union, Tuple

from microboss.utils.api import get_client, generate_code, fix_code, decompose_task, get_llm_client
from microboss.utils.execution import execute_file, execute_python_file
from microboss.utils.file_utils import (
    create_task_directory, save_code_to_file, read_code_from_file, 
    save_json_to_file, read_json_from_file, save_to_file
)
from microboss.utils.logging import (
    log_info, log_success, log_warning, log_error, log_task, 
    log_code, log_result, log_execution
)
from microboss.utils.adaptive_optimizer import optimize_decomposition_decision, meta_analyze_domain

# Initialize logger
logger = logging.getLogger(__name__)

def agent(
    task: str,
    depth: int = 1,
    max_depth: int = 10,
    max_retries: int = 3,
    max_decomposition_depth: int = 10,
    adaptive: bool = True,
    timeout: int = 600,  # 10-minute default timeout
) -> Any:
    """
    Execute a task using an AI agent.
    
    Args:
        task: The task to execute
        depth: Maximum decomposition depth (if adaptive=False)
        max_depth: Absolute maximum decomposition depth (if adaptive=True)
        max_retries: Maximum number of retries per step
        max_decomposition_depth: Maximum depth for task decomposition
        adaptive: Whether to use adaptive self-limiting decomposition
        timeout: Maximum execution time in seconds
        
    Returns:
        Any: The result of the task execution
    """
    logger.info(f"AGENT SOLVING TASK: '{task}' AT DEPTH {max_depth if adaptive else depth}")
    
    # Initialize the LLM client
    client = get_llm_client()
    model = client.model
    logger.info(f"USING MODEL: {model}")
    
    # Create a timestamped directory for the task
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    task_slug = "_".join(task.lower().split()[:8]).replace("/", "_")
    run_dir = Path("run") / f"{timestamp}_task_{task_slug}"
    run_dir.mkdir(parents=True, exist_ok=True)
    
    # Execute the task
    if adaptive:
        logger.info("USING ADAPTIVE DECOMPOSITION APPROACH")
        return recursive_solve(
            task=task,
            run_dir=run_dir,
            max_depth=max_depth,
            max_retries=max_retries,
            max_decomposition_depth=max_decomposition_depth,
            timeout=timeout,
        )
    elif depth > 1:
        logger.info(f"USING RECURSIVE DECOMPOSITION APPROACH (DEPTH {depth})")
        return execute_recursive(
            task=task,
            depth=depth,
            run_dir=run_dir,
            max_retries=max_retries,
            max_decomposition_depth=max_decomposition_depth,
            timeout=timeout,
        )
    else:
        logger.info("USING DIRECT SOLUTION APPROACH (DEPTH 1)")
        return execute_direct(
            task=task,
            run_dir=run_dir,
            max_retries=max_retries,
        )

def recursive_solve(
    task: str,
    run_dir: Path,
    max_depth: int = 10,
    current_depth: int = 0,
    context: Optional[Dict[str, Any]] = None,
    max_retries: int = 3,
    max_decomposition_depth: int = 10,
    start_time: Optional[float] = None,
    timeout: int = 600,  # 10-minute default timeout per task
) -> Any:
    """Solve a task recursively with adaptive optimization."""
    context = context or {}
    
    # Initialize timing if needed
    if start_time is None:
        start_time = time.time()
    
    # Check timeout (early exit)
    elapsed_time = time.time() - start_time
    if elapsed_time > timeout * 0.9:
        logger.warning(f"Task execution approaching timeout ({elapsed_time:.1f}/{timeout}s)")
        return execute_direct(task, run_dir, max_retries)
        
    # Update context for domain-aware optimization
    client = get_llm_client()
    if "analysis" not in context:
        analysis = meta_analyze_domain(task, client)
        context["analysis"] = analysis
        context["domain"] = analysis["domain"]
        context["archetype"] = analysis["archetype"]
    
    # Update context with execution info
    context.update({
        "task": task,
        "current_depth": current_depth,
        "remaining_time": timeout - elapsed_time,
        "timeout": timeout
    })
    
    # Check if we've reached the maximum depth
    if current_depth >= max_depth:
        logger.info(f"Reached maximum depth {max_depth}, executing directly")
        return execute_direct(task, run_dir, max_retries, context=context)
    
    # Check if task matches known patterns that don't benefit from decomposition
    if matches_simple_task_pattern(task):
        logger.info(f"Task matches simple pattern, solving directly")
        return execute_direct(task, run_dir, max_retries)
    
    # Estimate code size first to potentially skip decomposition decision
    code_size = estimate_code_size(task)
    if code_size <= 200:  # If task can be solved in 200 lines or less
        logger.info(f"Task can be solved directly in approximately {code_size} lines, skipping decomposition")
        return execute_direct(task, run_dir, max_retries)
    
    # Ask the LLM if this task should be decomposed further
    decomposition_decision = ask_llm_if_decomposition_needed(task, context, current_depth)
    
    if decomposition_decision["should_decompose"]:
        logger.info(f"Decomposing task: {decomposition_decision['reasoning']}")
        
        # Create directory for decomposed tasks
        decomposed_dir = run_dir / "decomposed"
        decomposed_dir.mkdir(exist_ok=True)
        
        # Get subtasks with dependencies
        subtasks, levels = decompose_task(
            task, 
            context, 
            max_decomposition_depth
        )
        
        # Save decomposition info
        save_to_file(
            decomposed_dir / "decomposition.json",
            json.dumps({
                "subproblems": subtasks,
                "levels": levels,
                "aggregation_code": "results.get('task_final', None)",
            }, indent=2),
        )
        
        # Create subtasks directory
        subtasks_dir = decomposed_dir / "subtasks"
        subtasks_dir.mkdir(exist_ok=True)
        
        # Execute tasks level by level
        results = {}
        for level_idx, level in enumerate(levels):
            level_dir = subtasks_dir / f"level_{level_idx}"
            level_dir.mkdir(exist_ok=True)
            
            logger.info(f"PROCESSING LEVEL {level_idx} WITH {len(level)} TASKS")
            
            # Check remaining time before processing level
            current_elapsed = time.time() - start_time
            time_per_task = (timeout - current_elapsed) / max(1, len(level))
            
            # Process all tasks in this level
            for task_id, task_desc, dependencies in level:
                # Create task directory
                task_dir = level_dir / task_id
                task_dir.mkdir(exist_ok=True)
                
                # Get dependency results
                dependency_results = [results.get(dep, None) for dep in dependencies]
                
                # Update task description with inputs if needed
                if dependency_results and any(dep is not None for dep in dependency_results):
                    task_desc_with_inputs = f"{task_desc} with inputs {dependency_results}"
                else:
                    task_desc_with_inputs = task_desc
                
                logger.info(f"Task {task_id}: {task_desc_with_inputs}")
                
                # Recursively solve the subtask
                subtask_context = context.copy()
                subtask_context["parent_task"] = task
                subtask_context["dependency_results"] = dependency_results
                
                try:
                    result = recursive_solve(
                        task=task_desc_with_inputs,
                        run_dir=task_dir,
                        max_depth=max_depth,
                        current_depth=current_depth + 1,
                        context=subtask_context,
                        max_retries=max_retries,
                        max_decomposition_depth=max_decomposition_depth,
                        start_time=start_time,
                        timeout=timeout,
                    )
                    results[task_id] = result
                    
                    # Save result
                    save_to_file(
                        task_dir / "result.json",
                        json.dumps({"result": result}, indent=2),
                    )
                    
                    logger.info(f"Task {task_id} completed successfully")
                except Exception as e:
                    logger.error(f"Error executing subtask {task_id}: {e}")
                    results[task_id] = None
                    
                # Check if we should continue with remaining tasks
                if time.time() - start_time > timeout * 0.9:  # If 90% of time is used
                    logger.warning(f"Time limit approaching, will skip remaining tasks")
                    break
            
            logger.info(f"Level {level_idx} completed")
            
            # Stop processing levels if we're running out of time
            if time.time() - start_time > timeout * 0.9:
                logger.warning(f"Time limit approaching, stopping further decomposition levels")
                break
        
        # Save all results
        save_to_file(
            run_dir / "results.json",
            json.dumps({"results": results}, indent=2),
        )
        
        # Determine the final result (last task in the last level)
        try:
            final_result = results.get("task_final") or results.get(levels[-1][-1][0])
            save_to_file(
                run_dir / "final_result.json",
                json.dumps(final_result, indent=2),
            )
            return final_result
        except Exception as e:
            logger.error(f"Error getting final result: {e}")
            # Return the last result as a fallback
            for task_id in reversed(list(results.keys())):
                if results[task_id] is not None:
                    return results[task_id]
            return None
    else:
        logger.info(f"Solving directly: {decomposition_decision['reasoning']}")
        return execute_direct(task, run_dir, max_retries)

def matches_simple_task_pattern(task: str) -> bool:
    """
    Check if the task matches known patterns that don't benefit from decomposition.
    
    Args:
        task: The task description
        
    Returns:
        bool: True if task matches a simple pattern
    """
    # List of regex patterns for common simple tasks
    simple_patterns = [
        r"calculate\s+(\w+)\s+of\s+(\d+)",  # e.g., "calculate factorial of 5"
        r"convert\s+(\d+)\s+from\s+(\w+)\s+to\s+(\w+)",  # e.g., "convert 10 from decimal to binary"
        r"sort\s+(\w+)",  # e.g., "sort array"
        r"find\s+(greatest|smallest|maximum|minimum)",  # e.g., "find maximum"
        r"(add|subtract|multiply|divide)\s+(\d+)\s+(\w+)\s+(\d+)",  # simple arithmetic
        r"check\s+if\s+(\w+)\s+is\s+(prime|even|odd)",  # simple checks
    ]
    
    # Check task against all patterns
    for pattern in simple_patterns:
        if re.search(pattern, task.lower()):
            return True
    
    # List of keywords associated with simple tasks
    simple_keywords = [
        "calculate", "compute", "evaluate", "find value", 
        "simple function", "basic algorithm", "straightforward"
    ]
    
    # Check for simple keywords
    for keyword in simple_keywords:
        if keyword in task.lower():
            return True
            
    return False

def estimate_code_size(task: str) -> int:
    """
    Estimate the number of lines of code needed to solve a task directly.
    
    Args:
        task: The task description
        
    Returns:
        int: Estimated number of lines of code
    """
    # Simple heuristic estimation based on task length and complexity
    words = len(task.split())
    complexity_factor = 1.0
    
    # Increase complexity factor for certain types of tasks
    if any(kw in task.lower() for kw in ["web", "scraper", "api", "interface", "gui", "database", "machine learning"]):
        complexity_factor = 2.0
    
    if any(kw in task.lower() for kw in ["simple", "basic", "elementary", "calculate", "compute"]):
        complexity_factor = 0.5
    
    # Base heuristic: ~5 lines per word with adjustment for complexity
    lines = min(500, int(words * 5 * complexity_factor))
    
    logger.info(f"Estimated code size for task: ~{lines} lines")
    return lines

def ask_llm_if_decomposition_needed(task: str, context: Optional[Dict[str, Any]] = None, current_depth: int = 0) -> Dict[str, Any]:
    """Ask LLM if task should be decomposed."""
    client = get_llm_client()
    
    # Use optimizer to make quick decision
    should_decompose, analysis = optimize_decomposition_decision(task, client, current_depth)
    
    # If optimizer is confident, use its decision
    if analysis["complexity"] > 7 or analysis["complexity"] < 3:
        reasoning = f"Task is a {analysis['domain']} domain task with complexity {analysis['complexity']}/10"
        return {
            "should_decompose": should_decompose,
            "reasoning": reasoning
        }
    
    # For borderline cases, defer to the standard LLM decision process
    prompt = f"""
    For this task: "{task}"
    
    Should I:
    A) Solve directly with a single Python function/script (for tasks requiring <200 lines of code)
    B) Decompose into subtasks (for complex tasks with multiple distinct steps)
    
    Current depth: {current_depth}
    
    Consider:
    - Tasks that can be solved with a straightforward algorithm should use option A
    - Tasks requiring multiple independent components should use option B
    - Decomposition adds overhead but helps manage complexity
    
    Choose A or B, then provide a ONE SENTENCE justification.
    """
    
    if context:
        # Add time constraints if available
        if "remaining_time" in context:
            prompt += f"\n\nTime constraint: {context['remaining_time']:.1f} seconds remaining of {context['timeout']} seconds total."
    
    response = client.generate(prompt)
    
    # Parse the response
    if "A)" in response or "A:" in response or "SOLVE DIRECTLY" in response.upper():
        return {
            "should_decompose": False,
            "reasoning": extract_reasoning(response)
        }
    else:
        return {
            "should_decompose": True,
            "reasoning": extract_reasoning(response)
        }

def extract_reasoning(response: str) -> str:
    """Extract reasoning from LLM response."""
    reasoning = ""
    if "Reasoning:" in response:
        reasoning = response.split("Reasoning:")[1].strip()
        reasoning = reasoning.split("\n")[0]
    return reasoning[:100]  # Limit length for logging

def decompose_task(
    task: str, 
    context: Optional[Dict[str, Any]] = None,
    max_depth: int = 10
) -> Tuple[List, List]:
    """
    Decompose a task into subtasks with dependencies.
    
    Args:
        task: The task description
        context: Additional context
        max_depth: Maximum depth for task decomposition
        
    Returns:
        Tuple[List, List]: Subtasks and levels
    """
    client = get_llm_client()
    
    prompt = f"""
    Please decompose the following task into logical subtasks:
    
    Task: {task}
    
    First, analyze the task and determine how many subtasks would be appropriate.
    Then, list each subtask with a brief description.
    
    For each subtask:
    1. Provide a clear, specific description
    2. Ensure it's focused on a single responsibility
    3. Indicate any dependencies on other subtasks
    
    Your subtasks should collectively cover the entire original task.
    
    Format your response as follows:
    
    Number of subtasks: [number]
    
    Subtask 1: [description]
    Dependencies: [none or list of subtask numbers]
    
    Subtask 2: [description]
    Dependencies: [none or list of subtask numbers]
    
    ...and so on.
    """
    
    if context:
        prompt += f"\n\nAdditional context: {json.dumps(context, indent=2)}"
    
    logger.info("DECOMPOSING TASK: '%s' AT DEPTH %d", task, max_depth)
    start_time = time.time()
    response = client.generate(prompt)
    logger.info("DECOMPOSITION RESULTS (%.2fs)", time.time() - start_time)
    
    # Parse the subtasks and dependencies
    subtasks = []
    
    # Find all subtasks
    subtask_pattern = re.compile(r"Subtask (\d+): (.+?)(?:\n|$)")
    dependency_pattern = re.compile(r"Dependencies: (.+?)(?:\n|$)")
    
    subtask_matches = subtask_pattern.findall(response)
    
    for idx, (subtask_num, subtask_desc) in enumerate(subtask_matches):
        # Find dependency information
        deps_match = dependency_pattern.findall(response[response.find(f"Subtask {subtask_num}"):])
        dependencies = []
        
        if deps_match and len(deps_match) > 0:
            deps_text = deps_match[0]
            if not re.search(r"none|no dependencies", deps_text, re.IGNORECASE):
                # Extract numbers from dependency text
                dep_nums = re.findall(r"\d+", deps_text)
                dependencies = [f"task_{num}" for num in dep_nums]
        
        task_id = f"task_{subtask_num}"
        subtasks.append([task_id, subtask_desc.strip(), dependencies])
    
    # Add a final aggregation task if needed
    if len(subtasks) > 1:
        all_task_ids = [t[0] for t in subtasks]
        subtasks.append([
            "task_final", 
            f"Combine the results of all previous subtasks to solve: {task}",
            all_task_ids
        ])
    
    # Convert to level-based structure
    levels = []
    remaining = subtasks.copy()
    
    while remaining and len(levels) < max_depth:
        level = []
        next_remaining = []
        
        for task_info in remaining:
            task_id, task_desc, dependencies = task_info
            
            # If no dependencies or all dependencies are in previous levels
            if not dependencies or all(
                any(dep_task[0] == dep for dep_task in [t for l in levels for t in l])
                for dep in dependencies
            ):
                level.append(task_info)
            else:
                next_remaining.append(task_info)
        
        if level:
            levels.append(level)
            remaining = next_remaining
        else:
            # If we can't add any tasks, there might be circular dependencies
            # Add the first remaining task to break the cycle
            if remaining:
                levels.append([remaining[0]])
                remaining = remaining[1:]
            else:
                break
    
    logger.info("Converting simple subtask list to structured format")
    
    # If there are still remaining tasks, add them all to the final level
    if remaining:
        levels.append(remaining)
    
    return subtasks, levels

def execute_direct(task: str, run_dir: Path, max_retries: int = 3, context: Optional[Dict[str, Any]] = None) -> Any:
    """Execute a task directly without decomposition."""
    logger.info(f"Executing task directly: {task[:50]}...")
    
    # Create directory if it doesn't exist
    os.makedirs(run_dir, exist_ok=True)
    
    # Get LLM client
    client = get_llm_client()
    
    # Analyze domain if not already in context
    if context is None:
        context = {}
    
    if "analysis" not in context:
        analysis = meta_analyze_domain(task, client)
        context["domain"] = analysis["domain"]
        context["archetype"] = analysis["archetype"]
        context["analysis"] = analysis
    
    # Generate code
    code = generate_code(client, task)
    
    # Save code to file
    main_py_path = run_dir / "main.py"
    with open(main_py_path, "w") as f:
        f.write(code)
    
    # Try to generate and execute code up to max_retries times
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                logger.info(f"RETRY ATTEMPT {attempt}/{max_retries}")
                
            if attempt == 0:
                # Generate code for the first attempt
                code = client.generate(prompt)
                
                # Extract code from the response if needed
                if "```python" in code:
                    code = code.split("```python")[1].split("```")[0].strip()
                elif "```" in code:
                    code = code.split("```")[1].split("```")[0].strip()
            else:
                # For retry attempts, edit the existing file
                file_path = run_dir / "main.py"
                if file_path.exists():
                    logger.info(f"EDITING EXISTING FILE: {file_path}")
                    with open(file_path, "r") as f:
                        previous_code = f.read()
                    
                    fix_prompt = f"""
                    The following Python code was written to solve this task: {task}
                    
                    ```python
                    {previous_code}
                    ```
                    
                    However, there were errors during execution. Please fix the code.
                    
                    Provide only the corrected code, without any explanations.
                    """
                    
                    code = client.generate(fix_prompt)
                    
                    # Extract code from the response if needed
                    if "```python" in code:
                        code = code.split("```python")[1].split("```")[0].strip()
                    elif "```" in code:
                        code = code.split("```")[1].split("```")[0].strip()
                    
                    logger.info("FIXING CODE IN FILE: {file_path}")
                else:
                    # If file doesn't exist, generate new code
                    code = client.generate(prompt)
                    
                    # Extract code from the response if needed
                    if "```python" in code:
                        code = code.split("```python")[1].split("```")[0].strip()
                    elif "```" in code:
                        code = code.split("```")[1].split("```")[0].strip()
            
            # Save code to file
            file_path = run_dir / "main.py"
            save_to_file(file_path, code)
            logger.info(f"GENERATED CODE")
            
            # Execute the code
            logger.info(f"EXECUTING FILE: {file_path}")
            result, output = execute_python_file(file_path)
            
            if result is not None:
                logger.info(f"EXECUTION COMPLETE ({result.get('execution_time', 0):.2f}s)")
                
                if "result" in result:
                    logger.info(f"CALCULATION RESULT: {str(result['result'])[:100]}...")
                    
                    # Save the final result
                    final_result = result["result"]
                    save_to_file(
                        run_dir / "result.json",
                        json.dumps({"result": final_result}, indent=2),
                    )
                    save_to_file(
                        run_dir / "final_result.json",
                        json.dumps(final_result, indent=2),
                    )
                    
                    return final_result
                else:
                    logger.warning("No result.json file found. Using console output as the result.")
                    # Try to parse result from output
                    if output:
                        return output
            
            logger.warning("Execution completed but no result was found")
            return None
            
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"ERROR IN EXECUTION: {e}")
                logger.info(f"RETRYING ({attempt + 1}/{max_retries})...")
            else:
                logger.error(f"FAILED AFTER {max_retries} ATTEMPTS: {e}")
                raise
    
    return None

# For backward compatibility
def execute_recursive(
    task: str,
    depth: int,
    run_dir: Path,
    max_retries: int = 3,
    max_decomposition_depth: int = 10,
    timeout: int = 600,  # 10-minute default timeout
) -> Any:
    """Legacy recursive execution function for backward compatibility."""
    return recursive_solve(
        task=task,
        run_dir=run_dir,
        max_depth=depth,
        current_depth=0,
        context=None,
        max_retries=max_retries,
        max_decomposition_depth=max_decomposition_depth,
        timeout=timeout,
    ) 