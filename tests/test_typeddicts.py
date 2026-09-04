# -*- coding: UTF-8 -*-
"""
Tests: TypedDicts
=================
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
Test the parsing of typed dictionary classes.
"""

import logging

from typing_extensions import Literal, TypedDict, NotRequired

import pytest

from pydocusaurus.core import typeddicts as _typeddicts


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


class _ExampleDictSub(TypedDict):
    """Prototype dict."""

    var1: int
    """A required keyword."""


class ExampleDictSub(_ExampleDictSub, total=False):
    """A typed dictionary defined by mixing the total option."""

    var2: str
    """An optional keyword."""


def test_typeddict_vanilla() -> None:
    """Test of a vanilla typeddict with required and optional fields."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    doc = _typeddicts.parse_typeddict_doc(ExampleDict)
    log.info("Test the class: {0}".format(doc.name))
    assert doc.name == "ExampleDict"
    assert doc.descr.strip() == "An example typed dictionary with docs."
    assert len(doc.dict_items) == 5

    # Test dict items.
    item = doc.dict_items[0]
    log.info('Test the typed dictionary item: {0}["{1}"]'.format(doc.name, item.name))
    assert item.name == "var1"
    assert item.type == "int"
    assert not item.optional
    assert item.descr.strip() == "An example field."

    item = doc.dict_items[1]
    log.info('Test the typed dictionary item: {0}["{1}"]'.format(doc.name, item.name))
    assert item.name == "var2"
    assert item.type == "float"
    assert not item.optional
    assert item.descr.strip() == "Another field."

    item = doc.dict_items[2]
    log.info('Test the typed dictionary item: {0}["{1}"]'.format(doc.name, item.name))
    assert item.name == "var3"
    assert item.type == "str"
    assert item.optional
    assert (
        item.descr.strip() == "An optional field, while the other fields are required."
    )

    item = doc.dict_items[3]
    log.info('Test the typed dictionary item: {0}["{1}"]'.format(doc.name, item.name))
    assert item.name == "var4"
    assert item.type == "tuple[int, int]"
    assert not item.optional
    assert item.descr.strip() == "A field of tuple."

    item = doc.dict_items[4]
    log.info('Test the typed dictionary item: {0}["{1}"]'.format(doc.name, item.name))
    assert item.name == "var5"
    assert item.type == 'Literal["a", "b", "c"]'
    assert not item.optional
    assert item.descr.strip() == "A literal field."


def test_typeddict_sub() -> None:
    """Test of a typeddict defined by the subclass and the "total" option."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    doc = _typeddicts.parse_typeddict_doc(ExampleDictSub)
    log.info("Test the class: {0}".format(doc.name))
    assert doc.name == "ExampleDictSub"
    assert doc.descr.strip() == "A typed dictionary defined by mixing the total option."
    assert len(doc.dict_items) == 2

    # Test dict items.
    item = doc.dict_items[0]
    log.info('Test the typed dictionary item: {0}["{1}"]'.format(doc.name, item.name))
    assert item.name == "var1"
    assert item.type == "int"
    assert not item.optional
    assert item.descr.strip() == "A required keyword."

    item = doc.dict_items[1]
    log.info('Test the typed dictionary item: {0}["{1}"]'.format(doc.name, item.name))
    assert item.name == "var2"
    assert item.type == "str"
    assert item.optional
    assert item.descr.strip() == "An optional keyword."


def test_typeddict_dynamic(caplog: pytest.LogCaptureFixture) -> None:
    """Test of a typeddict defined dynamically."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    ExampleDyn1 = TypedDict("ExampleDyn1", {"var1": int})

    class ExampleDyn2(ExampleDyn1, total=False):
        """A typed dictionary relying on a dynamically defined typed dictionary."""

        var2: str
        """An optional keyword."""

    with caplog.at_level(logging.WARNING):
        doc = _typeddicts.parse_typeddict_doc(ExampleDyn2)

    assert len(caplog.records) == 1
    log.info("Expected warnings are captured.")

    log.info("Test the class: {0}".format(doc.name))
    assert doc.name == "ExampleDyn2"
    assert (
        doc.descr.strip()
        == "A typed dictionary relying on a dynamically defined typed dictionary."
    )
    assert len(doc.dict_items) == 2

    # Test dict items.
    item = doc.dict_items[0]
    log.info('Test the typed dictionary item: {0}["{1}"]'.format(doc.name, item.name))
    assert item.name == "var1"
    assert item.type == "int"
    assert not item.optional
    assert item.descr.strip() == ""

    item = doc.dict_items[1]
    log.info('Test the typed dictionary item: {0}["{1}"]'.format(doc.name, item.name))
    assert item.name == "var2"
    assert item.type == "str"
    assert item.optional
    assert item.descr.strip() == "An optional keyword."
