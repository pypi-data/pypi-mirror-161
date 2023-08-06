#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""
import pprint
from typing import Any, List, Union

import azureml
import pandas

from energinetml.core.logger import MetricsLogger


class AzureMlLogger(MetricsLogger):
    """[summary]"""

    def __init__(self, run: azureml.core.Run):
        """[summary]

        Args:
            run (azureml.core.Run): [description]
        """
        self.run = run

    def echo(self, s: str) -> None:
        """Echo wrapper.

        Args:
            s (str): String we want to log.
        """
        print(s)

    def log(self, name: str, value: Union[float, int, str]) -> None:
        """[summary]

        Args:
            name (str): [description]
            value (Union[float, int, str]): [description]
        """
        self.run.log(name, value)
        self.echo(f"LOG: {name} = {value}")

    def tag(self, key: str, value: str) -> None:
        """[summary]

        Args:
            key (str): [description]
            value (str): [description]
        """
        self.run.tag(key, value)
        self.echo(f"TAG: {key} = {value}")

    def table(
        self, name: Union[str, Any], dict_of_lists: List[dict], echo=True
    ) -> None:
        """[summary]

        Args:
            name (Union[str, Any]): [description]
            dict_of_lists (List[dict]): [description]
            echo (bool, optional): [description]. Defaults to True.
        """
        list_of_dicts = [
            dict(zip(dict_of_lists, t)) for t in zip(*dict_of_lists.values())
        ]

        for _dict in list_of_dicts:
            self.run.log_table(name, _dict)

        if echo:
            # TODO print actual table
            self.echo(f"{name}:")
            self.echo(pprint.PrettyPrinter(indent=4).pformat(dict_of_lists))

    def dataframe(self, name: str, df: pandas.DataFrame) -> None:
        """[summary]

        Args:
            name (str): [description]
            df (pandas.DataFrame): [description]
        """
        df = df.reset_index()
        self.table(name, df.to_dict(orient="list"), echo=False)
        self.echo(df.to_string())
