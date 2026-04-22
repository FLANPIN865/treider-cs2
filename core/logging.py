"""Logging setup using loguru."""

import sys

from loguru import logger


def configure_logging(level: str) -> None:
    """Configure structured-ish logging output."""
    logger.remove()
    logger.add(
        sys.stdout,
        level=level,
        serialize=True,
        backtrace=False,
        diagnose=False,
    )
