#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""

from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List

from energinetml.core.submitting import SubmitContext
from energinetml.core.training import AbstractTrainingContext

if TYPE_CHECKING:
    from energinetml.core.model import Model


class ComputeType(Enum):
    """[summary]"""

    CPU = "CPU"
    GPU = "GPU"


class BackendException(Exception):
    """[summary]"""

    pass


class AbstractBackend:
    """[summary]"""

    BackendException = BackendException

    def get_available_subscriptions(self):
        """[summary]

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError

    def get_available_resource_groups(self, subscription_id: str):
        """[summary]

        Args:
            subscription_id (str): [description]

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError

    # -- Workspaces ----------------------------------------------------------

    def get_available_workspaces(self, subscription_id: str, resource_group: str):
        """[summary]

        Args:
            subscription_id (str): [description]
            resource_group (str): [description]

        Raises:
            NotImplementedError: [description]
        """

        raise NotImplementedError

    def get_available_workspace_names(self, subscription_id: str, resource_group: str):
        """[summary]

        Args:
            subscription_id (str): [description]
            resource_group (str): [description]

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError

    def get_workspace(self, project_meta: Dict[str, str]):
        """[summary]

        Args:
            subscription_id (str): [description]
            resource_group (str): [description]
            name (str): [description]

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError

    # -- Compute clusters ----------------------------------------------------

    def get_compute_clusters(self, workspace: Any):
        """[summary]

        Args:
            workspace (Any): [description]

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError

    def get_available_vm_sizes(self, workspace: Any) -> List[str]:
        """[summary]

        Args:
            workspace (Any): [description]

        Raises:
            NotImplementedError: [description]

        Returns:
            List[str]: [description]
        """
        raise NotImplementedError

    def create_compute_cluster(
        self,
        workspace: Any,
        name: str,
        vm_size: str,
        min_nodes: int,
        max_nodes: int,
        vnet_resource_group_name: str,
        vnet_name: str,
        subnet_name: str,
    ):
        """[summary]

        Args:
            workspace (Any): [description]
            name (str): [description]
            vm_size (str): [description]
            min_nodes (int): [description]
            max_nodes (int): [description]
            vnet_resource_group_name (str): [description]
            vnet_name (str): [description]
            subnet_name (str): [description]

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError

    # -- Contexts ------------------------------------------------------------

    def get_local_training_context(
        self, force_download: bool
    ) -> AbstractTrainingContext:
        """[summary]

        Args:
            force_download (bool): [description]

        Raises:
            NotImplementedError: [description]

        Returns:
            AbstractTrainingContext: [description]
        """
        raise NotImplementedError

    def get_cloud_training_context(self) -> AbstractTrainingContext:
        """[summary]

        Raises:
            NotImplementedError: [description]

        Returns:
            AbstractTrainingContext: [description]
        """
        raise NotImplementedError

    def submit_model(self, model: "Model", params: List[str]) -> SubmitContext:
        """[summary]

        Args:
            model (Model): [description]
            params (List[str]): [description]

        Raises:
            NotImplementedError: [description]

        Returns:
            SubmitContext: [description]
        """
        raise NotImplementedError
