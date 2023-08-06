#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]"""

import importlib
import inspect
import json
import os
import pickle
import random
import shutil
import sys
import tempfile
import zipfile
from dataclasses import dataclass, field
from functools import cached_property
from typing import (
    TYPE_CHECKING,
    Any,
    ContextManager,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Union,
)

import pandas as pd
import pydantic

from energinetml.azure.datasets import MLDataStore
from energinetml.backend import default_backend as backend
from energinetml.core.configurable import Configurable, locate_file_upwards
from energinetml.core.files import FileMatcher, temporary_folder
from energinetml.core.logger import MetricsLogger
from energinetml.core.predicting import PredictionController, PredictResponse
from energinetml.core.project import MachineLearningProject, Project
from energinetml.core.requirements import RequirementList
from energinetml.core.validation import Validator
from energinetml.settings import (
    DEFAULT_RELATIVE_ARTIFACT_PATH,
    EMPTY_MODEL_TEMPLATE_DIR,
)

if TYPE_CHECKING:
    from energinetml.core.predicting import PredictionInput

# Constants
# TODO Move to settings.py?
REQUIREMENTS_FILE_NAME = "requirements.txt"
DEFAULT_FILES_INCLUDE = ["**/*.py", "model.json", REQUIREMENTS_FILE_NAME]
DEFAULT_FILES_EXCLUDE = []


