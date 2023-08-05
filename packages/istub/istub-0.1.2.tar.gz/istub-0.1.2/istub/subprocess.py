import logging
import subprocess
import tempfile
from pathlib import Path

from istub.constants import LOGGER_NAME
from istub.exceptions import SubprocessError


def check_call(cmd: list[str]) -> None:
    """
    Check command exit code and output on error.
    """
    try:
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        logger = logging.getLogger(LOGGER_NAME)
        for line in e.output.decode().splitlines():
            logger.error(line)
        raise


def get_call_output(
    cmd: list[str],
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
