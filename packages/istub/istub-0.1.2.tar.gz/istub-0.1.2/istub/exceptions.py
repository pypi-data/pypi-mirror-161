"""
iStub exceptions.
"""
from typing import Iterable


class ConfigError(Exception):
    """
    Exception for config usage.
    """


class SubprocessError(Exception):
    """
    Exception for subprocess usage.
    """

    def __init__(self, data: str) -> None:
        super().__init__("Subprocess error")
        self.data = data


class CheckFailedError(Exception):
    """
    Exception for check failures.
    """

    def __init__(self, message: str, diff: Iterable[str], data: Iterable[str]) -> None:
        super().__init__(message)
        self.diff = list(diff)
        self.data = list(data)
