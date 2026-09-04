# -*- coding: UTF-8 -*-
"""
Tests: Functions
================
@ pyDocusaurus

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
Test the parsing of functions.
"""

import logging
import inspect

from typing import Any
from typing_extensions import overload
from collections.abc import Generator, Iterator

import pytest

import mdformat

from pydocusaurus.core import functions as _funcs


def example_func(arg1: str, arg2: int = 0) -> float:
    """An example function.

    Arguments
    ---------
    arg1: `str`
        The first argument.

    arg2: `int`
        The second argument.

    Returns
    -------
    #1: `float`
        The returned value.
    """
    raise NotImplementedError


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


def example_generator_func(
    arg1: str, arg2: int
) -> Generator[tuple[str, str, Iterator[tuple[str]]], None, None]:
    """Another example function iteratively return items.

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


def example_single_tuple_return_v1(arg1: str, arg2: int = 0) -> tuple[float]:
    """An example function testing a function returning a single tuple.

    Arguments
    ---------
    arg1: `str`
        The first argument.

    arg2: `int`
        The second argument.

    Returns
    -------
    #1: `tuple[float]`
        The returned value.
    """
    raise NotImplementedError


def example_single_tuple_return_v2(arg1: str, arg2: int = 0) -> tuple[float, ...]:
    """Another example function testing a function returning a single tuple.

    Arguments
    ---------
    arg1: `str`
        The first argument.

    arg2: `int`
        The second argument.

    Returns
    -------
    #1: `tuple[float, ...]`
        The returned value.
    """
    raise NotImplementedError


def example_incomplete_doc(arg1: str, arg2: int) -> tuple[float, ...]:
    """An example of incomplete docstring.

    Arguments
    ---------
    arg1: `str`
        The first argument.
    """
    raise NotImplementedError


def example_missing_doc(arg1: Any, arg2: int = 1) -> tuple[float, ...]:
    raise NotImplementedError


def example_rely_on_doc(arg1, arg2: int, arg3: Any):
    """An example where the arguments are annotated by docstring.

    Arguments
    ---------
    arg1: `str`
        The argument without type annotation.

    arg2: `str`
        The argument that docstring type conflicts with the type annotation.

    arg3: `MyClass`
        The argument that the annotation is overridden.

    arg4: `What`
        An redundant argment only appearing in docs.

    Returns
    -------
    #1: `MyType1`
        The first returned value without type annotation.

    #2: `MyType2`
        The second returned value without type annotation.
    """
    raise NotImplementedError


def example_long_paragraphs(arg1: str, arg2: int) -> str:
    """An example function with docstring containing several long paragraphs. Even the
    description contains some rich features:

    ```python
    is_this_good_or_not(...)
    ```

    Arguments
    ---------
    arg1: `str`
        The first argument has two long paragraphs. Lorem ipsum dolor sit amet,
        consectetur adipiscing elit. Donec auctor, odio a maximus tempor, velit
        nisl sodales erat, nec tincidunt ipsum nisi et lectus. Morbi eget dolor
        id ante sollicitudin vehicula. Phasellus ut ex vel ipsum sagittis convallis
        vitae tristique arcu. Ut vitae ultrices arcu. Suspendisse a nibh eros.
        Phasellus maximus posuere justo bibendum gravida. Nunc lobortis venenatis
        tristique. Suspendisse potenti. Pellentesque nibh nulla, dictum ac sodales
        sit amet, tincidunt ut nisl. Phasellus iaculis volutpat felis, a commodo
        velit sodales sed. Maecenas ac mattis ligula, et interdum massa.

        Integer gravida posuere libero non porta. Orci varius natoque penatibus et
        magnis dis parturient montes, nascetur ridiculus mus. Nunc pellentesque lacinia
        libero, sed semper nulla pulvinar nec. Cras mollis ultrices rhoncus. Nunc sit
        amet lectus ante. Nulla facilisi. Vestibulum posuere ac nisi non cursus. Duis
        sem justo, semper eu sapien in, consequat vehicula lorem. Sed a tellus tempor
        ipsum porttitor iaculis eu et felis. Aliquam et lacus sit amet ligula venenatis
        elementum vel sed leo. Aliquam nec consequat eros. Vestibulum condimentum mi
        nisl, sodales convallis magna imperdiet quis. Fusce ut dolor porta, viverra
        dui vel, dapibus urna. Ut non mauris quis lectus mattis facilisis quis eu
        metus.

    arg2: `int`
        The second argument contains rich Markdown features:

        - The first item.

        - The second item is long: Morbi faucibus orci ligula, in fringilla augue
          hendrerit quis. Sed venenatis lacinia purus sit amet gravida. Nam accumsan
          arcu sed egestas porttitor. Quisque mollis nec turpis ut volutpat. Maecenas
          leo nisl, congue gravida sagittis quis, facilisis a leo. Quisque quis augue
          risus. Suspendisse at facilisis augue, non dictum elit. Ut ac lectus eros.
          Integer at placerat leo.

        - The third item.

    Returns
    -------
    #1: `str`
        Cras tincidunt diam libero, id consequat mi posuere ac. Phasellus ac nibh
        neque. Donec ultrices aliquam neque, non porta felis tempus nec.

        - Praesent vestibulum pharetra nisi in aliquet.

        - Quisque in nibh at nisi venenatis dapibus viverra bibendum nunc. Sed sit
        amet nisl sed estscelerisque fermentum nec eu ante.

        - Mauris pretium ante molestie, venenatis justo interdum, pulvinar augue.
    """
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


def test_funcs_normal() -> None:
    """Test of the vanilla function."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    doc = _funcs.parse_func_docs(example_func)
    log.info("Test the function: {0}".format(doc.name))

    assert doc.name == "example_func"
    assert doc.descr.strip() == "An example function."
    assert len(doc.args) == 2
    assert len(doc.retval) == 1

    assert doc.args[0].name == "arg1"
    assert doc.args[0].type == "str"
    assert doc.args[0].default == ""
    assert doc.args[0].format_doc() == "The first argument."

    assert doc.args[1].name == "arg2"
    assert doc.args[1].type == "int"
    assert doc.args[1].default == "0"
    assert doc.args[1].format_doc() == "The second argument."

    assert doc.retval[0].name == "#1"
    assert doc.retval[0].type == "float"
    assert doc.retval[0].format_doc() == "The returned value."


