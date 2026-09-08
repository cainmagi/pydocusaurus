# -*- coding: UTF-8 -*-
"""
Example: Customized saver
=========================
@ pyDocusaurus

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
This example shows how to implement a customized saver. This customized saver allows
users to put all document files in a single file.

In the project folder, run the following command:
```
python -m examples.custom_saver
```
"""

import os
import json

from typing import Any

import yaml

import pydocusaurus

__all__ = ("render",)


class SaverSingleFile(pydocusaurus.renderer.package.SaverAbstract):
    """The saver that dumps all documentation files in a single file."""

    def __init__(self) -> None:
        """Initialization."""
        super().__init__()
        self.data: dict[str, str] = dict()

    def dump_yaml(self, out_path: str) -> None:
        """Dump the cached documentation files as a single YAML data file.

        Arguments
        ---------
        out_path: `str`
            The path will the document is saved. It is a YAML file.
        """
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fobj:
            yaml.safe_dump(self.data, fobj, indent=2)

    def save_bytes(self, file_path: str | os.PathLike[str], data: bytes) -> None:
        """Save the binary data.

        Arguments
        ---------
        file_path: `str | PathLike[str]`
            The path to the output file.

        data: `bytes`
            The byte data to be saved.
        """
        self.data[str(file_path).strip()] = data.decode("utf-8")

    def save_text(self, file_path: str | os.PathLike[str], data: str) -> None:
        """Save the text file.

        Arguments
        ---------
        file_path: `str | PathLike[str]`
            The path to the output file.

        data: `str`
            The text data to be saved.
        """
        self.data[str(file_path).strip()] = data

    def save_data(self, file_path: str | os.PathLike[str], data: Any) -> None:
        """Save the structured data (such as json).

        Arguments
        ---------
        file_path: `str | PathLike[str]`
            The path to the output file.

        data: `Any`
            The structured data to be saved.
        """
        self.data[str(file_path).strip()] = json.dumps(data, indent=2)


def render() -> None:
    """Render the documentation of pydocusaurus."""
    cur_dir = os.path.dirname(__file__)
    out_dir = os.path.join(cur_dir, "docs-{0}".format(pydocusaurus.__name__))
    print(
        "Producing the documentation with the saver {1}: {0}".format(
            out_dir, SaverSingleFile.__name__
        )
    )
    saver = SaverSingleFile()
    pydocusaurus.render_package_as_mdx(
        pydocusaurus, out_dir=out_dir, saver=saver, package_info="cainmagi"
    )
    saver.dump_yaml(os.path.join(cur_dir, "docs-pydocusaurus-single.yml"))


if __name__ == "__main__":
    render()
