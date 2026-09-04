# -*- coding: UTF-8 -*-
"""
Tests: Classes
==============
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
Test the parsing of classes.
"""

import logging
from functools import cached_property

from typing import Any
from typing_extensions import overload
from collections.abc import Generator

import pytest

from pydocusaurus.core import classes as _cls


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
    def prop2(self):
        """A cached property without annotation."""
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


class ExampleSubClass(ExampleClass):
    """Test the subclass without customized initialization."""

    @property
    def prop1(self) -> int:
        """A overriden property."""
        raise NotImplementedError

    @prop1.setter
    def prop1(self, val: int) -> None:
        """The setter of prop1. This docstring should not be used.

        Arguments
        ---------
        val: `int`
            The new val to be configured.
        """

    @staticmethod
    def method_c(arg: tuple[int, int], arg2: bool = False) -> tuple[str, str]:
        """An overridden version of the parent method.

        Arguments
        ---------
        arg: `tuple[int, int]`
            The input argument is a single tuple.

        arg2: `bool`
            A boolean flag that only exists in this version.

        Returns
        -------
        #1: `str`
            The first returned value.

        #2: `str`
            The second returned value.
        """
        raise NotImplementedError

    def new_method(self) -> str:
        """A newly defined method without input arguments.

        Returns
        -------
        #1: `str`
            The returned value.
        """
        raise NotImplementedError


