# -*- coding: UTF-8 -*-
"""
Classes
=======
@ pyDocusaurus - Tests: Render Example

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
Test the rendering of classes.
"""

import enum

from functools import cached_property

from typing import Any
from typing_extensions import Annotated, overload
from collections.abc import Generator

from pydantic import BaseModel, Field

__all__ = ("ExampleClass", "ExampleModel", "ExampleEnum")


class ExampleClass:
    """An example class which is a mixture of methods, properties, and operators."""

    def __init__(self, key: str, val: int = 10) -> None:
        """Initialization.

        Arguments
        ---------
        key: `str`
            The first key to be configured.

        val: `int`
            The first value of the given key.
        """
        raise NotImplementedError

    @overload
    def __add__(self, val: int) -> int:
        """The add operator (overload 1).

        Arguments
        ---------
        val: `int`
            The number to be added.

        Returns
        -------
        #1: `int`
            An added number.
        """
        ...

    @overload
    def __add__(self, val: str) -> str:
        """The add operator (overload 2).

        Arguments
        ---------
        val: `str`
            The string to be merged.

        Returns
        -------
        #1: `str`
            An concatenated string.
        """
        ...

    def __add__(self, val) -> Any:
        """The add operator with overloads."""
        raise NotImplementedError

    def __str__(self) -> str:
        """The string operator will not be documented."""
        raise NotImplementedError

    def __getitem__(self, key: str) -> int:
        """An example of the get-item operator.

        Arguments
        ---------
        key: `str`
            A key used for getting the number.

        Returns
        -------
        #1: `int`
            The number extracted by the key.
        """
        raise NotImplementedError

    def __setitem__(self, key: str, val: int) -> None:
        """An example of the set-item operator.

        Arguments
        ---------
        key: `str`
            A key used for setting the number.

        val: `int`
            The value to be configured.
        """
        raise NotImplementedError

    def __iter__(
        self,
    ) -> Generator[tuple[int, str], tuple[int, int, int], tuple[str, ...]]:
        """An example of the iterator.

        Yields
        ------
        #1: `int`
            The number in the item.

        #2: `str`
            The key of the number.
        """
        raise NotImplementedError

    @property
    def prop1(self) -> int:
        """A vanilla property with annotation."""
        raise NotImplementedError

    @cached_property
    def prop2(self) -> str:
        """A cached property."""
        raise NotImplementedError

    def method_a(self, arg: int, /, arg_any: Any, *, arg_key: str = "test") -> str:
        """A vanilla instance method.

        Arguments
        ---------
        arg: `int`
            The input argument that is positional-only.

        arg_any: `Any`
            The input argument without specified type.

        arg_key: `str`
            The input argument that is keyword-only.

        Returns
        -------
        #1: `str`
            The returned value.
        """
        raise NotImplementedError

    @classmethod
    def method_b(cls) -> None:
        """A class method."""
        raise NotImplementedError

    @staticmethod
    def method_c(arg: tuple[int, int]) -> tuple[str, str]:
        """A static method.

        Arguments
        ---------
        arg: `tuple[int, int]`
            The input argument is a single tuple.

        Returns
        -------
        #1: `str`
            The first returned value.

        #2: `str`
            The second returned value.
        """
        raise NotImplementedError


class ExampleModel(BaseModel):
    """An example PyDantic model that is used for testing the docstring extraction.

    The initialization function are synthesized from the field definitions.
    """

    val_1: int
    """The most plain field that is required."""

    val_2: str = ""
    """An optional field with a default value."""

    val_3: int | str = Field(default="")
    """A union field with the default value specified by the `Field` creator."""

    val_4: list[str] = Field(default_factory=list)
    """A list field with a default value specified by the factory function."""

    val_5: Annotated[list[str], Field(default_factory=list)]
    """A list field with the default value specified by the annotation."""

    @property
    def prop1(self) -> int:
        """A model property which is not a field."""
        raise NotImplementedError

    def method_ex(self, arg: int) -> int:
        """A model method testing the functionality of the model as a vanilla
        class.

        Arguments
        ---------
        arg:
            The input value with the type specified by the annotation.

        Returns
        -------
        #1:
            The method output.
        """
        raise NotImplementedError


class ExampleEnum(enum.Enum):
    """An example enum class with a property and a method."""

    enum_1 = 1
    """The enum option 1."""

    enum_2 = 2
    """The enum option 2."""

    enum_3 = 10
    """The enum option 3."""

    @property
    def prop1(self) -> int:
        """An enum property which is not a field."""
        raise NotImplementedError

    def method_ex(self, arg: int) -> int:
        """An enum method testing the functionality of the enum class as a vanilla
        class.

        Arguments
        ---------
        arg:
            The input value with the type specified by the annotation.

        Returns
        -------
        #1:
            The method output.
        """
        raise NotImplementedError
