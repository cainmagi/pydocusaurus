# -*- coding: UTF-8 -*-
"""
Modules
=======
@ pyDocusaurus - Core

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
The documentation extraction of modules and packages.
"""

import inspect
import types
import logging

from typing_extensions import Literal, Self
from collections.abc import Sequence

from pydantic import BaseModel, Field

import mdformat

from . import texts as _texts
from ..components.comprotocol import ProtocolComponent

from . import functions as _funcs
from . import classes as _classes
from . import datacls as _datacls
from . import enums as _enums
from . import typeddicts as _tdicts
from . import protocols as _protocols
from . import typealiases as _taliases
from . import inspectors as _inspectors

__all__ = ("DocModuleProp", "DocModule", "parse_module_doc")
log = logging.getLogger("pydocusaurus")


class DocModuleProp(BaseModel):
    """The docstring and basic information of a module property."""

    name: str
    """The name of the module property."""

    descr: str = ""
    """The description body, i.e., the docstring of the module property."""

    type: Literal["package", "module", "class", "func", "type"] = "package"
    """The type of the module property."""

    slang: str = ""
    """The internal code identifying this property."""


class DocModuleMetadata(BaseModel):
    """The module metadata extracted from the top docstring."""

    title: str = ""
    """The module title."""

    author: str = ""
    """The author section specified in the docstring."""

    license: str = ""
    """The license section specified in the docstring."""

    descr: str = ""
    """The description body specified in the docstring."""

    @classmethod
    def from_long_descr(cls, text: str) -> Self:
        """Parse the long description texts (many sections) as the metadata."""
        secs = _texts.Section.from_md_text(mdformat.text(text, options={"wrap": "no"}))
        info: dict[str, str] = dict()
        for sec in secs:
            if "title" not in info and sec.level == 0 or sec.level == 1:
                info["title"] = (
                    " ".join(sec.content) if sec.level == 0 else sec.title
                ).strip()
            elif (
                "author" not in info
                and sec.level >= 2
                and sec.title.strip().casefold() == "author"
            ):
                info["author"] = "\n".join(sec.content).strip()
            elif (
                "license" not in info
                and sec.level >= 2
                and sec.title.strip().casefold() == "license"
            ):
                info["license"] = "\n".join(sec.content).strip()
            elif (
                "descr" not in info
                and sec.level >= 2
                and sec.title.strip().casefold() == "description"
            ):
                info["descr"] = "\n".join(sec.content).strip()
        return cls.model_validate(info)


