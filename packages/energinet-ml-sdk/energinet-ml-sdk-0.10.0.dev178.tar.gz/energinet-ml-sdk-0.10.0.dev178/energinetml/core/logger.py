#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The logger module is essential for logging an experiment important numbers
doing a training.
"""
from __future__ import annotations

import io
import os
import sys
from typing import TYPE_CHECKING, Any, Tuple  # noqa TYP001

if TYPE_CHECKING:
    import pandas as pd

from energinetml.settings import (
    DEFAULT_LOG_ENCODING,
    DEFAULT_LOG_FILENAME,
    DEFAULT_LOG_PATH,
)


class ConsoleLogger:
    """This class enables logging of stdout and stderr.
    The class is used during local trainings and finally uploaded to the azure ml
    expirment.

    Args:
        name (str): Name of the log file.
        console (io.TextIOWrapper, optional): Possible values
            [sys.stdout, sys.stderr]. Defaults to sys.stdout.

    Returns:
        object: A console logger object which can be used to overwrite
            the default sys.std* object.
    """

    def __init__(
        self,
        name: str,
        console: io.TextIOWrapper = sys.stdout,
    ):
        """Init ConsoleLogger with either sys.stdout or sys.stderr."""
        self.console = console

        file_prefix, ext = DEFAULT_LOG_FILENAME.split(".")
        self.filename = f"{file_prefix}_{name}.{ext}"

        self.filepath, self.log = self._init_log_file(self.filename)

    def _init_log_file(self, filename: str) -> Tuple[str, io.TextIOWrapper]:
        """Performs Initialization of the log file and further enrich the object."""
        os.makedirs(DEFAULT_LOG_PATH, exist_ok=True)

        filepath = f"{DEFAULT_LOG_PATH}/{filename}"
        return filepath, open(filepath, "w", encoding=DEFAULT_LOG_ENCODING)

    def isatty(self) -> bool:
        """A requried function for sys.stdout and sys.stderr.

        Returns:
            bool: This function will only return False.
        """
        return False

    def write(self, message: str) -> None:
        """A requried function for sys.stdout and sys.stderr.
        The function will both print to file and to console.

        Args:
            message (str): The string which needs to be appended to the log.
        """
        self.log.write(message)
        self.console.write(message)

    def flush(self):
        """The function flush the io buffer.
        This function is called before uploading to azure ml.
        """
        self.log.flush()


class MetricsLogger:
    """A logger to use for logging experiments."""

    def echo(self, s: str) -> None:
        """Write to console.

        Args:
            s: The string to be shown.

        Raises:
            NotImplementedError: [description]

        Example:
            >>> s = "Loading data"
            >>> logger.echo(s)

        """
        raise NotImplementedError

    def log(self, name: str, value: Any) -> None:
        """Log a name-value pair.

        Args:
            name (str): Name for the logged parameter.
            value (Any): Value for the logged parameter.

        Example:
            >>> name = "score"
            >>> value = model.score()
            >>> logger.log(name, value)

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError

    def tag(self, key: str, value: str) -> None:
        """[summary]

        Args:
            key (str): [description]
            value (str): [description]

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError

    def dataframe(self, name: str, df: pd.DataFrame) -> None:
        """[summary]

        Args:
            name (str): [description]
            df (pd.DataFrame): [description]

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError
