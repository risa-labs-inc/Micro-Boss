"""
Visualization utilities for Microboss.
"""

from typing import Dict, List, Any, Optional


def create_graph_data(decomposition_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert task decomposition data to a format suitable for visualization with vis.js.
    
    Args:
        decomposition_data: Dictionary containing 'subproblems' and 'levels' from decomposition,
                           or can be a list of subproblems directly
        
    Returns:
        Dictionary with 'nodes' and 'edges' for graph visualization
    """
    nodes = []
    edges = []
    
    # Handle different formats of decomposition data
    if isinstance(decomposition_data, list):
        # If passed a list directly, treat it as subproblems
        subproblems = decomposition_data
    else:
        # If passed a dictionary, extract subproblems
        subproblems = decomposition_data.get('subproblems', [])
    
    # Process subproblems to create nodes and edges
    for subproblem in subproblems:
        # Skip invalid subproblems
        if not isinstance(subproblem, dict):
            continue
            
        task_id = subproblem.get('id')
        description = subproblem.get('description', '')
        dependencies = subproblem.get('dependencies', [])
        status = subproblem.get('status', 'pending')
        
        # Ensure task_id is valid
        if not task_id:
            continue
            
        # Create node
        node = {
            'id': task_id,
            'label': f"{task_id[:6]}...",
            'title': description,
            'description': description,
            'status': status
        }
        
        nodes.append(node)
        
        # Create edges from dependencies
        for dep in dependencies:
            if dep:  # Ensure valid dependency ID
                edges.append({
                    'from': dep,
                    'to': task_id
                })
    
    # Return graph data
    return {
        'nodes': nodes,
        'edges': edges
    }


def create_timeline_data(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert log events to timeline visualization data.
    
    Args:
        events: List of log event dictionaries
        
    Returns:
        List of timeline event dictionaries for visualization
    """
    timeline_events: List[Dict[str, Any]] = []
    
    for event in events:
        level = event.get('level')
        message = event.get('message', '')
        timestamp = event.get('timestamp')
        
        # Skip events without required data
        if not (level and timestamp):
            continue
        
        # Create timeline event
        timeline_event = {
            'id': len(timeline_events),
            'level': level,
            'message': message,
            'time': timestamp,
            'formatted_time': event.get('formatted_time', '')
        }
        
        # Add additional data if available
        if 'data' in event:
            timeline_event['data'] = event['data']
            
        timeline_events.append(timeline_event)
    
    return timeline_events 