def test_cls_normal(caplog: pytest.LogCaptureFixture) -> None:
    """Test of a vanilla class with methods, properties, and operators."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    with caplog.at_level(logging.WARNING):
        doc = _cls.parse_class_docs(ExampleClass)

    assert len(caplog.records) == 1
    log.info("Expected warnings are captured.")

    log.info("Test the class: {0}".format(doc.name))
    assert doc.name == "ExampleClass"
    assert doc.descr.strip() == (
        "An example class which is a mixture of methods, properties, and operators."
    )
    assert len(doc.methods) == 3
    assert len(doc.properties) == 2
    assert len(doc.operators) == 4

    # Test init.
    assert doc.init_func_specified
    assert len(doc.init_func.args) == 3
    assert doc.init_func.descr.strip() == "Initialization."
    assert doc.init_func.args[0].name == "self"
    assert doc.init_func.args[1].name == "key"
    assert doc.init_func.args[1].type == "str"
    assert doc.init_func.args[1].default == ""
    assert doc.init_func.args[1].format_doc() == "The first key to be configured."
    assert doc.init_func.args[2].name == "val"
    assert doc.init_func.args[2].type == "int"
    assert doc.init_func.args[2].default == "10"
    assert doc.init_func.args[2].format_doc() == "The first value of the given key."

    # Test methods.
    methods = list(sorted(doc.methods, key=lambda doc: doc.name))

    method = methods[0]
    log.info("Test the class method: {0}.{1}".format(doc.name, method.name))
    assert method.name == "method_a"
    assert method.descr.strip() == "A vanilla instance method."
    assert len(method.args) == 4
    assert len(method.retval) == 1
    assert method.args[0].name == "self"
    assert method.args[1].name == "arg"
    assert method.args[1].type == "int"
    assert method.args[1].p_type.value == "positional-only"
    assert method.args[1].default == ""
    assert method.args[1].format_doc() == "The input argument that is positional-only."
    assert method.args[2].name == "arg_any"
    assert method.args[2].type == "Any"
    assert method.args[2].p_type.value == "positional or keyword"
    assert method.args[2].default == ""
    assert method.args[2].format_doc() == "The input argument without specified type."
    assert method.args[3].name == "arg_key"
    assert method.args[3].type == "str"
    assert method.args[3].p_type.value == "keyword-only"
    assert method.args[3].default == '"test"'
    assert method.args[3].format_doc() == "The input argument that is keyword-only."
    assert method.retval[0].name == "#1"
    assert method.retval[0].type == "str"
    assert method.retval[0].format_doc() == "The returned value."

    method = methods[1]
    log.info("Test the class method: {0}.{1}".format(doc.name, method.name))
    assert method.name == "method_b"
    assert method.descr.strip() == "A class method."
    assert len(method.args) == 1
    assert len(method.retval) == 0
    assert method.args[0].name == "cls"

    method = methods[2]
    log.info("Test the class method: {0}.{1}".format(doc.name, method.name))
    assert method.name == "method_c"
    assert method.descr.strip() == "A static method."
    assert len(method.args) == 1
    assert len(method.retval) == 2
    assert method.args[0].name == "arg"
    assert method.args[0].type == "tuple[int, int]"
    assert method.args[0].default == ""
    assert method.args[0].format_doc() == "The input argument is a single tuple."
    assert method.retval[0].name == "#1"
    assert method.retval[0].type == "str"
    assert method.retval[0].format_doc() == "The first returned value."
    assert method.retval[1].name == "#2"
    assert method.retval[1].type == "str"
    assert method.retval[1].format_doc() == "The second returned value."

    # Test properties.
    props = list(sorted(doc.properties, key=lambda doc: doc.name))

    prop = props[0]
    log.info("Test the class prop: {0}.{1}".format(doc.name, prop.name))
    assert prop.name == "prop1"
    assert prop.type == "int"
    assert prop.descr.strip() == "A vanilla property with annotation."

    prop = props[1]
    log.info("Test the class prop: {0}.{1}".format(doc.name, prop.name))
    assert prop.name == "prop2"
    assert prop.type == "Unknown"
    assert prop.descr.strip() == "A cached property without annotation."

    # Test operators.
    ops = list(sorted(doc.operators, key=lambda doc: doc.name))

    op = ops[0]
    log.info("Test the class op: {0}.{1}".format(doc.name, op.name))
    assert op.name == "add"
    assert len(op.func.overloads) == 2
    op_func = op.func.overloads[0]
    assert op_func.descr.strip() == "The add operator (overload 1)."
    assert len(op_func.args) == 2
    assert len(op_func.retval) == 1
    assert op_func.args[0].name == "self"
    assert op_func.args[1].name == "val"
    assert op_func.args[1].type == "int"
    assert op_func.args[1].default == ""
    assert op_func.args[1].format_doc() == "The number to be added."
    assert op_func.retval[0].name == "#1"
    assert op_func.retval[0].type == "int"
    assert op_func.retval[0].format_doc() == "An added number."
    op_func = op.func.overloads[1]
    assert op_func.descr.strip() == "The add operator (overload 2)."
    assert len(op_func.args) == 2
    assert len(op_func.retval) == 1
    assert op_func.args[0].name == "self"
    assert op_func.args[1].name == "val"
    assert op_func.args[1].type == "str"
    assert op_func.args[1].default == ""
    assert op_func.args[1].format_doc() == "The string to be merged."
    assert op_func.retval[0].name == "#1"
    assert op_func.retval[0].type == "str"
    assert op_func.retval[0].format_doc() == "An concatenated string."

    op = ops[1]
    log.info("Test the class op: {0}.{1}".format(doc.name, op.name))
    assert op.name == "getitem"
    assert len(op.func.overloads) == 0
    op_func = op.func
    assert op_func.descr.strip() == "An example of the get-item operator."
    assert len(op_func.args) == 2
    assert len(op_func.retval) == 1
    assert op_func.args[0].name == "self"
    assert op_func.args[1].name == "key"
    assert op_func.args[1].type == "str"
    assert op_func.args[1].default == ""
    assert op_func.args[1].format_doc() == "A key used for getting the number."
    assert op_func.retval[0].name == "#1"
    assert op_func.retval[0].type == "int"
    assert op_func.retval[0].format_doc() == "The number extracted by the key."

    op = ops[2]
    log.info("Test the class op: {0}.{1}".format(doc.name, op.name))
    assert op.name == "iter"
    assert len(op.func.overloads) == 0
    assert op.func.is_yield
    op_func = op.func
    assert op_func.descr.strip() == "An example of the iterator."
    assert len(op_func.args) == 1
    assert len(op_func.retval) == 2
    assert op_func.args[0].name == "self"
    assert op_func.retval[0].name == "#1"
    assert op_func.retval[0].type == "int"
    assert op_func.retval[0].format_doc() == "The number in the item."
    assert op_func.retval[1].name == "#2"
    assert op_func.retval[1].type == "str"
    assert op_func.retval[1].format_doc() == "The key of the number."

    op = ops[3]
    log.info("Test the class op: {0}.{1}".format(doc.name, op.name))
    assert op.name == "setitem"
    assert len(op.func.overloads) == 0
    op_func = op.func
    assert op_func.descr.strip() == "An example of the set-item operator."
    assert len(op_func.args) == 3
    assert len(op_func.retval) == 0
    assert op_func.args[0].name == "self"
    assert op_func.args[1].name == "key"
    assert op_func.args[1].type == "str"
    assert op_func.args[1].default == ""
    assert op_func.args[1].format_doc() == "A key used for setting the number."
    assert op_func.args[2].name == "val"
    assert op_func.args[2].type == "int"
    assert op_func.args[2].default == ""
    assert op_func.args[2].format_doc() == "The value to be configured."


def test_cls_subclass() -> None:
    """Test of a subclass class with methods overriden."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    doc = _cls.parse_class_docs(ExampleSubClass)

    log.info("Test the class: {0}".format(doc.name))
    assert doc.name == "ExampleSubClass"
    assert doc.descr.strip() == ("Test the subclass without customized initialization.")
    assert len(doc.methods) == 2
    assert len(doc.properties) == 1
    assert len(doc.operators) == 0

    # Test init.
    assert doc.init_func_specified
    assert len(doc.init_func.args) == 3
    assert doc.init_func.descr.strip() == "Initialization."
    assert doc.init_func.args[0].name == "self"
    assert doc.init_func.args[1].name == "key"
    assert doc.init_func.args[1].type == "str"
    assert doc.init_func.args[1].default == ""
    assert doc.init_func.args[1].format_doc() == "The first key to be configured."
    assert doc.init_func.args[2].name == "val"
    assert doc.init_func.args[2].type == "int"
    assert doc.init_func.args[2].default == "10"
    assert doc.init_func.args[2].format_doc() == "The first value of the given key."

    # Test methods.
    methods = list(sorted(doc.methods, key=lambda doc: doc.name))

    method = methods[0]
    log.info("Test the class method: {0}.{1}".format(doc.name, method.name))
    assert method.name == "method_c"
    assert method.descr.strip() == "An overridden version of the parent method."
    assert len(method.args) == 2
    assert len(method.retval) == 2
    assert method.args[0].name == "arg"
    assert method.args[0].type == "tuple[int, int]"
    assert method.args[0].default == ""
    assert method.args[0].format_doc() == "The input argument is a single tuple."
    assert method.args[1].name == "arg2"
    assert method.args[1].type == "bool"
    assert method.args[1].default == "False"
    assert (
        method.args[1].format_doc()
        == "A boolean flag that only exists in this version."
    )
    assert method.retval[0].name == "#1"
    assert method.retval[0].type == "str"
    assert method.retval[0].format_doc() == "The first returned value."
    assert method.retval[1].name == "#2"
    assert method.retval[1].type == "str"
    assert method.retval[1].format_doc() == "The second returned value."

    method = methods[1]
    log.info("Test the class method: {0}.{1}".format(doc.name, method.name))
    assert method.name == "new_method"
    assert method.descr.strip() == "A newly defined method without input arguments."
    assert len(method.args) == 1
    assert len(method.retval) == 1
    assert method.args[0].name == "self"
    assert method.retval[0].name == "#1"
    assert method.retval[0].type == "str"
    assert method.retval[0].format_doc() == "The returned value."

    # Test properties.
    props = list(sorted(doc.properties, key=lambda doc: doc.name))

    prop = props[0]
    log.info("Test the class prop: {0}.{1}".format(doc.name, prop.name))
    assert prop.name == "prop1"
    assert prop.type == "int"
    assert prop.descr.strip() == "A overriden property."
