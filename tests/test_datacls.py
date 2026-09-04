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
Test the parsing of dataclasses and pydantic models.
"""

import inspect
import logging

from dataclasses import dataclass, field as dcls_field

from typing_extensions import Annotated, ClassVar

from pydantic import BaseModel, Field, PrivateAttr

import mdformat

from pydocusaurus.core import datacls as _datacls


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


class ExampleSubClassModel(ExampleModel):
    """A model defined by a subclass."""

    new_val1: float = Field(gt=1.0)
    """A newly added required value."""

    new_val2: int | None = Field(default=None)
    """An optional value that has a `None` default value."""

    new_val3: Annotated[list[Annotated[int, Field(gt=1)]], Field(min_length=1)]
    """A complicated required field."""

    priv1: ClassVar[int]
    """The first private value. It is not real "private" but a class member."""

    _priv2: int = 2
    """The second private value without requiring any annotations."""

    _priv3: int = PrivateAttr(default=10)
    """The third private value that is explicitly configured."""


@dataclass
class ExampleDataClass:
    """An example dataclass that is used for testing the docstring extraction.

    The initialization function are synthesized from the field definitions.
    """

    val_1: int
    """The most plain field that is required."""

    val_2: str = ""
    """An optional field with a default value."""

    val_3: int | str = dcls_field(default="")
    """A union field with the default value specified by the `Field` creator."""

    val_4: list[str] = dcls_field(default_factory=list)
    """A list field with a default value specified by the factory function."""

    @property
    def prop1(self) -> int:
        """A dataclass property which is not a field."""
        raise NotImplementedError

    def method_ex(self, arg: int) -> int:
        """A dataclass method testing the functionality of a vanilla class.

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


@dataclass
class ExampleSubDataClass(ExampleDataClass):
    """A dataclass defined by a subclass."""

    new_val1: float = 1.0
    """The newly added value can only be an optional field."""

    new_val2: int | None = dcls_field(default=None)
    """An optional value that has a `None` default value."""

    new_val3: list[int] = dcls_field(default_factory=lambda: [1, 2, 3])
    """A field with a customized factory."""

    priv1: ClassVar[int]
    """The first private value. It is not real "private" but a class member."""

    _priv2: int = 2
    """Using slash name in dataclass does not yield a private field."""


def test_datacls_model() -> None:
    """Test of a vanilla pydantic model with fields defined in different ways, and
    other features such as methods and properties."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    def long_format(text: str) -> str:
        """Format long text."""
        return mdformat.text(inspect.cleandoc(text), options={"wrap": "no"}).strip()

    doc = _datacls.parse_dataclass_docs(ExampleModel)
    log.info("Test the class: {0}".format(doc.name))
    assert doc.name == "ExampleModel"
    assert doc.descr.strip() == long_format(
        """An example PyDantic model that is used for testing the docstring extraction.

        The initialization function are synthesized from the field definitions."""
    )
    assert len(doc.fields) == 5
    assert len(doc.methods) == 1
    assert len(doc.properties) == 1
    assert len(doc.operators) == 0

    # Test init.
    assert not doc.init_func_specified

    # Test fields
    field = doc.fields[0]
    log.info("Test the model field: {0}.{1}".format(doc.name, field.name))
    assert field.name == "val_1"
    assert field.type == "int"
    assert field.default == ""
    assert field.descr == "The most plain field that is required."

    field = doc.fields[1]
    log.info("Test the model field: {0}.{1}".format(doc.name, field.name))
    assert field.name == "val_2"
    assert field.type == "str"
    assert field.default == '""'
    assert field.descr == "An optional field with a default value."

    field = doc.fields[2]
    log.info("Test the model field: {0}.{1}".format(doc.name, field.name))
    assert field.name == "val_3"
    assert field.type == "int | str"
    assert field.default == '""'
    assert (
        field.descr
        == "A union field with the default value specified by the `Field` creator."
    )

    field = doc.fields[3]
    log.info("Test the model field: {0}.{1}".format(doc.name, field.name))
    assert field.name == "val_4"
    assert field.type == "list[str]"
    assert field.default == "[]"
    assert (
        field.descr
        == "A list field with a default value specified by the factory function."
    )

    field = doc.fields[4]
    log.info("Test the model field: {0}.{1}".format(doc.name, field.name))
    assert field.name == "val_5"
    assert field.type == "list[str]"
    assert field.default == "[]"
    assert (
        field.descr
        == "A list field with the default value specified by the annotation."
    )

    # Test methods.
    method = doc.methods[0]
    log.info("Test the model method: {0}.{1}".format(doc.name, method.name))
    assert method.name == "method_ex"
    assert (
        method.descr.strip()
        == "A model method testing the functionality of the model as a vanilla class."
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
    log.info("Test the model prop: {0}.{1}".format(doc.name, prop.name))
    assert prop.name == "prop1"
    assert prop.type == "int"
    assert prop.descr.strip() == "A model property which is not a field."


def test_datacls_subclass_model() -> None:
    """Test of a pydantic model created by subclass."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    doc = _datacls.parse_dataclass_docs(ExampleSubClassModel)
    log.info("Test the class: {0}".format(doc.name))
    assert doc.name == "ExampleSubClassModel"
    assert doc.descr.strip() == "A model defined by a subclass."
    assert len(doc.fields) == 5 + 3
    assert len(doc.methods) == 0
    assert len(doc.properties) == 0
    assert len(doc.operators) == 0

    # Test init.
    assert not doc.init_func_specified

    # Test fields
    log.info("Test the model fields from base class.")
    field = doc.fields[0]
    assert field.name == "val_1"
    field = doc.fields[1]
    assert field.name == "val_2"
    field = doc.fields[2]
    assert field.name == "val_3"
    field = doc.fields[3]
    assert field.name == "val_4"
    field = doc.fields[4]
    assert field.name == "val_5"

    field = doc.fields[5]
    log.info("Test the model field: {0}.{1}".format(doc.name, field.name))
    assert field.name == "new_val1"
    assert field.type == "float"
    assert field.default == ""
    assert field.descr == "A newly added required value."

    field = doc.fields[6]
    log.info("Test the model field: {0}.{1}".format(doc.name, field.name))
    assert field.name == "new_val2"
    assert field.type == "int | None"
    assert field.default == "None"
    assert field.descr == "An optional value that has a `None` default value."

    field = doc.fields[7]
    log.info("Test the model field: {0}.{1}".format(doc.name, field.name))
    assert field.name == "new_val3"
    assert field.type == "list[int]"
    assert field.default == ""
    assert field.descr == "A complicated required field."


