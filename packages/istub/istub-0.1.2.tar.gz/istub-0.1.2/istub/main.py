#!/usr/bin/env python
"""
Main API entrypoint.
"""
import logging
import shlex
import sys

from istub.checks.base import BaseCheck
from istub.cli import CLINamespace, parse_args
from istub.config import Config
from istub.constants import LOGGER_NAME
from istub.exceptions import CheckFailedError, ConfigError
from istub.logger import setup_logging
from istub.subprocess import check_call


def pip_install(config: Config) -> None:
    """
    Install pip requirements.
    """
    logger = logging.getLogger(LOGGER_NAME)
    if config.pip_uninstall:
        logger.info("Uninstalling pip packages...")
        command = [sys.executable, "-m", "pip", "uninstall", *config.pip_uninstall]
        logger.debug(shlex.join(command))
        check_call(command)
    if config.pip_install:
        logger.info("Installing pip requirements...")
        command = [sys.executable, "-m", "pip", "install", *config.pip_install]
        logger.debug(shlex.join(command))
        check_call(command)


def path_install(config: Config) -> None:
    """
    Install requirements.
    """
    logger = logging.getLogger(LOGGER_NAME)
    if config.path_install:
        logger.info("Installing requirements...")
        for path_package in config.path_install:
            logger.debug(f"Installing {path_package.as_posix()}")
            command = [sys.executable, "-m", "pip", "install", path_package.as_posix()]
            logger.debug(shlex.join(command))
            check_call(command)


def build(config: Config) -> None:
    """
    Build requirements.
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.info("Building requirements...")
    for build_cmd in config.build:
        logger.debug(f"Running {build_cmd}")
        check_call(shlex.split(build_cmd))


def check_packages(config: Config, args: CLINamespace) -> list[BaseException]:
    """
    Check packages.
    """
    logger = logging.getLogger(LOGGER_NAME)

    errors: list[BaseException] = []
    enabled_check_names = [i.NAME for i in args.checks]
    for package in config.packages:
        for check_name in package.enabled_checks:
            if check_name not in enabled_check_names:
                continue
            check = get_check_cls(check_name, args.checks)(package)
            logger.info(f"Checking {package.name} with {check.NAME}...")
            try:
                check.check()
            except CheckFailedError as e:
                if args.update:
                    package.set_snapshot(check.NAME, e.data)
                    continue

                logger.error(e)
                for line in e.diff:
                    logger.error(line)
                errors.append(e)
    return errors


def get_check_cls(name: str, checks: list[type[BaseCheck]]) -> type[BaseCheck]:
    """
    Get check class by name.
    """
    for check in checks:
        if check.NAME == name:
            return check
    raise ConfigError(f"Unknown check {name}")


def main() -> None:
    """
    Main CLI entrypoint.
    """
    try:
        main_api()
    except ConfigError as e:
        setup_logging(logging.INFO).error(f"Configuration error: {e}")
        exit(1)


def main_api() -> None:
    """
    Main API entrypoint.
    """
    args = parse_args()
    logger = setup_logging(args.log_level)
    config = args.config
    if args.packages:
        config.filter(args.packages)
    if args.install:
        pip_install(config)
    if args.build and config.build:
        build(config)
    if args.install:
        path_install(config)

    errors = check_packages(config, args)

    if config.is_updated():
        logger.info("Saving configuration...")
        config.save()

    if errors:
        exit(1)


if __name__ == "__main__":
    main()
