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
from importlib.metadata import version, PackageNotFoundError
from types import ModuleType

from typing import Any
from collections.abc import Mapping
from typing_extensions import Self

from pydantic import BaseModel

from .. import core
from ..core.attree import build_sidebar
from ..core.walker import ParserAbstract, PackageWalker, fast_import
from .saver import SaverAbstract, SaverDefault
from .page import RendererPage
from .resources import render_resource_tree

__all__ = (
    "PackageInformation",
    "URIHolder",
    "PackageRenderer",
    "render_package_as_mdx",
)


class PackageInformation(BaseModel):
    """The basic information of a package. All fields are optional and can be
    inferred from the solved results."""

    user: str | None = None
    """The user name of the repository owner. It needs to be the GitHub user name."""

    package_name: str | None = None
    """The name of the package rendered as the documentation. If not specified, will
    infer the name automatically."""

    sidebar: list[str | dict[str, Any]] | None = None
    """The rendered sidebar data of the API documentation. If not specified, will
    infer this sidebar structure automatically."""

    source_uris: dict[str, dict[str, str]] | None = None
    """The list of source URIs. It is used for providing the links to the source
    codes. If not specified, will infer these URIs automatically."""

    source_versions: dict[str, str] | None = None
    """A mapping from the version names to the version identifiers. The version names
    are used as the keys of `source_uris`, and the version identifiers are used for
    locating the version links. If not spcified, will infer this mapping from the
    `source_uris`."""

    def as_vardict(self) -> dict[str, Any]:
        """Dump the information as a variable dictionary.

        Returns
        -------
        #1: `dict[str, Any]`
            The variable dictionary to be used in resource rendering.
        """
        return {key: val for key, val in self.model_dump().items() if val is not None}

    def set_pkg_info(self, pkg: ModuleType) -> Self:
        """Set the `package_name` if it is not specified.

        Arguments
        ---------
        pkg: `ModuleType`
            The package providing the name.

        Returns
        -------
        #1: `Self`
            This data model.
        """
        if self.package_name:
            return self
        name = str(pkg.__name__).rsplit(sep=".")[-1].strip()
        self.package_name = name
        return self

    def set_sidebar(self, pkg_renderer: PackageRenderer) -> Self:
        """Set the `sidebar` if it is not specified.

        Arguments
        ---------
        pkg_renderer: `PackageRenderer`
            The package renderer providing the sidebar.

        Returns
        -------
        #1: `Self`
            This data model.
        """
        if self.sidebar:
            return self
        self.sidebar = pkg_renderer.sidebar.serialize_unpacked()
        return self

    def set_source_uris(
        self, pkg_renderer: PackageRenderer, version: str | None = None
    ) -> Self:
        """Set the `source_uris` if it is not specified.

        Arguments
        ---------
        pkg_renderer: `PackageRenderer`
            The package renderer providing the uris.

        version: `str | None`
            The version text provided by the package.

        Returns
        -------
        #1: `Self`
            This data model.
        """
        if self.source_uris:
            return self
        uris = pkg_renderer.uris.render()
        if version:
            self.source_uris = {
                "v{0}".format(str(version).strip()): uris,
                "main": uris,
            }
        else:
            self.source_uris = {"main": uris}
        return self

    def set_source_versions(self, versions: Mapping[str, str] | None = None) -> Self:
        """Set the `source_versions` if it is not specified.

        Arguments
        ---------
        versions: `Mapping[str, str] | None`
            The version mapping from version names to the version identifiers.
            If not specified, will use the keys of `source_uris` to infer this value.

        Returns
        -------
        #1: `Self`
            This data model.
        """
        if self.source_versions:
            return self
        _versions = (
            dict(versions)
            if versions
            else (
                {key: key for key in self.source_uris.keys()}
                if self.source_uris
                else {"main": "main"}
            )
        )
        if "main" not in _versions:
            _versions["main"] = "main"
        self.source_versions = _versions
        return self


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
    package_info: str | PackageInformation | None = None,
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

    package_info: `str | PackageInformation | None`
        The package information. If `str` is provided, it will be viewed as the
        author name. If this value is not specified or partially specified, will
        attempt to retrive the package information from the parsed results.
    """
    package_name = str(package.__name__ if isinstance(package, ModuleType) else package)
    package_info = (
        (
            PackageInformation(user=package_info)
            if isinstance(package_info, str)
            else package_info
        )
        if package_info is not None
        else PackageInformation()
    )
    _pacakge = fast_import(package)
    _name = package_name.split(".")
    try:
        _ver = version(_name[0]) if _name else None
    except PackageNotFoundError:
        _ver = getattr(_pacakge, "__version__", None)
    saver = SaverDefault() if saver is None else saver
    parser = PackageRenderer(os.path.join(out_dir, "docs"), saver=saver)
    PackageWalker().walk_package(_pacakge, parser)
    package_info = (
        package_info.set_pkg_info(_pacakge)
        .set_sidebar(parser)
        .set_source_uris(parser, version=_ver)
        .set_source_versions()
    )
    render_resource_tree(
        out_dir=out_dir,
        variables=package_info.as_vardict(),
        package="pydocusaurus",
        resource_root="resources",
        saver=saver,
    )
