from unittest.mock import ANY, Mock, PropertyMock, patch

import pytest
from click.testing import CliRunner

from energinetml.cli.cluster.create import (
    DEFAULT_VM_CPU,
    DEFAULT_VM_GPU,
    _get_default_vm_size,
    _get_specific_vm_size,
    _get_vm_size_and_cluster_name,
    _update_model_properties,
    create,
)
from tests.constants import CLUSTER_NAME, RESOURCE_GROUP, VM_SIZE, WORKSPACE_NAME

# -- create() Tests ----------------------------------------------------------


@patch("energinetml.cli.cluster.create.backend")
@patch("energinetml.cli.cluster.create._get_vm_size_and_cluster_name", name="asd")
@patch("energinetml.cli.cluster.create._normalize_cluster_name")
@patch("energinetml.cli.cluster.create._update_model_properties")
def test__create_cluster__should_create_new_cluster(
    _update_model_properties_mock,
    _normalize_cluster_name_mock,
    _get_vm_size_and_cluster_name_mock,
    backend_mock,
    model_with_project,
):
    """
    :param Mock _update_model_properties_mock:
    :param Mock _normalize_cluster_name_mock:
    :param Mock _get_vm_size_and_cluster_name_mock:
    :param Mock backend_mock:
    :param Model model_with_project:
    """
    backend_mock.get_workspace.return_value = WORKSPACE_NAME
    _get_vm_size_and_cluster_name_mock.return_value = VM_SIZE, "existing-cluster"
    _normalize_cluster_name_mock.return_value = "actual-cluster-name"

    # Workaround: Can not mock property "name" of Mock object
    cluster = Mock()
    type(cluster).name = PropertyMock(return_value="existing-cluster")

    backend_mock.get_compute_clusters.return_value = [cluster]

    # Act
    result = CliRunner().invoke(
        cli=create,
        args=["--path", model_with_project.path],
        # input='%s\n' % CLUSTER_NAME,
        input="\n".join(
            ["123", "456", CLUSTER_NAME]  # min_nodes  # max_nodes  # cluster_name
        ),
    )

    # Assert
    assert result.exit_code == 0

    backend_mock.create_compute_cluster.assert_called_once_with(
        workspace=WORKSPACE_NAME,
        name="actual-cluster-name",
        vm_size=VM_SIZE,
        min_nodes=123,
        max_nodes=456,
        vnet_resource_group_name=RESOURCE_GROUP,
        vnet_name=ANY,
        subnet_name=ANY,
    )

    _update_model_properties_mock.assert_called_once_with(
        model=ANY,  # Model is not the same instance as defined above
        cluster="actual-cluster-name",
        vm_size=VM_SIZE,
    )


# -- _update_model_properties() Tests ----------------------------------------


def test__update_model_properties__should_set_properties_and_save():
    # Arrange
    model = Mock()

    # Act
    _update_model_properties(model=model, cluster="cluster", vm_size="vm-size")

    # Assert
    assert model.compute_target == "cluster"
    assert model.vm_size == "vm-size"
    model.save.assert_called_once()


# -- _update_model_properties() Tests ----------------------------------------


@patch("energinetml.cli.cluster.create.backend")
@patch("energinetml.cli.cluster.create._get_specific_vm_size")
@patch("energinetml.cli.cluster.create._get_default_vm_size")
@patch("energinetml.cli.cluster.create.click.prompt")
def test__get_vm_size_and_cluster_name__should_prompt_to_specify_vm(
    prompt_mock, _get_default_vm_size_mock, _get_specific_vm_size_mock, backend_mock
):
    """
    :param Mock prompt_mock:
    :param Mock backend_mock:
    """
    # Arrange
    _get_default_vm_size_mock.return_value = "VM_1", "cluster-name-1"
    _get_specific_vm_size_mock.return_value = "VM_2", "cluster-name-2"
    backend_mock.get_available_vm_sizes.return_value = [
        {"name": "VM_1"},
        {"name": "VM_2"},
    ]

    # Act
    vm_size, cluster_name = _get_vm_size_and_cluster_name(
        workspace=WORKSPACE_NAME, specify_vm=None, vm_size="vm-size", cpu=False
    )

    # Assert
    prompt_mock.assert_called_once_with(
        text="How would you like to specify VM Size, or use a default?", type=ANY
    )


@patch("energinetml.cli.cluster.create.backend")
@patch("energinetml.cli.cluster.create._get_specific_vm_size")
@patch("energinetml.cli.cluster.create._get_default_vm_size")
@patch("energinetml.cli.cluster.create.click.prompt")
def test__get_vm_size_and_cluster_name__specify_vm__should_return_vm_size_and_cluster_name(  # noqa: E501
    prompt_mock, _get_default_vm_size_mock, _get_specific_vm_size_mock, backend_mock
):
    """
    :param Mock prompt_mock:
    :param Mock backend_mock:
    """
    # Arrange
    _get_default_vm_size_mock.return_value = "VM_1", "cluster-name-1"
    _get_specific_vm_size_mock.return_value = "VM_2", "cluster-name-2"
    backend_mock.get_available_vm_sizes.return_value = [
        {"name": "VM_1"},
        {"name": "VM_2"},
    ]

    # Act
    vm_size, cluster_name = _get_vm_size_and_cluster_name(
        workspace=WORKSPACE_NAME, specify_vm=True, vm_size="vm-size", cpu=False
    )

    # Assert
    prompt_mock.assert_not_called()
    _get_default_vm_size_mock.assert_not_called()
    _get_specific_vm_size_mock.assert_called_once_with(WORKSPACE_NAME, "vm-size")
    assert vm_size == "VM_2"
    assert cluster_name == "cluster-name-2"