@dataclass
class Model(Configurable):
    """
    Class for holding a model.

    Attributes:
        name: Name of the model
        experiment: Name of the experiment
        compute_target: Compute target
        vm_size: Size of the virtual machine targeted
    """

    name: str
    experiment: str
    compute_target: str
    vm_size: str
    datasets: List[str] = field(default_factory=list)
    datasets_local: List[str] = field(default_factory=list)
    datasets_cloud: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    parameters_local: Dict[str, Any] = field(default_factory=dict)
    parameters_cloud: Dict[str, Any] = field(default_factory=dict)
    features: List[str] = field(default_factory=list)
    files_include: List[str] = field(default_factory=list)
    files_exclude: List[str] = field(default_factory=list)

    # Constants
    _CONFIG_FILE_NAME = "model.json"
    _SCRIPT_FILE_NAME = "model.py"
    _TRAINED_MODEL_FILE_NAME = "model.pkl"
    _META_FILE_NAME = "meta.json"
    _REQUIREMENTS_FILE_NAME = REQUIREMENTS_FILE_NAME

    @classmethod
    def create(cls, *args: Any, **kwargs: Dict[str, Any]) -> "Model":
        """[summary]

        Returns:
            Model: [description]
        """
        model = super().create(*args, **kwargs)

        # Copy template files
        for filename in os.listdir(EMPTY_MODEL_TEMPLATE_DIR):
            src = os.path.join(EMPTY_MODEL_TEMPLATE_DIR, filename)
            dst = os.path.join(model.path, filename)
            if os.path.isfile(src):
                shutil.copyfile(src, dst)

        return model

    @cached_property
    def project(self) -> Union[MachineLearningProject, None]:
        """Returns the Project which this model belongs to.

        Returns:
            Union[MachineLearningProject, None]
        """

        try:
            return MachineLearningProject.from_directory(self.path)
        except MachineLearningProject.ConfigNotFound:
            return None

    @cached_property
    def datasets_parsed(self) -> "ModelDatasets":
        """[summary]

        Returns:
            ModelDatasets
        """
        return ModelDatasets(self)

    @property
    def trained_model_path(self) -> str:
        """Returns path to the trained model."""
        return self.get_file_path(
            DEFAULT_RELATIVE_ARTIFACT_PATH, self._TRAINED_MODEL_FILE_NAME
        )

    @property
    def parent_levels(self) -> int:
        """
        Returns the number of parent levels.

        This is relevant in regards to support of relative imports.

        Returns:
            int
        """

        counts = [dir.count("..") for dir in self.files_include]
        relative_import_levels = max(counts)

        return relative_import_levels + 1

    @property
    def artifact_path(self) -> str:
        """Path to the artifact folder of a trained model. The folder should contain
        the model.pkl file.

        Returns:
            str
        """
        return self.get_file_path(DEFAULT_RELATIVE_ARTIFACT_PATH)

    @property
    def data_folder_path(self) -> str:
        """Returns path to the data folder.

        Returns:
            str
        """
        return self.get_file_path("data")

    @property
    def requirements_file_path(self) -> str:
        """Absolute path to requirements.txt file.

        Returns:
            str
        """
        return self.get_file_path(self._REQUIREMENTS_FILE_NAME)

    @cached_property
    def requirements(self) -> RequirementList:
        """[summary]

        Returns:
            RequirementList
        """
        if os.path.isfile(self.requirements_file_path):
            return RequirementList.from_file(self.requirements_file_path)
        elif self.project:
            return self.project.requirements
        else:
            return RequirementList()

    @property
    def files(self) -> FileMatcher:
        """Returns an iterable of files to include when submitting a model to
        the cloud. These are the files necessary to run training in the cloud.

        File paths are relative to model root.

        NB: Does NOT include requirements.txt !!!

        Returns:
            FileMatcher
        """
        return FileMatcher(
            root_path=self.path,
            include=self.files_include,
            exclude=self.files_exclude,
            recursive=True,
        )

    @property
    def module_name(self) -> str:
        """The name of the module to which the model belongs.

        The last part of the name is excluded, since it is always `model`
        and is unneeded.

        Returns:
            str
        """
        module_parts = self.__module__.split(".")[:-1]

        return ".".join(module_parts)

    def temporary_folder(
        self, include_trained_model: bool = False
    ) -> ContextManager[None]:
        """Returns a context manager which creates a temporary folder on the
        filesystem and copies all model's files into the folder including
        the project's requirements.txt file (if it exists).

        Example:
            >>> with model.temporary_folder() as temp_path:
            >>>    # files are available in temp_path

        Args:
            include_trained_model (bool, optional): [description]. Defaults to False.

        Returns:
                ContextManager[str]
        """
        files_to_copy = []

        # Model-specific files (relative to model root)
        path = os.path.normpath(self.path)
        relevant_parent_folders = path.split(os.sep)[-self.parent_levels :]
        parent_dir = os.path.join(*relevant_parent_folders)

        for relative_path in self.files:
            files_to_copy.append(
                (
                    self.get_file_path(relative_path),
                    os.path.join(parent_dir, relative_path),
                )
            )

        # Trained model (model.pkl) if necessary
        if include_trained_model:
            files_to_copy.append(
                (
                    self.trained_model_path,
                    self.get_relative_file_path(self.trained_model_path),
                )
            )

        # requirements.txt from this folder or project folder
        if os.path.isfile(self.requirements_file_path):
            files_to_copy.append(
                (self.requirements_file_path, self._REQUIREMENTS_FILE_NAME)
            )
        elif self.project and os.path.isfile(self.project.requirements_file_path):
            files_to_copy.append(
                (self.project.requirements_file_path, self._REQUIREMENTS_FILE_NAME)
            )

        return temporary_folder(files_to_copy)

    # -- Partially abstract interface ----------------------------------------

    # The following methods are meant to be overwritten by inherited classes
    # if necessary. Some can be omitted, and will return default values.

    def extra_tags(self) -> Dict[str, Any]:
        """TODO: What is this function for?

        Returns:
            Dict[str, Any]: [description]
        """
        return {}

    def generate_seed(self) -> int:
        """Generates a random seed between :math:`0` and :math:`10^9`.

        Returns:
            int: A random number between :math:`0` and :math:`10^9`.
        """
        return random.randint(0, 10 ** 9)

    def train(
        self,
        datasets: MLDataStore,
        logger: MetricsLogger,
        seed: int,
        **params: Dict[str, Any],
    ) -> None:
        """Define your training logic.

        Args:
            datasets (MLDataStore): A reference to the data set.
            logger (MetricsLogger): The logger argument handle metric logging, etc.
            seed (typing.Any): The seed argument tries to obtain a deterministic
                environment for model experiments.
        """
        raise NotImplementedError

    def predict(
        self,
        trained_model: "TrainedModel",
        input_data: "PredictionInput",
        identifier: str,
    ) -> None:
        """Define your prediction logic.

        Args:
            trained_model (TrainedModel): Your trained model object.
            input_data (PredictionInput): Data used for inference.
            identifier (str): A unique identifier which refers to a specific model in
                the model object.
        """
        raise NotImplementedError

    @staticmethod
    def load(fp: str) -> "TrainedModel":
        """Load trained model from filepath.

        Args:
            fp (str): [description]

        Raises:
            TrainedModel.Invalid: [description]

        Returns:
            TrainedModel: [description]
        """
        with open(fp, "rb") as f:
            try:
                loaded_model = pickle.load(f)

                if not isinstance(loaded_model, TrainedModel):
                    raise TrainedModel.Invalid(
                        f"The file at {fp}"
                        f"does not contain a {TrainedModel.__name__} object."
                    )

                loaded_model.verify()

                return loaded_model
            except pickle.UnpicklingError:
                raise TrainedModel.Invalid("Failed to load trained model.")

    @staticmethod
    def dump(file_path: str, trained_model: "TrainedModel") -> None:
        """Dump :ref:`TrainedModel` to pickle-file in file path.

        Args:
            file_path (str): The filepath to dump the pickle-file to.
            trained_model (TrainedModel): The trained model to dump.
        """
        folder = os.path.split(file_path)[0]
        if not os.path.isdir(folder):
            os.makedirs(folder)
        with open(file_path, "wb") as f:
            pickle.dump(trained_model, f)


