"""
Web application for the Microboss package.
"""

import json
import os
import glob
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import logging

import markdown
from flask import (
    Flask, render_template, request, jsonify, 
    redirect, url_for, send_from_directory, session, flash
)
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import requests
import anthropic
import openai

from microboss.utils.logging import event_logger, LogEvent, LogLevel
from microboss.web.services import task_service, Task, TaskStatus
from microboss.web.helpers import register_template_filters, create_graph_data


# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "microboss-secret-key")
socketio = SocketIO(app)

# Register template filters
register_template_filters(app)


# Helper function to get available models based on API keys
def get_available_models():
    """Check available API keys and return available models.
    
    Returns:
        dict: Dictionary with provider names as keys and list of models as values
    """
    available_models = {}
    
    # Check for Anthropic API Key
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if anthropic_key:
        try:
            # Try a simple validation of the key
            if len(anthropic_key) > 20 and anthropic_key.startswith("sk-ant"):
                available_models["Anthropic"] = [
                    "claude-3-7-sonnet-20250219", 
                    "claude-3-5-sonnet-20240620", 
                    "claude-3-opus-20240229"
                ]
        except Exception as e:
            logging.warning(f"Error validating Anthropic API key: {str(e)}")
    
    # Check for OpenAI API Key
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        try:
            # Try a simple validation of the key
            if len(openai_key) > 20 and (openai_key.startswith("sk-") or openai_key.startswith("sk-proj")):
                available_models["OpenAI"] = [
                    "gpt-4o-2024-05-13", 
                    "gpt-4-turbo", 
                    "gpt-4"
                ]
        except Exception as e:
            logging.warning(f"Error validating OpenAI API key: {str(e)}")
    
    return available_models


# Event handlers for logging and task events
def on_log_event(event: LogEvent):
    """Handle log events."""
    # Convert LogEvent to dictionary for JSON serialization
    event_dict = event.to_dict()
    
    # Log the event emission for debugging
    print(f"Emitting log event: {event.level.value} - {event.message[:50]}...")
    
    # Emit the event to all connected clients
    try:
        socketio.emit('log_event', event_dict)
    except Exception as e:
        print(f"Error emitting log event: {e}")
        app.logger.error(f"Error emitting log event: {e}")


def on_task_event(event_type: str, task: Task):
    """Handle task events."""
    # Convert Task to dictionary for JSON serialization
    task_dict = task.to_dict()
    
    # Log the event emission for debugging
    print(f"Emitting task event: {event_type} for task {task.task_id}")
    
    # Emit the event to all connected clients
    try:
        socketio.emit('task_event', {
            'event_type': event_type,
            'task': task_dict
        })
    except Exception as e:
        print(f"Error emitting task event: {e}")
        app.logger.error(f"Error emitting task event: {e}")


# Register event handlers
event_logger.register_callback(on_log_event)
task_service.register_callback(on_task_event)


# Flask routes

@app.route("/")
def home():
    """Render the home page."""
    return render_template("index.html")


@app.route("/tasks", methods=["GET", "POST"])
def tasks():
    """Handle task listing and creation."""
    if request.method == "POST":
        # Create a new task
        task_description = request.form.get("task", "") or request.form.get("task_description", "")
        
        # Ensure we have a valid task description
        if not task_description:
            task_description = "Calculate factorial of 5"  # Default task if none provided
            
        # Log the task description for debugging
        logging.info(f"Created task: {task_description}")
            
        depth = int(request.form.get("depth", 1))
        max_retries = int(request.form.get("max_retries", 3))
        max_decomposition_depth = int(request.form.get("max_decomposition_depth", 10))
        
        # Get the selected model if provided
        selected_model = request.form.get("selected_model")
        
        task = task_service.create_task(
            description=task_description,
            depth=depth,
            max_retries=max_retries,
            max_decomposition_depth=max_decomposition_depth
        )
        
        # Set environment variable for model if provided
        if selected_model:
            os.environ["DEFAULT_MODEL"] = selected_model
            logging.info(f"Using selected model: {selected_model}")
        
        # Immediately start the task
        task_service.start_task(task.task_id)
        
        return redirect(url_for("task_detail", task_id=task.task_id))
    
    # GET request - list tasks
    tasks = task_service.get_tasks()
    tasks.sort(key=lambda t: t.created_at, reverse=True)
    
    # Get available models for the dropdown
    available_models = get_available_models()
    
    return render_template("tasks.html", tasks=tasks, available_models=available_models)


