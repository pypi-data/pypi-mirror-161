"""A module for the feature validator"""

import enum
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import uuid4

import numpy as np
import pandas as pd  # type: ignore
import pydantic


def get_uuid() -> str:
    """A function which returns a uuid4 as a string."""
    return str(uuid4())


class ValidatorStatus(str, enum.Enum):
    """Current possibly status of the validator."""

    VALID = enum.auto()
    WARNING = enum.auto()
    NOT_VALID = enum.auto()
    NOT_USED = enum.auto()


class ValidatorResponse(pydantic.BaseModel):
    """A container to hold validator information."""

    state: Union[ValidatorStatus, str]
    message: Optional[str]


class FeatureType(enum.Enum):
    """Currently supporten types. This enum is used when doing the dynamic pydantic
    Model creation inside pydantic.create_model()."""

    INT = int
    FLOAT = float
    STRING = str
    CATEGORY = str
    DATETIME = datetime


class FeatureMetaDataMissing(Exception):
    """The class raised if meta_data is not valid."""

    def __init__(self, name: str, message: str) -> None:
        self.name = name
        self.message = message
        super().__init__(message)


class FeatureValueError(ValueError):
    """The class is raised if feature validator gets a not valid input value."""

    def __init__(self, state: ValidatorStatus, message: str) -> None:
        self.state = state
        super().__init__(message)


@dataclass
class Validator:
    """The validator class contains one or several feature validator(s)."""

    dataset_id: str
    feature_models: List[
        Union[
            "IntegerFeature",
            "FloatFeature",
            "StringFeature",
            "CategoricalFeature",
            "DatetimeFeature",
        ]
    ]

    validator_uuid: str = field(default_factory=get_uuid)

    def get_features(self) -> Dict[str, Tuple["FeatureType", ...]]:
        """The get_feature() method can be unwrapped and used as input arguments
        in the dynamic model with the create_model() method.

        Returns:
            Dict[str, Tuple[FeatureType, ...]]: A dictionary with key as feature name
            and value as tuple with feature type and dots (...) for feature value.
        """
        return {
            feature.name: (feature.feature_type.value, ...)
            for feature in self.feature_models
        }

    def get_validators(self) -> Dict[str, pydantic.validator]:
        """The get_validators() method can be used as a validator when instantiating
        the dynamic model with the create_model() method.

        Returns:
            Dict[str, validator]: A dictionary with key as validatorname name
            and value as the validator for the given feature.
        """
        prefix: str = "_check_"

        return {
            f"{prefix}{feature.name}": feature.get_validator()
            for feature in self.feature_models
        }

    def get_pydantic_model(
        self, model_name: str = "PredictFeatures", use_validation: bool = True
    ) -> pydantic.BaseModel:
        """This method wraps the get_feature method and the get _valdiators method into
        a pydantic.BaseModel object.

        Args:
            model_name (str, optional): Name of the pydantic.BaseModel.
            Defaults to "PredictFeatures".
            use_validation (bool, optional): Boolean argument for including a validator.
            Defaults to True.

        Returns:
            pydantic.BaseModel: A pydantic.BaseModel which corresponds to the
            input features for a given model.
        """

        return pydantic.create_model(
            __model_name=model_name,
            **self.get_features(),
            __base__=pydantic.BaseModel,
            __validators__=self.get_validators() if use_validation else None,
        )


