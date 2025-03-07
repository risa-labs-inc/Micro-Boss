#!/bin/bash

# Microboss installer script

echo "⭐️ Installing Microboss ⭐️"
echo "------------------------"

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
else
    echo "Poetry is already installed."
fi

# Install dependencies with Poetry
echo "Installing dependencies with Poetry..."
poetry install

# Check for .env file
if [ ! -f .env ]; then
    echo ".env file not found. Creating one now..."
    
    # Create default .env file
    cat > .env << EOL
# Anthropic API key
ANTHROPIC_API_KEY=

# Configuration
DEFAULT_MODEL=claude-3-7-sonnet-20250219
MAX_TOKENS=4096
EOL
    
    echo ".env file created."
fi

# Set up API key if not already set
if ! grep -q "ANTHROPIC_API_KEY=." .env; then
    echo "ANTHROPIC_API_KEY is not set in .env file."
    echo "Would you like to set it now? (y/n)"
    read -r set_key
    
    if [[ "$set_key" =~ ^[Yy]$ ]]; then
        echo "Enter your Anthropic API key:"
        read -r api_key
        
        # Update the .env file
        sed -i '' "s/ANTHROPIC_API_KEY=/ANTHROPIC_API_KEY=$api_key/" .env
        echo "API key saved to .env file."
        
        # Add to current shell session
        export ANTHROPIC_API_KEY="$api_key"
        echo "API key added to current shell session."
    else
        echo "You can set the API key later by:"
        echo "1. Editing the .env file directly"
        echo "2. Exporting it: export ANTHROPIC_API_KEY=your-api-key"
        echo "3. Passing it via CLI: poetry run microboss \"task\" --api-key your-api-key"
    fi
else
    echo "ANTHROPIC_API_KEY is already set in .env file."
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Try running a simple task:"
echo "poetry run microboss \"Calculate the factorial of 5\""
echo "" 