class ModelDatasets:
    """
    A wrapper for parsing datasets in string-format to specific
    name and version. Distinguishes between datasets for local
    and cloud training.
    """

    def __init__(self, model: Model):
        """[summary]

        Args:
            model (Model): [description]
        """
        self.model = model

    def _parse_datasets(self, datasets: List[str]) -> Iterable[Tuple[str, str]]:
        """Parses datasets in the format of either "name" or "name:version"
        and returns an iterable of (name, version), where version is
        optional and can be None.

        Args:
            datasets (List[str]): [description]

        Raises:
            ValueError: [description]

        Returns:
            Iterable[Tuple[str, str]]: [description]

        Yields:
            Iterator[Iterable[Tuple[str, str]]]: [description]
        """
        for dataset in datasets:
            if dataset.count(":") > 1:
                raise ValueError(f"Invalid dataset '{dataset}'")
            colon_at = dataset.find(":")
            if colon_at != -1:
                yield dataset[:colon_at], dataset[colon_at + 1 :]
            else:
                yield dataset, None

    @property
    def local(self) -> List[Tuple[str, str]]:
        """[summary]

        Returns:
            List[Tuple[str, str]]: [description]
        """
        all_ = self._parse_datasets(self.model.datasets)
        local = self._parse_datasets(self.model.datasets_local)
        return list(all_) + list(local)

    @property
    def cloud(self) -> List[Tuple[str, str]]:
        """[summary]

        Returns:
            List[Tuple[str, str]]: [description]
        """
        all_ = self._parse_datasets(self.model.datasets)
        cloud = self._parse_datasets(self.model.datasets_cloud)
        return list(all_) + list(cloud)


