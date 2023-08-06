#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict  # noqa TYP001

if TYPE_CHECKING:
    from energinetml import Model, TrainedModel

from energinetml.core.logger import ConsoleLogger


class TrainingError(Exception):
    pass


class AbstractTrainingContext:
    """[summary]"""

    def train_model(
        self, model: Model, tags: Dict[str, Any], *args: Any, **kwargs: Dict[str, Any]
    ) -> TrainedModel:
        """[summary]

        Args:
            model (Model): [description]
            tags (Dict[str, Any]): [description]

        Returns:
            TrainedModel: [description]
        """
        pass

    def save_artifacts(self, model: Model) -> None:
        """Saves output files from a training run if necessary.

        Args:
            model (Model): [description]
        """
        pass

    def get_parameters(self, model: Model) -> Dict[str, str]:
        """Returns parameters for a training.

        Args:
            model (Model): [description]

        Returns:
            Dict[str, str]: [description]
        """
        return {}

    def get_tags(self, model: Model) -> Dict[str, str]:
        """Returns tags for a training.

        Args:
            model (Model): [description]

        Returns:
            Dict[str, str]: [description]
        """
        return {}

    def save_logs(self, clog: ConsoleLogger) -> None:
        """This function takes the log file generated from clog and
        pushes the log into the azure ml expiremnt tab called output.

        Args:
            clog (ConsoleLogger): This argument is an object of our logger function.

        """
        pass

    def save_meta_data(self, meta_data: Dict[str, str], meta_file_path: str):
        """Create a meta json-file with the content from a meta_data dictionary
        and save it to the path specified.

        Args:
            meta_data (Dict[str, str])): A dictionary of meta_data to persist in the
            json-file
            meta_file_path (str): The local path where the json-file is persisted.

        """
        pass


def requires_parameter(name, typ):
    """[summary]

    Args:
        name ([type]): [description]
        typ ([type]): [description]
    """

    def requires_parameter_decorator(func):
        """[summary]

        Args:
            func ([type]): [description]
        """

        def requires_parameter_inner(*args: Any, **kwargs: Dict[str, Any]):
            """[summary]

            Raises:
                TrainingError: [description]
                TrainingError: [description]

            Returns:
                [type]: [description]
            """
            if name not in kwargs:
                raise TrainingError(f'Missing parameter "{name}"')
            try:
                kwargs[name] = typ(kwargs.get(name))
            except ValueError:
                raise TrainingError(
                    (
                        f'Parameter "{name}" could not be cast '
                        f"to type { typ.__name__}: { kwargs.get(name)}"
                    )
                )
            return func(*args, **kwargs)

        return requires_parameter_inner

    return requires_parameter_decorator
