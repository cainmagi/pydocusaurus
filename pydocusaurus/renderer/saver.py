# -*- coding: UTF-8 -*-
"""
Saver
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
The saver used for dumping output files.
"""

import os
import abc
import json

from typing import Any

__all__ = ("SaverAbstract", "SaverDefault")


class SaverAbstract(abc.ABC):
    """The abstract file saver."""

    @abc.abstractmethod
    def save_bytes(self, file_path: str | os.PathLike[str], data: bytes) -> None:
        """Save the binary data.

        Arguments
        ---------
        file_path: `str | PathLike[str]`
            The path to the output file.

        data: `bytes`
            The byte data to be saved.
        """
        raise NotImplementedError

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

    def save_bytes(self, file_path: str | os.PathLike[str], data: bytes) -> None:
        """Save the binary data.

        Arguments
        ---------
        file_path: `str | PathLike[str]`
            The path to the output file.

        data: `bytes`
            The byte data to be saved.
        """
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "wb") as fobj:
            fobj.write(data)

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