def test_funcs_complicated() -> None:
    """Test of a function with complicated signature."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    doc = _funcs.parse_func_docs(example_complicated_func)
    log.info("Test the function: {0}".format(doc.name))
    assert doc.name == "example_complicated_func"
    assert doc.descr.strip() == "A complicated example function."
    assert len(doc.args) == 4
    assert len(doc.retval) == 2

    assert doc.args[0].name == "arg1"
    assert doc.args[0].type == "str"
    assert doc.args[0].default == '"test"'
    assert doc.args[0].format_doc() == "The first argument."

    assert doc.args[1].name == "arg2"
    assert doc.args[1].type == "int"
    assert doc.args[1].default == "0"
    assert doc.args[1].format_doc() == "The second argument."

    assert doc.args[2].name == "args"
    assert doc.args[2].type == "str | int"
    assert doc.args[2].default == ""
    assert doc.args[2].p_type.value == "variadic positional"
    assert doc.args[2].format_doc() == "More arguments."

    assert doc.args[3].name == "kwargs"
    assert doc.args[3].type == "list[str]"
    assert doc.args[3].default == ""
    assert doc.args[3].p_type.value == "variadic keyword"
    assert doc.args[3].format_doc() == "More keyword arguments."

    assert doc.retval[0].name == "#1"
    assert doc.retval[0].type == "int"
    assert doc.retval[0].format_doc() == "The returned value."

    assert doc.retval[1].name == "#2"
    assert doc.retval[1].type == "tuple[str, str]"
    assert doc.retval[1].format_doc() == "The second returned value."


def test_funcs_yields() -> None:
    """Test of a function providing an iterator."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    doc1 = _funcs.parse_func_docs(example_iterator_func)
    assert doc1.name == "example_iterator_func"
    assert doc1.descr.strip() == "An example function iteratively return items."

    doc2 = _funcs.parse_func_docs(example_generator_func)
    assert doc2.name == "example_generator_func"
    assert doc2.descr.strip() == "Another example function iteratively return items."

    for doc in (doc1, doc2):
        log.info("Test the function: {0}".format(doc.name))
        assert len(doc.args) == 2
        assert len(doc.retval) == 3

        assert doc.args[0].name == "arg1"
        assert doc.args[0].type == "str"
        assert doc.args[0].default == ""
        assert doc.args[0].format_doc() == "The first argument."

        assert doc.args[1].name == "arg2"
        assert doc.args[1].type == "int"
        assert doc.args[1].default == ""
        assert doc.args[1].format_doc() == "The second argument."

        assert doc.retval[0].name == "#1"
        assert doc.retval[0].type == "str"
        assert doc.retval[0].format_doc() == "The first iterator item."

        assert doc.retval[1].name == "#2"
        assert doc.retval[1].type == "str"
        assert doc.retval[1].format_doc() == "The second iterator item."

        assert doc.retval[2].name == "#3"
        assert doc.retval[2].type == "Iterator[tuple[str]]"
        assert (
            doc.retval[2].format_doc() == "The third iterator item a nested iterator."
        )


