"""
Utils for subprocess calls.
"""
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import List, Sequence

from istub.constants import LOGGER_NAME
from istub.exceptions import SubprocessError


def check_call(command: List[str]) -> None:
    """
    Check command exit code and output on error.
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.debug(" ".join(command))
    try:
        subprocess.check_output(command, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        logger = logging.getLogger(LOGGER_NAME)
        for line in e.output.decode().splitlines():
            logger.error(line)
        raise


def get_call_output(
    cmd: Sequence[str],
    capture_stderr: bool = False,
    raise_errors: bool = False,
) -> str:
    with tempfile.NamedTemporaryFile("w+b") as f:
        try:
            subprocess.check_call(
                cmd,
                stderr=f if capture_stderr else subprocess.DEVNULL,
                stdout=f,
            )
        except subprocess.CalledProcessError:
            if raise_errors:
                result = Path(f.name).read_text()
                raise SubprocessError(result)

        result = Path(f.name).read_text()

    return result
