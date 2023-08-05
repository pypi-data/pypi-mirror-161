from istub.checks.base import BaseCheck
from istub.checks.flake8 import Flake8Check
from istub.checks.mypy import MypyCheck
from istub.checks.pyright import PyrightCheck
from istub.checks.stubtest import StubtestCheck

CHECKS: list[type[BaseCheck]] = [
    Flake8Check,
    StubtestCheck,
    PyrightCheck,
    MypyCheck,
]
