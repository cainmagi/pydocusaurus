# -*- coding: UTF-8 -*-
"""
Package
============
@ pyDocusaurus - CLIs

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
The implementation of commands belonging to this package.
"""

import os
import inspect
import logging

from typing_extensions import Annotated

import typer
from rich.logging import RichHandler

from ..core.walker import fast_import
from ..renderer.package import render_package_as_mdx

app = typer.Typer()
__all__ = ("app", "is_subdir", "render_doc")


def is_subdir(child: str, parent: str) -> bool:
    """Check whether a directory is in another directory.

    Arguments
    ---------
    child: `str`
        The path to the directory that may be in the `parent`.

    parent: `str`
        The path to the parent candidate.

    Returns
    -------
    #1: `bool`
        A flag that will be `True` if `child` is in `parent`.
    """
    child = os.path.normpath(os.path.realpath(child))
    parent = os.path.normpath(os.path.realpath(parent))

    child_parts = child.split(os.sep)
    parent_parts = parent.split(os.sep)

    return (
        len(child_parts) > len(parent_parts)
        and child_parts[: len(parent_parts)] == parent_parts
    )


@app.command(help="Render the documentation of a specific package.")
def render_doc(
    name: Annotated[
        str,
        typer.Argument(
            help=(
                "The name of the package to be rendered. The package needs to be "
                "importable compared to the working directory."
            )
        ),
    ],
    out_dir: Annotated[
        str,
        typer.Option(
            "--out-dir",
            "-o",
            help=(
                "The path of the directory where the documentation files will be "
                "output."
            ),
        ),
    ],
) -> None:
    """Render the documentation of a specific package."""
    package = fast_import(name)
    if not inspect.ispackage(package):
        raise TypeError(
            'The specified module "{0}" is not a package.'.format(package.__name__)
        )
    if not getattr(package, "__path__", None):
        raise TypeError(
            'The specified package "{0}" does not provide file '
            "domain.".format(package.__name__)
        )

    for path in package.__path__:
        if os.path.exists(out_dir) and os.path.samefile(path, out_dir):
            raise TypeError(
                "The specified output path conflicts with the package "
                "path: {0}".format(out_dir)
            )
        if is_subdir(out_dir, path):
            raise TypeError(
                "The specified output path conflicts with the package "
                "path: {0}".format(out_dir)
            )

    render_package_as_mdx(package, out_dir=out_dir)


if __name__ == "__main__":
    log = logging.getLogger("pydocusaurus")
    logging.basicConfig(
        format="%(name)s - %(message)s",
        datefmt="[%X]",
        level=logging.INFO,
        handlers=[RichHandler(rich_tracebacks=True)],
    )
    log.setLevel(logging.INFO)
    app()