def test_funcs_single_tuple_return() -> None:
    """Test of the function returning a value that is a tuple."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    doc1 = _funcs.parse_func_docs(example_single_tuple_return_v1)
    log.info("Test the function: {0}".format(doc1.name))
    assert doc1.name == "example_single_tuple_return_v1"
    assert (
        doc1.descr.strip()
        == "An example function testing a function returning a single tuple."
    )

    assert len(doc1.args) == 2
    assert len(doc1.retval) == 1

    assert doc1.args[0].name == "arg1"
    assert doc1.args[0].type == "str"
    assert doc1.args[0].default == ""
    assert doc1.args[0].format_doc() == "The first argument."

    assert doc1.args[1].name == "arg2"
    assert doc1.args[1].type == "int"
    assert doc1.args[1].default == "0"
    assert doc1.args[1].format_doc() == "The second argument."

    assert doc1.retval[0].name == "#1"
    assert doc1.retval[0].type == "tuple[float]"
    assert doc1.retval[0].format_doc() == "The returned value."

    doc2 = _funcs.parse_func_docs(example_single_tuple_return_v2)
    log.info("Test the function: {0}".format(doc2.name))
    assert doc2.name == "example_single_tuple_return_v2"
    assert (
        doc2.descr.strip()
        == "Another example function testing a function returning a single tuple."
    )

    assert len(doc2.args) == 2
    assert len(doc2.retval) == 1

    assert doc2.args[0].name == "arg1"
    assert doc2.args[0].type == "str"
    assert doc2.args[0].default == ""
    assert doc2.args[0].format_doc() == "The first argument."

    assert doc2.args[1].name == "arg2"
    assert doc2.args[1].type == "int"
    assert doc2.args[1].default == "0"
    assert doc2.args[1].format_doc() == "The second argument."

    assert doc2.retval[0].name == "#1"
    assert doc2.retval[0].type == "tuple[float, ...]"
    assert doc2.retval[0].format_doc() == "The returned value."


def test_funcs_incomplete_doc(caplog: pytest.LogCaptureFixture) -> None:
    """Test of the function returning a value that is a one-element tuple."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    with caplog.at_level(logging.WARNING):
        doc = _funcs.parse_func_docs(example_incomplete_doc)

    assert len(caplog.records) == 2
    log.info("Expected warnings are captured.")

    log.info("Test the function: {0}".format(doc.name))
    assert doc.name == "example_incomplete_doc"
    assert doc.descr.strip() == "An example of incomplete docstring."

    assert len(doc.args) == 2
    assert len(doc.retval) == 1

    assert doc.args[0].name == "arg1"
    assert doc.args[0].type == "str"
    assert doc.args[0].default == ""
    assert doc.args[0].format_doc() == "The first argument."

    assert doc.args[1].name == "arg2"
    assert doc.args[1].type == "int"
    assert doc.args[1].default == ""
    assert doc.args[1].format_doc() == ""

    assert doc.retval[0].name == "#1"
    assert doc.retval[0].type == "tuple[float, ...]"
    assert doc.retval[0].format_doc() == ""


