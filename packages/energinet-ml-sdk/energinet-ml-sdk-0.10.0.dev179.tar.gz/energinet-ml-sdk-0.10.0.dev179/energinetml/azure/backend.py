#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""
import os
import re
from functools import cached_property
from typing import TYPE_CHECKING, Dict, List

import azureml
from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient
from azureml._common.exceptions import AzureMLException
from azureml.core import ComputeTarget, Environment, Experiment
from azureml.core import Model as AzureMLModel
from azureml.core import Run, RunConfiguration, ScriptRunConfig, Workspace
from azureml.core.authentication import InteractiveLoginAuthentication
from azureml.core.compute import AmlCompute
from azureml.core.conda_dependencies import CondaDependencies

from energinetml.core.backend import AbstractBackend
from energinetml.core.project import Project
from energinetml.settings import (
    CLUSTER_IDLE_SECONDS_BEFORE_SCALEDOWN,
    PACKAGE_NAME,
    PYTHON_VERSION,
)

from .submitting import AzureSubmitContext
from .training import AzureCloudTrainingContext, AzureLocalTrainingContext

if TYPE_CHECKING:
    from energinetml.core.model import Model as EnerginetMLModel


class AzureBackend(AbstractBackend):
    def parse_azureml_exception(
        self, e: AzureMLException
    ) -> AbstractBackend.BackendException:
        """Extracts error message from AzureMLException and
        returns a BackendException.

        Args:
            e (AzureMLException): [description]

        Returns:
            AbstractBackend.BackendException: [description]
        """
        msg = str(e)
        matches = re.findall(r'"message":\s*"([^"]+)"', msg)
        if matches:
            return self.BackendException(matches[0])
        else:
            return self.BackendException(msg)

    @cached_property
    def _credential(self) -> InteractiveLoginAuthentication:
        """[summary]

        Returns:
            InteractiveLoginAuthentication: [description]
        """
        return InteractiveLoginAuthentication()

    def get_available_subscriptions(self) -> List[str]:
        """[summary]

        Raises:
            self.parse_azureml_exception: [description]

        Returns:
            List[str]: [description]
        """
        subscription_client = SubscriptionClient(self._credential)
        try:
            return list(subscription_client.subscriptions.list())
        except azureml._common.exceptions.AzureMLException as e:
            raise self.parse_azureml_exception(e)

    def get_available_resource_groups(self, subscription_id: str) -> List[str]:
        """[summary]

        Args:
            subscription_id (str): [description]

        Raises:
            self.parse_azureml_exception: [description]

        Returns:
            List[str]: [description]
        """
        resource_client = ResourceManagementClient(self._credential, subscription_id)
        try:
            return list(resource_client.resource_groups.list())
        except azureml._common.exceptions.AzureMLException as e:
            raise self.parse_azureml_exception(e)

    # -- Workspaces ----------------------------------------------------------

    def get_available_workspaces(
        self, subscription_id: str, resource_group: str
    ) -> List[Workspace]:
        """[summary]

        Args:
            subscription_id (str): [description]
            resource_group (str): [description]

        Raises:
            self.parse_azureml_exception: [description]

        Returns:
            List[Workspace]: [description]
        """
        try:
            workspaces_mapped = Workspace.list(
                auth=self._credential,
                subscription_id=subscription_id,
                resource_group=resource_group,
            )
        except azureml._common.exceptions.AzureMLException as e:
            raise self.parse_azureml_exception(e)

        workspaces = []

        for workspace_list in workspaces_mapped.values():
            workspaces.extend(workspace_list)

        return workspaces

    def get_available_workspace_names(
        self, subscription_id: str, resource_group: str
    ) -> List[str]:
        """[summary]

        Args:
            subscription_id (str): [description]
            resource_group (str): [description]

        Returns:
            List[str]: [description]
        """
        available_workspaces = self.get_available_workspaces(
            subscription_id=subscription_id, resource_group=resource_group
        )

        return [w.name for w in available_workspaces]

    def get_workspace(self, project_meta: Dict[str, str]) -> Workspace:
        """_summary_

        Args:
            project_meta (dict): _description_

        Raises:
            self.parse_azureml_exception: _description_

        Returns:
            Workspace: _description_
        """

        expected_keywords = ["subscription_id", "resource_group", "workspace_name"]
        for keyword in expected_keywords:
            if keyword not in project_meta:
                raise Project.ConfigError(f"Expected '{keyword}' as a key.")

        try:
            return Workspace.get(
                auth=self._credential,
                subscription_id=project_meta["subscription_id"],
                resource_group=project_meta["resource_group"],
                name=project_meta["workspace_name"],
            )
        except azureml._common.exceptions.AzureMLException as e:
            raise self.parse_azureml_exception(e)

    # -- Compute clusters ----------------------------------------------------

    def get_compute_clusters(self, workspace: Workspace) -> List[AmlCompute]:
        """[summary]

        Args:
            workspace (Workspace): [description]

        Raises:
            self.parse_azureml_exception: [description]

        Returns:
            List[AmlCompute]: [description]
        """
        try:
            return AmlCompute.list(workspace=workspace)
        except azureml._common.exceptions.AzureMLException as e:
            raise self.parse_azureml_exception(e)

    def get_available_vm_sizes(self, workspace: Workspace) -> List[str]:
        """[summary]

        Args:
            workspace (Workspace): [description]

        Raises:
            self.parse_azureml_exception: [description]

        Returns:
            List[str]: [description]
        """
        try:
            return AmlCompute.supported_vmsizes(workspace=workspace)
        except azureml._common.exceptions.AzureMLException as e:
            raise self.parse_azureml_exception(e)

    def create_compute_cluster(
        self,
        workspace: Workspace,
        name: str,
        vm_size: str,
        min_nodes: int,
        max_nodes: int,
        vnet_resource_group_name: str,
        vnet_name: str,
        subnet_name: str,
    ) -> None:
        """[summary]

        Args:
            workspace (Workspace): [description]
            name (str): [description]
            vm_size (str): [description]
            min_nodes (int): [description]
            max_nodes (int): [description]
            vnet_resource_group_name (str): [description]
            vnet_name (str): [description]
            subnet_name (str): [description]

        Raises:
            self.parse_azureml_exception: [description]
        """

        compute_config = AmlCompute.provisioning_configuration(
            vm_size=vm_size,
            min_nodes=min_nodes,
            max_nodes=max_nodes,
            vnet_resourcegroup_name=vnet_resource_group_name,
            vnet_name=vnet_name,
            subnet_name=subnet_name,
            idle_seconds_before_scaledown=CLUSTER_IDLE_SECONDS_BEFORE_SCALEDOWN,
        )

        try:
            ComputeTarget.create(workspace, name, compute_config).wait_for_completion(
                show_output=False
            )
        except azureml._common.exceptions.AzureMLException as e:
            raise self.parse_azureml_exception(e)

    # -- Contexts ------------------------------------------------------------

    def get_local_training_context(
        self, force_download: bool
    ) -> AzureLocalTrainingContext:
        """[summary]

        Args:
            force_download (bool): [description]

        Returns:
            AzureLocalTrainingContext: [description]
        """
        return AzureLocalTrainingContext(self, force_download)

    def get_cloud_training_context(self) -> AzureCloudTrainingContext:
        """[summary]

        Returns:
            AzureCloudTrainingContext: [description]
        """
        return AzureCloudTrainingContext()

    def submit_model(
        self, model: "EnerginetMLModel", params: List[str]
    ) -> AzureSubmitContext:
        """[summary]

        Args:
            model (Model): [description]
            params (List[str]): [description]

        Raises:
            self.parse_azureml_exception: [description]

        Returns:
            AzureSubmitContext: [description]
        """
        cd = CondaDependencies()
        cd.set_python_version(PYTHON_VERSION)

        # Project requirements (from requirements.txt)
        for requirement in model.requirements:
            cd.add_pip_package(requirement.line)

        # Python environment
        env = Environment(model.requirements.get(PACKAGE_NAME).line)
        env.python.conda_dependencies = cd

        compute_config = RunConfiguration()
        compute_config.target = model.compute_target
        compute_config.environment = env

        project_meta = model.project.as_dict()
        workspace = self.get_workspace(project_meta)

        experiment = Experiment(workspace=workspace, name=model.experiment)

        # Change the python module path to a folder path,
        # so that we can cd to and run the script in the cloud.
        snapshot_relative_path = model.module_name.replace(".", os.path.sep)

        with model.temporary_folder() as path:
            config = ScriptRunConfig(
                source_directory=path,
                # Command to enter the module directory and running a cloud training
                # The 'python .'-command runs the energinetml-cli.
                command=[
                    "cd",
                    snapshot_relative_path,
                    "&&",
                    "python",
                    ".",
                    "model",
                    "train",
                    "--cloud-mode",
                ]
                + list(params),
                run_config=compute_config,
            )
            try:
                run = experiment.submit(config)
            except azureml._common.exceptions.AzureMLException as e:
                raise self.parse_azureml_exception(e)

            return AzureSubmitContext(model, run)

    def release_model(
        self, workspace: Workspace, model_path: str, model_name: str, **kwargs
    ) -> AzureMLModel:
        """[summary]

        Args:
            workspace (Workspace): [description]
            model_path (str): [description]
            model_name (str): [description]

        Raises:
            self.parse_azureml_exception: [description]

        Returns:
            AzureMLModel: [description]
        """
        try:
            asset = AzureMLModel._create_asset(
                workspace.service_context, model_path, model_name, None
            )

            return AzureMLModel._register_with_asset(
                workspace=workspace, model_name=model_name, asset_id=asset.id, **kwargs
            )
        except azureml._common.exceptions.AzureMLException as e:
            raise self.parse_azureml_exception(e)

    def download_model_files(
        self, workspace: Workspace, experiment_name: str, run_id: str, folder_path: str
    ) -> str:
        """Downloads model files to folder including snapshot
        (model.py, model.json, etc) as a zip-file and trainedmodel filesfrom the
        Azure ML cloud, based on an `experiment_name` and a `run_id`.

        Args:
            workspace (Workspace): An Azure workspace
            experiment_name (str): The name of the experiment
            run_id (str): The id of the run

        Returns:
        str: The path to the snapshot zip-file.
        """

        experiment = Experiment(workspace, experiment_name)
        run = Run(experiment, run_id)

        # Download project snapshot (model.py, model.json, etc).
        # Snapshot is downloaded as a zip-archive.
        print("Downloading model code snapshot")
        snapshot_zip_path = run.restore_snapshot(path=folder_path)

        print("Downloading trained model file")
        run.download_files(output_directory=folder_path)

        return snapshot_zip_path

    def get_portal_url(self, project_meta: dict, experiment_name: str, run_id: str):
        """Get the url to the Azure ML portal for a specific run

        Args:
            project_meta (dict): Project information for retrieving workspace
            experiment_name (str): Name of the experiment
            run_id (str): Id of the run
        """
        workspace = self.get_workspace(project_meta)
        experiment = Experiment(workspace, experiment_name)
        run = Run(experiment, run_id)

        return run.get_portal_url()
