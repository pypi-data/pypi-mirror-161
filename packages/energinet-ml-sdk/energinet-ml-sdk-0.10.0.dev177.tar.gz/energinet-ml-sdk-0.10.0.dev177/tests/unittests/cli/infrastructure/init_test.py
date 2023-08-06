import os
import tempfile
from pathlib import Path
from unittest.mock import ANY, patch

import click
import pytest

from energinetml.cli.infrastructure.init import (
    _parse_input_path,
    _parse_input_project_name,
    _parse_input_resource_group,
    _parse_input_service_connection,
)

NAME = "NAME"
SUBSCRIPTION_NAME = "MY-SUBSCRIPTION"
SUBSCRIPTION_ID = "SUBSCRIPTION-ID"
RESOURCE_GROUP = "RESOURCE-GROUP"
WORKSPACE_NAME = "WORKSPACE-NAME"
VNET = "VNET"
SUBNET = "SUBNET"


# -- _parse_input_path() Tests -----------------------------------------------


@patch("energinetml.cli.infrastructure.init.click.prompt")
def test__parse_input_path__value_is_none__should_prompt_for_path(prompt_mock):
    """
    :param Mock prompt_mock:
    """

    # Act
    _parse_input_path(ctx=None, param=None, value=None)

    # Assert
    prompt_mock.assert_called_once_with(
        text="Enter project location", default=ANY, type=ANY
    )


@patch("energinetml.cli.infrastructure.init.click.echo")
def test__parse_input_path__path_is_a_file__should_abort_with_error(echo_mock):
    """
    :param Mock echo_mock:
    """
    with tempfile.TemporaryDirectory() as path:
        fp = os.path.join(path, "somefile.txt")

        Path(fp).touch()

        # Act + Assert
        with pytest.raises(click.Abort):
            _parse_input_path(ctx=None, param=None, value=fp)


@patch("energinetml.cli.infrastructure.init.click.prompt")
def test__parse_input_path__value_is_valid__should_return_value(prompt_mock):
    """
    :param Mock prompt_mock:
    """

    # Act
    returned_value = _parse_input_path(ctx=None, param=None, value="valid-value")

    # Assert
    assert returned_value == "valid-value"
    prompt_mock.assert_not_called()


# -- _parse_input_project_name() Tests ---------------------------------------


@patch("energinetml.cli.infrastructure.init.click.prompt")
def test__parse_input_project_name__should_prompt_for_value_and_return_it(prompt_mock):
    """
    :param Mock prompt_mock:
    """

    # Arrange
    prompt_mock.return_value = "projectname"

    # Act
    returned_value = _parse_input_project_name(ctx=None, param=None, value=None)

    # Assert
    assert returned_value == "projectname"

    prompt_mock.assert_called_once_with(text="Please enter a project name", type=ANY)


# -- _parse_input_resource_group() Tests -------------------------------------


@patch("energinetml.cli.infrastructure.init.click.prompt")
def test__parse_input_resource_group__should_prompt_for_value_and_return_it(
    prompt_mock,
):  # noqa: E501
    """
    :param Mock prompt_mock:
    """

    # Arrange
    prompt_mock.return_value = "rgname"

    # Act
    returned_value = _parse_input_resource_group(ctx=None, param=None, value=None)

    # Assert
    assert returned_value == "rgname"

    prompt_mock.assert_called_once_with(text="Enter resource group name", type=ANY)


# -- _parse_input_service_connection() Tests ---------------------------------


@patch("energinetml.cli.infrastructure.init.click.prompt")
def test__parse_input_service_connection__should_prompt_for_value_and_return_it(
    prompt_mock,
):  # noqa: E501
    """
    :param Mock prompt_mock:
    """

    # Arrange
    prompt_mock.return_value = "scname"

    # Act
    returned_value = _parse_input_service_connection(ctx=None, param=None, value=None)

    # Assert
    assert returned_value == "scname"

    prompt_mock.assert_called_once_with(
        text="Enter Azure DevOps service connection name", type=ANY
    )
