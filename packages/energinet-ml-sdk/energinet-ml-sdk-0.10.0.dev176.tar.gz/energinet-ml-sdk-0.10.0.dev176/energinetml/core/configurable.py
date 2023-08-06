#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""

import json
import os
from dataclasses import asdict, dataclass
from typing import Dict, Union

from energinetml.settings import DEFAULT_ENCODING


@dataclass
class Configurable:
    """[summary]"""

    class ConfigNotFound(Exception):
        """[summary]"""

        pass

    class ConfigError(Exception):
        """_summary_

        Args:
            Exception (_type_): _description_

        Raises:
            RuntimeError: _description_
            cls.NotFound: _description_

        Returns:
            _type_: _description_
        """

        pass

    # Constants
    _CONFIG_FILE_NAME = None

    # Members
    path: str

    @classmethod
    def create(cls, path: str, **kwargs) -> "Configurable":
        """[summary]

        Args:
            path (str): [description]

        Returns:
            Configurable: [description]
        """
        obj = cls(path=path, **kwargs)
        obj.save()
        return obj

    @classmethod
    def from_config_file(cls, file_path: str) -> "Configurable":
        """[summary]

        Args:
            file_path (str): [description]

        Returns:
            Configurable: [description]
        """
        with open(file_path, encoding=DEFAULT_ENCODING) as f:
            return cls(path=os.path.split(file_path)[0], **json.load(f))

    @classmethod
    def from_directory(cls, path: str) -> "Configurable":
        """[summary]

        Args:
            path (str): [description]

        Raises:
            RuntimeError: [description]
            cls.NotFound: [description]

        Returns:
            Configurable: [description]
        """
        if cls._CONFIG_FILE_NAME is None:
            raise RuntimeError("Attribute _CONFIG_FILE_NAME is None")

        file_pointer = locate_file_upwards(path, cls._CONFIG_FILE_NAME)

        if file_pointer is not None:
            return cls.from_config_file(file_pointer)
        else:
            raise cls.ConfigNotFound()

    def get_file_path(self, *relative_path: str) -> str:
        """Returns absolute path to a file at relative_path,
        where relative_path is relative to config file.

        Args:
            *relative_path (str): [description]

        Returns:
            str: [description]
        """

        return os.path.abspath(os.path.join(self.path, *relative_path))

    def get_relative_file_path(self, absolute_path: str) -> str:
        """Provided an absolute file path, returns the path relative
        to config file.

        Args:
            absolute_path (str): [description]

        Returns:
            str: [description]
        """
        return os.path.relpath(absolute_path, self.path)

    def save(self) -> None:
        """Saved config as JSON to filesystem."""
        if not os.path.isdir(self.path):
            os.makedirs(self.path)

        config_file_path = self.get_file_path(self._CONFIG_FILE_NAME)
        with open(config_file_path, "w", encoding=DEFAULT_ENCODING) as f:
            d = asdict(self)
            d.pop("path")
            json.dump(d, f, indent=4, sort_keys=True)

    def as_dict(self) -> Dict[str, str]:
        """Get the object variables as a dictionary.
        Helpful in creation of a meta_data dictionary

        returns:
            Dict[str, str]:
        """
        return self.__dict__


def locate_file_upwards(path: str, filename: str) -> Union[str, None]:
    """locate a file and return its path. starts from the path-parameter and searches
    upwards to the root.

    args:
        path (str): the path where the search will start
        filename (str): the filename of the file to search for

    returns:
        str: the path of the file if found
    """

    def __is_root(_path: str) -> str:
        """[summary]

        args:
            _path (str): [description]

        returns:
            str: [description]
        """
        # you have yourself root.
        # works on windows and *nix paths.
        # does not work on windows shares (\\server\share)
        return os.path.dirname(_path) == _path

    while 1:
        file_pointer = os.path.join(path, filename)
        if os.path.isfile(file_pointer):
            return file_pointer
        elif __is_root(path):
            return None
        else:
            path = os.path.abspath(os.path.join(path, ".."))