def test_datacls_dataclass() -> None:
    """Test of a vanilla dataclass with fields defined in different ways, and other
    features such as methods and properties."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    def long_format(text: str) -> str:
        """Format long text."""
        return mdformat.text(inspect.cleandoc(text), options={"wrap": "no"}).strip()

    doc = _datacls.parse_dataclass_docs(ExampleDataClass)
    log.info("Test the class: {0}".format(doc.name))
    assert doc.name == "ExampleDataClass"
    assert doc.descr.strip() == long_format(
        """An example dataclass that is used for testing the docstring extraction.

        The initialization function are synthesized from the field definitions."""
    )
    assert len(doc.fields) == 4
    assert len(doc.methods) == 1
    assert len(doc.properties) == 1
    assert len(doc.operators) == 0

    # Test init.
    assert not doc.init_func_specified

    # Test fields
    field = doc.fields[0]
    log.info("Test the dataclass field: {0}.{1}".format(doc.name, field.name))
    assert field.name == "val_1"
    assert field.type == "int"
    assert field.default == ""
    assert field.descr == "The most plain field that is required."

    field = doc.fields[1]
    log.info("Test the dataclass field: {0}.{1}".format(doc.name, field.name))
    assert field.name == "val_2"
    assert field.type == "str"
    assert field.default == '""'
    assert field.descr == "An optional field with a default value."

    field = doc.fields[2]
    log.info("Test the dataclass field: {0}.{1}".format(doc.name, field.name))
    assert field.name == "val_3"
    assert field.type == "int | str"
    assert field.default == '""'
    assert (
        field.descr
        == "A union field with the default value specified by the `Field` creator."
    )

    field = doc.fields[3]
    log.info("Test the dataclass field: {0}.{1}".format(doc.name, field.name))
    assert field.name == "val_4"
    assert field.type == "list[str]"
    assert field.default == "[]"
    assert (
        field.descr
        == "A list field with a default value specified by the factory function."
    )

    # Test methods.
    method = doc.methods[0]
    log.info("Test the dataclass method: {0}.{1}".format(doc.name, method.name))
    assert method.name == "method_ex"
    assert (
        method.descr.strip()
        == "A dataclass method testing the functionality of a vanilla class."
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
    log.info("Test the model prop: {0}.{1}".format(doc.name, prop.name))
    assert prop.name == "prop1"
    assert prop.type == "int"
    assert prop.descr.strip() == "A dataclass property which is not a field."


def test_datacls_subclass_dataclass() -> None:
    """Test of a pydantic model created by subclass."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    doc = _datacls.parse_dataclass_docs(ExampleSubDataClass)
    log.info("Test the class: {0}".format(doc.name))
    assert doc.name == "ExampleSubDataClass"
    assert doc.descr.strip() == "A dataclass defined by a subclass."
    assert len(doc.fields) == 4 + 4
    assert len(doc.methods) == 0
    assert len(doc.properties) == 0
    assert len(doc.operators) == 0

    # Test init.
    assert not doc.init_func_specified

    # Test fields
    log.info("Test the model fields from base class.")
    field = doc.fields[0]
    assert field.name == "val_1"
    field = doc.fields[1]
    assert field.name == "val_2"
    field = doc.fields[2]
    assert field.name == "val_3"
    field = doc.fields[3]
    assert field.name == "val_4"

    field = doc.fields[4]
    log.info("Test the model field: {0}.{1}".format(doc.name, field.name))
    assert field.name == "new_val1"
    assert field.type == "float"
    assert field.default == "1.0"
    assert field.descr == "The newly added value can only be an optional field."

    field = doc.fields[5]
    log.info("Test the model field: {0}.{1}".format(doc.name, field.name))
    assert field.name == "new_val2"
    assert field.type == "int | None"
    assert field.default == "None"
    assert field.descr == "An optional value that has a `None` default value."

    field = doc.fields[6]
    log.info("Test the model field: {0}.{1}".format(doc.name, field.name))
    assert field.name == "new_val3"
    assert field.type == "list[int]"
    assert field.default == "lambda : [1, 2, 3]"
    assert field.descr == "A field with a customized factory."

    field = doc.fields[7]
    log.info("Test the model field: {0}.{1}".format(doc.name, field.name))
    assert field.name == "_priv2"
    assert field.type == "int"
    assert field.default == "2"
    assert (
        field.descr == "Using slash name in dataclass does not yield a private field."
    )
