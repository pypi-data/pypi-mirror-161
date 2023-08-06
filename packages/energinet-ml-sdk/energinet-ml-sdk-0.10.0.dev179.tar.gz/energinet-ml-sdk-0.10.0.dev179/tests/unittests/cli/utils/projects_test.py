import os
import tempfile
from pathlib import Path
from unittest.mock import ANY, Mock, PropertyMock, patch

import click
import pytest

from energinetml.cli.utils import (
    parse_input_path,
    parse_input_project_name,
    parse_input_resource_group,
    parse_input_subscription_id,
    parse_input_workspace_name,
)

NAME = "PROJECT-NAME"
SUBSCRIPTION_NAME = "MY-SUBSCRIPTION"
SUBSCRIPTION_ID = "SUBSCRIPTION-ID"
RESOURCE_GROUP = "RESOURCE-GROUP"
WORKSPACE_NAME = "WORKSPACE-NAME"
VNET = "VNET"
SUBNET = "SUBNET"


# -- _parse_input_path() Tests -----------------------------------------------


@patch("energinetml.cli.project.init.click.prompt")
def test__parse_input_path__value_is_none__should_prompt_for_path(prompt_mock):
    """
    :param Mock prompt_mock:
    """

    # Act
    parse_input_path([])(ctx=None, param=None, value=None)

    # Assert
    prompt_mock.assert_called_once_with(
        text="Enter project location", default=ANY, type=ANY
    )


@patch("energinetml.cli.project.init.click.echo")
def test__parse_input_path__path_is_a_file__should_abort_with_error(echo_mock):
    """
    :param Mock echo_mock:
    """
    with tempfile.TemporaryDirectory() as path:
        fp = os.path.join(path, "somefile.txt")

        Path(fp).touch()

        # Act + Assert
        with pytest.raises(click.Abort):
            parse_input_path([])(ctx=None, param=None, value=fp)


@patch("energinetml.cli.project.init.click.echo")
@patch("energinetml.cli.project.init.click.confirm")
def test__parse_input_path__project_files_already_exists_in_folder__should_prompt_to_override(  # noqa: E501
    confirm_mock, echo_mock
):
    """
    :param Mock confirm_mock:
    :param Mock echo_mock:
    """
    confirm_mock.side_effect = (True, False)

    with tempfile.TemporaryDirectory() as path:
        fp1 = os.path.join(path, "project.json")
        fp2 = os.path.join(path, "requirements.txt")

        Path(fp1).touch()
        Path(fp2).touch()

        # Act
        with pytest.raises(click.Abort):
            project_files = ["project.json", "requirements.txt"]
            parse_input_path(project_files)(ctx=None, param=None, value=path)

        # Assert
        echo_mock.assert_any_call("File already exists: %s" % fp1)
        echo_mock.assert_any_call("File already exists: %s" % fp2)

        confirm_mock.assert_any_call("Really override existing project.json?")
        confirm_mock.assert_any_call("Really override existing requirements.txt?")


# -- _parse_input_project_name() Tests ---------------------------------------


@patch("energinetml.cli.project.init.click.prompt")
def test__parse_input_project_name__value_is_none__should_prompt_for_name(
    prompt_mock,
):
    """
    :param Mock prompt_mock:
    """
    params = {"path": "project-path"}
    prompt_mock.return_value = NAME

    # Act
    value = parse_input_project_name()(ctx=Mock(params=params), param=None, value=None)

    # Assert
    prompt_mock.assert_called_once_with(
        text="Please enter a project name", default="project-path", type=str
    )

    assert value == NAME


@patch("energinetml.cli.project.init.click.prompt")
def test__parse_input_project_name__value_is_provided__should_return_value(
    prompt_mock,
):
    """
    :param Mock prompt_mock:
    """

    # Act
    value = parse_input_project_name()(ctx=None, param=None, value=NAME)

    # Assert
    assert value == NAME
    prompt_mock.assert_not_called()


# -- _parse_input_subscription_id() Tests ------------------------------------


