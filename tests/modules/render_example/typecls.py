# -*- coding: UTF-8 -*-
"""
Type classes
============
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
Test the rendering of types (classes used for annotating).
"""

from typing import Any, TypeVar
from typing_extensions import Literal, NotRequired, TypeAlias, TypedDict, Protocol

__all__ = (
    "CustomType",
    "SpecifiedList",
    "ComplicatedList",
    "ExampleDict",
    "ExampleProtocol",
)

T = TypeVar("T")
"""Should be ignored."""

CustomType: TypeAlias = int | T
"""docstring for CustomType"""

type SpecifiedList = list[int]
"""docstring for SpecifiedList"""

ComplicatedList = CustomType[
    tuple[
        int,
        float,
        str,
    ]
]
"""A multi-line type."""


class ExampleDict(TypedDict):
    """An example typed dictionary with docs."""

    var1: int
    """An example field."""

    var2: float
    """Another field."""

    var3: NotRequired[str]
    """An optional field, while the other fields are required."""

    var4: tuple[int, int]
    """A field of tuple."""

    var5: Literal["a", "b", "c"]
    """A literal field."""


class ExampleProtocol(Protocol):
    """An example protocol class. It should be processed in the same way of a vanilla
    class.
    """

    def __call__(self, arg1: float, arg2: float = 1.0, **kwargs: str) -> Any:
        """Call-object operator.

        Arguments
        ---------
        arg1:
            The first input value is required.

        arg2: `float`
            The second input value is optional.

        **kwargs: `str`
            The extended key values.

        Returns
        -------
        #1: `Any`
            The unknown output.
        """
        ...

    @property
    def prop1(self) -> int:
        """A protocol property which is not a field."""
        ...

    def method_ex(self, arg: int) -> int:
        """A protocol method.

        Arguments
        ---------
        arg:
            The input value with the type specified by the annotation.

        Returns
        -------
        #1:
            The method output.
        """
        ...
