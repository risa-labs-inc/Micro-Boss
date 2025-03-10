"""
File utility functions for the microboss package.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Union, Dict, Any
import time
import logging

# Configure logging
logger = logging.getLogger(__name__)


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


def create_task_directory(task: str) -> Path:
    """
    Create a timestamped directory for a task.
    
    Args:
        task: Task description
        
    Returns:
        Path to the created directory
    """
    # Create a timestamped directory name
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    task_slug = "_".join(task.lower().split()[:8]).replace("/", "_")
    task_dir_name = f"{timestamp}_task_{task_slug}"
    
    # Ensure the run directory exists
    run_dir = Path("run")
    run_dir.mkdir(exist_ok=True)
    
    # Create the task directory
    task_dir = run_dir / task_dir_name
    task_dir.mkdir(exist_ok=True)
    
    return task_dir


def save_to_file(file_path: Union[str, Path], content: str) -> Path:
    """
    Save content to a file, creating any necessary directories.
    
    Args:
        file_path: Path to save the file
        content: Content to write to the file
        
    Returns:
        Path object for the saved file
    """
    file_path = Path(file_path)
    
    # Create parent directories if they don't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write the content to the file
    with open(file_path, 'w') as f:
        f.write(content)
    
    logger.info(f"📄 Code saved to: {file_path}")
    return file_path


def save_code_to_file(code: str, file_path: Union[str, Path]) -> Path:
    """
    Save code to a file.
    
    Args:
        code: The code to save
        file_path: Path to save the code to
        
    Returns:
        Path to the saved file
    """
    return save_to_file(file_path, code)


def read_code_from_file(file_path: Union[str, Path]) -> str:
    """
    Read code from a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        The code from the file
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r') as f:
        return f.read()


def save_json_to_file(data: Dict[str, Any], file_path: Union[str, Path]) -> Path:
    """
    Save data as JSON to a file.
    
    Args:
        data: Data to save
        file_path: Path to save the data to
        
    Returns:
        Path to the saved file
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    return file_path


def read_json_from_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Read JSON from a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        The data from the file
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r') as f:
        return json.load(f) 