@app.route("/tasks/<task_id>")
def task_detail(task_id: str):
    """Display detailed information about a task."""
    task = task_service.get_task(task_id)
    if not task:
        return redirect(url_for("tasks"))
    
    # Get task events
    try:
        task_events = event_logger.get_events(task_id=task_id)
        # Convert LogEvents to dictionaries for the template
        events = [event.to_dict() for event in task_events]
        print(f"Loaded {len(events)} events for task {task_id}")
    except Exception as e:
        app.logger.error(f"Error loading events for task {task_id}: {e}")
        events = []
    
    # Initialize graph data
    graph_data = None
    
    # Try to find task decomposition data from the run directory
    try:
        # Get all subdirectories in the 'run' directory
        run_dir = Path("run")
        if run_dir.exists() and run_dir.is_dir():
            # Find run directories that match this task (by description)
            task_dirs = [d for d in run_dir.iterdir() if d.is_dir() and d.name.endswith(task.description.lower().replace(' ', '_')[:30])]
            
            # Sort by modification time (newest first)
            task_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            decomp_file = None
            for task_dir in task_dirs:
                # Check for decomposition file
                decomp_path = task_dir / "decomposed" / "decomposition.json"
                if decomp_path.exists():
                    decomp_file = decomp_path
                    app.logger.info(f"Trying decomposition data from: {decomp_file}")
                    print(f"Trying decomposition data from: {decomp_file}")
                    break
            
            if decomp_file:
                with open(decomp_file, 'r') as f:
                    decomp_data = json.load(f)
                
                if decomp_data:
                    # Create graph data from decomposition data
                    try:
                        # Handle different decomposition data structures
                        # Some may be lists, others may be dictionaries with 'subproblems' and 'levels' keys
                        if isinstance(decomp_data, list):
                            # If decomp_data is a list, assume it's a list of subproblems
                            subproblems = decomp_data
                            levels: List[Dict[str, Any]] = []  # No levels data available
                            
                            app.logger.info(f"Found decomposition data in list format: {len(subproblems)} subproblems")
                            print(f"Found decomposition data in list format: {len(subproblems)} subproblems")
                            
                            # Create a compatible format for visualization
                            formatted_data = {
                                "subproblems": subproblems,
                                "levels": levels
                            }
                        else:
                            # If decomp_data is a dictionary, use it directly
                            formatted_data = decomp_data
                            
                            # Log what we found for debugging
                            subproblems = formatted_data.get('subproblems', [])
                            levels = formatted_data.get('levels', [])
                            
                            app.logger.info(f"Found decomposition data in dict format: {len(subproblems)} subproblems, {len(levels)} levels")
                            print(f"Found decomposition data in dict format: {len(subproblems)} subproblems, {len(levels)} levels")
                        
                        # Create graph data using the viz module
                        from microboss.utils.viz import create_graph_data
                        graph_data = create_graph_data(formatted_data)
                    except ImportError:
                        # Fallback implementation if viz module is not available
                        print("Using fallback graph data creation since microboss.utils.viz is not available")
                        
                        # Simple fallback implementation
                        nodes = []
                        edges = []
                        
                        # Process subproblems based on data structure
                        if isinstance(decomp_data, list):
                            subproblems = decomp_data
                        else:
                            subproblems = decomp_data.get('subproblems', [])
                        
                        for subproblem in subproblems:
                            task_id = subproblem.get('id')
                            description = subproblem.get('description', '')
                            dependencies = subproblem.get('dependencies', [])
                            status = subproblem.get('status', 'pending')
                            
                            if task_id:
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
                                    if dep:
                                        edges.append({
                                            'from': dep,
                                            'to': task_id
                                        })
                        
                        graph_data = {
                            'nodes': nodes,
                            'edges': edges
                        }
                    
                    # Try to associate results from task events
                    if graph_data and 'nodes' in graph_data:
                        result_events = [e for e in events if e['level'] == 'result']
                        for node in graph_data['nodes']:
                            for event in result_events:
                                if event.get('task_id') == node['id']:
                                    node['result'] = event.get('data', {}).get('result')
                    
                    # Log decomposition results
                    if isinstance(decomp_data, list):
                        app.logger.info(f"Processed list-format decomposition data: {len(decomp_data)} items")
                        print(f"Processed list-format decomposition data: {len(decomp_data)} items")
                    else:
                        subproblems_count = len(decomp_data.get('subproblems', []))
                        levels_count = len(decomp_data.get('levels', []))
                        app.logger.info(f"Processed dict-format decomposition data: {subproblems_count} subproblems, {levels_count} levels")
                        print(f"Processed dict-format decomposition data: {subproblems_count} subproblems, {levels_count} levels")
                else:
                    app.logger.warning(f"Empty decomposition data found in {decomp_file}")
                    print(f"Empty decomposition data found in {decomp_file}")
            else:
                app.logger.warning(f"No decomposition data found for task {task_id}")
                print(f"No decomposition data found for task {task_id}")
    except Exception as e:
        app.logger.error(f"Error loading decomposition data: {str(e)}")
        print(f"Error loading decomposition data: {str(e)}")
        import traceback
        traceback.print_exc()  # More detailed error information
    
    return render_template(
        "task_detail.html", 
        task=task, 
        events=events,
        graph_data=graph_data
    )