@dataclass
class TrainedModel:
    """TrainedModel Class

    Attributes:
        model: Your model.
        models: A dictionary of models.
        features: A list of the model features.
        params: The parameters of your model.
    """

    # TODO: Simon will look into the field typing
    model: Any = field(default=None)
    models: Dict[str, Any] = field(default_factory=dict)
    features: List[str] = field(default_factory=list)
    params: Dict[str, Any] = field(default_factory=dict)
    validator: Optional[Validator] = None

    class Invalid(Exception):
        """[summary]"""

        pass

    def __new__(cls, **kwargs):
        """Creates a new TrainedModel"""
        if "model" in kwargs and "models" in kwargs:
            raise ValueError(
                (
                    f"Can not instantiate {cls.__name__} using both 'model' and "
                    "'models' parameters. "
                    "Either provide a default model to the 'model' "
                    "parameter, or provide a series of identifiable models "
                    "to the 'models' parameter."
                )
            )
        return object.__new__(cls)

    @property
    def identifiers(self) -> List[str]:
        """[summary]

        Returns:
            List[str]: [description]
        """
        return list(self.models.keys())

    def has_model(self, identifier) -> bool:
        """[summary]

        Args:
            identifier ([type]): [description]

        Returns:
            bool: [description]
        """
        return identifier in self.models

    def get_model(self, identifier: str = None):
        """[summary]

        Args:
            identifier (str, optional): [description]. Defaults to None.

        Raises:
            ValueError: [description]

        Returns:
            [type]: [description]
        """
        if identifier is None:
            return self.get_default_model()
        elif identifier in self.models:
            return self.models[identifier]
        else:
            raise ValueError(f"No model exists with identifier: {identifier}")

    def has_default_model(self) -> bool:
        """[summary]

        Returns:
            bool: [description]
        """
        return self.model is not None

    def get_default_model(self):
        """
        :rtype: object
        """
        if not self.has_default_model():
            raise ValueError(
                "No default model exists for this model. "
                "Use get_model() instead and provide a model identifier."
            )
        return self.model

    def verify(self):
        """
        TODO move to function outside class?
        """
        if not isinstance(self.features, list):
            features_type = str(type(self.features))
            raise self.Invalid(
                "Must provide a list of features. "
                f"You gave me something of type {features_type}"
            )
        if not all(isinstance(s, str) for s in self.features):
            raise self.Invalid("All features must be of type str")
        if not [f.strip() for f in self.features if f.strip()]:
            raise self.Invalid(
                (
                    "No feature names provided. "
                    f"Instantiate {self.__class__.__name__} with a list "
                    "of features using the 'features' parameter."
                )
            )


@dataclass
class ModelArtifact:
    """Contains all data that is neccesary for a model to be instanciated and function.
    The artifact is the output of a completion of a model training.

    It contains a TrainedModel and the user-defined code as files.

    It can be used to re-instancesiate a model from an older run,
    to test or deploy the model.

    """

    path: str
    run_id: str
    experiment_name: str
    project_meta: Dict[str, str]
    _tempdir: tempfile.TemporaryDirectory = None

    @property
    def portal_url(self) -> str:
        """The URL to a training run.

        Returns:
            str: The URL of the training run
        """
        return backend.get_portal_url(
            self.project_meta, self.experiment_name, self.run_id
        )

    @classmethod
    def from_cloud(
        cls, experiment_name: str, run_id: str, path=None, project_meta=None
    ) -> "ModelArtifact":
        """Download model and trained_model files from cloud environment
        to a (temporary) folder.

        Args:
            experiment_name (str): The name of the experiment
            run_id (str): The id of the run
            path (str): The path to which the files are downloaded. If None, the files
            are downloaded to a temporary folder.
            project_meta (dict): A dictionary of project information required
            to obtain a workspace. If None, it looks for a project.json
            file with the required information.

        Returns:
            ModelArtifact: This contains model information which makes it possible
            to initiate a LoadedModel

        Example:
            The method can be used as a ContextManager:

            >>> with ModelArtifact.from_cloud(experiment_name, run_id)
            ... as model_artifact:
            >>>     # The downloaded files are downloaded to a temporary folder
            ...     # and they are accesible from the model_artifact-instance
            >>>     print(model_artifact.portal_url)

        It can also be used as an object, but then you have to clean up in the
        temporary folder afterwards:

            >>> model_artifact = ModelArtifact.from_cloud(experiment_name, run_id)
            >>> model_artifact.clean_up() # Clean up in the temporary directory

        """

        if project_meta is None:
            current_path = os.getcwd()
            project_path = locate_file_upwards(current_path, Project._CONFIG_FILE_NAME)

            if project_path is None:
                raise Project.ConfigNotFound(
                    f"Could not find the file '{Project._CONFIG_FILE_NAME}' in this "
                    f"folder (or any of its parents): '{current_path}'.\n"
                    f"I am looking for a folder which contains a file "
                    f"named '{Project._CONFIG_FILE_NAME}' - either in the "
                    f"folder itself or in one of its parent folders. \n\n"
                    f"You can either use the 'project_meta'-argument and provide a "
                    f"dictionary with workspace information, "
                    f"or create a file called '{Project._CONFIG_FILE_NAME}'."
                )

            with open(project_path) as fp:
                project_meta = json.load(fp)

        workspace = backend.get_workspace(project_meta)

        tempdir = None
        if not path:
            tempdir = tempfile.TemporaryDirectory()
            path = os.path.join(tempdir.name, "artifact")

        snapshot_zip_path = backend.download_model_files(
            workspace, experiment_name, run_id, path
        )
        with zipfile.ZipFile(snapshot_zip_path, "r") as zip_ref:
            zip_ref.extractall(path)

        os.remove(snapshot_zip_path)

        artifact = cls(
            path=path,
            run_id=run_id,
            experiment_name=experiment_name,
            project_meta=project_meta,
        )

        if tempdir:
            artifact._tempdir = tempdir

        return artifact

    def clean_up(self):
        if self._tempdir:
            self._tempdir.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, exc, value, tb):
        self.clean_up()


