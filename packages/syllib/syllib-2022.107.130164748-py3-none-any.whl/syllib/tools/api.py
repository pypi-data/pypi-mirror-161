import os
import sys


def safe_create_dir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


def get_run_dir() -> str:
    return os.path.split(sys.executable)[0]
