# -*- coding: UTF-8 -*-
"""
Tests: Type Aliases
===================
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
Test the parsing of type aliases.
"""

import os
import sys
import importlib.util
import logging

import pytest

from pydocusaurus.core import modules as _modules
from pydocusaurus.core.walker import PackageWalker


def test_module_vanilla() -> None:
    """Test of a not-nested module."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    cur_folder = os.path.dirname(__file__)
    spec = importlib.util.spec_from_file_location(
        "tests.modules.example", os.path.join(cur_folder, "modules", "example.py")
    )
    assert spec is not None
    assert spec.loader is not None
    example = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(example)
    sys.modules["tests.modules.example"] = example

    doc = _modules.parse_module_doc(example)
    log.info("Test module: {0}".format(doc.name))
    for member, is_alias in PackageWalker().iter_module_members(example):
        log.info("Detect module member: {0}.{1}".format(doc.name, member.name))
        doc.add_member(member=member, is_alias=is_alias)

    assert doc.name == "example"
    assert doc.metadata.title == "Modules: Example"
    assert doc.metadata.author == "Yuchen Jin (cainmagi) cainmagi@gmail.com"
    assert doc.metadata.license == "MIT License"
    assert doc.metadata.descr == "An example module containing different members."
    assert not doc.is_package

    assert len(doc.modules) == 1
    assert len(doc.classes) == 4
    assert len(doc.funcs) == 1
    assert len(doc.types) == 3
    assert len(doc.aliases) == 0

    # modules
    item = doc.modules[0]
    log.info("Test item: {0}.{1}".format(doc.name, item.name))
    assert item.name == "exampleModule"
    assert item.type == "module"
    assert item.descr == "Example Docstring."

    # classes
    item = doc.classes[0]
    log.info("Test item: {0}.{1}".format(doc.name, item.name))
    assert item.name == "ExampleClass"
    assert item.type == "class"
    assert item.descr == "An example class."

    item = doc.classes[1]
    log.info("Test item: {0}.{1}".format(doc.name, item.name))
    assert item.name == "ExampleDataclass"
    assert item.type == "class"
    assert item.descr == "An example data class."

    item = doc.classes[2]
    log.info("Test item: {0}.{1}".format(doc.name, item.name))
    assert item.name == "ExampleModel"
    assert item.type == "class"
    assert item.descr == "An example pydantic model."

    item = doc.classes[3]
    log.info("Test item: {0}.{1}".format(doc.name, item.name))
    assert item.name == "ExampleEnum"
    assert item.type == "class"
    assert item.descr == "An example enum."

    # funcs
    item = doc.funcs[0]
    log.info("Test item: {0}.{1}".format(doc.name, item.name))
    assert item.name == "example_func"
    assert item.type == "func"
    assert item.descr == "An example function."

    # type
    item = doc.types[0]
    log.info("Test item: {0}.{1}".format(doc.name, item.name))
    assert item.name == "CustomType"
    assert item.type == "type"
    assert item.descr == "An example type alias."

    item = doc.types[1]
    log.info("Test item: {0}.{1}".format(doc.name, item.name))
    assert item.name == "ExampleProtocol"
    assert item.type == "type"
    assert item.descr == "An example protocol."

    item = doc.types[2]
    log.info("Test item: {0}.{1}".format(doc.name, item.name))
    assert item.name == "ExampleDict"
    assert item.type == "type"
    assert item.descr == "An example typeddict."


def test_module_nested(caplog: pytest.LogCaptureFixture) -> None:
    """Test of a nested package."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    cur_folder = os.path.dirname(__file__)
    pkg_folder = os.path.join(cur_folder, "modules", "nested")
    spec = importlib.util.spec_from_file_location(
        "tests.modules.nested",
        os.path.join(pkg_folder, "__init__.py"),
        submodule_search_locations=[pkg_folder],
    )
    assert spec is not None
    assert spec.loader is not None
    nested = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(nested)
    sys.modules["tests.modules.nested"] = nested

    doc = _modules.parse_module_doc(nested)

    log.info("Test module: {0}".format(doc.name))
    caplog.clear()
    with caplog.at_level(logging.WARNING):
        for member, is_alias in PackageWalker().iter_module_members(nested):
            log.info("Detect module member: {0}.{1}".format(doc.name, member.name))
            doc.add_member(member=member, is_alias=is_alias)

    assert len(caplog.records) == 1
    log.info("Expected warnings are captured.")

    assert doc.name == "nested"
    assert doc.metadata.title == "Modules: Nested"
    assert doc.metadata.author == "Yuchen Jin (cainmagi) cainmagi@gmail.com"
    assert doc.metadata.license == "MIT License"
    assert doc.metadata.descr == "A minimal package containing a member module."
    assert doc.is_package

    assert len(doc.modules) == 2
    assert len(doc.classes) == 1
    assert len(doc.funcs) == 1
    assert len(doc.types) == 0
    assert len(doc.aliases) == 1

    # modules
    item = doc.modules[0]
    log.info("Test item: {0}.{1}".format(doc.name, item.name))
    assert item.name == "member"
    assert item.type == "module"
    assert item.descr == "The member module in the minimal `nested` package."

    item = doc.modules[1]
    log.info("Test item: {0}.{1}".format(doc.name, item.name))
    assert item.name == "empty"
    assert item.type == "module"
    assert item.descr == ""

    # classes
    item = doc.classes[0]
    log.info("Test item: {0}.{1}".format(doc.name, item.name))
    assert item.name == "ExampleRootClass"
    assert item.type == "class"
    assert item.descr == "An example class in the package root."

    # funcs
    item = doc.funcs[0]
    log.info("Test item: {0}.{1}".format(doc.name, item.name))
    assert item.name == "example_root_func"
    assert item.type == "func"
    assert item.descr == "An example function in the package root."

    # aliases
    item = doc.aliases[0]
    log.info("Test item: {0}.{1}".format(doc.name, item.name))
    assert item.name == "example_func"
    assert item.type == "func"
    assert item.descr == "An example function."
