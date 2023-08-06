"""
Check package with mypy.stubtest.
"""
from istub.checks.base import BaseCheck


class StubtestCheck(BaseCheck):
    """
    Check package with mypy.stubtest.
    """

    NAME = "stubtest"

    def run(self) -> str:
        output = self.get_call_output(
            [self.python_path, "-m", "mypy.stubtest", self.package.name],
            capture_stderr=False,
        )
        return "\n".join(output.splitlines()[:-1])
