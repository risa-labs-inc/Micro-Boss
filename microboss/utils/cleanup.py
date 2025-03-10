"""
Utility for cleaning up run folders in the Microboss project.
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def cleanup_run_folders(
    run_dir: str = "run",
    keep_days: int = 7,
    keep_latest: int = 10,
    dry_run: bool = False
) -> None:
    """
    Cleanup old run folders in the specified directory.
    
    Args:
        run_dir: Path to the run directory
        keep_days: Number of days of runs to keep
        keep_latest: Minimum number of latest runs to keep
        dry_run: If True, only show what would be deleted without actually deleting
    """
    logger.info("Starting cleanup of run directory")
    
    # Get the path to the run directory
    run_path = Path(run_dir)
    
    # Check if the run directory exists
    if not run_path.exists():
        logger.info(f"Run directory '{run_dir}' does not exist, nothing to clean up")
        return
    
    # Get all folders in the run directory
    run_folders = [f for f in run_path.iterdir() if f.is_dir()]
    
    # Skip if there are no folders
    if not run_folders:
        logger.info("No run folders found")
        return
    
    # Sort folders by creation time (newest first)
    run_folders.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    # Keep the latest N folders
    folders_to_keep = run_folders[:keep_latest]
    folders_to_check = run_folders[keep_latest:]
    
    # Calculate the cutoff date
    cutoff_date = datetime.now() - timedelta(days=keep_days)
    cutoff_timestamp = cutoff_date.timestamp()
    
    # Identify folders to delete (older than cutoff_date)
    folders_to_delete = [
        folder for folder in folders_to_check 
        if folder.stat().st_mtime < cutoff_timestamp
    ]
    
    # If there are folders to delete, log their count
    if folders_to_delete:
        logger.info(f"Found {len(folders_to_delete)} folders older than {keep_days} days to delete")
        
        # Delete each folder or just log in dry run mode
        for folder in folders_to_delete:
            if dry_run:
                logger.info(f"Would delete: {folder}")
            else:
                try:
                    shutil.rmtree(folder)
                    logger.info(f"Deleted: {folder}")
                except Exception as e:
                    logger.error(f"Error deleting {folder}: {e}")
        
        if not dry_run:
            logger.info(f"Cleanup completed. Deleted {len(folders_to_delete)} folders.")
    else:
        logger.info("No folders to delete.")

def main():
    """Command line interface for the cleanup utility."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean up old run folders")
    parser.add_argument("--run-dir", default="run", help="Path to the run directory")
    parser.add_argument("--keep-days", type=int, default=7, help="Number of days of runs to keep")
    parser.add_argument("--keep-latest", type=int, default=10, help="Minimum number of latest runs to keep")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted without actually deleting")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    # Run the cleanup
    cleanup_run_folders(
        run_dir=args.run_dir,
        keep_days=args.keep_days,
        keep_latest=args.keep_latest,
        dry_run=args.dry_run
    )

if __name__ == "__main__":
    main() 