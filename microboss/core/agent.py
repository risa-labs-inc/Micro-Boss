"""
Core agent functionality for the microboss package.
"""

import time
import uuid
from datetime import datetime
from pathlib import Path
import os

from microboss.utils.api import get_client, generate_code, fix_code, decompose_task
from microboss.utils.execution import execute_file
from microboss.utils.file_utils import (
    create_task_directory, save_code_to_file, read_code_from_file, 
    save_json_to_file, read_json_from_file
)
from microboss.utils.logging import (
    log_info, log_success, log_warning, log_error, log_task, 
    log_code, log_result, log_execution
)


def agent(task, depth=1, max_retries=3):
    """
    Entry point for the agent that solves tasks.
    
    Args:
        task (str): Task to solve.
        depth (int): Depth of recursion.
        max_retries (int): Maximum number of retries on code execution failure.
    
    Returns:
        Generated result.
    """
    start_time = time.time()
    task_id = str(uuid.uuid4())
    
    log_task(
        f"AGENT SOLVING TASK: '{task}' AT DEPTH {depth}",
        task_id=task_id,
        depth=depth,
        data={
            "max_retries": max_retries,
            "started_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    )

    # Create a task directory for this run
    task_dir = create_task_directory(task)
    
    # Get the API client
    client, model_info = get_client()
    
    # Log which model is being used - log this multiple times for persistence
    log_info(
        f"USING MODEL: {model_info}",
        task_id=task_id,
        depth=depth,
        data={"model_info": model_info}
    )
    
    # Log it again with a different message to ensure it's captured
    log_info(
        f"Task will be solved using {model_info}",
        task_id=task_id,
        depth=depth,
        data={"model_info": model_info}
    )
    
    retries = 0
    last_error = None
    code_file_path = None
    
    while retries <= max_retries:
        try:
            if depth <= 1:
                # For depth 1, use the direct solution approach
                log_info(
                    f"USING DIRECT SOLUTION APPROACH (DEPTH 1)",
                    task_id=task_id,
                    depth=depth
                )
                
                if retries > 0:
                    log_info(
                        f"RETRY ATTEMPT {retries}/{max_retries}",
                        task_id=task_id,
                        depth=depth
                    )
                    
                # Generate code or edit existing file
                if retries == 0 or code_file_path is None:
                    # Generate new code on first attempt
                    code = generate_code(client, task)
                    main_file = task_dir / "main.py"
                    code_file_path = save_code_to_file(code, main_file)
                    
                    log_code(
                        "GENERATED CODE",
                        code=code,
                        task_id=task_id,
                        depth=depth
                    )
                else:
                    # On retry, edit the existing file
                    log_info(
                        f"EDITING EXISTING FILE: {code_file_path}",
                        task_id=task_id,
                        depth=depth
                    )
                    code = fix_code_file(client, code_file_path, last_error, task_id, depth)
                
                # Execute the file instead of the code directly
                result = execute_file(code_file_path, task_id, depth)
                
                log_success(
                    f"AGENT COMPLETED TASK AT DEPTH {depth} IN {time.time() - start_time:.2f}s",
                    task_id=task_id,
                    depth=depth
                )
                
                log_result(
                    f"FINAL RESULT: {str(result)[:1000] if result is not None else 'None'}",
                    result=result,
                    task_id=task_id,
                    depth=depth
                )
                
                return result
            else:
                # For depth > 1, use the recursive decomposition approach
                log_info(
                    f"USING RECURSIVE DECOMPOSITION APPROACH (DEPTH {depth})",
                    task_id=task_id,
                    depth=depth
                )
                
                if retries > 0:
                    log_info(
                        f"RETRY ATTEMPT {retries}/{max_retries}",
                        task_id=task_id,
                        depth=depth
                    )
                
                # First get the decomposition
                log_info(
                    f"DECOMPOSING TASK: '{task}' AT DEPTH {depth}",
                    task_id=task_id,
                    depth=depth
                )
                
                subtasks = decompose_task(client, task, depth)
                
                # Convert subtasks to a string representation for logging
                code = "Subtasks:\n" + "\n".join([f"{i+1}. {task}" for i, task in enumerate(subtasks)])
                
                log_code(
                    f"DECOMPOSITION RESULTS ({time.time() - start_time:.2f}s)",
                    code=code,
                    task_id=task_id,
                    depth=depth
                )
                
                # Create a directory for the decomposed tasks
                decomp_dir = task_dir / "decomposed"
                decomp_dir.mkdir(exist_ok=True)
                
                # Process the subtasks to get the proper structure
                # When decompose_task returns a simple list of strings, we need to create the proper structure
                if isinstance(subtasks, list) and all(isinstance(t, str) for t in subtasks):
                    log_info(
                        "Converting simple subtask list to structured format",
                        task_id=task_id,
                        depth=depth
                    )
                    subproblems, levels, aggregation_code = decompose_complex_task(client, task, depth, task_id)
                else:
                    # This will likely never happen due to the changes in decompose_task,
                    # but kept for backward compatibility
                    log_warning(
                        "Unexpected format from decompose_task. Attempting to process directly.",
                        task_id=task_id,
                        depth=depth
                    )
                    subproblems = subtasks
                    levels = [[subtask] for subtask in subtasks]
                    aggregation_code = f"results.get('task_{len(subtasks)}', None)"
                
                # Save the decomposition details
                decomp_file = decomp_dir / "decomposition.json"
                save_json_to_file({
                    "subproblems": [[id, template, deps] for id, template, deps in subproblems],
                    "levels": [[[id, template, deps] for id, template, deps in level] for level in levels],
                    "aggregation_code": aggregation_code
                }, decomp_file)
                
                # For depth > 1, use a simplified approach to avoid the syntax errors in generated code
                result = execute_simplified_subproblems(client, task, subproblems, levels, depth, aggregation_code, task_dir, task_id, max_retries)
                
                log_success(
                    f"AGENT COMPLETED TASK AT DEPTH {depth} IN {time.time() - start_time:.2f}s",
                    task_id=task_id,
                    depth=depth
                )
                
                log_result(
                    f"FINAL RESULT: {str(result)[:1000] if result is not None else 'None'}",
                    result=result,
                    task_id=task_id,
                    depth=depth
                )
                
                return result
        except Exception as e:
            retries += 1
            last_error = e
            if retries <= max_retries:
                log_warning(
                    f"ERROR IN EXECUTION: {str(e)}",
                    task_id=task_id,
                    depth=depth
                )
                log_info(
                    f"RETRYING ({retries}/{max_retries})...",
                    task_id=task_id,
                    depth=depth
                )
                time.sleep(1)  # Short pause before retrying
            else:
                log_error(
                    f"ALL RETRIES FAILED. LAST ERROR: {str(e)}",
                    task_id=task_id,
                    depth=depth
                )
                break
    
    if last_error:
        log_error(
            f"EXECUTION FAILED AFTER {max_retries} RETRIES",
            task_id=task_id,
            depth=depth
        )
        log_error(
            f"FINAL ERROR: {str(last_error)}",
            task_id=task_id,
            depth=depth
        )
        raise last_error
    
    return None


def fix_code_file(client, file_path, error, task_id=None, depth=None):
    """
    Fix code in a file based on the error.
    
    Args:
        client: API client
        file_path: Path to the file to fix
        error: Error message
        task_id: Optional task ID for logging
        depth: Optional depth for logging
        
    Returns:
        The fixed code
    """
    # Convert file_path to a Path object if it's a string
    file_path = Path(file_path)
    
    log_info(
        f"FIXING CODE IN FILE: {file_path}",
        task_id=task_id,
        depth=depth
    )
    
    # Read the code
    code = read_code_from_file(file_path)
    
    try:
        # Fix the code
        fixed_code = fix_code(client, code, error)
        
        # Save the fixed code
        save_code_to_file(fixed_code, file_path)
        
        log_info(
            "FIXED CODE",
            task_id=task_id,
            depth=depth
        )
        
        return fixed_code
    except Exception as e:
        log_error(
            f"ERROR FIXING CODE: {e}",
            task_id=task_id,
            depth=depth
        )
        raise


def decompose_complex_task(client, task, depth, task_id):
    """
    Decomposes a task into subproblems with dependencies.

    Args:
        client: The API client (Anthropic or OpenAI)
        task (str): Task description.
        depth (int): Current depth.
        task_id: The task ID.

    Returns:
        tuple: (subproblems, levels, aggregation_code)
            - subproblems: List of (id, template, deps) tuples
            - levels: List of lists, where each inner list contains subproblems at that level
            - aggregation_code: String representing code to aggregate results
    """
    start_time = time.time()
    log_info(
        f"DECOMPOSING TASK: '{task}' AT DEPTH {depth}",
        task_id=task_id,
        depth=depth
    )
    
    # Get the decomposition code
    result = decompose_task(client, task, depth)
    
    # Convert to a string representation for logging
    if isinstance(result, list) and all(isinstance(item, str) for item in result):
        # Handle case where decompose_task returns a simple list of subtasks
        subtasks_str = "Subtasks:\n" + "\n".join([f"{i+1}. {task}" for i, task in enumerate(result)])
    else:
        # Handle original format
        subtasks_str = str(result)
    
    log_code(
        f"DECOMPOSITION RESULTS ({time.time() - start_time:.2f}s)",
        code=subtasks_str,
        task_id=task_id,
        depth=depth
    )
    
    # Create a simplified dependency structure if we just get a list of subtasks
    # This handles the case when decompose_task returns just a list without proper dependency info
    if isinstance(result, list) and all(isinstance(item, str) for item in result):
        log_info(
            "Creating simplified dependency structure from subtasks list",
            task_id=task_id,
            depth=depth
        )
        
        # Create subproblems with sequential dependencies
        subproblems = []
        for i, subtask in enumerate(result):
            subtask_id = f"task_{i+1}"
            # Each task depends on the previous one, except for the first task
            dependencies = [f"task_{i}"] if i > 0 else []
            subproblems.append((subtask_id, subtask, dependencies))
        
        # Create sequential levels based on dependencies
        levels = []
        for i, (subtask_id, subtask_text, deps) in enumerate(subproblems):
            levels.append([subproblems[i]])
        
        # Create a simple aggregation code that returns the last result
        aggregation_code = f"results.get('task_{len(result)}', None)"
        
        return subproblems, levels, aggregation_code
    
    try:
        # For backward compatibility with original approach
        local_vars = {}
        exec(subtasks_str, {}, local_vars)
        
        # Safely handle the aggregation code (handle lists/numbers/etc)
        aggregation_code = local_vars.get('aggregation_code', "None")
        if aggregation_code is None:
            aggregation_code = "None"
            
        if isinstance(aggregation_code, str) and "[" in aggregation_code and "]" in aggregation_code:
            # If it's trying to access a list item, add a simple handling
            aggregation_code = f"results.get({aggregation_code.split('[')[1].split(']')[0]}, 0)"
        
        # Ensure subproblems exists
        if 'subproblems' not in local_vars:
            raise ValueError("No 'subproblems' defined in the output")
            
        # Validate that all dependencies exist
        all_ids = [id for id, _, _ in local_vars['subproblems']]
        invalid_deps = []
        for _, _, deps in local_vars['subproblems']:
            for dep in deps:
                if dep not in all_ids:
                    invalid_deps.append(dep)
        
        if invalid_deps:
            log_warning(
                f"Found invalid dependencies: {invalid_deps}. Removing them.",
                task_id=task_id,
                depth=depth
            )
            # Remove invalid deps
            cleaned_subproblems = []
            for id, template, deps in local_vars['subproblems']:
                cleaned_deps = [dep for dep in deps if dep in all_ids]
                cleaned_subproblems.append((id, template, cleaned_deps))
            local_vars['subproblems'] = cleaned_subproblems
        
        # Ensure no circular dependencies
        try:
            dep_graph = {}
            for id, _, deps in local_vars['subproblems']:
                dep_graph[id] = deps
            # Check for cycles
            visited = set()
            path = set()
            
            def dfs(node):
                if node in path:
                    raise ValueError(f"Circular dependency detected involving node {node}")
                if node in visited:
                    return
                visited.add(node)
                path.add(node)
                for neighbor in dep_graph.get(node, []):
                    dfs(neighbor)
                path.remove(node)
            
            for node in dep_graph:
                dfs(node)
        except ValueError as e:
            log_warning(
                f"Dependency issue detected: {str(e)}. Using simplified approach.",
                task_id=task_id,
                depth=depth
            )
            # Fall back to simplified approach
            raise
        
        # Get levels if present, or build them if not
        if 'levels' in local_vars:
            levels = local_vars['levels']
        else:
            # Build levels from subproblems
            levels = build_dependency_levels(local_vars['subproblems'])
        
        return local_vars['subproblems'], levels, aggregation_code
        
    except Exception as e:
        log_warning(
            f"Error interpreting decomposition: {str(e)}. Using simplified approach.",
            task_id=task_id,
            depth=depth
        )
        
        # Create a simple linear decomposition as fallback
        subtasks = result if isinstance(result, list) else [task]
        subproblems = []
        
        for i, subtask in enumerate(subtasks):
            if isinstance(subtask, str):
                subtask_text = subtask
            else:
                subtask_text = f"Subtask {i+1}"
                
            subtask_id = f"task_{i+1}"
            dependencies = [f"task_{i}"] if i > 0 else []
            subproblems.append((subtask_id, subtask_text, dependencies))
        
        # Create a simple linear level structure
        levels = [[subproblem] for subproblem in subproblems]
        
        # Create a simple aggregation that returns the last result
        aggregation_code = f"results.get('task_{len(subproblems)}', None)"
        
        return subproblems, levels, aggregation_code


def execute_simplified_subproblems(client, task, subproblems, levels, depth, aggregation_code, task_dir, task_id, max_retries=3):
    """
    A simplified execution of subproblems that avoids complex code generation.
    This function executes each subproblem directly in sequence.
    
    Args:
        client: The Anthropic API client
        task (str): The main task
        subproblems (list): List of subproblems
        levels (list): Subproblems grouped by level
        depth (int): Current depth
        aggregation_code (str): Code to aggregate results
        task_dir (Path): Directory for storing task-related files
        task_id (str): The task ID.
        max_retries (int): Maximum number of retries for each subtask
        
    Returns:
        The aggregated result or the last subproblem's result
    """
    start_time = time.time()
    log_info(
        "EXECUTING SIMPLIFIED RECURSIVE PROCESS",
        task_id=task_id,
        depth=depth
    )
    
    # Directory for subtasks
    subtasks_dir = task_dir / "subtasks"
    subtasks_dir.mkdir(exist_ok=True)
    
    # Dictionary to store results for each subproblem
    results = {}
    results_file = task_dir / "results.json"
    
    # Process each level sequentially
    for level_index, level in enumerate(levels):
        log_info(
            f"PROCESSING LEVEL {level_index} WITH {len(level)} TASKS",
            task_id=task_id,
            depth=depth
        )
        level_start_time = time.time()
        
        # Create a directory for this level
        level_dir = subtasks_dir / f"level_{level_index}"
        level_dir.mkdir(exist_ok=True)
        
        for subtask_id, task_template, deps in level:
            clean_task = task_template.replace('"', '\\"').replace('\n', ' ')
            log_task(
                f"Task {subtask_id}: {clean_task}",
                task_id=task_id,
                subtask_id=subtask_id,
                depth=depth,
                parent_id=task_id
            )
            
            # Create a directory for this subtask
            subtask_dir = level_dir / subtask_id
            subtask_dir.mkdir(exist_ok=True)
            
            task_success = False
            subtask_retries = 0
            last_subtask_error = None
            
            while not task_success and subtask_retries <= max_retries:
                try:
                    if not deps:
                        # No dependencies, just execute the task directly
                        results[subtask_id] = agent(task_template, depth - 1, max_retries)
                    else:
                        # With dependencies, include them in the task description
                        deps_values = [results.get(d) for d in deps if d in results]
                        input_str = str(deps_values)
                        if len(input_str) > 100:
                            input_str = input_str[:97] + "..."
                        
                        modified_task = f"{clean_task} with inputs {input_str}"
                        results[subtask_id] = agent(modified_task, depth - 1, max_retries)
                    
                    task_success = True
                    log_success(
                        f"Task {subtask_id} completed successfully",
                        task_id=task_id,
                        subtask_id=subtask_id,
                        depth=depth,
                        parent_id=task_id
                    )
                    
                    # Save this result to subtask directory
                    save_json_to_file(results[subtask_id], subtask_dir / "result.json")
                except Exception as e:
                    subtask_retries += 1
                    last_subtask_error = e
                    if subtask_retries <= max_retries:
                        log_warning(
                            f"ERROR IN SUBTASK {subtask_id}: {str(e)}",
                            task_id=task_id,
                            subtask_id=subtask_id,
                            depth=depth,
                            parent_id=task_id
                        )
                        log_info(
                            f"RETRYING SUBTASK ({subtask_retries}/{max_retries})...",
                            task_id=task_id,
                            subtask_id=subtask_id,
                            depth=depth,
                            parent_id=task_id
                        )
                        time.sleep(1)  # Short pause before retrying
                    else:
                        log_error(
                            f"ALL RETRIES FAILED FOR SUBTASK {subtask_id}. LAST ERROR: {str(e)}",
                            task_id=task_id,
                            subtask_id=subtask_id,
                            depth=depth,
                            parent_id=task_id
                        )
                        # Store a placeholder result
                        results[subtask_id] = f"Failed after {max_retries} retries: {str(e)}"
                        
                        # Save the error result
                        with open(subtask_dir / "error.txt", 'w') as f:
                            f.write(f"Failed after {max_retries} retries: {str(e)}")
                        break
            
            # Save the current state of all results after each subtask
            save_json_to_file(results, results_file)
        
        log_info(
            f"Level {level_index} completed in {time.time() - level_start_time:.2f}s",
            task_id=task_id,
            depth=depth
        )
    
    # Get the final result
    try:
        # Extract the key from the aggregation code
        key = None
        if "results.get" in aggregation_code:
            key = aggregation_code.split('"')[1]
        elif "results[" in aggregation_code:
            key = aggregation_code.split('[')[1].split(']')[0].strip('"\'')
        
        if key and key in results:
            final_result = results[key]
        else:
            # If the key doesn't exist, use the last task's result
            last_level = levels[-1]
            last_task_id = last_level[-1][0]
            final_result = results.get(last_task_id)
    except Exception as e:
        log_warning(
            f"Error getting final result: {e}",
            task_id=task_id,
            depth=depth
        )
        # Just return the last result as fallback
        last_level = levels[-1]
        last_task_id = last_level[-1][0]
        final_result = results.get(last_task_id)
    
    # Log summary of results
    log_info(
        f"SUBTASK PROCESSING COMPLETED IN {time.time() - start_time:.2f}s",
        task_id=task_id,
        depth=depth
    )
    
    log_info(
        "RESULTS BY TASK ID:",
        task_id=task_id,
        depth=depth,
        data={"results": {k: str(v)[:50] + ('...' if len(str(v)) > 50 else '') for k, v in results.items()}}
    )
    
    # Save the final consolidated result
    save_json_to_file(final_result, task_dir / "final_result.json")
    
    return final_result 


def build_dependency_levels(subproblems):
    """
    Build levels of task execution based on dependencies.
    
    Args:
        subproblems: List of (id, template, dependencies) tuples
        
    Returns:
        List of levels, where each level is a list of tasks that can be executed in parallel
    """
    # Initialize level map
    level_map = {}
    
    # Get all task IDs
    all_ids = set(id for id, _, _ in subproblems)
    
    # Create a map of task ID to its dependencies
    dep_map = {id: set(deps) for id, _, deps in subproblems}
    
    # Tasks with no remaining dependencies are at level 0
    remaining = set(all_ids)
    level = 0
    
    while remaining:
        current_level = []
        to_remove = set()
        
        # Find tasks with no remaining dependencies
        for task_id in remaining:
            # If all dependencies have been processed (not in remaining)
            if all(dep not in remaining for dep in dep_map[task_id]):
                task_data = None
                for id, template, deps in subproblems:
                    if id == task_id:
                        task_data = (id, template, deps)
                        break
                
                if task_data:
                    current_level.append(task_data)
                    to_remove.add(task_id)
        
        # Handle circular dependencies by picking an arbitrary task
        if not current_level and remaining:
            # Choose the first remaining task
            task_id = next(iter(remaining))
            for id, template, deps in subproblems:
                if id == task_id:
                    # Only include dependencies that are not in remaining
                    filtered_deps = [dep for dep in deps if dep not in remaining]
                    task_data = (id, template, filtered_deps)
                    current_level.append(task_data)
                    to_remove.add(task_id)
                    break
        
        remaining -= to_remove
        level_map[level] = current_level
        level += 1
    
    # Convert map to list of levels
    levels = [level_map[l] for l in range(level)]
    return levels 