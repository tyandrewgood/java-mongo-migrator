import os
from pathlib import Path
from typing import List
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def find_java_files(root_dir: str) -> List[str]:
    """
    Recursively find all Java source files under the root directory.

    Args:
        root_dir (str): Path to the root directory of the Java codebase.

    Returns:
        List[str]: List of absolute paths to Java source files.
    """
    java_files: List[str] = []
    root_path = Path(root_dir).resolve()

    if not root_path.is_dir():
        logger.error(f"Provided path is not a valid directory: {root_dir}")
        return java_files

    for path in root_path.rglob("*.java"):
        java_files.append(str(path))

    return java_files


def main():
    import sys
    if len(sys.argv) != 2:
        logger.error("Usage: python scanner.py <root_directory>")
        sys.exit(1)

    root = sys.argv[1]
    files = find_java_files(root)
    logger.info(f"Found {len(files)} Java files:")
    for f in files:
        print(f)


if __name__ == "__main__":
    main()
