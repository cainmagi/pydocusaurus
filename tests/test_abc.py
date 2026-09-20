# -*- coding: UTF-8 -*-
"""
Tests: Abstract Classes
=======================
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
Test the parsing of abstract classes.
"""

import abc

import logging
from functools import cached_property

from typing_extensions import Self

from pydocusaurus.core import classes as _cls


class ExampleAbtractClass(abc.ABC):
    """A class mixing the not implemented and implemented methods."""

    @abc.abstractmethod
    def __add__(self, val: str) -> Self:
        """An example of the not implemented operator.

        Arguments
        ---------
        val: `str`
            A value used as the add method.

        Returns
        -------
        #1: `Self`
            The self body of the operator.
        """
        raise NotImplementedError

    def __getitem__(self, key: str) -> int:
        """An example of the implemented operator.

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

    @property
    @abc.abstractmethod
    def prop1(self) -> int:
        """An example of not implemented property."""
        raise NotImplementedError

    @cached_property
    def prop2(self) -> None:
        """An example of implemented property."""
        raise NotImplementedError

    @abc.abstractmethod
    def method_a(self) -> None:
        """An example of the not implemented vanilla method."""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def method_b(cls) -> None:
        """An example of the not implemented class method."""
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def method_c() -> None:
        """An example of the not implemented static method."""
        raise NotImplementedError


class ExamplePartialClass(ExampleAbtractClass):
    """A class that is partially implemented."""

    def __add__(self, val: str) -> Self:
        """An example of the implemented operator.

        Arguments
        ---------
        val: `str`
            A value used as the add method.

        Returns
        -------
        #1: `Self`
            The self body of the operator.
        """
        raise NotImplementedError

    def method_a(self) -> None:
        """An example of the implemented vanilla method."""
        raise NotImplementedError


class ExampleFullClass(ExamplePartialClass):
    """A class that is fully implemented."""

    @property
    def prop1(self) -> int:
        """An example of implemented property."""
        raise NotImplementedError

    @classmethod
    def method_b(cls) -> None:
        """An example of the implemented class method."""
        raise NotImplementedError

    @staticmethod
    def method_c() -> None:
        """An example of the implemented static method."""
        raise NotImplementedError


def test_abc_normal() -> None:
    """Test of a vanilla and representative abstract class."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    doc = _cls.parse_class_docs(ExampleAbtractClass)

    log.info("Test the class: {0}".format(doc.name))
    assert doc.name == "ExampleAbtractClass"
    assert doc.descr.strip() == (
        "A class mixing the not implemented and implemented methods."
    )
    assert len(doc.methods) == 0
    assert len(doc.properties) == 1
    assert len(doc.operators) == 1
    abs_attrs = doc.abstract_attrs
    assert abs_attrs is not None
    assert len(abs_attrs.methods) == 3
    assert len(abs_attrs.properties) == 1
    assert len(abs_attrs.operators) == 1

    assert doc.is_abstract
    log.info("Get the is_abstract field: {0}".format(doc.is_abstract))

    # Test methods.
    methods_names = list(
        method.name for method in sorted(doc.methods, key=lambda doc: doc.name)
    )
    assert methods_names == []
    methods_names = list(
        method.name for method in sorted(abs_attrs.methods, key=lambda doc: doc.name)
    )
    assert methods_names == ["method_a", "method_b", "method_c"]

    # Test properties.
    prop_names = list(
        prop.name for prop in sorted(doc.properties, key=lambda doc: doc.name)
    )
    assert prop_names == ["prop2"]
    prop_names = list(
        prop.name for prop in sorted(abs_attrs.properties, key=lambda doc: doc.name)
    )
    assert prop_names == ["prop1"]

    # Test operators.
    op_names = list(op.name for op in sorted(doc.operators, key=lambda doc: doc.name))
    assert op_names == ["getitem"]
    op_names = list(
        op.name for op in sorted(abs_attrs.operators, key=lambda doc: doc.name)
    )
    assert op_names == ["add"]


def test_abc_partial() -> None:
    """Test of a partial abstract class."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    doc = _cls.parse_class_docs(ExamplePartialClass)

    log.info("Test the class: {0}".format(doc.name))
    assert doc.name == "ExamplePartialClass"
    assert doc.descr.strip() == "A class that is partially implemented."
    assert len(doc.methods) == 1
    assert len(doc.properties) == 0
    assert len(doc.operators) == 1
    abs_attrs = doc.abstract_attrs
    assert abs_attrs is not None
    assert len(abs_attrs.methods) == 2
    assert len(abs_attrs.properties) == 1
    assert len(abs_attrs.operators) == 0

    assert doc.is_abstract
    log.info("Get the is_abstract field: {0}".format(doc.is_abstract))

    # Test methods.
    methods_names = list(
        method.name for method in sorted(doc.methods, key=lambda doc: doc.name)
    )
    assert methods_names == ["method_a"]
    methods_names = list(
        method.name for method in sorted(abs_attrs.methods, key=lambda doc: doc.name)
    )
    assert methods_names == ["method_b", "method_c"]

    # Test properties.
    prop_names = list(
        prop.name for prop in sorted(doc.properties, key=lambda doc: doc.name)
    )
    assert prop_names == []
    prop_names = list(
        prop.name for prop in sorted(abs_attrs.properties, key=lambda doc: doc.name)
    )
    assert prop_names == ["prop1"]

    # Test operators.
    op_names = list(op.name for op in sorted(doc.operators, key=lambda doc: doc.name))
    assert op_names == ["add"]
    op_names = list(
        op.name for op in sorted(abs_attrs.operators, key=lambda doc: doc.name)
    )
    assert op_names == []


def test_abc_implemented() -> None:
    """Test of an implemented abstract class."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    doc = _cls.parse_class_docs(ExampleFullClass)

    log.info("Test the class: {0}".format(doc.name))
    assert doc.name == "ExampleFullClass"
    assert doc.descr.strip() == "A class that is fully implemented."
    assert len(doc.methods) == 2
    assert len(doc.properties) == 1
    assert len(doc.operators) == 0
    abs_attrs = doc.abstract_attrs
    assert abs_attrs is not None
    assert len(abs_attrs.methods) == 0
    assert len(abs_attrs.properties) == 0
    assert len(abs_attrs.operators) == 0

    assert not doc.is_abstract
    log.info("Get the is_abstract field: {0}".format(doc.is_abstract))

    # Test methods.
    methods_names = list(
        method.name for method in sorted(doc.methods, key=lambda doc: doc.name)
    )
    assert methods_names == ["method_b", "method_c"]
    methods_names = list(
        method.name for method in sorted(abs_attrs.methods, key=lambda doc: doc.name)
    )
    assert methods_names == []

    # Test properties.
    prop_names = list(
        prop.name for prop in sorted(doc.properties, key=lambda doc: doc.name)
    )
    assert prop_names == ["prop1"]
    prop_names = list(
        prop.name for prop in sorted(abs_attrs.properties, key=lambda doc: doc.name)
    )
    assert prop_names == []

    # Test operators.
    op_names = list(op.name for op in sorted(doc.operators, key=lambda doc: doc.name))
    assert op_names == []
    op_names = list(
        op.name for op in sorted(abs_attrs.operators, key=lambda doc: doc.name)
    )
    assert op_names == []