def test_funcs_missing_doc(caplog: pytest.LogCaptureFixture) -> None:
    """Test of the function containing an incomplete docstring."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    with caplog.at_level(logging.WARNING):
        doc = _funcs.parse_func_docs(example_missing_doc)

    assert len(caplog.records) == 4
    log.info("Expected warnings are captured.")

    log.info("Test the function: {0}".format(doc.name))
    assert doc.name == "example_missing_doc"
    assert doc.descr.strip() == ""

    assert len(doc.args) == 2
    assert len(doc.retval) == 1

    assert doc.args[0].name == "arg1"
    assert doc.args[0].type == "Any"
    assert doc.args[0].default == ""
    assert doc.args[0].format_doc() == ""

    assert doc.args[1].name == "arg2"
    assert doc.args[1].type == "int"
    assert doc.args[1].default == "1"
    assert doc.args[1].format_doc() == ""

    assert doc.retval[0].name == "#1"
    assert doc.retval[0].type == "tuple[float, ...]"
    assert doc.retval[0].format_doc() == ""


def test_funcs_rely_on_doc() -> None:
    """Test of the function with incomplete annotations. The information can be
    compensated by docstring."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    doc = _funcs.parse_func_docs(example_rely_on_doc)
    log.info("Test the function: {0}".format(doc.name))
    assert doc.name == "example_rely_on_doc"
    assert (
        doc.descr.strip()
        == "An example where the arguments are annotated by docstring."
    )

    assert len(doc.args) == 3
    assert len(doc.retval) == 2

    assert doc.args[0].name == "arg1"
    assert doc.args[0].type == "str"
    assert doc.args[0].format_doc() == "The argument without type annotation."

    assert doc.args[1].name == "arg2"
    assert doc.args[1].type == "int"
    assert (
        doc.args[1].format_doc()
        == "The argument that docstring type conflicts with the type annotation."
    )

    assert doc.args[2].name == "arg3"
    assert doc.args[2].type == "MyClass"
    assert doc.args[2].format_doc() == "The argument that the annotation is overridden."

    assert doc.retval[0].name == "#1"
    assert doc.retval[0].type == "MyType1"
    assert (
        doc.retval[0].format_doc()
        == "The first returned value without type annotation."
    )

    assert doc.retval[1].name == "#2"
    assert doc.retval[1].type == "MyType2"
    assert (
        doc.retval[1].format_doc()
        == "The second returned value without type annotation."
    )


