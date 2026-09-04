# -*- coding: UTF-8 -*-
"""
Modules: Example
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
An example module containing different members.
"""

import enum
import types

import dataclasses

from typing_extensions import Protocol, TypedDict

from pydantic import BaseModel

__all__ = (
    "exampleModule",
    "CustomType",
    "ExampleClass",
    "ExampleProtocol",
    "ExampleDict",
    "ExampleDataclass",
    "ExampleModel",
    "ExampleEnum",
    "example_func",
)

exampleModule = types.ModuleType(
    "tests.modules.example.exampleModule",
    doc=("""
        exampleModule
        =============

        Author
        ------
        Yuchen Jin (cainmagi)
        cainmagi@gmail.com

        License
        -------
        MIT License

        Description
        -----------
        Example Docstring"""),
)

type CustomType = int | str
"""An example type alias."""


class ExampleClass:
    """An example class."""


class ExampleProtocol(Protocol):
    """An example protocol."""


class ExampleDict(TypedDict):
    """An example typeddict."""


@dataclasses.dataclass
class ExampleDataclass:
    """An example data class."""


class ExampleModel(BaseModel):
    """An example pydantic model."""


class ExampleEnum(enum.Enum):
    """An example enum"""


def example_func() -> None:
    """An example function."""
    pass