class DocModule(BaseModel):
    """The docstring of a module."""

    type: Literal["module"] = "module"
    """The identifier of this documentation item."""

    name: str = Field(min_length=1)
    """The name of the module."""

    metadata: DocModuleMetadata = Field(default_factory=DocModuleMetadata)
    """The metadata of the module. This metadata body is extracted from the top
    docstring."""

    is_package: bool = False
    """A flag marking whether the module is a package."""

    slang: str = ""
    """The internal code identifying this module."""

    modules: list[DocModuleProp] = Field(default_factory=list)
    """All submodules belongling to this module. In this case, the current module
    should be a package."""

    classes: list[DocModuleProp] = Field(default_factory=list)
    """All classes defined in this module."""

    funcs: list[DocModuleProp] = Field(default_factory=list)
    """All functions defined in this module."""

    types: list[DocModuleProp] = Field(default_factory=list)
    """The types (type alias, typed dict, and protocol)  defined in this module."""

    aliases: list[DocModuleProp] = Field(default_factory=list)
    """The items imported from the other modules/packages."""

    @property
    def descr(self) -> str:
        """The docstring of the module, it is defined at the beginning of the file."""
        return self.metadata.descr

    def add_member(
        self,
        member: """(
            DocModule | _classes.DocClass | _datacls.DocDataClass | _enums.DocEnum
            | _tdicts.DocTypedDict | _protocols.DocProtocol | _taliases.DocTypeAlias
            | _funcs.DocFunction
        )""",
        is_alias: bool,
    ) -> None:
        """Add a member to this module.

        Arguments
        ---------
        member: `DocModule | DocClass | DocDataClass | DocEnum | ...`
            The member to be added to this module.

        is_alias: `bool`
            A flag specifying whether the member added to this module is an alias.
        """
        if is_alias:
            match (member.type):
                case "module":
                    _type = "package" if member.is_package else "module"
                case "class" | "dataclass" | "enum":
                    _type = "class"
                case "typeddict" | "protocol" | "alias":
                    _type = "type"
                case "function":
                    _type = "func"
                case _:
                    return
            self.aliases.append(
                DocModuleProp(
                    name=member.name,
                    descr=_inspectors.get_short_descr(member.descr),
                    type=_type,
                    slang=member.slang,
                )
            )
            return
        match (member.type):
            case "module":
                self.modules.append(
                    DocModuleProp(
                        name=member.name,
                        descr=_inspectors.get_short_descr(member.descr),
                        type="package" if member.is_package else "module",
                        slang=member.slang,
                    )
                )
            case "class" | "dataclass" | "enum":
                self.classes.append(
                    DocModuleProp(
                        name=member.name,
                        descr=_inspectors.get_short_descr(member.descr),
                        type="class",
                        slang=member.slang,
                    ),
                )
            case "typeddict" | "protocol" | "alias":
                self.types.append(
                    DocModuleProp(
                        name=member.name,
                        descr=_inspectors.get_short_descr(member.descr),
                        type="type",
                        slang=member.slang,
                    )
                )
            case "function":
                _overloads = member.overloads
                descr = member.descr
                if (not descr) and _overloads:
                    for _overload in _overloads:
                        if _overload.descr:
                            descr = _overload.descr
                            break
                self.funcs.append(
                    DocModuleProp(
                        name=member.name,
                        descr=_inspectors.get_short_descr(descr),
                        type="func",
                        slang=member.slang,
                    )
                )

    @property
    def str_v2(self) -> str:
        """Render as V2 string.

        The V2 string of a module is the same as the default string.
        """
        return str(self)

    def __str__(self) -> str:
        """Format the function signature as a string.

        The string format is compatible with the black formatter.
        """
        return self.slang

    def table_members(
        self,
        renderer: ProtocolComponent,
        members: Sequence[DocModuleProp],
        has_relink: bool = True,
        has_doc: bool = True,
    ) -> str:
        """Format the module properties as a table.

        Arguments
        ---------
        renderer: `ProtocolComponent`
            The renderer providing component rendering.

        members: `list[DocModuleProp]`
            The list of members to be displayed in the table.

        has_relink: `bool`
            A flag. If specified, will render the first (name) column as relative
            links.

        has_doc: `bool`
            A flag. If specified, will display the docstring of the keyword-value.

        Returns
        -------
        #1: `str`
            The Markdown table of the keywords.
        """
        cols: list[str] = ["Member"] + (["Description"] if has_doc else [])
        idx_doc: int | None = (
            cols.index("Description") if "Description" in cols else None
        )
        col_styles: dict[int, Literal["l", "c", "r", "n"]] = {0: "c"}
        for idx, style in zip((idx_doc,), ("l",)):
            if idx:
                col_styles[idx] = style
        table = _texts.Table(
            n_rows=len(members) + 1,
            n_cols=len(cols),
            col_styles=col_styles,
            cells={(0, 0): cols[0]},
        )
        if idx_doc is not None:
            table.cells[(0, idx_doc)] = "<center>{0}</center>".format(cols[idx_doc])
        for idx, member in enumerate(members, start=1):
            name = member.name
            icon_name = renderer.icon_obj(type=member.type, text=name)
            if has_relink:
                icon_name = "[{0}]({1}{2}.mdx)".format(
                    icon_name,
                    _inspectors.relative_url_path(
                        path_from=_inspectors.get_slug(self.slang),
                        path_to=_inspectors.get_slug(member.slang),
                    ),
                    "/index" if member.type in ("module", "package") else "",
                )
            table.cells[(idx, 0)] = icon_name
            if idx_doc is not None:
                table.cells[(idx, idx_doc)] = _texts.santize_doc_cell(
                    mdformat.text(
                        member.descr,
                        options={"wrap": "no"},
                    )
                )
        return table.as_md_text()

    def as_md_text(self, renderer: ProtocolComponent) -> str:
        """Render as Markdown text.

        Arguments
        ---------
        renderer: `ProtocolComponent`
            The renderer providing component rendering.

        Returns
        -------
        #1: `str`
            The Markdown text rendered from the module.
        """
        texts: list[str] = []
        texts.append(
            str(
                renderer.apibar(
                    type="package" if self.is_package else "module", slang=self.slang
                )
            )
        )
        if self.descr:
            texts.append(self.descr)

        if self.modules:
            texts.append("## Modules")
            texts.append(self.table_members(renderer, members=self.modules))

        if self.classes:
            texts.append("## Classes")
            texts.append(self.table_members(renderer, members=self.classes))

        if self.funcs:
            texts.append("## Functions")
            texts.append(self.table_members(renderer, members=self.funcs))

        if self.types:
            texts.append("## Types")
            texts.append(self.table_members(renderer, members=self.types))

        if self.aliases:
            texts.append("## Aliases")
            texts.append(self.table_members(renderer, members=self.aliases))

        return mdformat.text("\n\n".join(texts))


def parse_module_doc(module: types.ModuleType) -> DocModule:
    """Parse the docstring of a package or a module.

    Arguments
    ---------
    module: `ModuleType`
        A package/module object to be parsed.

    Returns
    -------
    #1: `DocModule`
        The parsed docstring of the module. Note that the members of the module is
        not parsed by this method. Use a module walker and the `add_member()` method
        of the returned value to complete the module information.
    """
    _slang_segs = module.__name__.split(".", 1)
    slang = _slang_segs[-1] if len(_slang_segs) > 1 else "."
    name = getattr(module, "__qualname__", slang.split(".")[-1])
    if not name:
        name = "."
    is_package = inspect.ispackage(module)
    is_file = getattr(module, "__file__", None) is not None
    if not is_file:
        log.info(
            "Module {0} is detected as a namespace which is not searched.".format(name)
        )
    descr = module.__doc__
    descr = inspect.cleandoc(descr) if descr else ""
    if is_file and (not descr):
        log.warning("Module {0} does not provide its main docstring.".format(name))
    metadata = DocModuleMetadata.from_long_descr(descr)
    return DocModule(name=name, metadata=metadata, is_package=is_package, slang=slang)
