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

import os
import sys
import enum
import types
import importlib.util

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


def _load_module(module_name: str) -> types.ModuleType:
    """(Private) load a local module."""
    cur_folder = os.path.dirname(__file__)
    spec = importlib.util.spec_from_file_location(
        "tests.modules.example.{0}".format(module_name),
        os.path.join(cur_folder, "{0}.py".format(module_name)),
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules["tests.modules.example.{0}".format(module_name)] = module
    return module


exampleModule = _load_module("example_submodule")

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
