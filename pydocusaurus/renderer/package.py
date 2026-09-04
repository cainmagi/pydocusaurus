# -*- coding: UTF-8 -*-
"""
Package
============
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
Walkthrough a python package, and render the package docstrings as the mdx-formatted
API documentation.
"""

import os
import abc
from importlib.metadata import version, PackageNotFoundError
from types import ModuleType

from typing import Any

import json

from .. import core
from ..core.attree import build_sidebar
from ..core.walker import ParserAbstract, PackageWalker, fast_import
from .page import RendererPage

__all__ = (
    "SaverAbstract",
    "SaverDefault",
    "URIHolder",
    "PackageRenderer",
    "render_package_as_mdx",
)


class SaverAbstract(abc.ABC):
    """The abstract file saver."""

    @abc.abstractmethod
    def save_text(self, file_path: str | os.PathLike[str], data: str) -> None:
        """Save the text file.

        Arguments
        ---------
        file_path: `str | PathLike[str]`
            The path to the output file.

        data: `str`
            The text data to be saved.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def save_data(self, file_path: str | os.PathLike[str], data: Any) -> None:
        """Save the structured data (such as json).

        Arguments
        ---------
        file_path: `str | PathLike[str]`
            The path to the output file.

        data: `Any`
            The structured data to be saved.
        """
        raise NotImplementedError


class SaverDefault(SaverAbstract):
    """The default implementation of the file saver. It can be overriden if special
    customization is required."""

    def save_text(self, file_path: str | os.PathLike[str], data: str) -> None:
        """Save the text file.

        Arguments
        ---------
        file_path: `str | PathLike[str]`
            The path to the output file.

        data: `str`
            The text data to be saved.
        """
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as fobj:
            fobj.write(data)

    def save_data(self, file_path: str | os.PathLike[str], data: Any) -> None:
        """Save the structured data (such as json).

        Arguments
        ---------
        file_path: `str | PathLike[str]`
            The path to the output file.

        data: `Any`
            The structured data to be saved.
        """
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as fobj:
            json.dump(data, fobj, indent=2)


class URIHolder:
    """A temporary storage used for managing URIs."""

    def __init__(self) -> None:
        """Initialization."""
        self.data: dict[str, tuple[str, bool, int | None]] = dict()
        self.pkgs: set[str] = set()

    def add(self, page: RendererPage) -> None:
        """Add a slang to the URI storage.

        Arguments
        ---------
        page: `RendererPage`
            A page providing the slang and URI.
        """
        slang = page.data.slang
        is_package = page.data.type == "module" and page.data.is_package
        is_module = page.data.type == "module"
        uri_base = slang.strip().strip(".").split(".")
        _uri_base = "/".join(
            uri_base[:-1] if ((not is_module) and uri_base) else uri_base
        )
        lineno = page.data.lineno if page.data.type != "module" else None
        if is_package:
            self.pkgs.add(slang)
        if not _uri_base:
            self.data[slang] = (".", True, lineno)
            return
        self.data[slang] = (_uri_base, is_package, lineno)

    def update(self) -> None:
        """Refresh the URI list, and update the `is_package` flags.

        This method is used to compensate the information of the undetected package
        members.
        """
        for key, (_uri_base, is_package, lineno) in self.data.items():
            if is_package:
                continue
            uri_base = _uri_base.replace("/", ".")
            if uri_base in self.pkgs:
                self.data[key] = (_uri_base, True, lineno)

    def render(self) -> dict[str, str]:
        """Render the data as the URI list.

        Returns
        -------
        #1: `dict[str, str]`
            A mapping from `slang` to the document file `uri`.
        """
        self.update()
        return {
            key: (
                "{0}{1}.py{2}".format(
                    _uri_base,
                    "/__init__" if is_package else "",
                    "#L{0}".format(lineno) if lineno else "",
                )
            )
            for key, (_uri_base, is_package, lineno) in sorted(
                self.data.items(), key=lambda item: item[0]
            )
        }


class PackageRenderer(ParserAbstract):
    """The module parser implemented for rendering documentation pages.

    This renderer will be called on each package member and save the parsed information
    as a documentation page file.
    """

    def __init__(self, out_dir: str | os.PathLike[str], saver: SaverAbstract) -> None:
        """Initialization.

        Arguments
        ---------
        out_dir: `str | PathLike[str]`
            The output directory where the documentation is saved.

        saver: `SaverAbstract`
            The saver used for dumping the files.
        """
        super().__init__()
        if not isinstance(saver, SaverAbstract):
            raise TypeError(
                'The arugment "saver" has a wrong type: '
                "{0}".format(saver.__class__.__name__)
            )
        out_dir = str(out_dir)
        os.makedirs(out_dir, exist_ok=True)
        self.out_dir: str = out_dir
        self.uris: URIHolder = URIHolder()
        self.sidebar = build_sidebar()
        self.saver = saver

    def save_page(self, page: RendererPage) -> None:
        """Save the documentation page.

        Arguments
        ---------
        page: `RendererPage`
            The page to be rendered and saved.
        """
        file_path = os.path.join(self.out_dir, page.file_path)
        self.uris.add(page)
        self.saver.save_text(file_path, data=page.render())

    def parse_module(self, obj: core.modules.DocModule) -> None:
        """Render a member object when it is a module.

        Arguments
        ---------
        obj: `DocModule`
            The module information to be rendered and saved.
        """
        page = RendererPage(data=obj)
        self.sidebar.add(
            obj.slang,
            node_attrs={"type": "module", "path": page.file_path.removesuffix(".mdx")},
        )
        self.save_page(page)

    def parse_function(self, obj: core.functions.DocFunction) -> None:
        """Render a member object when it is a function.

        Arguments
        ---------
        obj: `DocFunction`
            The function information to be rendered and saved.
        """
        page = RendererPage(data=obj)
        self.sidebar.add(
            obj.slang,
            node_attrs={"type": "leaf", "path": page.file_path.removesuffix(".mdx")},
        )
        self.save_page(page)

    def parse_typealias(self, obj: core.typealiases.DocTypeAlias) -> None:
        """Render a member object when it is a type alias.

        Arguments
        ---------
        obj: `DocTypeAlias`
            The alias information to be rendered and saved.
        """
        page = RendererPage(data=obj)
        self.sidebar.add(
            obj.slang,
            node_attrs={"type": "leaf", "path": page.file_path.removesuffix(".mdx")},
        )
        self.save_page(page)

    def parse_protocol(self, obj: core.protocols.DocProtocol) -> None:
        """Render a member object when it is a protocol class.

        Arguments
        ---------
        obj: `DocProtocol`
            The protocol class information to be rendered and saved.
        """
        page = RendererPage(data=obj)
        self.sidebar.add(
            obj.slang,
            node_attrs={"type": "leaf", "path": page.file_path.removesuffix(".mdx")},
        )
        self.save_page(page)

    def parse_typeddict(self, obj: core.typeddicts.DocTypedDict) -> None:
        """Render a member object when it is a typed dictionary.

        Arguments
        ---------
        obj: `DocTypedDict`
            The typed dictionary information to be rendered and saved.
        """
        page = RendererPage(data=obj)
        self.sidebar.add(
            obj.slang,
            node_attrs={"type": "leaf", "path": page.file_path.removesuffix(".mdx")},
        )
        self.save_page(page)

    def parse_enum(self, obj: core.enums.DocEnum) -> None:
        """Render a member object when it is an enum class.

        Arguments
        ---------
        obj: `DocEnum`
            The enum information to be rendered and saved.
        """
        page = RendererPage(data=obj)
        self.sidebar.add(
            obj.slang,
            node_attrs={"type": "leaf", "path": page.file_path.removesuffix(".mdx")},
        )
        self.save_page(page)

    def parse_dataclass(self, obj: core.datacls.DocDataClass) -> None:
        """Render a member object when it is a data class.

        Arguments
        ---------
        obj: `DocDataClass`
            The data class information to be rendered and saved.
        """
        page = RendererPage(data=obj)
        self.sidebar.add(
            obj.slang,
            node_attrs={"type": "leaf", "path": page.file_path.removesuffix(".mdx")},
        )
        self.save_page(page)

    def parse_class(self, obj: core.classes.DocClass) -> None:
        """Render a member object when it is a class.

        Arguments
        ---------
        obj: `DocClass`
            The class information to be rendered and saved.
        """
        page = RendererPage(data=obj)
        self.sidebar.add(
            obj.slang,
            node_attrs={"type": "leaf", "path": page.file_path.removesuffix(".mdx")},
        )
        self.save_page(page)


def render_package_as_mdx(
    package: str | ModuleType,
    out_dir: str | os.PathLike[str],
    saver: SaverAbstract | None = None,
) -> None:
    """Render a package as MDX documentation files.

    Arguments
    ---------
    package: `str | ModuleType`
        The name or the module object of a package.

    out_dir: `str | PathLike[str]`
        The output directory where the documentation is saved.

    saver: `SaverAbstract`
        The saver used for dumping the ouput files. It can be overriden if the file
        saving needs to be customized. If not specified, will use the default saver.
    """
    package_name = str(package.__name__ if isinstance(package, ModuleType) else package)
    _pacakge = fast_import(package)
    _name = package_name.split(".")
    try:
        _ver = version(_name[0]) if _name else None
    except PackageNotFoundError:
        _ver = getattr(_pacakge, "__version__", None)
    saver = SaverDefault() if saver is None else saver
    parser = PackageRenderer(out_dir, saver=saver)
    PackageWalker().walk_package(_pacakge, parser)
    uri_dir = os.path.join(parser.out_dir, "src", "envs", "uris")
    saver.save_data(
        os.path.join(
            uri_dir,
            "v{0}.json".format(str(_ver).replace(".", "_") if _ver else "_main"),
        ),
        data=parser.uris.render(),
    )
    sbar_dir = os.path.join(parser.out_dir, "src", "envs", "sidebars")
    saver.save_data(
        os.path.join(
            sbar_dir,
            "v{0}.json".format(str(_ver).replace(".", "_") if _ver else "_main"),
        ),
        data=parser.sidebar.serialize_unpacked(),
    )