def create_feature_models(
    feature_names: List[str],
    feature_types: List["FeatureType"],
    feature_values: List[Union[pd.Series, np.ndarray]],
) -> List[
    Union[
        "IntegerFeature",
        "FloatFeature",
        "StringFeature",
        "CategoricalFeature",
        "DatetimeFeature",
    ]
]:
    """The functuon takes three arguments. All arguments are lists and need to have an
    equal length.
    The function returns a list of features which will be used as an argument in the
    Validator class.

    Args:
        feature_names (List[str]): List with feature names.
        feature_types (List[FeatureType]): List with feature types.
        feature_values (List[Union[pd.Series, np.ndarray]]): List with feature values

    Raises:
        ValueError: Is raised if the input arguments have different lengths.
        NotImplementedError: Is raised if feature types are unknown.

    Returns:
        [List]: A list with Features.
    """
    if (len(feature_names) != len(feature_types)) | (
        len(feature_names) != len(feature_values)
    ):
        raise ValueError(
            (
                "The input arguments have inconsistent lengths:"
                f" feature_names={len(feature_names)},"
                f" feature_types={len(feature_types)},"
                f" feature_values={len(feature_values)}."
            )
        )

    features: List[
        Union[
            "IntegerFeature",
            "FloatFeature",
            "StringFeature",
            "CategoricalFeature",
            "DatetimeFeature",
        ]
    ] = []

    for f_name, f_type, f_values in zip(feature_names, feature_types, feature_values):

        if f_type == FeatureType.INT:
            feature = IntegerFeature(f_name)
        elif f_type == FeatureType.FLOAT:
            feature = FloatFeature(f_name)
        elif f_type == FeatureType.STRING:
            feature = StringFeature(f_name)
        elif f_type == FeatureType.CATEGORY:
            feature = CategoricalFeature(f_name)
        elif f_type == FeatureType.DATETIME:
            feature = DatetimeFeature(f_name)
        else:
            raise NotImplementedError(
                f"The feature type '{f_type}' is not implemented."
            )

        feature.describe_func(f_values)
        features.append(feature)

    return features


@dataclass
class Feature(ABC):
    """The Feature class defines the interface for the default and
    future customised feature validators."""

    name: str
    feature_type: "FeatureType"
    meta_data: Optional[Dict[str, Any]] = None

    @abstractmethod
    def describe_func(self, *args) -> None:
        """This method is used to update the meta_data dictionary
        which later will be used in its validate_func()."""

    @abstractmethod
    def validate_func(self, v: Any) -> None:
        """A method which performs validation accordently to the values
        in the meta_data dictionary. It returns the input value if valid
        otherwise raises a proper exepction."""

    def get_validator(self) -> pydantic.validator:
        """A method used to return the validator of a given feature."""
        val_args: Dict = {"pre": True, "each_item": True, "allow_reuse": True}

        if self.meta_data:
            return pydantic.validator(self.name, **val_args)(self.validate_func)
        else:
            return None


@dataclass
class IntegerFeature(Feature):
    """The default class used for an integer feature."""

    feature_type: "FeatureType" = FeatureType.INT

    def describe_func(
        self, x: Union[pd.Series, np.ndarray, list], x_percentile: float = 0.95
    ) -> None:
        """This method is used to update the meta_data dictionary for the
        default integer feature validation.

        Args:
            x (pd.Series, np.ndarray, list): A list of numbers.
            x_percentile (float, optional): The percentile we want to use as a
            warning level. Defaults to 0.95.
        """
        if not isinstance(x, (pd.Series, np.ndarray, list)):
            raise TypeError(
                f"The input argument 'x' must be a pandas Series, numpy array or list."
                f" The input argument is of type {type(x)}."
            )

        warn_low, warn_high = np.percentile(
            x,
            q=np.array(
                # compute lower and upper quantile
                [((1 - x_percentile) / 2) * 100, (1 - (1 - x_percentile) / 2) * 100]
            ),
        )

        self.meta_data = {
            "warn_low": warn_low,
            "warn_high": warn_high,
            "skip_low": min(x),
            "skip_high": max(x),
        }

    def validate_func(self, v: Union[int, float]) -> Union[int, float]:
        """The integer validation function which uses its meta_data dictionary.

        Args:
            v (Union[int, float]): An input value the model needs to validate.

        Raises:
            ValueError: Will raised if the input value does not comply with
            the validation schema.

        Returns:
            Union[int, float]: A valid input value.
        """
        skip_low: float = self.meta_data.get("skip_low", None)
        skip_high: float = self.meta_data.get("skip_high", None)
        warn_low: float = self.meta_data.get("warn_low", None)
        warn_high: float = self.meta_data.get("warn_high", None)

        if v < skip_low:
            raise FeatureValueError(
                message=(
                    f"{self.name}={v} - lower than skip level ({v} < {skip_low})."
                ),
                state=ValidatorStatus.NOT_VALID,
            )
        if v > skip_high:
            raise FeatureValueError(
                message=(
                    f"{self.name}={v} - higher than skip level ({v} > {skip_high})."
                ),
                state=ValidatorStatus.NOT_VALID,
            )
        if v < warn_low:
            raise FeatureValueError(
                message=f"{self.name}={v} - lower than warn level ({v} < {warn_low}).",
                state=ValidatorStatus.WARNING,
            )
        if v > warn_high:
            raise FeatureValueError(
                message=(
                    f"{self.name}={v} - higher than warn level ({v} > {warn_high})."
                ),
                state=ValidatorStatus.WARNING,
            )
        return v