@app.route("/api/tasks", methods=["GET", "POST"])
def api_tasks():
    """API endpoint for tasks."""
    if request.method == "POST":
        # Handle both form data and JSON requests
        if request.is_json:
            data = request.json or {}
            task_description = data.get("description", "") or data.get("task", "")
            depth = data.get("depth", 1)
            max_retries = data.get("max_retries", 3)
            max_decomposition_depth = data.get("max_decomposition_depth", 10)
            selected_model = data.get("selected_model")
        else:
            # Handle form data
            task_description = request.form.get("task", "") or request.form.get("task_description", "")
            depth = int(request.form.get("depth", 1))
            max_retries = int(request.form.get("max_retries", 3))
            max_decomposition_depth = int(request.form.get("max_decomposition_depth", 10))
            selected_model = request.form.get("selected_model")
            
        # Ensure we have a valid task description
        if not task_description:
            task_description = "Calculate factorial of 5"  # Default task if none provided
            
        # Log the task description for debugging
        logging.info(f"API created task: {task_description}")
        
        task = task_service.create_task(
            description=task_description,
            depth=depth,
            max_retries=max_retries,
            max_decomposition_depth=max_decomposition_depth
        )
        
        # Set environment variable for model if provided
        if selected_model:
            os.environ["DEFAULT_MODEL"] = selected_model
            logging.info(f"API using selected model: {selected_model}")
        
        # Auto-start if requested
        if data.get("auto_start", True):
            task_service.start_task(task.task_id)
        
        return jsonify(task.to_dict())
    
    # GET request - list tasks
    tasks = task_service.get_tasks()
    return jsonify([task.to_dict() for task in tasks])


@app.route("/api/tasks/<task_id>", methods=["GET", "POST"])
def api_task_detail(task_id: str):
    """API endpoint for task details."""
    task = task_service.get_task(task_id)
    if not task:
        return jsonify({"error": f"Task {task_id} not found"}), 404
    
    if request.method == "POST":
        # Start the task
        task_service.start_task(task_id)
    
    return jsonify(task.to_dict())


@app.route("/api/tasks/<task_id>/events")
def api_task_events(task_id: str):
    """API endpoint to get events for a specific task."""
    events = event_logger.get_events(task_id=task_id)
    
    # Convert events to dictionaries with proper formatting for timeline
    event_dicts = []
    for event in events:
        event_dict = event.to_dict()
        
        # Ensure formatted_time is available
        if 'timestamp' in event_dict and not event_dict.get('formatted_time'):
            event_time = datetime.fromtimestamp(event_dict['timestamp'])
            event_dict['formatted_time'] = event_time.strftime('%H:%M:%S')
            
        event_dicts.append(event_dict)
    
    # Log that we're serving events
    print(f"Serving {len(event_dicts)} events for task {task_id}")
    
    return jsonify(event_dicts)


