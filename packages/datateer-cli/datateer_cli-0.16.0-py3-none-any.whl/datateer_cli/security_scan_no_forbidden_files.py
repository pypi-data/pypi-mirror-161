"""A pre-commit hook"""

import argparse
import glob
import os
import sys
from typing import List, Sequence

FORBIDDEN_EXTENSIONS = ["pem"]


def find_forbidden_files(
    forbidden_extensions: List[str], files_to_check: List[str] = None
) -> List[str]:
    forbidden_files = []
    if not forbidden_extensions:
        print("No extensions provided")
        return []
    if not files_to_check or not len(files_to_check):
        print("No files to check")
        return []
    for file in files_to_check:
        for extension in forbidden_extensions:
            if file.lower().endswith(extension.lower()):
                forbidden_files.append(file)
    return forbidden_files


def main() -> int:
    """Returns exit code 0 if all good, or 1 if forbidden files were found"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--extensions", nargs=1, default=FORBIDDEN_EXTENSIONS)
    parser.add_argument("filenames", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    retval = 0
    print("Scanning for forbidden extensions", args.extensions)
    print()

    files = find_forbidden_files(args.extensions[0].split(","), args.filenames)
    for f in files:
        print(f"Forbidden file at {f}")
        retval = 1
    return retval


if __name__ == "__main__":
    exit(main())
