# -*- coding: UTF-8 -*-
"""
Protocols
=========
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
The documentation extraction of protocol classes.
"""

from typing import Any
from typing_extensions import Literal

import mdformat

from . import classes as _classes
from ..components.comprotocol import ProtocolComponent

__all__ = ("DocProtocol", "parse_protocol_docs")


class DocProtocol(_classes._DocClassPrototype):
    """The docstring and basic information of a protocol (typing class).

    The protocol is a specialized abstract class. However, it does not provide
    functionalities in run time but only used during the type checking. The
    serialized information is rendered differenly compared to regular classes.
    """

    type: Literal["protocol"] = "protocol"
    """The identifier of this documentation item."""

    def _topbar(self, renderer: ProtocolComponent) -> str:
        """(Private) Render the class top bar."""
        return str(renderer.apibar(type="type", slang=self.slang))

    def as_md_text(self, renderer: ProtocolComponent) -> str:
        """Render as Markdown text.

        Arguments
        ---------
        renderer: `ProtocolComponent`
            The renderer providing component rendering.

        Returns
        -------
        #1: `str`
            The Markdown text rendered from the protocol class.
        """
        texts: list[str] = []
        texts.append(self._as_md_title(renderer=renderer))
        if self.methods:
            texts.append("## Protocol methods")
            for idx, method in enumerate(self.methods):
                if idx > 0:
                    texts.append("---")
                texts.append(method.as_md_text(renderer=renderer))
        if self.properties:
            texts.append("## Protocol properties")
            for idx, prop in enumerate(self.properties):
                if idx > 0:
                    texts.append("---")
                texts.append(prop.as_md_text(renderer=renderer))
        if self.operators:
            texts.append("## Protocol operators")
            for idx, op in enumerate(self.operators):
                if idx > 0:
                    texts.append("---")
                texts.append(op.as_md_text(renderer=renderer))
        return mdformat.text("\n\n".join(texts))


def parse_protocol_docs(cls: type[Any]) -> DocProtocol:
    """Parse the docstring of a protocol class.

    Arguments
    ---------
    cls: `type[Any]`
        A class object to be parsed.

    Returns
    -------
    #1: `DocClass`
        The parsed docstring of the protocol class.
    """
    doc_class = _classes.parse_class_docs(cls)

    return DocProtocol(
        name=doc_class.name,
        descr=doc_class.descr,
        init_func=doc_class.init_func,
        init_func_specified=doc_class.init_func_specified,
        methods=doc_class.methods,
        properties=doc_class.properties,
        operators=doc_class.operators,
        abstract_attrs=None,
        lineno=doc_class.lineno,
        slang=doc_class.slang,
    )