@patch("energinetml.cli.cluster.create.backend")
@patch("energinetml.cli.cluster.create._get_specific_vm_size")
@patch("energinetml.cli.cluster.create._get_default_vm_size")
@patch("energinetml.cli.cluster.create.click.prompt")
def test__get_vm_size_and_cluster_name__use_default_vm__should_return_vm_size_and_cluster_name(  # noqa: E501
    prompt_mock, _get_default_vm_size_mock, _get_specific_vm_size_mock, backend_mock
):
    """
    :param Mock prompt_mock:
    :param Mock backend_mock:
    """
    # Arrange
    _get_default_vm_size_mock.return_value = "VM_1", "cluster-name-1"
    _get_specific_vm_size_mock.return_value = "VM_2", "cluster-name-2"
    backend_mock.get_available_vm_sizes.return_value = [
        {"name": "VM_1"},
        {"name": "VM_2"},
    ]

    # Act
    vm_size, cluster_name = _get_vm_size_and_cluster_name(
        workspace=WORKSPACE_NAME, specify_vm=False, vm_size="vm-size", cpu=False
    )

    # Assert
    prompt_mock.assert_not_called()
    _get_specific_vm_size_mock._get_default_vm_size_mock(False)
    _get_specific_vm_size_mock.assert_not_called()
    assert vm_size == "VM_1"
    assert cluster_name == "cluster-name-1"


@patch("energinetml.cli.cluster.create.backend")
@patch("energinetml.cli.cluster.create._get_specific_vm_size")
@patch("energinetml.cli.cluster.create._get_default_vm_size")
@patch("energinetml.cli.cluster.create.click.prompt")
def test__get_vm_size_and_cluster_name__vm_unavailable__should_prompt_for_vm_size(  # noqa: E501
    prompt_mock, _get_default_vm_size_mock, _get_specific_vm_size_mock, backend_mock
):
    """
    :param Mock prompt_mock:
    :param Mock backend_mock:
    """
    # Arrange
    _get_default_vm_size_mock.return_value = "VM-NAME-DOES-NOT-EXIST", "cluster-name-1"
    _get_specific_vm_size_mock.return_value = "VM_2", "cluster-name-2"
    backend_mock.get_available_vm_sizes.return_value = [
        {"name": "VM_1"},
        {"name": "VM_2"},
    ]

    prompt_mock.return_value = "VM_1"

    # Act
    vm_size, cluster_name = _get_vm_size_and_cluster_name(
        workspace=WORKSPACE_NAME, specify_vm=False, vm_size="vm-size", cpu=False
    )

    # Assert
    prompt_mock.assert_called_once_with(text="Please enter a VM size", type=ANY)
    _get_specific_vm_size_mock._get_default_vm_size_mock(False)
    _get_specific_vm_size_mock.assert_not_called()
    assert vm_size == "VM_1"
    assert cluster_name == "cluster-name-1"


# -- _get_specific_vm_size() Tests -------------------------------------------


@patch("energinetml.cli.cluster.create.backend")
@patch("energinetml.cli.cluster.create._normalize_cluster_name")
@patch("energinetml.cli.cluster.create.click.prompt")
def test__get_specific_vm_size__should_prompt_for_vm_size_and_return_normalized_name(
    prompt_mock, _normalize_cluster_name_mock, backend_mock
):
    """
    :param Mock prompt_mock:
    :param Mock _normalize_cluster_name_mock:
    :param Mock backend_mock:
    """
    # Arrange
    _normalize_cluster_name_mock.return_value = "normalized-cluster-name"
    backend_mock.get_available_vm_sizes.return_value = [
        {"name": "VM_1"},
        {"name": "VM_2"},
    ]

    prompt_mock.return_value = "VM_1"

    # Act
    vm_size, cluster_name = _get_specific_vm_size(
        workspace=WORKSPACE_NAME, vm_size=None
    )

    # Assert
    prompt_mock.assert_called_once_with(text="Please enter a VM size", type=ANY)
    assert vm_size == "VM_1"
    assert cluster_name == "normalized-cluster-name"


# -- _get_default_vm_size() Tests --------------------------------------------


@patch("energinetml.cli.cluster.create.click.prompt")
@pytest.mark.parametrize(
    "prompt_value, vm_size, cluster_name",
    (("cpu", DEFAULT_VM_CPU, "CPU-Cluster"), ("gpu", DEFAULT_VM_GPU, "GPU-Cluster")),
)
def test__get_default_vm_size__should_prompt_for_vm_type_and_return_vm_size_and_name(
    prompt_mock, prompt_value, vm_size, cluster_name
):
    """
    :param Mock prompt_mock:
    """
    # Arrange
    prompt_mock.return_value = prompt_value

    # Act
    actual_vm_size, actual_cluster_name = _get_default_vm_size(cpu=None)

    # Assert
    assert actual_vm_size == vm_size
    assert actual_cluster_name == cluster_name
