import tempfile
from unittest.mock import PropertyMock, patch

from click.testing import CliRunner

from energinetml.cli.model.init import init_model
from energinetml.core.model import Model
from energinetml.core.project import MachineLearningProject

# Project
PROJECT_NAME = "PROJECTNAME"
SUBSCRIPTION_ID = "SUBSCRIPTION-ID"
RESOURCE_GROUP = "RESOURCE-GROUP"
WORKSPACE_NAME = "WORKSPACE-NAME"
VNET = "VNET"
SUBNET = "SUBNET"


# Model
MODEL_NAME = "MODELNAME"
EXPERIMENT = "EXPERIMENT"
COMPUTE_TARGET = "COMPUTE-TARGET"
VM_SIZE = "VM-SIZE"
DATASETS = ["iris", "hades:2"]
FEATURES = ["feature1", "feature2"]
PARAMETERS = {"param1": "value1", "param2": "value2"}


# -- Tests -------------------------------------------------------------------


@patch("energinetml.cli.model.init.os.path.isfile")
@patch("energinetml.cli.model.init.click.confirm")
@patch.object(Model, "create", new_callable=PropertyMock)
def test__init_model__deny_override_existing_files__should_abort(
    model_create_mock, confirm_mock, isfile_mock
):
    """
    :param Mock model_create_mock:
    :param Mock confirm_mock:
    :param Mock isfile_mock:
    """
    isfile_mock.return_value = True
    confirm_mock.return_value = False

    runner = CliRunner()

    with tempfile.TemporaryDirectory() as path:
        MachineLearningProject.create(
            path=path,
            name=PROJECT_NAME,
            subscription_id=SUBSCRIPTION_ID,
            resource_group=RESOURCE_GROUP,
            workspace_name=WORKSPACE_NAME,
            vnet_name=VNET,
            subnet_name=SUBNET,
        )

        # Act
        result = runner.invoke(
            cli=init_model, args=["--path", path, "--name", "mymodel"]
        )

        # Assert
        assert result.exit_code == 1


@patch("energinetml.cli.model.init.click.confirm")
@patch("energinetml.cli.model.init.create_cluster")
def test__init_model__no_name_provided__should_prompt_for_name_and_create_model_and_new_cluster(  # noqa: E501
    create_cluster_mock, confirm_mock
):
    """
    :param Mock create_cluster_mock:
    :param Mock confirm_mock:
    """
    confirm_mock.return_value = True

    runner = CliRunner()

    with tempfile.TemporaryDirectory() as path:
        MachineLearningProject.create(
            path=path,
            name=PROJECT_NAME,
            subscription_id=SUBSCRIPTION_ID,
            resource_group=RESOURCE_GROUP,
            workspace_name=WORKSPACE_NAME,
            vnet_name=VNET,
            subnet_name=SUBNET,
        )

        # Act
        result = runner.invoke(
            cli=init_model, args=["--path", path], input="MODEL-NAME\nnew\n"
        )

        # Assert
        assert result.exit_code == 0

        create_cluster_mock.assert_called_once()


@patch("energinetml.cli.model.init.click.confirm")
@patch("energinetml.cli.model.init.change_cluster")
def test__init_model__no_name_provided__should_prompt_for_name_and_create_model_and_change_cluster(  # noqa: E501
    change_cluster_mock, confirm_mock
):
    """
    :param Mock change_cluster_mock:
    :param Mock confirm_mock:
    """
    confirm_mock.return_value = True

    runner = CliRunner()

    with tempfile.TemporaryDirectory() as path:
        MachineLearningProject.create(
            path=path,
            name=PROJECT_NAME,
            subscription_id=SUBSCRIPTION_ID,
            resource_group=RESOURCE_GROUP,
            workspace_name=WORKSPACE_NAME,
            vnet_name=VNET,
            subnet_name=SUBNET,
        )

        # Act
        result = runner.invoke(
            cli=init_model, args=["--path", path], input="MODEL-NAME\nexisting\n"
        )

        # Assert
        assert result.exit_code == 0

        change_cluster_mock.assert_called_once()