class LoadedModel:
    """Class for a loaded model ready to use in a piece of code.
    The class can be instantiated from a
    :class:`~energinetml.core.model.ModelArtifact`-object.

    Attributes:
        model (Model):
        trained_model (TrainedModel):
        controller (PredictionController): Handles the invokation of the user-specified
        prediction logic
    """

    model: "Model"
    trained_model: "TrainedModel"
    controller: PredictionController

    def __init__(self, model: "Model", trained_model: "TrainedModel"):
        """Initialize a LoadedModel

        Args:
            model (Model): The model which holds a
            ``:func: ~energinetml.model.predict``-function
            trained_model (TrainedModel):
        """
        self.model = model
        self.trained_model = trained_model
        self.controller = PredictionController(model, trained_model)

    @classmethod
    def from_artifact(cls, model_artifact: "ModelArtifact") -> "LoadedModel":
        """Creates a LoadedModel from a :class:`~energinetml.core.model.ModelArtifact`
        instance.

        Args:
            model_artifact (ModelArtifact)

        Returns:
            LoadedModel: A loaded model ready for prediction
        """
        artifact_path = os.path.join(
            model_artifact.path, DEFAULT_RELATIVE_ARTIFACT_PATH
        )
        meta_file_path = os.path.join(
            artifact_path,
            Model._META_FILE_NAME,
        )

        meta_data = cls.read_meta_data(meta_file_path, model_artifact)
        module_name = meta_data["module_name"]

        module_path = os.path.join(
            model_artifact.path, module_name.replace(".", os.sep)
        )

        parent_levels = Model.from_directory(module_path).parent_levels

        model_class = import_model_class(module_path, parent_levels)
        model = model_class.from_directory(module_path)

        trained_model_path = os.path.join(
            artifact_path, model_class._TRAINED_MODEL_FILE_NAME
        )

        trained_model = model.load(trained_model_path)

        return cls(model, trained_model)

    def predict(self, input_data: Union[pd.DataFrame, str]) -> PredictResponse:
        """Make predictions based on data from a DataFrame or a json string.
        The prediction logic is specified in the user-defined
        :func: `~energinetml.model.predict`.

        Args:
            input_data (Union[pd.DataFrame, str]): Either a pd.DataFrame
            or a json string

        Returns:
            Tuple[List[Any], List[ValidatorResponse]]: A list of predictions
            and a list of validations
        """

        if isinstance(input_data, pd.DataFrame):
            # Convert pd.DataFrame to json
            json_data = df_to_pydantic_json(input_data)
        else:
            # The data is already in json format
            json_data = input_data

        # Load data model from JSON
        try:
            request = pydantic.parse_obj_as(self.controller.request_model, json_data)
        except pydantic.error_wrappers.ValidationError as e:
            print("Invalid input JSON provided. Error description follows:")
            print(str(e.json(indent=4)))

        # Invoke user-defined prediction logic
        try:
            _, _, predictions, validations = self.controller.invoke_model(request)
        except NotImplementedError:
            print("Prediction script needs an implementation!")
            print(
                "The predict() method of your model raised a NotImplementedError "
                "which indicates that you have not yet implemented it."
            )
            print("Stacktrace follows:")
            print("-" * 79)
            raise

        return self.controller.response_model(
            predictions=predictions, validations=validations
        )

    @staticmethod
    def read_meta_data(meta_file_path: str, model_artifact: "ModelArtifact"):
        try:
            with open(meta_file_path) as meta_data_file:
                meta_data = json.load(meta_data_file)
        except FileNotFoundError:
            raise MetaFileMissing(model_artifact)

        return meta_data


