"""
File utility functions for the microboss package.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path


def ensure_run_directory():
    """Create the run directory if it doesn't exist"""
    run_dir = Path("run")
    run_dir.mkdir(exist_ok=True)
    return run_dir


def create_safe_filename(task, prefix="task"):
    """Create a safe filename from a task description"""
    # Handle None values
    if task is None:
        task = "unknown_task"
        
    # Replace spaces and special chars with underscores, limit length
    safe_name = re.sub(r'[^\w\s-]', '', task.lower())
    safe_name = re.sub(r'[\s-]+', '_', safe_name)
    safe_name = safe_name[:50]  # Limit length
    return f"{prefix}_{safe_name}"


def create_task_directory(task):
    """Create a directory for the current task run"""
    run_dir = ensure_run_directory()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_name = create_safe_filename(task)
    task_dir = run_dir / f"{timestamp}_{safe_name}"
    task_dir.mkdir(exist_ok=True)
    return task_dir


def save_code_to_file(code, file_path):
    """Save code to a file"""
    with open(file_path, 'w') as f:
        f.write(code)
    print(f"📄 Code saved to: {file_path}")
    return file_path


def read_code_from_file(file_path):
    """Read code from a file"""
    with open(file_path, 'r') as f:
        return f.read()


def save_json_to_file(data, file_path, default_handler=str):
    """Save data to a JSON file"""
    with open(file_path, 'w') as f:
        json.dump(data, f, default=default_handler, indent=2)
    return file_path


def read_json_from_file(file_path):
    """Read data from a JSON file"""
    if Path(file_path).exists():
        with open(file_path, 'r') as f:
            return json.load(f)
    return None 