@dataclass
class FloatFeature(IntegerFeature):
    """The default class used for an float feature."""

    feature_type: FeatureType = FeatureType.FLOAT


@dataclass
class StringFeature(Feature):
    """The default class used for an string (/character) feature."""

    feature_type: FeatureType = FeatureType.STRING

    def describe_func(self, x: Union[pd.Series, np.ndarray]) -> None:
        """A method to update the meta_data dictionary with unique string values.

        Args:
            x (pd.Series): A pandas series with object aka. characters
            (or categorical) values.
        """
        self.meta_data = {
            "unique_values": x.unique().tolist(),
        }

    def validate_func(self, v: str) -> str:
        """The string validation function which uses its meta_data dictionary.

        Args:
            v str: An input value the model needs to validate.

        Raises:
            ValueError: Will raised if the input value does not comply with
            the validation schema.

        Returns:
            str: A valid input value.
        """
        unique_values: List[str] = self.meta_data.get("unique_values", None)

        if v not in unique_values:
            raise FeatureValueError(
                message=f"{self.name}={v} - value is not in ({unique_values}).",
                state=ValidatorStatus.NOT_VALID,
            )
        return v


@dataclass
class CategoricalFeature(StringFeature):
    """The default class used for an categorical feature."""

    ordered: bool = False
    feature_type: FeatureType = FeatureType.CATEGORY


@dataclass
class DatetimeFeature(Feature):
    """The default class used for an integer feature."""

    feature_type: FeatureType = FeatureType.DATETIME
    datetime_format: str = "%Y-%m-%d %H:%M:%S.%f"

    def describe_func(self, x: Union[pd.Series, np.ndarray]) -> None:
        """This method is used to update the meta_data dictionary for the
        default datetime feature validation.

        Args:
            x (pd.Series): A pandas series with datetime values.
        """
        self.meta_data = {
            "skip_low": x.min(),
            "skip_high": x.max(),
        }

    def validate_func(self, v: datetime) -> datetime:
        """The datetime validation function which uses its meta_data dictionary.

        Args:
            v datetime: An input value the model needs to validate.

        Raises:
            ValueError: Will raised if the input value does not comply with
            the validation schema.

        Returns:
            datetime: A valid input value.
        """

        """"""
        skip_low: datetime = self.meta_data.get("skip_low", None)
        skip_high: datetime = self.meta_data.get("skip_high", None)

        if isinstance(v, str):
            v = datetime.strptime(v, self.datetime_format)
        if v < skip_low:
            raise FeatureValueError(
                message=f"{self.name}={v} - lower than skip level ({v} < {skip_low}).",
                state=ValidatorStatus.NOT_VALID,
            )
        if v > skip_high:
            raise FeatureValueError(
                message=(
                    f"{self.name}={v} - higher than skip level ({v} > {skip_high})."
                ),
                state=ValidatorStatus.NOT_VALID,
            )
        return v
