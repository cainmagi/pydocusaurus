# -*- coding: UTF-8 -*-
"""
Tests: Enums
============
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
Test the parsing of enums.
"""

import logging
import enum

from pydocusaurus.core import enums as _enums


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


class ExampleFlagEnum(enum.IntFlag):
    """An example of a flag enum shown in the official document."""

    RED = enum.auto()
    """The red flag created by auto."""

    GREEN = enum.auto()
    """The green flag created by auto."""

    BLUE = enum.auto()
    """The blue flag created by auto."""

    @classmethod
    def method_cls(cls, arg: tuple[int]) -> None:
        """An example of the class method.

        Arguments
        ---------
        arg: `tuple[int]`
            The method input.
        """
        raise NotImplementedError


def test_enum_normal() -> None:
    """Test of a vanilla enum with methods and properties."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    doc = _enums.parse_enum_docs(ExampleEnum)
    log.info("Test the class: {0}".format(doc.name))
    assert doc.name == "ExampleEnum"
    assert doc.descr.strip() == "An example enum class with a property and a method."
    assert len(doc.enum_items) == 3
    assert len(doc.methods) == 1
    assert len(doc.properties) == 1
    assert len(doc.operators) == 0

    # Test init.
    assert not doc.init_func_specified

    # Test fields
    eitem = doc.enum_items[0]
    log.info("Test the enum item: {0}.{1}".format(doc.name, eitem.name))
    assert eitem.name == "enum_1"
    assert eitem.type == "int"
    assert eitem.value == "1"
    assert eitem.descr == "The enum option 1."

    eitem = doc.enum_items[1]
    log.info("Test the enum item: {0}.{1}".format(doc.name, eitem.name))
    assert eitem.name == "enum_2"
    assert eitem.type == "int"
    assert eitem.value == "2"
    assert eitem.descr == "The enum option 2."

    eitem = doc.enum_items[2]
    log.info("Test the enum item: {0}.{1}".format(doc.name, eitem.name))
    assert eitem.name == "enum_3"
    assert eitem.type == "int"
    assert eitem.value == "10"
    assert eitem.descr == "The enum option 3."

    # Test methods.
    method = doc.methods[0]
    log.info("Test the enum method: {0}.{1}".format(doc.name, method.name))
    assert method.name == "method_ex"
    assert method.descr.strip() == (
        "An enum method testing the functionality of the enum class as a vanilla "
        "class."
    )
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
    log.info("Test the enum prop: {0}.{1}".format(doc.name, prop.name))
    assert prop.name == "prop1"
    assert prop.type == "int"
    assert prop.descr.strip() == "An enum property which is not a field."


def test_enum_flag() -> None:
    """Test of a flag enum with methods and properties."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    doc = _enums.parse_enum_docs(ExampleFlagEnum)
    log.info("Test the class: {0}".format(doc.name))
    assert doc.name == "ExampleFlagEnum"
    assert (
        doc.descr.strip() == "An example of a flag enum shown in the official document."
    )
    assert len(doc.enum_items) == 3
    assert len(doc.methods) == 1
    assert len(doc.properties) == 0
    assert len(doc.operators) == 0

    # Test init.
    assert not doc.init_func_specified

    # Test fields
    eitem = doc.enum_items[0]
    log.info("Test the enum item: {0}.{1}".format(doc.name, eitem.name))
    assert eitem.name == "RED"
    assert eitem.type == "int"
    assert eitem.value == "1"
    assert eitem.descr == "The red flag created by auto."

    eitem = doc.enum_items[1]
    log.info("Test the enum item: {0}.{1}".format(doc.name, eitem.name))
    assert eitem.name == "GREEN"
    assert eitem.type == "int"
    assert eitem.value == "2"
    assert eitem.descr == "The green flag created by auto."

    eitem = doc.enum_items[2]
    log.info("Test the enum item: {0}.{1}".format(doc.name, eitem.name))
    assert eitem.name == "BLUE"
    assert eitem.type == "int"
    assert eitem.value == "4"
    assert eitem.descr == "The blue flag created by auto."

    # Test methods.
    method = doc.methods[0]
    log.info("Test the enum method: {0}.{1}".format(doc.name, method.name))
    assert method.name == "method_cls"
    assert method.f_type.value == "classmethod"
    assert method.descr.strip() == ("An example of the class method.")
    assert len(method.args) == 2
    assert len(method.retval) == 0
    assert method.args[0].name == "cls"
    assert method.args[1].name == "arg"
    assert method.args[1].type == "tuple[int]"
    assert method.args[1].default == ""
    assert method.args[1].format_doc() == "The method input."