@app.route("/api/events")
def api_events():
    """API endpoint for all events."""
    events = [event.to_dict() for event in event_logger.events]
    return jsonify(events)


@app.route("/api/test-key")
def test_api_key():
    """Test the API keys and return the result."""
    results = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "pending",
        "details": []
    }
    
    # Step 1: Check for Anthropic API key
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if anthropic_key:
        # Log key format (safely)
        key_prefix = anthropic_key[:8] if len(anthropic_key) >= 8 else anthropic_key
        key_suffix = anthropic_key[-4:] if len(anthropic_key) >= 4 else ""
        results["details"].append({
            "step": "Check Anthropic API Key",
            "status": "success",
            "message": f"Found Anthropic API key: {key_prefix}...{key_suffix}"
        })
        
        # Step 2: Verify Anthropic key format
        if not anthropic_key.startswith("sk-ant-"):
            results["details"].append({
                "step": "Validate Anthropic Key Format", 
                "status": "warning",
                "message": "Anthropic API key does not start with expected prefix 'sk-ant-'"
            })
        else:
            results["details"].append({
                "step": "Validate Anthropic Key Format",
                "status": "success",
                "message": "Anthropic API key has correct prefix"
            })
        
        # Step 3: Test Anthropic API connection
        try:
            # Create the Anthropic client safely without 'proxies' parameter
            # Use kwargs to avoid errors with unsupported parameters
            client_kwargs = {"api_key": anthropic_key}
            
            # Create client with only the API key parameter
            client = anthropic.Anthropic(**client_kwargs)
            
            results["details"].append({
                "step": "Create Anthropic Client",
                "status": "success",
                "message": "Successfully created Anthropic client"
            })
            
            # Make a test request using the Messages API
            response = client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=20,
                messages=[
                    {"role": "user", "content": "Say hello"}
                ]
            )
            
            # Check for a successful response
            if response and response.content:
                message_text = response.content[0].text
                results["status"] = "success"
                results["details"].append({
                    "step": "Anthropic API Response",
                    "status": "success",
                    "message": f"Received valid response: {message_text.strip()}"
                })
                # Successful Anthropic test, return early
                return jsonify(results)
            else:
                results["details"].append({
                    "step": "Anthropic API Response",
                    "status": "error",
                    "message": "Received empty response from API"
                })
                
        except anthropic.APIError as e:
            status_code = getattr(e, "status_code", None)
            if status_code == 401:
                results["details"].append({
                    "step": "Anthropic API Response",
                    "status": "error",
                    "message": "Anthropic API key is invalid (401 Unauthorized)"
                })
            else:
                results["details"].append({
                    "step": "Anthropic API Response",
                    "status": "error",
                    "message": f"Anthropic API error: {str(e)}"
                })
        except Exception as e:
            results["details"].append({
                "step": "Anthropic API Request",
                "status": "error",
                "message": f"Exception: {str(e)}"
            })
    else:
        results["details"].append({
            "step": "Check Anthropic API Key",
            "status": "warning",
            "message": "No Anthropic API key found in environment variables"
        })
    
    # If we get here, Anthropic failed or wasn't found, try OpenAI as fallback
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        # Log key format (safely)
        key_prefix = openai_key[:8] if len(openai_key) >= 8 else openai_key
        key_suffix = openai_key[-4:] if len(openai_key) >= 4 else ""
        results["details"].append({
            "step": "Check OpenAI API Key",
            "status": "success",
            "message": f"Found OpenAI API key: {key_prefix}...{key_suffix}"
        })
        
        # Verify OpenAI key format (sk-)
        if not openai_key.startswith("sk-"):
            results["details"].append({
                "step": "Validate OpenAI Key Format", 
                "status": "warning",
                "message": "OpenAI API key does not start with expected prefix 'sk-'"
            })
        else:
            results["details"].append({
                "step": "Validate OpenAI Key Format",
                "status": "success",
                "message": "OpenAI API key has correct prefix"
            })
        
        # Test OpenAI API connection
        try:
            # Check for custom base URL or organization
            base_url = os.environ.get("OPENAI_API_BASE")
            org_id = os.environ.get("OPENAI_ORGANIZATION")
            
            # Create the client with supported parameters
            kwargs = {"api_key": openai_key}
            if base_url:
                kwargs["base_url"] = base_url
            if org_id:
                kwargs["organization"] = org_id
                
            # Initialize the OpenAI client
            client = openai.OpenAI(**kwargs)
            
            results["details"].append({
                "step": "Create OpenAI Client",
                "status": "success",
                "message": "Successfully created OpenAI client"
            })
            
            # Make a test request using the ChatCompletions API
            response = client.chat.completions.create(
                model="gpt-4o-2024-05-13",  # Latest GPT model
                max_tokens=20,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say hello"}
                ]
            )
            
            # Check for a successful response
            if response and response.choices:
                message_text = response.choices[0].message.content
                results["status"] = "success"
                results["details"].append({
                    "step": "OpenAI API Response",
                    "status": "success",
                    "message": f"Received valid response: {message_text.strip()}"
                })
            else:
                results["details"].append({
                    "step": "OpenAI API Response",
                    "status": "error",
                    "message": "Received empty response from API"
                })
                
        except Exception as e:
            results["status"] = "error"
            results["details"].append({
                "step": "OpenAI API Request",
                "status": "error",
                "message": f"Exception: {str(e)}"
            })
    else:
        results["details"].append({
            "step": "Check OpenAI API Key",
            "status": "warning",
            "message": "No OpenAI API key found in environment variables"
        })
    
    # If we get here with pending status, it means neither API worked
    if results["status"] == "pending":
        results["status"] = "error"
        results["details"].append({
            "step": "API Test Summary",
            "status": "error",
            "message": "All available APIs failed. Please check API keys and try again."
        })
    
    return jsonify(results)


