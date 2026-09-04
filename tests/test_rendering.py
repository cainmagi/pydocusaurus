# -*- coding: UTF-8 -*-
"""
Tests: Rendering
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
Test the rendering of documents.
"""

import os
import sys
import json
import logging
import importlib.util
from types import ModuleType

from typing import Any

import pydocusaurus


class Validator(pydocusaurus.renderer.package.SaverAbstract):
    """The validation tool used to compare the rendered documents and the save
    documents."""

    def __init__(
        self, ref_path: str | os.PathLike[str], logger: logging.Logger | None = None
    ) -> None:
        """Initialization.

        Arguments
        ---------
        ref_path: `str | os.PathLike[str]`
            The path to the reference documentation that will be compared.

        logger: `Logger`
            An optional logger used for showing the validation messages.
        """
        super().__init__()
        self.ref_path = ref_path
        self.logger = logger

    def save_text(self, file_path: str | os.PathLike[str], data: str) -> None:
        """Dummy text saving. The data will not be really saved but compared with the
        existing documentation file.

        Arguments
        ---------
        file_path: `str | PathLike[str]`
            The path to the output file.

        data: `str`
            The text data to be saved.
        """
        if self.logger is not None:
            self.logger.debug("Validating: {0}".format(file_path))
        with open(file_path, "r", encoding="utf-8") as fobj:
            assert data == fobj.read()

    def save_data(self, file_path: str | os.PathLike[str], data: Any) -> None:
        """Dummy structured data (such as json) saving. The data will not be really
        saved but compared with the existing documentation file.

        Arguments
        ---------
        file_path: `str | PathLike[str]`
            The path to the output file.

        data: `Any`
            The structured data to be saved.
        """
        if self.logger is not None:
            self.logger.debug("Validating: {0}".format(file_path))
        with open(file_path, "r", encoding="utf-8") as fobj:
            assert json.dumps(data, indent=2) == fobj.read()


def get_example_package() -> ModuleType:
    """Get the example package used for testing.

    Returns
    -------
    #1: `ModuleType`
        The package `render_example` used to test the performance.
    """
    cur_folder = os.path.dirname(__file__)
    pkg_folder = os.path.join(cur_folder, "modules", "render_example")
    spec = importlib.util.spec_from_file_location(
        "render_example",
        os.path.join(pkg_folder, "__init__.py"),
        submodule_search_locations=[pkg_folder],
    )
    assert spec is not None
    assert spec.loader is not None
    render_example = importlib.util.module_from_spec(spec)
    sys.modules["render_example"] = render_example
    spec.loader.exec_module(render_example)
    return render_example


def test_protocol_vanilla() -> None:
    """Test of a vanilla protocol class with a method, a property, and an operator."""
    log = logging.getLogger("pydocusaurus").getChild("test")

    pkg_name = "render_example"
    log.info("Get the testing package: {0}".format(pkg_name))
    pkg = get_example_package()
    assert pkg.__name__ == pkg_name

    cur_folder = os.path.dirname(__file__)
    pkg_folder = os.path.join(cur_folder, "docs", "render_example")
    pydocusaurus.render_package_as_mdx(
        pkg, out_dir=pkg_folder, saver=Validator(pkg_folder, logger=log)
    )