# -- Model importing ---------------------------------------------------------


class MetaFileMissing(Exception):
    def __init__(self, model_artifact):
        msg = (
            f"Could not find a meta data file "
            f"'{Model._META_FILE_NAME}' in the experiment folder "
            f"'{DEFAULT_RELATIVE_ARTIFACT_PATH}' from the run\n"
            f"Portal link: {model_artifact.portal_url}\n\n"
            f"Check that the file '{Model._META_FILE_NAME}' exists. If not, "
            "the experiment may have been run with an older version of the SDK."
        )

        super().__init__(msg)


class ModelError(Exception):
    """[summary]"""

    pass


class ModelModuleError(ModelError):
    """
    Raised if there is a problem importing the usermodel as a module.
    """

    def __init__(self, msg):
        user_msg = """\n
            There was a problem importing modules in your 'model.py'.\n
            If you import a python module from a parent folder, remember to add
            the relative filepath to 'files_include' in 'model.json."""
        output_msg = msg + user_msg

        super().__init__(output_msg)


class ModelImportError(ModelError):
    """
    Raised if script does not contain a 'model' object
    in the global scope.
    """

    pass


class ModelNotClassError(ModelError):
    """
    Raised if imported 'model' object is not a class type.
    """

    pass


class ModelNotInheritModel(ModelError):
    """
    Raised if imported 'model' does not inherit from Model.
    """

    pass


def import_model_class(path, parent_levels):
    """
    Imports user defined 'model' object from python-module at 'path'.
    Validates that its a class, and that it inherits from Model.

    Args:
        path (str): path to the Model class that should be imported.
        parent_levels (int):
            How many parent levels to go up in the path to support
            relative imports.

    Raises:
        ModelImportError: [description]
        ModelNotClassError: [description]
        ModelNotInheritModel: [description]

    Returns:
        Model: A User defined Model class
    """
    modules = []
    folder = path

    # Go up in the path to support relative imports
    for _ in range(parent_levels):
        folder, name = os.path.split(os.path.normpath(folder))
        modules.append(name)

    if folder not in sys.path:
        sys.path.append(folder)

    # Revert list of module names to get python module path
    # This is to support relative imports in model.py
    module_to_import = ".".join(modules[::-1])

    try:
        module = importlib.import_module(module_to_import)
    except ImportError as e:
        raise ModelModuleError(e.msg)

    if not hasattr(module, "model"):
        raise ModelImportError(module)

    sys.modules["model"] = module

    model_class = getattr(module, "model")

    if not inspect.isclass(model_class):
        raise ModelNotClassError()
    if not issubclass(model_class, Model):
        raise ModelNotInheritModel()

    return model_class


def df_to_pydantic_json(df: pd.DataFrame) -> Dict[str, List[Any]]:
    """Convert a pd.DataFrame object to a dictionary in expected format.

    Args:
        df (pd.DataFrame): _description_

    Returns:
        Dict[str, List[Any]]: _description_
    """
    json_dict = df.to_dict(orient="records")
    features_list = []
    for record in json_dict:
        features_list.append({"features": record})

    json_data = {"inputs": features_list}
    return json_data
