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
from microboss.utils.cleanup import cleanup_run_folders

# Load environment variables from .env file
load_dotenv()


def main():
    """Main entry point for the microboss CLI."""
    parser = argparse.ArgumentParser(
        description="Microboss: An AI agent system that decomposes complex tasks"
    )
    
    # Run command parameters
    parser.add_argument(
        "task",
        nargs="?",
        help="The task to be completed by the agent",
    )
    parser.add_argument(
        "--depth", "-d", type=int, default=1, help="Depth of task decomposition"
    )
    parser.add_argument(
        "--max-depth", "-m", type=int, default=10, help="Maximum depth of task decomposition"
    )
    parser.add_argument(
        "--max-retries", "-r", type=int, default=3, help="Maximum number of retries"
    )
    parser.add_argument(
        "--adaptive", "-a", action="store_true", help="Use adaptive depth"
    )
    parser.add_argument(
        "--timeout", "-t", type=int, default=600, help="Maximum execution time in seconds"
    )
    
    args = parser.parse_args()
    
    # Run cleanup with default settings (silently in background)
    # Keep 7 days of history and at least 10 latest runs
    _run_cleanup()
    
    # If task is provided, run the agent
    if args.task:
        _run_agent(args)
    else:
        # If no task is provided, show help
        parser.print_help()


def _run_cleanup():
    """Automatically run cleanup with reasonable defaults."""
    try:
        # Run cleanup in the background with reasonable defaults
        cleanup_run_folders(
            run_dir="run",
            keep_days=7,
            keep_latest=10,
            dry_run=False
        )
    except Exception as e:
        # Silently handle any errors during cleanup
        pass


def _run_agent(args):
    """Run the agent with the provided arguments."""
    task = args.task

    print("\n" + "=" * 80)
    print("🚀 STARTING MICROBOSS EXECUTION WITH ADAPTIVE DEPTH")
    print("=" * 80 + "\n")

    print(f"📋 TASK: {task}")
    print(f"⏰ START TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🤖 MODEL: {os.environ.get('DEFAULT_MODEL', 'claude-3-7-sonnet-20250219')}")
    print(f"🔍 ADAPTIVE MODE: Maximum depth {args.max_depth}")
    print(f"⏱️ TIMEOUT: {args.timeout} seconds")
    print()

    start_time = time.time()
    
    try:
        if args.adaptive:
            print("🧪 RUNNING WITH ADAPTIVE DEPTH:")
            result = agent(
                task,
                max_depth=args.max_depth,
                max_retries=args.max_retries,
                adaptive=True,
                timeout=args.timeout
            )
        else:
            print(f"📊 RUNNING WITH FIXED DEPTH {args.depth}:")
            result = agent(
                task,
                depth=args.depth,
                max_depth=args.max_depth,
                max_retries=args.max_retries,
                adaptive=False,
                timeout=args.timeout
            )
        
        # Display the actual result value
        if result:
            # Handle different result types
            if isinstance(result, dict):
                if "square_root" in result:
                    # Format square root calculations nicely
                    result_str = f"The square root of 16 is {result['square_root']}"
                else:
                    # Convert the dictionary to a readable string
                    result_str = ", ".join([f"{k}: {v}" for k, v in result.items()])
            else:
                result_str = str(result)
                
            # Truncate long results
            if len(result_str) > 100:
                result_str = result_str[:97] + "..."
                
            print(f"\n✅ EXECUTION RESULT: {result_str}")
        else:
            print("\n✅ EXECUTION RESULT: Task completed but no specific result was returned")
    except TimeoutError as e:
        print(f"\n⏱️ EXECUTION TIMED OUT: {e}")
    except Exception as e:
        print(f"\n❌ EXECUTION FAILED: {e}")
    
    execution_time = time.time() - start_time
    print("\n" + "=" * 80)
    print(f"✅ MICROBOSS EXECUTION COMPLETED IN {execution_time:.2f}s")
    print(f"⏰ END TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


if __name__ == "__main__":
    main() 