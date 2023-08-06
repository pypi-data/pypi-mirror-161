from dataclasses import dataclass
from unittest.mock import ANY, Mock, patch

import pytest
from azureml._common.exceptions import AzureMLException

from energinetml.azure.backend import AzureBackend
from energinetml.core.project import Project


@pytest.fixture
def azure_backend():
    azure_backend = AzureBackend()
    azure_backend._credential = Mock(return_value=Mock())
    yield azure_backend


class TestAzureBackend:

    # -- get_available_subscriptions() Tests -------------------------------------

    @patch("energinetml.azure.backend.SubscriptionClient")
    def test__get_available_subscriptions__should_return_subscriptions(
        self, subscription_client_mock, azure_backend
    ):
        """
        :param Mock subscription_client_mock:
        :param AzureBackend azure_backend:
        """
        subscriptions = [1, 2, 3]

        subscription_client_instance = Mock()
        subscription_client_instance.subscriptions.list.return_value = subscriptions
        subscription_client_mock.return_value = subscription_client_instance

        # Act
        return_value = azure_backend.get_available_subscriptions()

        # Assert
        assert return_value == subscriptions

    @patch("energinetml.azure.backend.SubscriptionClient")
    def test__get_available_subscriptions__raises_azure_ml_exception__should_raise_backend_exception(  # noqa: E501
        self, subscription_client_mock, azure_backend
    ):
        """
        :param Mock subscription_client_mock:
        :param AzureBackend azure_backend:
        """
        subscription_client_instance = Mock()
        subscription_client_instance.subscriptions.list.side_effect = AzureMLException(
            "x"
        )  # noqa: E501
        subscription_client_mock.return_value = subscription_client_instance

        # Act + Assert
        with pytest.raises(AzureBackend.BackendException):
            azure_backend.get_available_subscriptions()

    # -- get_available_resource_groups() Tests -----------------------------------

    @patch("energinetml.azure.backend.ResourceManagementClient")
    def test__get_available_resource_groups__should_return_resource_groups(
        self, subscription_client_mock, azure_backend
    ):
        """
        :param Mock subscription_client_mock:
        :param AzureBackend azure_backend:
        """
        resource_groups = [1, 2, 3]

        subscription_client_instance = Mock()
        subscription_client_instance.resource_groups.list.return_value = (
            resource_groups  # noqa: E501
        )
        subscription_client_mock.return_value = subscription_client_instance

        # Act
        return_value = azure_backend.get_available_resource_groups("subscription_id")

        # Assert
        assert return_value == resource_groups

    @patch("energinetml.azure.backend.ResourceManagementClient")
    def test__get_available_resource_groups__raises_azure_ml_exception__should_raise_backend_exception(  # noqa: E501
        self, subscription_client_mock, azure_backend
    ):
        """
        :param Mock subscription_client_mock:
        :param AzureBackend azure_backend:
        """
        subscription_client_instance = Mock()
        subscription_client_instance.resource_groups.list.side_effect = (
            AzureMLException("x")
        )
        subscription_client_mock.return_value = subscription_client_instance

        # Act + Assert
        with pytest.raises(AzureBackend.BackendException):
            azure_backend.get_available_resource_groups("subscription_id")

    # -- get_available_workspaces() Tests ----------------------------------------

    @patch("energinetml.azure.backend.Workspace")
    def test__get_available_workspaces__should_return_workspaces(
        self, workspace_mock, azure_backend
    ):
        """
        :param Mock workspace_mock:
        :param AzureBackend azure_backend:
        """
        workspaces_mapped = {
            "something1": ["workspace1", "workspace2"],
            "something2": ["workspace3", "workspace4"],
        }

        workspace_mock.list.return_value = workspaces_mapped

        # Act
        return_value = azure_backend.get_available_workspaces(
            "subscription_id", "resource_group"
        )

        # Assert
        assert return_value == ["workspace1", "workspace2", "workspace3", "workspace4"]

    @patch("energinetml.azure.backend.Workspace")
    def test__get_available_workspaces__raises_azure_ml_exception__should_raise_backend_exception(  # noqa: E501
        self, workspace_mock, azure_backend
    ):
        """
        :param Mock workspace_mock:
        :param AzureBackend azure_backend:
        """
        workspace_mock.list.side_effect = AzureMLException("x")

        # Act + Assert
        with pytest.raises(AzureBackend.BackendException):
            azure_backend.get_available_workspaces("subscription_id", "resource_group")

    # -- get_available_workspaces() Tests ----------------------------------------

    @patch.object(AzureBackend, "get_available_workspaces")
    def test__get_available_workspace_names__should_return_workspace_names(  # noqa: E501
        self, get_available_workspaces_mock, azure_backend
    ):
        """
        :param Mock get_available_workspaces_mock:
        :param AzureBackend azure_backend:
        """

        @dataclass
        class MockWorkspace:
            name: str

        get_available_workspaces_mock.return_value = [
            MockWorkspace("workspace1"),
            MockWorkspace("workspace2"),
            MockWorkspace("workspace3"),
            MockWorkspace("workspace4"),
        ]

        # Act
        return_value = azure_backend.get_available_workspace_names(
            "subscription_id", "resource_group"
        )

        # Assert
        assert return_value == ["workspace1", "workspace2", "workspace3", "workspace4"]

    # -- get_workspace() Tests ---------------------------------------------------

    @patch("energinetml.azure.backend.Workspace")
    def test__get_workspace__should_return_workspace(
        self, workspace_mock, azure_backend
    ):
        """
        :param Mock workspace_mock:
        :param AzureBackend azure_backend:
        """
        workspace = Mock()
        workspace_mock.get.return_value = workspace
        project_meta = {
            "subscription_id": "subscription_id",
            "resource_group": "resource_group",
            "workspace_name": "name",
        }

        # Act
        return_value = azure_backend.get_workspace(project_meta)

        # Assert
        workspace_mock.get.assert_called_once_with(
            auth=ANY,
            subscription_id="subscription_id",
            resource_group="resource_group",
            name="name",
        )

        assert return_value is workspace

    @patch("energinetml.azure.backend.Workspace")
    def test__get_workspace__should_raise_config_error(
        self, workspace_mock, azure_backend
    ):
        """
        :param Mock workspace_mock:
        :param AzureBackend azure_backend:
        """
        workspace = Mock()
        workspace_mock.get.return_value = workspace
        # Config missing key: 'subscription_id'
        project_meta = {"resource_group": "resource_group", "workspace_name": "name"}

        # Act + Assert
        with pytest.raises(Project.ConfigError):
            azure_backend.get_workspace(project_meta)

    @patch("energinetml.azure.backend.Workspace")
    def test__get_workspace__raises_azure_ml_exception__should_raise_backend_exception(  # noqa: E501
        self, workspace_mock, azure_backend
    ):
        """
        :param Mock workspace_mock:
        :param AzureBackend azure_backend:
        """
        workspace_mock.get.side_effect = AzureMLException("x")

        project_meta = {
            "subscription_id": "subscription_id",
            "resource_group": "resource_group",
            "workspace_name": "name",
        }
        # Act + Assert
        with pytest.raises(AzureBackend.BackendException):
            azure_backend.get_workspace(project_meta)

    # -- get_compute_clusters() Tests --------------------------------------------

    @patch("energinetml.azure.backend.AmlCompute")
    def test__get_compute_clusters__should_return_compute_clisters(
        self, aml_compute_mock, azure_backend
    ):
        """
        :param Mock aml_compute_mock:
        :param AzureBackend azure_backend:
        """
        compute_clusters = ["compute1", "compute2"]
        aml_compute_mock.list.return_value = compute_clusters

        # Act
        return_value = azure_backend.get_compute_clusters("workspace")

        # Assert
        aml_compute_mock.list.assert_called_once_with(workspace="workspace")

        assert return_value is compute_clusters

    @patch("energinetml.azure.backend.AmlCompute")
    def test__get_compute_clusters__raises_azure_ml_exception__should_raise_backend_exception(  # noqa: E501
        self, aml_compute_mock, azure_backend
    ):
        """
        :param Mock aml_compute_mock:
        :param AzureBackend azure_backend:
        """
        aml_compute_mock.list.side_effect = AzureMLException("x")

        # Act + Assert
        with pytest.raises(AzureBackend.BackendException):
            azure_backend.get_compute_clusters("workspace")

    # -- get_compute_clusters() Tests --------------------------------------------

    @patch("energinetml.azure.backend.AmlCompute")
    def test__get_available_vm_sizes__should_return_vm_sizes(
        self, aml_compute_mock, azure_backend
    ):
        """
        :param Mock aml_compute_mock:
        :param AzureBackend azure_backend:
        """
        vm_sizes = ["vm1", "vm2"]
        aml_compute_mock.supported_vmsizes.return_value = vm_sizes

        # Act
        return_value = azure_backend.get_available_vm_sizes("workspace")

        # Assert
        aml_compute_mock.supported_vmsizes.assert_called_once_with(
            workspace="workspace"
        )

        assert return_value is vm_sizes

    @patch("energinetml.azure.backend.AmlCompute")
    def test__get_available_vm_sizes__raises_azure_ml_exception__should_raise_backend_exception(  # noqa: E501
        self, aml_compute_mock, azure_backend
    ):
        """
        :param Mock aml_compute_mock:
        :param AzureBackend azure_backend:
        """
        aml_compute_mock.supported_vmsizes.side_effect = AzureMLException("x")

        # Act + Assert
        with pytest.raises(AzureBackend.BackendException):
            azure_backend.get_available_vm_sizes("workspace")
