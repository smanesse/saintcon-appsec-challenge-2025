#!/usr/bin/env python3
"""
SAINTCON AppSec Challenge Submission Packager

This script creates a submission zip file for a specific challenge by:
1. Reading the allowed_files.txt for the challenge
2. Finding those files in the challenge directory
3. Creating a zip with just the allowed files while preserving directory structure

Usage:
    python create_submission.py diceroller
    python create_submission.py encryptle/ecb
    python create_submission.py encryptle/cbc
"""

import os
import sys
import zipfile
import argparse
from pathlib import Path

# Base paths - script is now in the challenges repo root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHALLENGES_BASE = SCRIPT_DIR

def get_challenge_path(challenge_name):
    """Get the full path to a challenge directory."""
    challenge_path = os.path.join(CHALLENGES_BASE, challenge_name)
    if not os.path.exists(challenge_path):
        raise ValueError(f"Challenge directory not found: {challenge_path}")
    return challenge_path

def read_allowed_files(challenge_path):
    """Read the allowed_files.txt and return list of allowed file paths."""
    allowed_files_path = os.path.join(challenge_path, "allowed_files.txt")
    if not os.path.exists(allowed_files_path):
        raise FileNotFoundError(f"allowed_files.txt not found: {allowed_files_path}")
    
    with open(allowed_files_path, 'r') as f:
        # Strip whitespace and filter out empty lines
        allowed_files = [line.strip() for line in f.readlines() if line.strip()]
    
    return allowed_files

def find_files_in_directory(base_dir, file_paths):
    """Find the actual file paths in the directory, preserving structure."""
    found_files = []
    missing_files = []
    
    for file_path in file_paths:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path) and os.path.isfile(full_path):
            found_files.append((file_path, full_path))
        else:
            missing_files.append(file_path)
    
    return found_files, missing_files

def create_submission_zip(challenge_name, output_dir=None):
    """Create a submission zip file for the specified challenge."""
    print(f"Creating submission for challenge: {challenge_name}")

    # Get challenge directory
    try:
        challenge_path = get_challenge_path(challenge_name)
        print(f"Challenge directory: {challenge_path}")
    except ValueError as e:
        print(f"Error: {e}")
        return False

    # Read allowed files
    try:
        allowed_files = read_allowed_files(challenge_path)
        print(f"Found {len(allowed_files)} allowed files:")
        for file_path in allowed_files:
            print(f"  - {file_path}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return False

    # Find actual files
    found_files, missing_files = find_files_in_directory(challenge_path, allowed_files)

    if missing_files:
        print(f"\nWarning: {len(missing_files)} files not found:")
        for file_path in missing_files:
            print(f"  - {file_path}")

    if not found_files:
        print("Error: No files found to package!")
        return False

    print(f"\nPackaging {len(found_files)} files:")
    for rel_path, full_path in found_files:
        print(f"  - {rel_path}")

    # Create output directory if specified
    # Use just the final directory name for the zip file (not full path with slashes)
    zip_filename = challenge_name.replace('/', '_').replace('\\', '_')
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        zip_path = os.path.join(output_dir, f"{zip_filename}_submission.zip")
    else:
        zip_path = f"{zip_filename}_submission.zip"
    
    # Create zip file
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for rel_path, full_path in found_files:
                # Add file to zip preserving the relative directory structure
                zipf.write(full_path, rel_path)
                print(f"Added to zip: {rel_path}")
        
        print(f"\nSuccess! Created submission: {os.path.abspath(zip_path)}")
        
        # Show zip contents for verification
        print(f"\nZip contents:")
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            for info in zipf.infolist():
                print(f"  - {info.filename} ({info.file_size} bytes)")
        
        return True
        
    except Exception as e:
        print(f"Error creating zip file: {e}")
        return False

def list_available_challenges():
    """List available challenges by recursively scanning for allowed_files.txt."""
    challenges = []

    # Walk through all subdirectories
    for root, dirs, files in os.walk(CHALLENGES_BASE):
        # Skip hidden directories and test directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['tests', '__pycache__', 'node_modules']]

        if 'allowed_files.txt' in files:
            # Get relative path from CHALLENGES_BASE
            rel_path = os.path.relpath(root, CHALLENGES_BASE)
            if rel_path != '.':  # Don't include root directory itself
                challenges.append(rel_path)

    return challenges

def main():
    parser = argparse.ArgumentParser(
        description="Create submission zip files for SAINTCON AppSec challenges",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python create_submission.py diceroller
  python create_submission.py encryptle/ecb
  python create_submission.py encryptle/cbc --output-dir ./submissions
  python create_submission.py --list
        """
    )

    parser.add_argument('challenge', nargs='?',
                       help='Challenge name/path (e.g., diceroller, encryptle/ecb)')
    parser.add_argument('--output-dir', '-o',
                       help='Output directory for zip file (default: current directory)')
    parser.add_argument('--list', '-l', action='store_true',
                       help='List available challenges')

    args = parser.parse_args()
    
    if args.list:
        print("Available challenges:")
        challenges = list_available_challenges()
        if challenges:
            for challenge in sorted(challenges):
                print(f"  - {challenge}")
        else:
            print("  No challenges found")
        return
    
    if not args.challenge:
        print("Error: Challenge name is required (or use --list to see available challenges)")
        parser.print_help()
        return
    
    success = create_submission_zip(args.challenge, args.output_dir)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()