import os
import shutil
from pathlib import Path

def cleanup_cache(root_dir: str | Path):
    root_path = Path(root_dir)
    if not root_path.exists() or not root_path.is_dir():
        print(f"Error: Root directory does not exist or is not a directory: {root_path}")
        return

    print(f"Starting cleanup in {root_path}...")

    # Directories to delete
    cache_dirs = ['__pycache__', '.pytest_cache']
    # File extensions to delete
    cache_exts = ['.pyc', '.pyo', '.pyd']

    deleted_dirs = 0
    deleted_files = 0

    for path in root_path.rglob('*'):
        if path.is_dir() and path.name in cache_dirs:
            try:
                shutil.rmtree(path)
                print(f"Deleted directory: {path}")
                deleted_dirs += 1
            except Exception as e:
                print(f"Failed to delete directory {path}: {e}")
        elif path.is_file() and path.suffix in cache_exts:
            try:
                path.unlink()
                print(f"Deleted file: {path}")
                deleted_files += 1
            except Exception as e:
                print(f"Failed to delete file {path}: {e}")

    print(f"Cleanup complete. Deleted {deleted_dirs} directories and {deleted_files} files.")

if __name__ == "__main__":
    # Clean up the current directory and all subdirectories
    cleanup_cache(".")
