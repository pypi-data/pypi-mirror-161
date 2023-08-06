from unittest.mock import Mock

import numpy as np

from energinetml.core.model import TrainedModel
from energinetml.core.predicting import PredictionController
from energinetml.core.validation import (
    FeatureType,
    Validator,
    ValidatorStatus,
    create_feature_models,
)


class TestPredictionController:
    def test__predictions_returned_in_correct_order(self):
        def __model_predict(trained_model, identifier, input_data):
            """
            :param TrainedModel trained_model:
            :param str identifier:
            :param typing.List[typing.Dict[str, typing.Any]] input_data:
            """
            return [identifier for _ in range(len(input_data))]

        feature_names = ["feature1", "feature2"]
        feature_models = create_feature_models(
            feature_names=feature_names,
            feature_types=[FeatureType.INT, FeatureType.INT],
            feature_values=[np.array([1, 2, 3]), np.array([1, 2, 3])],
        )

        trained_model = TrainedModel(
            features=feature_names,
            models={"identifier1": Mock(), "identifier2": Mock()},
            validator=Validator(dataset_id="test", feature_models=feature_models),
        )
        uut = PredictionController(
            model=Mock(predict=__model_predict),
            trained_model=trained_model,
            model_version="123",
        )

        request = uut.request_model(
            inputs=[
                {
                    "identifier": "identifier1",
                    "features": {"feature1": 1, "feature2": 1},
                },
                {
                    "identifier": "identifier2",
                    "features": {"feature1": 2, "feature2": 2},
                },
                {
                    "identifier": "identifier1",
                    "features": {"feature1": 30, "feature2": 3},
                },
            ]
        )

        # Act
        result = uut.predict(request, correlation_id="uuid")

        # Assert
        assert result.predictions == ["identifier1", "identifier2", "identifier1"]
        assert result.validations is not None
        assert result.validations[0].get("state") == ValidatorStatus.WARNING.name
        assert result.validations[1].get("state") == ValidatorStatus.VALID.name
        assert result.validations[-1].get("state") == ValidatorStatus.NOT_VALID.name
