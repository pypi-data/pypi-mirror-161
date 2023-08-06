import os
import tempfile
from unittest.mock import Mock, patch

import click
import pytest
from click.testing import CliRunner

from energinetml.cli.utils.decorators import discover_model, discover_project
from energinetml.core.model import (
    Model,
    ModelImportError,
    ModelNotClassError,
    ModelNotInheritModel,
)
from energinetml.core.project import MachineLearningProject

PROJECT_NAME = "NAME"
PROJECT_SUBSCRIPTION_ID = "SUBSCRIPTION-ID"
PROJECT_RESOURCE_GROUP = "RESOURCE-GROUP"
PROJECT_WORKSPACE_NAME = "WORKSPACE-NAME"

MODEL_NAME = "NAME"
MODEL_EXPERIMENT = "EXPERIMENT"
MODEL_COMPUTE_TARGET = "COMPUTE-TARGET"
MODEL_VM_SIZE = "VM-SIZE"
MODEL_DATASETS = ["iris", "hades:2"]
MODEL_FEATURES = ["feature1", "feature2"]
MODEL_PARAMETERS = {"param1": "value1", "param2": "value2"}


# -- discover_project() Tests ------------------------------------------------


def test__discover_project__project_exists__should_exit_with_status_ok():
    runner = CliRunner()

    @click.command()
    @discover_project(Mock())
    def discover_project_testable(project):
        pass

    # Act
    result = runner.invoke(discover_project_testable, ["--path", "mock-path"])

    # Assert
    assert result.exit_code == 0, str(result.exception)


def test__discover_project__project_does_not_exist__should_exit_with_error():
    with tempfile.TemporaryDirectory() as path:

        runner = CliRunner()
        project_cls_mock = Mock()
        project_cls_mock.from_directory.side_effect = (
            MachineLearningProject.ConfigNotFound
        )

        @click.command()
        @discover_project(project_cls_mock)
        def discover_project_testable(project):
            pass

        # Act
        result = runner.invoke(discover_project_testable, ["--path", path])

        # Assert
        assert result.exit_code == 1, str(result.exception)

        project_cls_mock.from_directory.assert_called_once_with(path)


# -- discover_model() Tests --------------------------------------------------


@click.command()
@discover_model()
def discover_model_testable(model):
    """
    Empty function to allow invoking the decorator.
    """
    pass


@patch("energinetml.cli.utils.decorators.os.path.isdir")
def test__discover_model__model_file_does_not_exists__should_exit_with_error(
    isdir_mock,
):  # noqa: E501
    """
    :param Mock isdir_mock:
    """
    with tempfile.TemporaryDirectory() as path:
        isdir_mock.return_value = False

        runner = CliRunner()
        # Act
        result = runner.invoke(discover_model_testable, ["--path", path])

        # Assert
        assert result.exit_code == 1
        isdir_mock.assert_called_once_with(os.path.normpath(path))


@patch("energinetml.cli.utils.decorators.os.path.isdir")
@patch("energinetml.cli.utils.decorators.import_model_class")
@patch("energinetml.core.configurable.Configurable.from_directory")
@pytest.mark.parametrize(
    "exception", (ModelImportError, ModelNotClassError, ModelNotInheritModel)
)
def test__discover_model__import_model_class_raises_exception__should_exit_with_error(
    from_directory_mock, import_model_class_mock, isdir_mock, exception
):
    """
    :param Mock import_model_class_mock:
    :param Mock isdir_mock:
    :param Exception exception:
    """
    parent_levels = 1
    with tempfile.TemporaryDirectory() as path:
        isdir_mock.return_value = True
        from_directory_mock.return_value = Mock(parent_levels=parent_levels)
        import_model_class_mock.side_effect = exception

        runner = CliRunner()

        # Act
        result = runner.invoke(discover_model_testable, ["--path", path])

        # Assert
        assert result.exit_code == 1

        isdir_mock.assert_called_once_with(os.path.normpath(path))
        import_model_class_mock.assert_called_once_with(path, parent_levels)


@patch("energinetml.cli.utils.decorators.os.path.isdir")
@patch("energinetml.cli.utils.decorators.import_model_class")
@patch("energinetml.core.configurable.Configurable.from_directory")
def test__discover_model__model_not_found_in_directory__should_exit_with_error(
    from_directory_mock, import_model_class_mock, isdir_mock
):
    """
    :param Mock import_model_class_mock:
    :param Mock isdir_mock:
    """
    parent_levels = 1
    with tempfile.TemporaryDirectory() as path:
        from_directory_mock.return_value = Mock(parent_levels=parent_levels)
        model_class = Mock()
        model_class.from_directory.side_effect = Model.ConfigNotFound
        isdir_mock.return_value = True
        import_model_class_mock.return_value = model_class

        runner = CliRunner()

        # Act
        result = runner.invoke(discover_model_testable, ["--path", path])

        # Assert
        assert result.exit_code == 1

        isdir_mock.assert_called_once_with(os.path.normpath(path))

        import_model_class_mock.assert_called_once_with(path, parent_levels)
