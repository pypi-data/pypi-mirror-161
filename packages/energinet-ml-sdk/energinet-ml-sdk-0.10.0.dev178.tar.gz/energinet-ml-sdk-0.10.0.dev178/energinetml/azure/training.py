"""[summary]
"""
import json
import os
from typing import TYPE_CHECKING, Any, Dict, List

import azureml
from azureml.core import Experiment, Run

from energinetml.azure.datasets import (
    DownloadedAzureMLDataStore,
    MountedAzureMLDataStore,
)
from energinetml.azure.logger import AzureMlLogger
from energinetml.core.logger import ConsoleLogger
from energinetml.core.training import AbstractTrainingContext
from energinetml.settings import DEFAULT_RELATIVE_ARTIFACT_PATH

if TYPE_CHECKING:
    from energinetml.azure.backend import AzureBackend
    from energinetml.core.model import Model, TrainedModel


class AzureTrainingContext(AbstractTrainingContext):
    def save_artifacts(self, model: "Model"):
        """Save model artifacts to cloud.

        Args:
            model (Model): [description]

        Raises:
            AbstractBackend.BackendException: [description]
        """
        try:
            self.az_run.upload_folder(
                name=DEFAULT_RELATIVE_ARTIFACT_PATH, path=model.artifact_path
            )
        except azureml._common.exceptions.AzureMLException as ex:
            raise self.backend.parse_azureml_exception(ex)

    def save_logs(self, *cloggers: List[ConsoleLogger]):
        try:
            for clogger in cloggers:
                clogger.flush()
                self.az_run.upload_file(clogger.filename, clogger.filepath)
        except azureml._common.exceptions.AzureMLException as ex:
            raise self.backend.parse_azureml_exception(ex)

    def save_meta_data(self, meta_data: Dict[str, str], meta_file_path: str):
        """Create a meta json-file with the content from a meta_data dictionary
        and save it to the path specified.

        Args:
            meta_data (Dict[str, str])): A dictionary of meta_data to persist in the
            json-file
            meta_file_path (str): The local path where the json-file is persisted.

        """
        json_object = json.dumps(meta_data, indent=4)
        with open(meta_file_path, "w") as outfile:
            outfile.write(json_object)

    def get_portal_url(self) -> str:
        """Retrieve the URL to the AzureML Run.

        Raises:
            AbstractBackend.BackendException: [description]

        Returns:
            str:
        """
        try:
            return self.az_run.get_portal_url()
        except azureml._common.exceptions.AzureMLException as ex:
            raise self.backend.parse_azureml_exception(ex)


class AzureLocalTrainingContext(AzureTrainingContext):
    """[summary]"""

    def __init__(self, backend: "AzureBackend", force_download: bool):
        """[summary]

        Args:
            backend (AzureBackend): [description]
            force_download (bool): [description]
        """
        self.backend = backend
        self.force_download = force_download
        self.az_run = None

    def train_model(
        self, model: "Model", tags: Dict[str, Any], **kwargs
    ) -> "TrainedModel":
        """[summary]

        Args:
            model (Model): [description]
            tags (Dict[str, Any]): [description]

        Raises:
            AbstractBackend.BackendException: [description]
            AbstractBackend.BackendException: [description]

        Returns:
            TrainedModel: [description]
        """
        project_meta = model.project.as_dict()
        az_workspace = self.backend.get_workspace(project_meta)

        az_experiment = Experiment(workspace=az_workspace, name=model.experiment)

        datasets = DownloadedAzureMLDataStore.from_model(
            model=model,
            datasets=model.datasets_parsed.local,
            workspace=az_workspace,
            force_download=self.force_download,
        )

        with model.temporary_folder() as temp_path:
            # The "outputs" parameter is provided here with a non-existing
            # folder path to avoid having azureml upload files. We will do
            # this manually somewhere else.

            try:
                self.az_run = az_experiment.start_logging(
                    snapshot_directory=temp_path,
                    outputs=os.path.join(temp_path, "a-folder-that-does-not-exists"),
                )
            except azureml._common.exceptions.AzureMLException as ex:
                raise self.backend.parse_azureml_exception(ex)

            self.az_run.set_tags(tags)
            try:
                return model.train(
                    datasets=datasets, logger=AzureMlLogger(self.az_run), **kwargs
                )
            finally:
                try:
                    self.az_run.complete()
                except azureml._common.exceptions.AzureMLException as ex:
                    raise self.backend.parse_azureml_exception(ex)

    def get_parameters(self, model: "Model") -> Dict:
        """[summary]

        Args:
            model (Model): [description]

        Returns:
            Dict: [description]
        """
        params = {}
        params.update(model.parameters)
        params.update(model.parameters_local)
        return params

    def get_tags(self, model: "Model") -> Dict:
        """[summary]

        Args:
            model (Model): [description]

        Returns:
            Dict: [description]
        """
        return {"datasets": ", ".join(model.datasets + model.datasets_local)}


class AzureCloudTrainingContext(AzureTrainingContext):
    """[summary]"""

    def __init__(self):
        self.az_run = None

    def train_model(
        self, model: "Model", tags: Dict[str, Any], **kwargs
    ) -> "TrainedModel":
        """[summary]

        Args:
            model (Model): [description]
            tags (Dict[str, Any]): [description]

        Returns:
            TrainedModel: [description]
        """
        self.az_run = Run.get_context(allow_offline=False)
        self.az_run.set_tags(tags)

        datasets = MountedAzureMLDataStore.from_model(
            model=model,
            datasets=model.datasets_parsed.cloud,
            workspace=self.az_run.experiment.workspace,
        )

        try:
            return model.train(
                datasets=datasets, logger=AzureMlLogger(self.az_run), **kwargs
            )
        finally:
            self.az_run.complete()

    def get_parameters(self, model: "Model") -> Dict:
        """[summary]

        Args:
            model (Model): [description]

        Returns:
            Dict: [description]
        """
        params = {}
        params.update(model.parameters)
        params.update(model.parameters_cloud)
        return params

    def get_tags(self, model: "Model") -> Dict:
        """[summary]

        Args:
            model (Model): [description]

        Returns:
            Dict: [description]
        """
        return {"datasets": ", ".join(model.datasets + model.datasets_cloud)}
