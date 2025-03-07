"""
Helpers for the Microboss web application.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


def register_template_filters(app):
    """Register custom template filters for the Flask app."""
    
    @app.template_filter('datetime')
    def format_datetime(timestamp):
        """Format a Unix timestamp as a human-readable date and time."""
        if not timestamp:
            return "-"
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    
    @app.template_filter('duration')
    def format_duration(seconds):
        """Format a duration in seconds as a human-readable string."""
        if not seconds:
            return "-"
        
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            rem_seconds = int(seconds % 60)
            return f"{minutes}m {rem_seconds}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    @app.template_filter('pretty_json')
    def pretty_json(value):
        """Format JSON data as a pretty-printed string."""
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                pass
        
        return json.dumps(value, indent=2, sort_keys=True, default=str)
    
    @app.template_filter('truncate')
    def truncate_string(s, length=50, end='...'):
        """Truncate a string to a specific length."""
        if not s:
            return ""
        if len(s) <= length:
            return s
        return s[:length] + end


def create_graph_data(subproblems, levels, task_results=None):
    """
    Create a graph data structure for visualization from task decomposition data.
    
    Args:
        subproblems: List of (id, template, deps) tuples
        levels: List of levels, each containing subproblems
        task_results: Optional dictionary of task results
    
    Returns:
        Dict containing nodes and edges
    """
    task_results = task_results or {}
    
    # Create nodes
    nodes = []
    for task_id, template, deps in subproblems:
        status = "pending"
        if task_id in task_results:
            result = task_results[task_id]
            if isinstance(result, str) and result.startswith("Failed"):
                status = "failed"
            else:
                status = "completed"
        
        # Truncate template for label
        label = template
        if len(label) > 30:
            label = label[:27] + "..."
        
        nodes.append({
            "id": task_id,
            "label": label,
            "description": template,
            "status": status
        })
    
    # Create edges
    edges = []
    for task_id, _, deps in subproblems:
        for dep in deps:
            edges.append({
                "from": dep,
                "to": task_id
            })
    
    return {
        "nodes": nodes,
        "edges": edges
    } 