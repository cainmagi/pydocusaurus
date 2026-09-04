"""Pytest configurations"""

import logging
import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Pytest global configurations."""

    # Set the logger level.
    logging.getLogger("httpcore").setLevel(logging.INFO)
    logging.getLogger("markdown_it").setLevel(logging.INFO)
    logging.getLogger("pydocusaurus").setLevel(logging.DEBUG)
