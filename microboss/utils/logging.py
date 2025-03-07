"""
Logging utilities for the microboss package.
"""

import json
import logging
import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

# Set up logger
logger = logging.getLogger("microboss")
logger.setLevel(logging.INFO)

# Add console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class LogLevel(Enum):
    """Log levels for Microboss events."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"
    TASK = "task"
    CODE = "code"
    RESULT = "result"
    EXECUTION = "execution"


class LogEvent:
    """Event logged by Microboss."""
    
    def __init__(
        self,
        level: LogLevel,
        message: str,
        task_id: Optional[str] = None,
        subtask_id: Optional[str] = None,
        depth: Optional[int] = None,
        timestamp: Optional[float] = None,
        data: Optional[Dict[str, Any]] = None,
        parent_id: Optional[str] = None
    ):
        self.level = level
        self.message = message
        self.task_id = task_id
        self.subtask_id = subtask_id
        self.depth = depth
        self.timestamp = timestamp or time.time()
        self.data = data or {}
        self.parent_id = parent_id
        self.formatted_time = datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "level": self.level.value,
            "message": self.message,
            "task_id": self.task_id,
            "subtask_id": self.subtask_id,
            "depth": self.depth,
            "timestamp": self.timestamp,
            "formatted_time": self.formatted_time,
            "data": self.data,
            "parent_id": self.parent_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LogEvent':
        """Create LogEvent from dictionary."""
        return cls(
            level=LogLevel(data["level"]),
            message=data["message"],
            task_id=data.get("task_id"),
            subtask_id=data.get("subtask_id"),
            depth=data.get("depth"),
            timestamp=data.get("timestamp"),
            data=data.get("data", {}),
            parent_id=data.get("parent_id")
        )


class EventLogger:
    """Logger for Microboss events with support for web visualization."""
    
    def __init__(self):
        self.events: List[LogEvent] = []
        self.callbacks = []
    
    def log(
        self,
        level: LogLevel,
        message: str,
        task_id: Optional[str] = None,
        subtask_id: Optional[str] = None,
        depth: Optional[int] = None,
        data: Optional[Dict[str, Any]] = None,
        parent_id: Optional[str] = None
    ) -> LogEvent:
        """Log an event."""
        event = LogEvent(level, message, task_id, subtask_id, depth, None, data, parent_id)
        self.events.append(event)
        
        # Also log to Python logger
        if level == LogLevel.ERROR:
            logger.error(message)
        elif level == LogLevel.WARNING:
            logger.warning(message)
        else:
            logger.info(message)
        
        # Call any registered callbacks
        for callback in self.callbacks:
            callback(event)
        
        return event
    
    def register_callback(self, callback):
        """Register a callback for new events."""
        self.callbacks.append(callback)
    
    def unregister_callback(self, callback):
        """Unregister a callback."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def get_events(
        self,
        task_id: Optional[str] = None,
        subtask_id: Optional[str] = None,
        level: Optional[LogLevel] = None,
        depth: Optional[int] = None
    ) -> List[LogEvent]:
        """Get filtered events."""
        filtered = self.events
        
        if task_id is not None:
            filtered = [e for e in filtered if e.task_id == task_id]
        
        if subtask_id is not None:
            filtered = [e for e in filtered if e.subtask_id == subtask_id]
        
        if level is not None:
            filtered = [e for e in filtered if e.level == level]
        
        if depth is not None:
            filtered = [e for e in filtered if e.depth == depth]
        
        return filtered
    
    def clear(self):
        """Clear all events."""
        self.events = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "events": [event.to_dict() for event in self.events]
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'EventLogger':
        """Create EventLogger from JSON string."""
        data = json.loads(json_str)
        logger = cls()
        logger.events = [LogEvent.from_dict(event) for event in data["events"]]
        return logger
    
    def save(self, file_path: str):
        """Save events to file."""
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, file_path: str) -> 'EventLogger':
        """Load events from file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        logger = cls()
        logger.events = [LogEvent.from_dict(event) for event in data["events"]]
        return logger


# Global logger instance
event_logger = EventLogger()


# Convenience functions
def log_info(message: str, **kwargs) -> LogEvent:
    """Log an info message."""
    return event_logger.log(LogLevel.INFO, message, **kwargs)

def log_success(message: str, **kwargs) -> LogEvent:
    """Log a success message."""
    return event_logger.log(LogLevel.SUCCESS, message, **kwargs)

def log_warning(message: str, **kwargs) -> LogEvent:
    """Log a warning message."""
    return event_logger.log(LogLevel.WARNING, message, **kwargs)

def log_error(message: str, **kwargs) -> LogEvent:
    """Log an error message."""
    return event_logger.log(LogLevel.ERROR, message, **kwargs)

def log_debug(message: str, **kwargs) -> LogEvent:
    """Log a debug message."""
    return event_logger.log(LogLevel.DEBUG, message, **kwargs)

def log_task(message: str, **kwargs) -> LogEvent:
    """Log a task message."""
    return event_logger.log(LogLevel.TASK, message, **kwargs)

def log_code(message: str, code: str, **kwargs) -> LogEvent:
    """Log code."""
    data = {"code": code}
    return event_logger.log(LogLevel.CODE, message, data=data, **kwargs)

def log_result(message: str, result: Any, **kwargs) -> LogEvent:
    """Log a result."""
    # Convert result to string for display purposes
    result_str = str(result) if result is not None else "None"
    
    # Create data object with raw and formatted results
    data = {
        "result": result_str,
        "result_type": type(result).__name__ if result is not None else "NoneType"
    }
    
    # For numeric results, add formatted display
    if isinstance(result, (int, float)):
        data["formatted_result"] = f"{result:,}"
    
    # For factorials, add extra context
    if message.lower().startswith("final result") and isinstance(result, int) and result > 1000000:
        data["description"] = f"Factorial calculation complete. Result: {result:,}"
    
    return event_logger.log(LogLevel.RESULT, message, data=data, **kwargs)

def log_execution(message: str, stdout: str = "", stderr: str = "", **kwargs) -> LogEvent:
    """Log execution output."""
    data = {"stdout": stdout, "stderr": stderr}
    return event_logger.log(LogLevel.EXECUTION, message, data=data, **kwargs) 