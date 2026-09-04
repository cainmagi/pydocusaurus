# -*- coding: UTF-8 -*-
"""
Analyzer
========
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
The functionalities related to Markdown text analysis.
"""

from markdown_it import MarkdownIt
from markdown_it.token import Token

__all__ = ("is_single_paragraph",)

_BLOCK_DISALLOWED: set[str] = {
    "bullet_list_open",
    "ordered_list_open",
    "blockquote_open",
    "table_open",
    "thead_open",
    "tbody_open",
    "tr_open",
    "th_open",
    "td_open",
    "fence",
    "code_block",
    "hr",
    "heading_open",
}


def is_single_paragraph(md: MarkdownIt, text: str) -> bool:
    """Check whether the Markdown text only contains a single paragraph.

    Arguments
    ---------
    md: `MarkdownIt`
        The markdown-it parser.

    text: `str`
        The text to be analyzed.

    Returns
    -------
    #1: `bool`
        A flag. If it is `True`, the given `text` only contains one Markdown paragraph.
    """
    tokens = md.parse(text)

    para_opens: list[Token] = []
    para_closes: list[Token] = []
    for token in tokens:
        if token.type == "paragraph_open":
            para_opens.append(token)
        if token.type == "paragraph_close":
            para_closes.append(token)

    if len(para_opens) != 1 or len(para_closes) != 1:
        return False

    for token in tokens:
        if token.type in _BLOCK_DISALLOWED:
            return False

    para_index = tokens.index(para_opens[0])
    inline = tokens[para_index + 1]
    if inline.type != "inline":
        return False

    for child in inline.children or []:
        if child.type in _BLOCK_DISALLOWED:
            return False

    return True
