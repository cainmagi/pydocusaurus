# -*- coding: UTF-8 -*-
"""
Component Protocol
==================
@ pyDocusaurus - Components

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
The protocol of component synthesizer.
"""

from typing_extensions import Literal, Protocol

from . import apibar as _apibar

__all__ = ("ProtocolComponent",)


class ProtocolComponent(Protocol):
    """A protocol providing components. This protocol will be implemented in
    `renderer.components`.
    """

    @property
    def apibar(self) -> type[_apibar.ComponentAPIBar]:
        """The protocol of the top API bar. The returned value is a PyDantic model
        class.
        """
        ...

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
        ...

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
        ...
