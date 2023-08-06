"""
String utils.
"""
import re
import sys
from functools import lru_cache
from pathlib import Path
from typing import List

HASH_RE = re.compile(r"0x[0-9a-f]{12}")


@lru_cache()
def get_replace_paths() -> List[str]:
    """
    Generate a list of paths to replace in snapshot.
    """
    root_path = f"{Path.cwd()}/"
    result = [*sys.path, *[i.replace(root_path, "") for i in sys.path]]
    result = list(filter(lambda x: "/" in x, result))
    result.sort(key=lambda x: len(x), reverse=True)
    return result


def cleanup_output(data: List[str]) -> List[str]:
    """
    Replace hashes and paths in output.
    """
    result = []
    for line in data:
        line = HASH_RE.sub("HASH", line)
        for path in get_replace_paths():
            if path in line:
                line = line.replace(path, ".")
        result.append(line)
    while result and not result[0]:
        result = result[1:]
    while result and not result[-1]:
        result.pop()
    return result


def shorten_path(path: Path) -> str:
    """
    Shorten path to fit in terminal.
    """
    if not path.is_absolute():
        return path.as_posix()

    path_str = path.as_posix()
    root_path_str = Path.cwd().as_posix()
    if not path_str.startswith(root_path_str):
        return path_str

    short_path_str = path_str[len(root_path_str) + 1 :]
    if "/" in short_path_str:
        return short_path_str

    return f"./{short_path_str}"


def get_python_path_str() -> str:
    """
    Return python executable path.
    """
    return shorten_path(Path(sys.executable))
