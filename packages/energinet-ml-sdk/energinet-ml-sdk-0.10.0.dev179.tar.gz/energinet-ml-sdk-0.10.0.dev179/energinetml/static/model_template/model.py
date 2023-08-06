#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This is the NewModel class which defines the training logic and
inference logic.
"""

import typing

from energinetml import MetricsLogger, Model, PredictionInput, TrainedModel
from energinetml.azure.datasets import MLDataStore


class NewModel(Model):
    """EML SDK model class. This class captures training logic and inference logic."""

    def train(
        self,
        datasets: MLDataStore,
        logger: MetricsLogger,
        seed: int,
        **params: typing.Dict[str, typing.Any]
    ) -> TrainedModel:
        """Define your training logic.

        Args:
            datasets (MLDataStore): A reference to the data set.
            logger (MetricsLogger): The logger argument handle metric logging, etc.
            seed (typing.Any): The seed argument tries to obtain a deterministic
            environment for model experiments.

        Returns:
            TrainedModel: A serializable object of the train model.
        """

        # TODO Train your model here and return it

        raise NotImplementedError

        return TrainedModel()

    def predict(
        self, trained_model: TrainedModel, input_data: PredictionInput, identifier: str
    ) -> typing.List[typing.Any]:
        """Define your prediction logic.

        Args:
            trained_model (TrainedModel): Your trained model object.
            input_data (PredictionInput): Data used for inference.
            identifier (str): A unique identifier which refers to a specific model in
            the model obejct.

        Returns:
            typing.List[typing.Any]: The output(s) of the model.
        """

        # TODO Predict using the trained model and return the prediction

        raise NotImplementedError
