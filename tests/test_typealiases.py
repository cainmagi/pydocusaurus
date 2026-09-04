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
import inspect
import importlib.util

import logging

from pydocusaurus.core import typealiases as _typealiases


def test_typealiases_vanilla() -> None:
    """Test of a vanilla typealiases."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    def long_def_format(text: str) -> str:
        """Format long text."""
        return inspect.cleandoc(text).strip()

    cur_folder = os.path.dirname(__file__)
    spec = importlib.util.spec_from_file_location(
        "tests.modules.aliases", os.path.join(cur_folder, "modules", "aliases.py")
    )
    assert spec is not None
    assert spec.loader is not None
    aliases = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(aliases)
    sys.modules["tests.modules.aliases"] = aliases

    docs = _typealiases.parse_type_aliases_doc(aliases)
    log.info("Test type aliases, found {0} items.".format(len(docs)))

    doc = docs[0]
    log.info("Test the type alias: {0}".format(doc.name))
    assert doc.name == "CustomType"
    assert doc.definition == "CustomType: TypeAlias = int | str"
    assert doc.descr.strip() == "docstring for CustomType"

    doc = docs[1]
    log.info("Test the type alias: {0}".format(doc.name))
    assert doc.name == "SpecifiedList"
    assert doc.definition == "type SpecifiedList = list[str]"
    assert doc.descr.strip() == "docstring for SpecifiedList"

    doc = docs[2]
    log.info("Test the type alias: {0}".format(doc.name))
    assert doc.name == "ComplicatedList"
    assert doc.definition == long_def_format("""
        ComplicatedList = Custom[
            tuple[
                int,
                float,
                str,
            ]
        ]""")
    assert doc.descr.strip() == "A multi-line type."