@app.route("/test-key")
def test_key_page():
    """Render a page that tests the API key."""
    return render_template(
        "test_key.html", 
        title="API Key Test"
    )


@app.route("/api/tasks/<task_id>/debug/timeline-test", methods=["GET"])
def api_task_debug_timeline(task_id: str):
    """Debug API endpoint to generate test timeline events for a task."""
    task = task_service.get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    # Create a few test events for the timeline
    event_types = ["info", "warning", "success", "code", "result", "error"]
    messages = [
        "Starting task execution",
        "Processing input data",
        "Generating code for task",
        "Code execution complete",
        "Task completed successfully",
        "Warning: resource usage is high"
    ]
    
    for i, (level, message) in enumerate(zip(event_types, messages)):
        timestamp = time.time() - (len(messages) - i) * 60  # Spread events over time
        event_data = {}
        
        if level == "code":
            event_data["code"] = "def factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n-1)\n\nresult = factorial(10)"
        elif level == "result":
            event_data["result"] = "The factorial of 10 is 3,628,800"
        
        # Create the event
        event = LogEvent(
            level=LogLevel(level),
            message=message,
            task_id=task_id,
            timestamp=timestamp,
            data=event_data
        )
        
        # Emit event
        socketio.emit('log_event', event.to_dict())
        time.sleep(0.5)  # Small delay between events
    
    return jsonify({"status": "success", "message": f"Generated {len(messages)} test events for task {task_id}"})


# SocketIO events

@socketio.on("connect")
def handle_connect():
    """Handle client connection."""
    emit("connected", {"status": "connected"})


@socketio.on("disconnect")
def handle_disconnect():
    """Handle client disconnection."""
    pass


@socketio.on("start_task")
def handle_start_task(data):
    """Handle task start request."""
    task_id = data["task_id"]
    try:
        task = task_service.start_task(task_id)
        emit("task_started", task.to_dict())
    except Exception as e:
        emit("error", {"message": str(e)})


# Main entry point
def main():
    """Run the web application."""
    host = os.environ.get("MICROBOSS_HOST", "127.0.0.1")
    port = int(os.environ.get("MICROBOSS_PORT", 5000))
    debug = os.environ.get("MICROBOSS_DEBUG", "false").lower() == "true"
    
    print(f"Starting Microboss web interface at http://{host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    main() 