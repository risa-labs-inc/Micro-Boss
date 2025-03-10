#!/usr/bin/env python
"""
Clean test script for verifying Anthropic API functionality.
This script checks if the Anthropic API key is configured correctly
and if the API is responding properly.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_anthropic():
    """Test the Anthropic API connection and functionality."""
    print("\n" + "=" * 60)
    print("🔍 ANTHROPIC API CONNECTION CHECK")
    print("=" * 60)
    
    # 1. Check if Anthropic package is installed
    try:
        import anthropic
        version = getattr(anthropic, "__version__", "unknown")
        print(f"✅ Anthropic package is installed (version: {version})")
    except ImportError:
        print("❌ Anthropic package is not installed.")
        print("   Run: poetry add anthropic")
        return False
    
    # 2. Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY environment variable is not set")
        print("   Add it to your .env file or set it in your environment")
        return False
    
    print(f"✅ API key found (starts with: {api_key[:5]}...)")
    
    # 3. Initialize the client
    try:
        client = anthropic.Anthropic(api_key=api_key)
        print("✅ Successfully initialized Anthropic client")
    except Exception as e:
        print(f"❌ Failed to initialize Anthropic client: {e}")
        return False
    
    # 4. Test API with a simple request
    print("\nSending test request to Anthropic API...")
    try:
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=50,
            messages=[
                {"role": "user", "content": "Respond with a brief confirmation message."}
            ]
        )
        
        # Display result
        result = response.content[0].text
        print("\n" + "-" * 40)
        print("RESPONSE FROM ANTHROPIC API:")
        print("-" * 40)
        print(result)
        print("-" * 40)
        
        print("\n✅ Anthropic API is working properly!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error making API request: {e}")
        print("\nTroubleshooting tips:")
        print("1. Verify your API key is correct")
        print("2. Check your network connection")
        print("3. Ensure you're using a compatible Anthropic package version")
        return False

if __name__ == "__main__":
    success = check_anthropic()
    exit(0 if success else 1) 