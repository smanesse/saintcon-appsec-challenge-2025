#!/usr/bin/env python3
"""Simple cleanup script for Docker test containers."""

import os
import glob

def cleanup_test_files():
    """Remove all target files from shared directory."""
    results_dir = "/shared"
    target_files = glob.glob(os.path.join(results_dir, "target_*.txt"))
    
    removed_count = 0
    for file_path in target_files:
        try:
            os.remove(file_path)
            removed_count += 1
        except OSError as e:
            print(f"Error removing {file_path}: {e}")
    
    if removed_count > 0:
        print(f"Removed {removed_count} target files")

if __name__ == "__main__":
    cleanup_test_files()