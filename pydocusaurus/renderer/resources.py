# -*- coding: UTF-8 -*-
"""
Resources
=========
@ pyDocusaurus - Renderer

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
Rendering the resource files into the documentation.

This module manages the files in the resource folder. These files are not a part of
the codes but provide the templates and the files to be rendered as typescripts in
the exported documentation.
"""

import os
import json

from typing import Any

from importlib.resources import files
from importlib.resources.abc import Traversable
from jinja2 import Environment, BaseLoader

from . import saver as _saver

__all__ = (
    "is_jinja_template",
    "get_jinja_template_out_name",
    "ts_object",
    "as_pypi_name",
    "render_resource_tree",
)
TEMPLATE_EXTS = {".j2", ".jinja", ".jinja2", ".tmpl"}


def is_jinja_template(file_name: str) -> bool:
    """Check whether the file is a jinja2 template.

    Arguments
    ---------
    file_name: `str`
        The file name to be checked.

    Returns
    -------
    #1: `bool`
        A flag. It is `True` if the file is flagged as a jinja2 template.
    """
    _file_name, ext_l1 = os.path.splitext(file_name)
    if ext_l1.strip().casefold() in TEMPLATE_EXTS:
        return True
    ext_l2 = os.path.splitext(_file_name)[-1]
    if ext_l2.strip().casefold() in TEMPLATE_EXTS:
        return True
    return False


def get_jinja_template_out_name(file_name: str) -> str:
    """Get the destination name of the file rendered from a jinja2 template file.

    Arguments
    ---------
    file_name: `str`
        The jinja2 template file name.

    Returns
    -------
    #1: `str`
        The name of the destination file.
    """
    _file_name, ext_l1 = os.path.splitext(file_name)
    if ext_l1.strip().casefold() in TEMPLATE_EXTS:
        return _file_name.strip()
    _file_name, ext_l2 = os.path.splitext(_file_name)
    if ext_l2.strip().casefold() in TEMPLATE_EXTS:
        return _file_name.strip() + ext_l1.strip()
    return file_name.strip()


def ts_object(value: Any, indent: int = 2, base_indent: int = 0) -> str:
    """Dump a value as json, and put it in a typescript object.

    This is a customized Jinja2 template filter.

    Arguments
    ---------
    value: `Any`
        The value to be filtered.

    indent: `int`
        The indent of the dumped json.

    base_indent: `int`
        The indent of the current place. This value needs to be configured when
        the object is to be put at a value with an existing indent.

    Returns
    -------
    #1: `str`
        The rendered multi-line typescript object data.
    """
    # Use Jinja2's built-in tojson filter
    json_text = json.dumps(value, indent=indent)

    lines = json_text.split("\n")
    prefix = " " * base_indent

    # First line stays as-is; subsequent lines get base_indent
    adjusted = [lines[0]] + [prefix + line for line in lines[1:]]

    return "\n".join(adjusted)


def as_pypi_name(value: Any) -> str:
    """Convert the package name as a PyPI name.

    This is a customized Jinja2 template filter.

    Arguments
    ---------
    value: `Any`
        The value to be filtered. It supposes to be a `str`.

    Returns
    -------
    #1: `str`
        The normalized name. The space and underline symbols will be converted to the
        connection dash.
    """
    return "-".join(str(value).strip().replace(" ", "-").replace("_", "-").split("-"))


def render_resource_tree(
    out_dir: str | os.PathLike[str],
    variables: dict,
    package: str = "pydocusaurus",
    resource_root: str = "resources",
    saver: _saver.SaverAbstract | None = None,
) -> None:
    """Render the resource tree of a package.

    Recursively load a resource folder inside a package. Render Jinja2 templates and
    copy non-template files to `out_dir` while preserving folder structure.

    Arguments
    ---------
    out_dir: `str`
        The directory where the resource files will be dumped.

    variables: `Mapping[str, Any]`
        A mapping from names to the variables that the Jinja2 templates will use to
        render files.

    package: `str`
        The name of the package containing the resources.

    resource_root: `str`
        A relative path inside the package specifying the root of the resource folder.
        For example, "resources/ts".

    saver: `str`
        The saver used for dumping the output files. If not specified, will use the
        default file saver.
    """
    root: Traversable = files(package).joinpath(resource_root)
    env = Environment(loader=BaseLoader(), keep_trailing_newline=True)
    env.filters["ts_object"] = ts_object
    env.filters["as_pypi_name"] = as_pypi_name
    saver = (
        _saver.SaverDefault()
        if (not isinstance(saver, _saver.SaverAbstract))
        else saver
    )

    def recurse(src: Traversable, dst: str) -> None:
        """Recursive file renderere and writer.

        Will render the file if it is a jinja2 template. Otherwise, copy it.

        Arguments
        ---------
        src: `Traversable`
            The source file in the package resources.

        dst: `str`
            The folder path where the file will be saved.
        """
        dst = dst.strip()
        os.makedirs(dst, exist_ok=True)
        if src.is_dir():
            for child in src.iterdir():
                recurse(child, os.path.join(dst, child.name) if child.is_dir() else dst)
            return

        if is_jinja_template(src.name):
            template_text = src.read_text()
            template = env.from_string(template_text)

            dst_path = os.path.join(dst, get_jinja_template_out_name(src.name))
            saver.save_text(dst_path, template.render(variables))
            return

        # Non-template file case, copy verbatim
        dst_path = os.path.join(dst, src.name.strip())
        saver.save_bytes(dst_path, src.read_bytes())

    recurse(root, str(out_dir))
