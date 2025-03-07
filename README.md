# Microboss

An AI agent system that decomposes complex tasks into simpler subproblems and generates code to solve them.

## Features

- 🧠 AI-powered task decomposition
- 🔄 Recursive problem-solving approach
- 📝 Automatic code generation
- 🔧 Robust error handling and retries
- 📂 Organized file-based execution
- 📊 Detailed execution logging

## Installation

To install the package, use Poetry:

```bash
# Clone the repository
git clone https://github.com/yourusername/microboss.git
cd microboss

# Install with Poetry
poetry install
```

Or use the install script which also sets up the environment:

```bash
./install.sh
```

## Configuration

Microboss uses environment variables for configuration. You can set them in a `.env` file in the project root:

```
# Anthropic API key (required)
ANTHROPIC_API_KEY=your-api-key

# Configuration (optional)
DEFAULT_MODEL=claude-3-7-sonnet-20250219
MAX_TOKENS=4096
```

The install script will create this file for you and ask for your API key.

## Usage

### Command Line Interface

```bash
# Basic usage
poetry run microboss "Calculate the factorial of 10"

# With depth for complex tasks
poetry run microboss "Implement a weather forecasting system that predicts temperature based on historical data" --depth 2

# With custom retry count
poetry run microboss "Generate a Fibonacci sequence" --retries 5

# Providing API key directly
poetry run microboss "Solve this equation: 3x + 5 = 14" --api-key your-api-key
```

### Python API

```python
from microboss import agent

# Simple task
result = agent("Calculate the factorial of 10")
print(result)  # Output: 3628800

# Complex task with decomposition
result = agent(
    "Implement a weather forecasting system that predicts temperature based on historical data",
    depth=2,
    max_retries=3
)
print(result)  # Output: Generated weather forecasting system
```

## Environment Variables

- `ANTHROPIC_API_KEY`: Your Anthropic API key (required)
- `DEFAULT_MODEL`: The model to use for API calls (default: claude-3-7-sonnet-20250219)
- `MAX_TOKENS`: Maximum tokens for API responses (default: 4096)

## Directory Structure

The code is organized into a proper Python package with the following structure:

```
microboss/
├── __init__.py             # Package initialization
├── cli.py                  # Command-line interface
├── core/                   # Core functionality
│   ├── __init__.py
│   └── agent.py            # Main agent implementation
└── utils/                  # Utility modules
    ├── __init__.py
    ├── api.py              # API client utilities
    ├── execution.py        # Code execution utilities
    └── file_utils.py       # File handling utilities
```

## Output Structure

When you run the agent, it creates a structured output in the `run` directory:

```
run/
└── TIMESTAMP_task_name/
    ├── main.py             # Generated code for the task
    ├── result.json         # Result of the execution
    └── decomposed/         # For depth > 1
        ├── decomposition.json  # Task decomposition details
        └── subtasks/       # Individual subtasks
            └── level_0/    # Tasks at level 0
                └── id1/    # Task with ID "id1"
                    ├── result.json  # Result of the subtask
                    └── ...
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 