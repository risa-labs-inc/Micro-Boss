"""
Command-line interface for the microboss package.
"""

import argparse
import os
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from microboss.core.agent import agent

# Load environment variables from .env file
load_dotenv()


def main():
    """Main entry point for the microboss CLI."""
    parser = argparse.ArgumentParser(
        description="Microboss: An AI agent system that decomposes complex tasks"
    )
    parser.add_argument(
        "task",
        type=str,
        help="The task to solve"
    )
    parser.add_argument(
        "--depth",
        "-d",
        type=int,
        default=1,
        help="The decomposition depth (default: 1)"
    )
    parser.add_argument(
        "--retries",
        "-r",
        type=int,
        default=3,
        help="Maximum number of retries on failure (default: 3)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="Anthropic API key (will use ANTHROPIC_API_KEY environment variable if not provided)"
    )
    parser.add_argument(
        "--model",
        type=str,
        help=f"Model to use (default: {os.environ.get('DEFAULT_MODEL', 'claude-3-7-sonnet-20250219')})"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        help=f"Maximum tokens for API responses (default: {os.environ.get('MAX_TOKENS', 4096)})"
    )
    
    args = parser.parse_args()
    
    # Set environment variables if provided via CLI
    if args.api_key:
        os.environ["ANTHROPIC_API_KEY"] = args.api_key
    
    if args.model:
        os.environ["DEFAULT_MODEL"] = args.model
    
    if args.max_tokens:
        os.environ["MAX_TOKENS"] = str(args.max_tokens)
    
    # Print the header
    print("\n" + "="*80)
    print(f"🚀 STARTING MICROBOSS EXECUTION")
    print("="*80)
    
    print(f"\n📋 TASK: {args.task}")
    print(f"⏰ START TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🤖 MODEL: {os.environ.get('DEFAULT_MODEL', 'claude-3-7-sonnet-20250219')}")
    
    start_time = time.time()
    
    try:
        print(f"\n🧪 RUNNING WITH DEPTH {args.depth}:")
        result = agent(args.task, depth=args.depth, max_retries=args.retries)
        print(f"\n✅ EXECUTION RESULT SUMMARY: Successfully executed task with {len(str(result)) if result else 0} characters of solution")
    except Exception as e:
        print(f"\n❌ EXECUTION FAILED: {e}")
    
    print(f"\n{'='*80}")
    print(f"✅ MICROBOSS EXECUTION COMPLETED IN {time.time() - start_time:.2f}s")
    print(f"⏰ END TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")


if __name__ == "__main__":
    main() 