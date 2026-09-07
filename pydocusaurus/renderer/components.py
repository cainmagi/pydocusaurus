# -*- coding: UTF-8 -*-
"""
Components
==========
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
The implementation of the component synthesizer.
"""

from typing_extensions import Literal

from pydantic import BaseModel, Field

from ..components.apibar import ComponentAPIBar

__all__ = ("CompModule", "Components")


class CompModule(BaseModel):
    """The MDX component module to be rendered. Call `str(...)` to render this object
    as an MDX code line.
    """

    module: str = Field(min_length=1)
    """The full typescript module of the component."""

    default: str = ""
    """The default export of the module. If not specified, will not export the default
    value."""

    named: set[str | tuple[str, str]] = Field(default_factory=set)
    """The named export of the module. If not specified, will not export any names.

    If the element is a tuple, it means `(export_name, as_name)` during the import.
    """

    def __str__(self) -> str:
        if not self.default and not self.named:
            return ""
        named: str = ", ".join(
            ("{0} as {1}".format(val[0], val[1]) if isinstance(val, tuple) else val)
            for val in self.named
        )
        if self.default and named:
            return 'import {0}, {{{1}}} from "{2}";'.format(
                self.default, named, self.module
            )
        if self.default:
            return 'import {0} from "{1}";'.format(self.default, self.module)
        return 'import {{{0}}} from "{1}";'.format(named, self.module)


class Components:
    """The collection of components. This centralized component renderer will provide
    the components with proper memory.
    """

    def __init__(self) -> None:
        """Initialization.

        Create the storage of the component provider.
        """
        self.__store: dict[str, CompModule] = dict()

    def get_headers(self) -> str:
        """Format components as headers during the page rendering.

        Returns
        -------
        #1: `str`
            The header texts containing multiple import lines of the MDX components.
        """
        texts: list[str] = []
        for val in self.__store.values():
            _val = str(val)
            if not _val:
                continue
            texts.append(_val)
        return "\n".join(texts)

    @property
    def apibar(self) -> type[ComponentAPIBar]:
        """The API top bar component. It is an MDX API bar synthesizer."""
        _mod = self.__store.setdefault(
            "apibar", CompModule(module="@site/src/components/APITopBar")
        )
        _mod.default = "APITopBar"
        return ComponentAPIBar

    def icon_obj(
        self,
        type: Literal[
            "method", "op", "param", "package", "module", "class", "func", "type"
        ],
        text: str = "",
    ) -> str:
        """The protocol of the subtitle icon.

        Arguments
        ---------
        type: `"method" | "op" | "param" | "package" | "module" | ...`
            The name determining the icon.

        text: `str`
            An optional text after the icon. If it is empty, will only display the
            icon.

        Returns
        -------
        #1: `str`
            The MDX code of the icon-text.
        """
        _mod = self.__store.setdefault(
            "apibar", CompModule(module="@site/src/components/APITopBar")
        )
        _mod.named.add("IconObjType")
        if not text:
            return '<IconObjType type="{0}"/>'.format(type)
        return '<IconObjType type="{0}" hasText={{true}} text="{1}"/>'.format(
            type, text
        )

    def inline_icon(self, icon: Literal["check"]) -> str:
        """The protocol of special single icon.

        Arguments
        ---------
        icon: `"check"`
            The name determining the icon.

        Returns
        -------
        #1: `str`
            The MDX code of the icon.
        """
        _mod = self.__store.setdefault(
            "inlineicon", CompModule(module="@site/src/components/InlineIcon")
        )
        _mod.default = "InlineIcon"
        _icon = "Unknown"
        match (icon):
            case "check":
                _icon = "vsiCheckIcon"
                self.__store.setdefault(
                    "icon-check",
                    CompModule(
                        module="@iconify-icons/codicon/check",
                        default=_icon,
                    ),
                )
        return "<InlineIcon icon={{{0}}}/>".format(_icon)
