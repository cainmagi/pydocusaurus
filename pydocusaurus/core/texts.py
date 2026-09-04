# -*- coding: UTF-8 -*-
"""
Texts
======
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
The MDX rendering of documentation units.
"""

import re

from collections.abc import Sequence, Callable
from typing_extensions import Literal, Self

from pydantic import BaseModel, Field

import mdformat
import markdown_it

from .analyzer import is_single_paragraph

__all__ = ("Section", "Table")


class Section(BaseModel):
    """Document section extracted from a Markdown string."""

    title: str
    """The text of the title"""

    level: int = Field(default=0, ge=0, le=6)
    """The level number of the title."""

    content: list[str] = Field(default_factory=list)
    """The line-by-line content in the section."""

    @classmethod
    def _parse_md_line(
        cls: type[Self],
        current: Self | None,
        start_section: Callable[[Self | None, int, str], Self],
        lines: Sequence[str],
        idx: int,
    ) -> tuple[Self, int]:
        """(Private) Parse Markdown docstring as a list of sections.

        Each section starts with a title.

        Arguments
        ---------
        current: `Section | None`
            The current section where the texts will be added to.

        start_section: `(Section | None, int, str) -> Section`
            The function used for starting a new section. The input arguments are
            `current_section`, `section_index`, and `section_title`.

        lines: `Sequence[str]`
            The full text to be parsed.

        idx: `int`
            The index of the current parsed line.

        Returns
        -------
        #1: `Section`
            The modified current section.

        #2: `int`
            The modified index. It needs to be larger than the input index.
        """
        line = lines[idx]

        reobj = re.match(r"^(#{1,6})\s+(.*)", line)
        if reobj:
            level = len(reobj.group(1))
            title = reobj.group(2).strip()
            current = start_section(current, level, title)
            return current, idx + 1

        if idx + 1 < len(lines):  # Special headings
            next_line = lines[idx + 1].strip()
            if re.match(r"^=+$", next_line):  # H1
                current = start_section(current, 1, line.strip())
                return current, idx + 2
            if re.match(r"^-+$", next_line):  # H2
                current = start_section(current, 2, line.strip())
                return current, idx + 2

        if current:
            current.content.append(line)
        else:
            current = cls(level=0, title="", content=[line])

        return current, idx + 1

    @classmethod
    def from_md_text(cls: type[Self], md_text: str | None) -> list[Self]:
        """Parse Markdown docstring as a list of sections.

        Each section starts with a title.

        Arguments
        ---------
        md_text: `str | None`
            The text to be parsed. It is ususually a docstring.

        Returns
        -------
        #1: `list[DocSection]`
            A list of sections. Each section starts with a title. The content are
            preserved as a sequence of lines. If the section does not have a title,
            its title level will be 0.
        """
        if not md_text:
            return []
        lines = md_text.splitlines()
        sections: list[Self] = []
        current: Self | None = None

        def start_section(current: Self | None, level: int, title: str) -> Self:
            if current:
                sections.append(current)
            current = cls(level=level, title=title)
            return current

        idx = 0
        while idx < len(lines):
            current, idx = cls._parse_md_line(current, start_section, lines, idx)

        if current:  # Handle the last section
            sections.append(current)

        return sections

    def as_md_text(self) -> str:
        """Render as Markdown text.

        Returns
        -------
        #1: `str`
            The Markdown text rendered from the section.
        """
        title = (
            "{0} {1}".format("#" * self.level, self.title)
            if self.level > 0 and self.title
            else ""
        )
        text = "\n".join(self.content)
        if title:
            return mdformat.text(
                "{0}\n\n{1}".format(title, text), options={"wrap": "no"}
            )
        return mdformat.text(text, options={"wrap": "no"}).strip()


class Table(BaseModel):
    """The Markdown table used to displaying arguments."""

    n_rows: int = Field(ge=2)
    """Number of rows in the table. The first row is the table head."""

    n_cols: int = Field(ge=1)
    """Number of columns in the table."""

    cells: dict[tuple[int, int], str] = Field(default_factory=dict)
    """The cell data in the `{(index_row, index_col): text}` format."""

    col_styles: dict[int, Literal["l", "c", "r", "n"]] = Field(default_factory=dict)
    """The style of each column. The codes are: (l) left, (c): center, (r): right,
    (n): not specified."""

    def render_cell(self, md: markdown_it.MarkdownIt, text: str) -> str:
        """Safely render the cell text.

        If the text is a single pargraph, render it as it is. Otherwise, render it as
        HTML codes.

        Arguments
        ---------
        md: `MarkdownIt`
            The markdown-it renderer.

        text: `str`
            The cell text.

        Returns
        -------
        #1: `str`
            The rendered cell text.
        """
        if not text:
            return ""
        if is_single_paragraph(md, text):
            return mdformat.text(text, options={"wrap": "no"}).strip()
        return "".join((val.strip() for val in md.render(text).splitlines()))

    def as_md_text(self) -> str:
        """Render as Markdown text.

        Returns
        -------
        #1: `str`
            The Markdown text rendered from the table.
        """
        md = markdown_it.MarkdownIt("gfm-like")
        col_styles: dict[Literal["l", "c", "r", "n"], str] = {
            "l": " :------ |",
            "c": " :-----: |",
            "r": " ------: |",
            "n": " ------- |",
        }
        rows: list[str] = []
        rows.append(
            "| {0} |".format(
                " | ".join(
                    self.render_cell(md, self.cells.get((0, idx_j), ""))
                    for idx_j in range(self.n_cols)
                )
            )
        )
        rows.append(
            "".join(
                ["|"]
                + [
                    col_styles[self.col_styles.get(idx_j, "n")]
                    for idx_j in range(self.n_cols)
                ]
            )
        )

        for idx_i in range(1, self.n_rows):
            rows.append(
                "| {0} |".format(
                    " | ".join(
                        self.render_cell(md, self.cells.get((idx_i, idx_j), ""))
                        for idx_j in range(self.n_cols)
                    )
                )
            )

        text = "\n".join(rows)
        return mdformat.text(text).strip()
