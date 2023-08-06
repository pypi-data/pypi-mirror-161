"""
/predict request body JSON example:

    {
        "inputs": [
            {
                "identifier": "foo",
                "features": {
                    "age": 20,
                    "height": 180
                }
            },
            {
                "identifier": "bar",
                "features": {
                    "age": 30,
                    "height": 200
                }
            },
            {
                "identifier": "foo",
                "features": {
                    "age": 20,
                    "height": 180
                }
            }
        ]
    }

"""
import json
import time
from enum import Enum
from functools import cached_property
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

import pandas as pd
import pydantic
from opentelemetry import trace
from opentelemetry.trace import SpanKind

from energinetml.core.validation import ValidatorResponse, ValidatorStatus

if TYPE_CHECKING:
    from energinetml.core.model import Model, TrainedModel

tracer = trace.get_tracer(__name__)


class PredictionInput(list):
    """A class to use when handling data in :func:`~energinetml.Model.predict`"""

    def __init__(self, features: List[str], *args, **kwargs):
        """[summary]

        Args:
            features (List[str]): [description]
        """
        super().__init__(*args, **kwargs)
        self.features = features

    def as_dict_of_lists(self) -> Dict[str, Any]:
        """[summary]"""
        return {
            feature: [input[feature] for input in self] for feature in self.features
        }

    def as_pandas_dataframe(self) -> pd.DataFrame:
        """[summary]

        Raises:
            RuntimeError: [description]

        Returns:
            pd.DataFrame: [description]
        """

        return pd.DataFrame(self.as_dict_of_lists())


# -- Data models -------------------------------------------------------------


class PredictRequest(pydantic.BaseModel):
    """[summary]"""

    inputs: List[Any]

    def group_input_by_identifier(self):
        """[summary]

        Returns:
            [type]: TODO: I need help for this data structure.
        """
        inputs_per_identifier = {}

        for index, input in enumerate(self.inputs):
            if hasattr(input, "identifier"):
                identifier = input.identifier.value
            else:
                identifier = None

            inputs_per_identifier.setdefault(identifier, []).append(
                (index, dict(input.features))
            )

        return inputs_per_identifier.items()


class PredictResponse(pydantic.BaseModel):
    """[summary]"""

    predictions: List[Any]
    validations: Optional[List[Any]]


# -- Controller --------------------------------------------------------------


