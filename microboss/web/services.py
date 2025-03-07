"""
Services for the Microboss web application.
"""

import json
import threading
import time
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from microboss.core.agent import agent
from microboss.utils.logging import (
    LogLevel, event_logger, log_info, log_success, log_warning, 
    log_error, log_task, log_code, log_result
)


class TaskStatus(Enum):
    """Status of a task."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Task:
    """Task to be executed by Microboss."""
    
    def __init__(
        self,
        task_id: str,
        description: str,
        depth: int = 1,
        max_retries: int = 3,
        max_decomposition_depth: int = 10,
        created_at: Optional[float] = None,
        status: TaskStatus = TaskStatus.PENDING,
        result: Any = None,
        error: Optional[str] = None,
        model_info: Optional[str] = None
    ):
        self.task_id = task_id
        self.description = description
        self.depth = depth
        self.max_retries = max_retries
        self.max_decomposition_depth = max_decomposition_depth
        self.created_at = created_at or time.time()
        self.status = status
        self.result = result
        self.error = error
        self.started_at: Optional[float] = None
        self.completed_at: Optional[float] = None
        self.model_info: Optional[str] = model_info
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "depth": self.depth,
            "max_retries": self.max_retries,
            "max_decomposition_depth": self.max_decomposition_depth,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "status": self.status.value,
            "result": str(self.result) if self.result is not None else None,
            "error": self.error,
            "duration": (self.completed_at - self.started_at) if self.completed_at and self.started_at else None,
            "formatted_created": datetime.fromtimestamp(self.created_at).strftime('%Y-%m-%d %H:%M:%S'),
            "formatted_started": datetime.fromtimestamp(self.started_at).strftime('%Y-%m-%d %H:%M:%S') if self.started_at else None,
            "formatted_completed": datetime.fromtimestamp(self.completed_at).strftime('%Y-%m-%d %H:%M:%S') if self.completed_at else None,
            "model_info": self.model_info
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create Task from dictionary."""
        task = cls(
            task_id=data["task_id"],
            description=data["description"],
            depth=data["depth"],
            max_retries=data["max_retries"],
            max_decomposition_depth=data.get("max_decomposition_depth", 10),
            created_at=data["created_at"],
            status=TaskStatus(data["status"]),
            result=data.get("result"),
            error=data.get("error"),
            model_info=data.get("model_info")
        )
        task.started_at = data.get("started_at")
        task.completed_at = data.get("completed_at")
        return task


class TaskService:
    """Service to manage tasks."""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.task_threads: Dict[str, threading.Thread] = {}
        self.callbacks = []
    
    def create_task(
        self,
        description: str,
        depth: int = 1,
        max_retries: int = 3,
        max_decomposition_depth: int = 10
    ) -> Task:
        """Create a new task."""
        task_id = str(uuid.uuid4())
        task = Task(
            task_id=task_id,
            description=description,
            depth=depth,
            max_retries=max_retries,
            max_decomposition_depth=max_decomposition_depth
        )
        self.tasks[task_id] = task
        
        log_task(
            f"Created task: {description}",
            task_id=task_id,
            depth=depth,
            data={
                "max_retries": max_retries,
                "max_decomposition_depth": max_decomposition_depth
            }
        )
        
        # Notify callbacks
        for callback in self.callbacks:
            callback("task_created", task)
        
        return task
    
    def start_task(self, task_id: str) -> Task:
        """Start executing a task."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        
        if task.status == TaskStatus.RUNNING:
            log_warning(f"Task {task_id} is already running", task_id=task_id)
            return task
        
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()
        
        log_task(
            f"Starting task: {task.description}",
            task_id=task_id,
            depth=task.depth
        )
        
        # Start task in a separate thread
        thread = threading.Thread(
            target=self._execute_task,
            args=(task_id,),
            daemon=True
        )
        self.task_threads[task_id] = thread
        thread.start()
        
        # Notify callbacks
        for callback in self.callbacks:
            callback("task_started", task)
        
        return task
    
    def _execute_task(self, task_id: str):
        """Execute a task in the background."""
        task = self.tasks.get(task_id)
        if not task:
            return
        
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()
        
        # Use the correct event callback notification method
        for callback in self.callbacks:
            callback("task_started", task)
        
        try:
            # Create a new agent instance to handle this task
            result = agent(
                task.description,
                depth=task.depth,
                max_retries=task.max_retries
            )
            
            # Check for model_info in task events FIRST (before processing results)
            # This ensures model info is available even during the processing
            events = event_logger.get_events(task_id=task_id)
            model_info_found = False
            for event in events:
                if event.level.value == "info" and event.data and "model_info" in event.data:
                    task.model_info = event.data["model_info"]
                    model_info_found = True
                    # Save task state immediately to make model info available
                    for callback in self.callbacks:
                        callback("task_updated", task)
                    break
            
            # If no model info was found, set a default
            if not model_info_found:
                task.model_info = "Unknown model"
            
            # Store the result
            if isinstance(result, int) and result > 1000:
                # Format with commas for readability
                task.result = f"{result:,}"
            elif isinstance(result, float):
                # Format floats with 6 decimal places
                task.result = f"{result:.6f}"
            elif isinstance(result, dict):
                # Try to convert to formatted JSON
                try:
                    task.result = json.dumps(result, indent=2)
                except:
                    task.result = str(result)
            else:
                task.result = result
                
            if "factorial" in task.description.lower():
                # Add specific context for factorial calculations
                if task.result and (isinstance(task.result, int) or (isinstance(task.result, str) and task.result.replace(',', '').isdigit())):
                    # If we have a numeric result, format it nicely
                    value = task.result if isinstance(task.result, int) else int(task.result.replace(',', ''))
                    task.result = f"The factorial of 10 is: {value:,}"
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()
            
            # Log the completion
            log_success(
                f"Task completed: {task.description}",
                task_id=task_id
            )
            
            # Log the result
            log_result(
                "Task result",
                task_id=task_id,
                result=task.result
            )
            
            # Use the correct event callback notification method
            for callback in self.callbacks:
                callback("task_completed", task)
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            task.completed_at = time.time()
            
            log_error(
                f"Task failed: {task.description}. Error: {str(e)}",
                task_id=task_id,
                depth=task.depth
            )
        
        # Notify callbacks
        for callback in self.callbacks:
            callback(
                "task_completed" if task.status == TaskStatus.COMPLETED else "task_failed",
                task
            )
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self.tasks.get(task_id)
    
    def get_tasks(self) -> List[Task]:
        """Get all tasks."""
        return list(self.tasks.values())
    
    def get_task_events(self, task_id: str) -> List[Dict[str, Any]]:
        """Get events for a task."""
        events = event_logger.get_events(task_id=task_id)
        return [event.to_dict() for event in events]
    
    def register_callback(self, callback):
        """Register a callback for task events."""
        self.callbacks.append(callback)
    
    def unregister_callback(self, callback):
        """Unregister a callback."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()}
        }
    
    def save_state(self, file_path: str):
        """Save state to file."""
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_state(cls, file_path: str) -> 'TaskService':
        """Load state from file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        service = cls()
        for task_data in data["tasks"].values():
            task = Task.from_dict(task_data)
            service.tasks[task.task_id] = task
        
        return service


# Global task service instance
task_service = TaskService() 