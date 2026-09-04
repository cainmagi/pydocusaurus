# -*- coding: UTF-8 -*-
"""
Modules: Nested - Member
========================
@ pyDocusaurus - Tests

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
The member module in the minimal `nested` package.
"""

from typing_extensions import Literal

__all__ = ("CustomType", "example_func", "ExampleClass")

type CustomType = Literal["a", "b", "c"]
"""An example type alias."""


def example_func() -> None:
    """An example function."""
    pass


class ExampleClass:
    """An example class."""