class PredictionController:
    """[summary]"""

    def __init__(
        self,
        model: "Model",
        trained_model: "TrainedModel",
        model_version: str = None,
    ):
        """[summary]

        Args:
            model (Model): [description]
            trained_model (TrainedModel): [description]
            model_version (str, optional): [description]. Defaults to None.
        """
        self.model = model
        self.trained_model = trained_model
        self.model_version = model_version

        self.predict_features = self.generate_validator_model(
            model_name="PredictFeatures", use_validation=False
        )
        self.predict_features_validator = self.generate_validator_model(
            model_name="PredictFeaturesValidator", use_validation=True
        )

    def generate_validator_model(
        self, model_name: str, use_validation: bool = True
    ) -> Optional[pydantic.BaseModel]:
        """A method for creating the validator object during initialization of the
        endpoint. The method depends on self.trained_model.validator and returns a
        pydantic.BaseModel if validator has been provided during training.

        Args:
            model_name (str): Name of the pydantic.BaseModel.
            use_validation (bool, optional): A boolean which enables the
            pydantic.BaseModel to use a validtor. Defaults to True.

        Returns:
            pydantic.BaseModel: A pydantic.BaseModel with or without a valdator.
        """
        validator = self.trained_model.validator

        if validator:
            validator_model = validator.get_pydantic_model(
                model_name=model_name, use_validation=use_validation
            )
        else:
            validator_model = None

        return validator_model

    @property
    def identifiers(self) -> List[str]:
        """[summary]

        Returns:
            List[str]: [description]
        """
        return self.trained_model.identifiers

    @property
    def features(self) -> List[str]:
        """[summary]

        Returns:
            List[str]: [description]
        """
        return self.trained_model.features

    @property
    def requires_identity(self) -> bool:
        """[summary]

        Returns:
            bool: [description]
        """
        return not self.trained_model.has_default_model()

    @cached_property
    def request_model(self):
        """
        Build a request model class (inherited from pydantic.BaseModel)
        based on a specific TrainedModel instance. The resulting model
        can be used for JSON input validation, Swagger docs etc.
        """

        predict_features = (
            self.predict_features
            if self.predict_features
            else pydantic.create_model(
                "PredictFeatures", **{feature: (Any, ...) for feature in self.features}
            )
        )

        predict_input_attributes = {"features": (predict_features, ...)}

        if self.requires_identity:
            identifier_enum = Enum("IdentifierEnum", {i: i for i in self.identifiers})
            predict_input_attributes["identifier"] = (identifier_enum, ...)

        predict_input = pydantic.create_model(
            "PredictInput", **predict_input_attributes
        )

        return pydantic.create_model(
            "PredictRequest",
            __base__=PredictRequest,
            inputs=(List[predict_input], ...),
        )

    @property
    def response_model(self):
        """[summary]"""
        return PredictResponse

    def predict(
        self, request: PredictRequest, correlation_id: str = None
    ) -> PredictResponse:
        """[summary]

        Args:
            request (PredictRequest): [description]
            correlation_id (str, optional): [description]. Defaults to None.

        Returns:
            PredictResponse: [description]
        """
        start_span = tracer.start_span(name="prediction", kind=SpanKind.SERVER)

        with start_span as span:
            start = time.perf_counter()
            identifiers, features, predictions, validations = self.invoke_model(request)
            end = time.perf_counter()

            if correlation_id:
                span.set_attribute("correlation_id", correlation_id)
            span.set_attribute("duration_model", str(end - start))
            span.set_attribute("model_name", self.model.name)
            if self.model_version is not None:
                span.set_attribute("model_version", self.model_version)
            span.set_attribute("identifiers", json.dumps(identifiers))
            span.set_attribute("features", json.dumps(features))
            span.set_attribute("predictions", json.dumps(predictions))
            span.set_attribute("validations", json.dumps(validations))

        return self.response_model(predictions=predictions, validations=validations)

    def _validate_features(self, features: Dict[str, Any]) -> ValidatorResponse:
        """validate method for a single entity.

        Args:
            features (Dict[str, Any]): Key value mapping of given features.

        Returns:
            ValidatorResponse: The validator response.
        """
        try:
            self.predict_features_validator(**features)
        except pydantic.ValidationError as pve:

            error_dict = json.loads(pve.json())
            error_states = [
                ValidatorStatus(item.get("ctx", {}).get("state")) for item in error_dict
            ]
            error_state = (
                ValidatorStatus.NOT_VALID
                if ValidatorStatus.NOT_VALID in error_states
                else ValidatorStatus.WARNING
            )

            return ValidatorResponse(
                state=error_state.name,
                message=json.dumps(error_dict),
            )

        else:
            return ValidatorResponse(state=ValidatorStatus.VALID.name)

    def validate_input_data(
        self, input_data: PredictionInput
    ) -> List[ValidatorResponse]:
        """An nput data validation method.

        Args:
            input_data (PredictionInput): Retrived input data

        Returns:
            List[ValidatorResponse]: A list with ValidatorReponses.
        """

        if self.predict_features_validator:

            validated_inputs: List[ValidatorResponse] = [
                self._validate_features(features) for features in input_data
            ]

        else:
            validated_inputs: List[ValidatorResponse] = [
                ValidatorResponse(state=ValidatorStatus.NOT_USED.name)
                for _ in input_data
            ]

        return validated_inputs

    def invoke_model(
        self, request: PredictRequest
    ) -> Tuple[List[str], List[str], List[Any], List[ValidatorResponse]]:
        """[summary]

        Args:
            request (PredictRequest): [description]

        Raises:
            RuntimeError: [description]

        Returns:
            PredictResponse: [description]
        """
        groups = list(request.group_input_by_identifier())
        identifiers_ordered = [... for _ in range(len(request.inputs))]
        features_ordered = [i for i in request.inputs]
        predictions_ordered = [... for _ in range(len(request.inputs))]
        validated_features_ordered: List[ValidatorResponse] = [
            ... for _ in range(len(request.inputs))
        ]

        # Invoke predict() for each unique identifier
        for identifier, inputs in groups:
            indexes = [i[0] for i in inputs]
            feature_sets = [i[1] for i in inputs]
            input_data = PredictionInput(self.features, feature_sets)

            input_data_validated = self.validate_input_data(input_data)
            predict_result = self.model.predict(
                trained_model=self.trained_model,
                identifier=identifier,
                input_data=input_data,
            )

            for index, features, prediction, validated_inputs in zip(
                indexes, feature_sets, predict_result, input_data_validated
            ):

                identifiers_ordered[index] = identifier
                features_ordered[index] = features
                predictions_ordered[index] = prediction
                if self.predict_features_validator:
                    validated_features_ordered[index] = validated_inputs.dict()

        # If elipsis still exist in the predictions,
        # there is not the same number of inputs as outputs.
        # This is will most likely be due to a wrong predict
        # function implementation
        if ... in predictions_ordered:
            raise RuntimeError(
                "The number of inputs and outputs is not equal"
                " for the given model. Please check the predict function.\n"
            )

        return (
            identifiers_ordered,
            features_ordered,
            predictions_ordered,
            validated_features_ordered if self.predict_features_validator else None,
        )
