"""
Web application for the Microboss package.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import logging

import markdown
from flask import (
    Flask, render_template, request, jsonify, 
    redirect, url_for, send_from_directory
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


# Event handlers for logging and task events
def on_log_event(event: LogEvent):
    """Handle a log event by broadcasting it to connected clients."""
    socketio.emit("log_event", event.to_dict())


def on_task_event(event_type: str, task: Task):
    """Handle a task event by broadcasting it to connected clients."""
    socketio.emit("task_event", {
        "event_type": event_type,
        "task": task.to_dict()
    })


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
        
        task = task_service.create_task(
            description=task_description,
            depth=depth,
            max_retries=max_retries,
            max_decomposition_depth=max_decomposition_depth
        )
        
        # Immediately start the task
        task_service.start_task(task.task_id)
        
        return redirect(url_for("task_detail", task_id=task.task_id))
    
    # GET request - list tasks
    tasks = task_service.get_tasks()
    tasks.sort(key=lambda t: t.created_at, reverse=True)
    return render_template("tasks.html", tasks=tasks)


@app.route("/tasks/<task_id>")
def task_detail(task_id: str):
    """Render the task detail page."""
    task = task_service.get_task(task_id)
    if not task:
        return render_template("error.html", message=f"Task {task_id} not found"), 404
    
    # Get task events
    events = event_logger.get_events(task_id=task_id)
    
    return render_template("task_detail.html", task=task, events=events)


@app.route("/api/tasks", methods=["GET", "POST"])
def api_tasks():
    """API endpoint for tasks."""
    if request.method == "POST":
        # Handle both form data and JSON requests
        if request.is_json:
            data = request.json or {}
            task_description = data.get("description", "") or data.get("task", "")
        else:
            # Handle form data
            task_description = request.form.get("task", "") or request.form.get("task_description", "")
            
        # Ensure we have a valid task description
        if not task_description:
            task_description = "Calculate factorial of 5"  # Default task if none provided
            
        # Log the task description for debugging
        logging.info(f"API created task: {task_description}")
        
        # Get other parameters from form or JSON
        if request.is_json:
            data = request.json or {}
            depth = data.get("depth", 1)
            max_retries = data.get("max_retries", 3)
            max_decomposition_depth = data.get("max_decomposition_depth", 10)
        else:
            depth = int(request.form.get("depth", 1))
            max_retries = int(request.form.get("max_retries", 3))
            max_decomposition_depth = int(request.form.get("max_decomposition_depth", 10))
        
        task = task_service.create_task(
            description=task_description,
            depth=depth,
            max_retries=max_retries,
            max_decomposition_depth=max_decomposition_depth
        )
        
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
    """API endpoint for task events."""
    events = task_service.get_task_events(task_id)
    return jsonify(events)


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