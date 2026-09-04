# -*- coding: UTF-8 -*-
"""
Tests: Protocols
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
Test the parsing of protocol classes.
"""

import inspect
import logging

from typing import Any

from typing_extensions import Protocol

import mdformat

from pydocusaurus.core import protocols as _protocols


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


def test_protocol_vanilla() -> None:
    """Test of a vanilla protocol class with a method, a property, and an operator."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    def long_format(text: str) -> str:
        """Format long text."""
        return mdformat.text(inspect.cleandoc(text), options={"wrap": "no"}).strip()

    doc = _protocols.parse_protocol_docs(ExampleProtocol)
    log.info("Test the class: {0}".format(doc.name))
    assert doc.name == "ExampleProtocol"
    assert doc.descr.strip() == long_format(
        """An example protocol class. It should be processed in the same way of a
        vanilla class."""
    )
    assert len(doc.methods) == 1
    assert len(doc.properties) == 1
    assert len(doc.operators) == 1

    # Test init.
    assert not doc.init_func_specified

    # Test methods.
    method = doc.methods[0]
    log.info("Test the protocol method: {0}.{1}".format(doc.name, method.name))
    assert method.name == "method_ex"
    assert method.descr.strip() == "A protocol method."
    assert len(method.args) == 2
    assert len(method.retval) == 1
    assert method.args[0].name == "self"
    assert method.args[1].name == "arg"
    assert method.args[1].type == "int"
    assert method.args[1].default == ""
    assert (
        method.args[1].format_doc()
        == "The input value with the type specified by the annotation."
    )
    assert method.retval[0].name == "#1"
    assert method.retval[0].type == "int"
    assert method.retval[0].format_doc() == "The method output."

    # Test properties.
    prop = doc.properties[0]
    log.info("Test the protocol prop: {0}.{1}".format(doc.name, prop.name))
    assert prop.name == "prop1"
    assert prop.type == "int"
    assert prop.descr.strip() == "A protocol property which is not a field."

    # Test operators.
    op = doc.operators[0]
    op_func = op.func
    log.info("Test the protocol operator: {0}.{1}".format(doc.name, op.name))
    assert op.name == "call"
    assert op_func.descr.strip() == "Call-object operator."
    assert len(op_func.args) == 4
    assert len(op_func.retval) == 1
    assert op_func.args[0].name == "self"
    assert op_func.args[1].name == "arg1"
    assert op_func.args[1].type == "float"
    assert op_func.args[1].default == ""
    assert op_func.args[1].format_doc() == "The first input value is required."
    assert op_func.args[2].name == "arg2"
    assert op_func.args[2].type == "float"
    assert op_func.args[2].default == "1.0"
    assert op_func.args[2].format_doc() == "The second input value is optional."
    assert op_func.args[3].name == "kwargs"
    assert op_func.args[3].type == "str"
    assert op_func.args[3].default == ""
    assert op_func.args[3].p_type.value == "variadic keyword"
    assert op_func.args[3].format_doc() == "The extended key values."
    assert op_func.retval[0].name == "#1"
    assert op_func.retval[0].type == "Any"
    assert op_func.retval[0].format_doc() == "The unknown output."
