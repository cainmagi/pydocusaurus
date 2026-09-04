# -*- coding: UTF-8 -*-
"""
Functions
=========
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
Test the rendering of functions.
"""

from typing import Any
from typing_extensions import overload
from collections.abc import Iterator

__all__ = (
    "example_complicated_func",
    "example_iterator_func",
    "example_overload_func",
)


def example_complicated_func(
    arg1: str = "test", arg2: int = 0, *args: str | int, **kwargs: list[str]
) -> tuple[int, tuple[str, str]]:
    """A complicated example function.

    Arguments
    ---------
    arg1: `str`
        The first argument.

    arg2: `int`
        The second argument.

    *args: `str | int`
        More arguments.

    **kwargs: `list[str]`
        More keyword arguments.

    Returns
    -------
    #1: `int`
        The returned value.

    #2: `tuple[str, str]`
        The second returned value.
    """
    raise NotImplementedError


def example_iterator_func(
    arg1: str, arg2: int
) -> Iterator[tuple[str, str, Iterator[tuple[str]]]]:
    """An example function iteratively return items.

    Arguments
    ---------
    arg1: `str`
        The first argument.

    arg2: `int`
        The second argument.

    Yields
    ------
    #1: `str`
        The first iterator item.

    #2: `str`
        The second iterator item.

    #3: `Iterator[tuple[str]]`
        The third iterator item a nested iterator.
    """
    yield NotImplemented
    raise NotImplementedError


@overload
def example_overload_func(arg1: int) -> int:
    """An example function with two overloads.

    This is the first overload.

    Arguments
    ---------
    arg1: `int`
        The input argument.

    Returns
    -------
    #1: `int`
        The returned value is an `int`.
    """
    ...


@overload
def example_overload_func(arg1: str, arg2: str) -> str:
    """An example function with two overloads.

    This is the second overload.

    Arguments
    ---------
    arg1: `str`
        The first input argument.

    arg2: `str`
        The second input argument.

    Returns
    -------
    #1: `str`
        The returned value is a `str`.
    """
    ...


def example_overload_func(*args: Any, **kwargs: Any) -> int | str:
    raise NotImplementedError