def test_funcs_long_paragraphs() -> None:
    """Test of the function with long-paragraph docstrings."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    doc = _funcs.parse_func_docs(example_long_paragraphs)
    log.info("Test the function: {0}".format(doc.name))

    def long_format(text: str) -> str:
        """Format long text."""
        return mdformat.text(inspect.cleandoc(text), options={"wrap": "no"}).strip()

    assert doc.name == "example_long_paragraphs"
    assert doc.descr.strip() == long_format(
        """An example function with docstring containing
        several long paragraphs. Even the description contains some rich features:

        ```python
        is_this_good_or_not(...)
        ```"""
    )
    assert len(doc.args) == 2
    assert len(doc.retval) == 1

    assert doc.args[0].name == "arg1"
    assert doc.args[0].type == "str"
    assert doc.args[0].default == ""
    assert doc.args[0].format_doc() == long_format(
        """The first argument has two long paragraphs. Lorem ipsum dolor sit amet,
        consectetur adipiscing elit. Donec auctor, odio a maximus tempor, velit
        nisl sodales erat, nec tincidunt ipsum nisi et lectus. Morbi eget dolor
        id ante sollicitudin vehicula. Phasellus ut ex vel ipsum sagittis convallis
        vitae tristique arcu. Ut vitae ultrices arcu. Suspendisse a nibh eros.
        Phasellus maximus posuere justo bibendum gravida. Nunc lobortis venenatis
        tristique. Suspendisse potenti. Pellentesque nibh nulla, dictum ac sodales
        sit amet, tincidunt ut nisl. Phasellus iaculis volutpat felis, a commodo
        velit sodales sed. Maecenas ac mattis ligula, et interdum massa.

        Integer gravida posuere libero non porta. Orci varius natoque penatibus et
        magnis dis parturient montes, nascetur ridiculus mus. Nunc pellentesque lacinia
        libero, sed semper nulla pulvinar nec. Cras mollis ultrices rhoncus. Nunc sit
        amet lectus ante. Nulla facilisi. Vestibulum posuere ac nisi non cursus. Duis
        sem justo, semper eu sapien in, consequat vehicula lorem. Sed a tellus tempor
        ipsum porttitor iaculis eu et felis. Aliquam et lacus sit amet ligula venenatis
        elementum vel sed leo. Aliquam nec consequat eros. Vestibulum condimentum mi
        nisl, sodales convallis magna imperdiet quis. Fusce ut dolor porta, viverra
        dui vel, dapibus urna. Ut non mauris quis lectus mattis facilisis quis eu
        metus."""
    )

    assert doc.args[1].name == "arg2"
    assert doc.args[1].type == "int"
    assert doc.args[1].default == ""
    assert doc.args[1].format_doc() == long_format(
        """The second argument contains rich Markdown features:

        - The first item.

        - The second item is long: Morbi faucibus orci ligula, in fringilla augue
            hendrerit quis. Sed venenatis lacinia purus sit amet gravida. Nam accumsan
            arcu sed egestas porttitor. Quisque mollis nec turpis ut volutpat. Maecenas
            leo nisl, congue gravida sagittis quis, facilisis a leo. Quisque quis augue
            risus. Suspendisse at facilisis augue, non dictum elit. Ut ac lectus eros.
            Integer at placerat leo.

        - The third item."""
    )

    assert doc.retval[0].name == "#1"
    assert doc.retval[0].type == "str"
    assert doc.retval[0].format_doc() == long_format(
        """Cras tincidunt diam libero, id consequat mi posuere ac. Phasellus ac nibh
        neque. Donec ultrices aliquam neque, non porta felis tempus nec.

        - Praesent vestibulum pharetra nisi in aliquet.

        - Quisque in nibh at nisi venenatis dapibus viverra bibendum nunc. Sed sit
        amet nisl sed estscelerisque fermentum nec eu ante.

        - Mauris pretium ante molestie, venenatis justo interdum, pulvinar augue."""
    )


def test_funcs_overload() -> None:
    """Test of the function with multiple overloads."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    doc = _funcs.parse_func_docs(example_overload_func)
    log.info("Test the function: {0}".format(doc.name))

    def long_format(text: str) -> str:
        """Format long text."""
        return mdformat.text(inspect.cleandoc(text), options={"wrap": "no"}).strip()

    assert doc.name == "example_overload_func"
    assert doc.descr.strip() == ""
    assert len(doc.args) == 2
    assert len(doc.retval) == 1
    assert doc.args[0].name == "args"
    assert doc.args[1].name == "kwargs"
    assert doc.args[0].p_type.value == "variadic positional"
    assert doc.args[1].p_type.value == "variadic keyword"

    assert len(doc.overloads) == 2
    doc_o1, doc_o2 = doc.overloads

    assert doc_o1.descr.strip() == long_format(
        """An example function with two overloads.

        This is the first overload."""
    )
    assert len(doc_o1.args) == 1
    assert len(doc_o1.retval) == 1
    assert doc_o1.args[0].name == "arg1"
    assert doc_o1.args[0].type == "int"
    assert doc_o1.args[0].default == ""
    assert doc_o1.args[0].format_doc() == "The input argument."
    assert doc_o1.retval[0].name == "#1"
    assert doc_o1.retval[0].type == "int"
    assert doc_o1.retval[0].format_doc() == "The returned value is an `int`."

    assert doc_o2.descr.strip() == long_format(
        """An example function with two overloads.

        This is the second overload."""
    )
    assert len(doc_o2.args) == 2
    assert len(doc_o2.retval) == 1
    assert doc_o2.args[0].name == "arg1"
    assert doc_o2.args[0].type == "str"
    assert doc_o2.args[0].default == ""
    assert doc_o2.args[0].format_doc() == "The first input argument."
    assert doc_o2.args[1].name == "arg2"
    assert doc_o2.args[1].type == "str"
    assert doc_o2.args[1].default == ""
    assert doc_o2.args[1].format_doc() == "The second input argument."
    assert doc_o2.retval[0].name == "#1"
    assert doc_o2.retval[0].type == "str"
    assert doc_o2.retval[0].format_doc() == "The returned value is a `str`."
