import tempfile
from unittest.mock import ANY, Mock, PropertyMock, patch

from click.testing import CliRunner

from energinetml.cli.project.init import init_project

NAME = "PROJECT-NAME"
SUBSCRIPTION_NAME = "MY-SUBSCRIPTION"
SUBSCRIPTION_ID = "SUBSCRIPTION-ID"
RESOURCE_GROUP = "RESOURCE-GROUP"
WORKSPACE_NAME = "WORKSPACE-NAME"
VNET = "VNET"
SUBNET = "SUBNET"


# -- init_project() Tests ----------------------------------------------------


@patch("energinetml.cli.utils.projects.backend")
@patch("energinetml.cli.project.init.backend")
@patch("energinetml.cli.project.init.MachineLearningProject.create")
def test__init_project(project_create_mock, backend_mock2, backend_mock):
    """
    :param Mock project_create_mock:
    :param Mock backend_mock2:
    :param Mock backend_mock:
    """

    runner = CliRunner()

    subscription = Mock(subscription_id=SUBSCRIPTION_ID, display_name=SUBSCRIPTION_NAME)

    # Workaround: Can not mock property "name" of Mock object
    resource_group = Mock()
    p = PropertyMock(return_value=RESOURCE_GROUP)
    type(resource_group).name = p

    backend_mock2.get_workspace.return_value = Mock(
        tags={"vnet_name": VNET, "subnet_name": SUBNET}
    )

    backend_mock.get_available_subscriptions.return_value = [subscription]
    backend_mock.get_available_resource_groups.return_value = [resource_group]
    backend_mock.get_available_workspace_names.return_value = [WORKSPACE_NAME]

    with tempfile.TemporaryDirectory() as path:

        # Act
        result = runner.invoke(
            cli=init_project,
            args=[
                "--path",
                path,
                "--name",
                NAME,
                "--subscription",
                SUBSCRIPTION_NAME,
                "--resource-group",
                RESOURCE_GROUP,
                "--workspace",
                WORKSPACE_NAME,
            ],
        )

        # Assert
        assert result.exit_code == 0, str(result.exception)

        project_create_mock.assert_called_once_with(
            path=path,
            name=NAME,
            subscription_id=SUBSCRIPTION_ID,
            resource_group=RESOURCE_GROUP,
            workspace_name=WORKSPACE_NAME,
            location=ANY,
            vnet_name=VNET,
            subnet_name=SUBNET,
        )
