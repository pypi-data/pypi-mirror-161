from unittest.mock import Mock

from energinetml.core.model import TrainedModel
from energinetml.core.predicting import PredictionController


class TestPredictionController:
    def test__predictions_returned_in_correct_order(self):
        def __model_predict(trained_model, identifier, input_data):
            """
            :param TrainedModel trained_model:
            :param str identifier:
            :param typing.List[typing.Dict[str, typing.Any]] input_data:
            """
            return [identifier for _ in range(len(input_data))]

        trained_model = TrainedModel(
            features=["feature1", "feature2"],
            models={"identifier1": Mock(), "identifier2": Mock()},
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
                    "features": {"feature1": 3, "feature2": 3},
                },
            ]
        )

        # Act
        result = uut.predict(request, correlation_id="uuid")

        # Assert
        assert result.predictions == ["identifier1", "identifier2", "identifier1"]
        assert result.validations is None
