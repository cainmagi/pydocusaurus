# -*- coding: UTF-8 -*-
"""
Modules: Aliases
================
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
The module used for testing aliases.
"""

from typing import Generic, TypeVar
from typing_extensions import TypeAlias

__all__ = (
    "T",
    "Custom",
    "CustomType",
    "SpecifiedList",
    "ComplicatedList",
    "_PrivateAlias",
    "countervar",
)

T = TypeVar("T")
"""Should be ignored."""


class Custom(Generic[T]):
    """Should also be ignored."""

    pass


CustomType: TypeAlias = int | str
"""docstring for CustomType"""

type SpecifiedList = list[str]
"""docstring for SpecifiedList"""

ComplicatedList = Custom[
    tuple[
        int,
        float,
        str,
    ]
]
"""A multi-line type."""

_PrivateAlias = int | float
"""Ignored because private."""

countervar: int = 1
"""Ignored because it is not a type."""