@patch("energinetml.cli.utils.projects.backend")
@patch("energinetml.cli.project.init.click.prompt")
def test__parse_input_subscription_id__value_not_known_subscription__should_prompt_for_subscription_name(  # noqa: E501
    prompt_mock, backend_mock
):
    """
    :param Mock prompt_mock:
    :param Mock backend_mock:
    """
    prompt_mock.return_value = SUBSCRIPTION_NAME

    subscription = Mock(subscription_id=SUBSCRIPTION_ID, display_name=SUBSCRIPTION_NAME)

    backend_mock.get_available_subscriptions.return_value = [subscription]

    # Act
    value = parse_input_subscription_id()(ctx=None, param=None, value="foobar")

    # Assert
    prompt_mock.assert_called_once_with(
        text="Please enter Azure Subscription", type=ANY
    )

    assert value == SUBSCRIPTION_ID


# -- _parse_input_resource_group() Tests -------------------------------------


@patch("energinetml.cli.utils.projects.backend")
@patch("energinetml.cli.project.init.click.prompt")
def test__parse_input_resource_group__value_not_known_resource_group__should_prompt_for_resource_group(  # noqa: E501
    prompt_mock, backend_mock
):
    """
    :param Mock prompt_mock:
    :param Mock backend_mock:
    """
    ctx = Mock(params={"subscription_id": SUBSCRIPTION_ID})
    prompt_mock.return_value = RESOURCE_GROUP

    # Workaround: Can not mock property "name" of Mock object
    resource_group = Mock()
    p = PropertyMock(return_value=RESOURCE_GROUP)
    type(resource_group).name = p

    backend_mock.get_available_resource_groups.return_value = [resource_group]

    # Act
    value = parse_input_resource_group()(ctx=ctx, param=None, value="foobar")

    # Assert
    prompt_mock.assert_called_once_with(
        text="Please enter Azure Resource Group", default="", type=ANY
    )

    assert value == RESOURCE_GROUP


# -- _parse_input_workspace_name() Tests -------------------------------------


def test__parse_input_workspace_name__no_subscription_id_available__should_raise_runtime_error():  # noqa: E501
    ctx = Mock(params={"resource_group": RESOURCE_GROUP})

    with pytest.raises(RuntimeError):
        parse_input_workspace_name()(ctx=ctx, param=None, value=None)


def test__parse_input_workspace_name__no_resource_group_available__should_raise_runtime_error():  # noqa: E501
    ctx = Mock(params={"subscription_id": SUBSCRIPTION_ID})

    with pytest.raises(RuntimeError):
        parse_input_workspace_name()(ctx=ctx, param=None, value=None)


@patch("energinetml.cli.utils.projects.backend")
@patch("energinetml.cli.project.init.click.prompt")
def test__parse_input_workspace_name__no_workspaces_exists_in_resource_group__should_prompt_for_workspace(  # noqa: E501
    prompt_mock, backend_mock
):
    """
    :param Mock prompt_mock:
    :param Mock backend_mock:
    """
    ctx = Mock(
        params={"subscription_id": SUBSCRIPTION_ID, "resource_group": RESOURCE_GROUP}
    )

    backend_mock.get_available_workspace_names.return_value = []
    prompt_mock.return_value = "workspace!"

    # Act
    value = parse_input_workspace_name()(ctx=ctx, param=None, value=None)

    # Assert
    backend_mock.get_available_workspace_names.assert_called_once_with(
        subscription_id=SUBSCRIPTION_ID, resource_group=RESOURCE_GROUP
    )

    prompt_mock.assert_called_once_with(
        text="Please enter AzureML Workspace name", default=None, type=ANY
    )

    assert value == "workspace!"


@patch("energinetml.cli.utils.projects.backend")
@patch("energinetml.cli.project.init.click.prompt")
def test__parse_input_workspace_name__no_workspaces_provided__should_prompt_for_workspace(  # noqa: E501
    prompt_mock, backend_mock
):
    """
    :param Mock prompt_mock:
    :param Mock backend_mock:
    """
    ctx = Mock(
        params={"subscription_id": SUBSCRIPTION_ID, "resource_group": RESOURCE_GROUP}
    )

    backend_mock.get_available_workspace_names.return_value = [WORKSPACE_NAME]
    prompt_mock.return_value = "workspace!"

    # Act
    value = parse_input_workspace_name()(ctx=ctx, param=None, value=None)

    # Assert
    prompt_mock.assert_called_once_with(
        text="Please enter AzureML Workspace name", default=WORKSPACE_NAME, type=ANY
    )

    assert value == "workspace!"
