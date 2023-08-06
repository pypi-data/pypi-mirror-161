#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""
from typing import Tuple

import click
import click_spinner
from azureml.core.workspace import Workspace

from energinetml.backend import default_backend as backend
from energinetml.cli.utils import discover_model
from energinetml.core.model import Model
from energinetml.settings import DEFAULT_VM_CPU, DEFAULT_VM_GPU


@click.command()
@discover_model()
@click.option(
    "--min-nodes",
    "min_nodes",
    required=False,
    default=None,
    type=int,
    help="Min. number of compute nodes, if creating a new cluster",
)
@click.option(
    "--max-nodes",
    "max_nodes",
    required=False,
    default=None,
    type=int,
    help="Max. number of compute nodes, if creating a new cluster",
)
@click.option(
    "--cluster-name",
    "cluster_name",
    required=False,
    default=None,
    type=str,
    help="Name of compute cluster, if creating a new cluster",
)
@click.option(
    "--specify-vm/--default",
    "specify_vm",
    default=None,
    help=(
        "Whether to specify exact VM size, or use default for "
        "either CPU or GPU computation, if creating a new cluster"
    ),
)
@click.option(
    "--vm-size",
    "vm_size",
    required=False,
    default=None,
    type=str,
    help="VM Size to use, if using the --specify-vm parameter",
)
@click.option(
    "--cpu/--gpu",
    "cpu",
    default=None,
    help=(
        "Whether to use default CPU- og GPU VM-size, if "
        "using the --default parameter"
    ),
)
def create(
    model: Model,
    min_nodes: int,
    max_nodes: int,
    cluster_name: str,
    specify_vm: bool,
    vm_size: str,
    cpu: str,
) -> None:
    """Create a new compute cluster and attach it to the model."""

    project_meta = model.project.as_dict()
    workspace = backend.get_workspace(project_meta)

    vm_size, default_cluster_name = _get_vm_size_and_cluster_name(
        workspace=workspace, specify_vm=specify_vm, vm_size=vm_size, cpu=cpu
    )

    if min_nodes is None:
        min_nodes = click.prompt(
            text="Please enter minimum nodes available", default=0, type=click.INT
        )

    if max_nodes is None:
        max_nodes = click.prompt(
            text="Please enter maximum nodes available", default=1, type=click.INT
        )

    if cluster_name is None:
        cluster_name = click.prompt(
            text="Please enter a name for the compute cluster",
            default=default_cluster_name,
            type=click.STRING,
        )

    cluster_name = _normalize_cluster_name(cluster_name)
    existing_clusters = backend.get_compute_clusters(workspace)
    existing_cluster_names = [c.name for c in existing_clusters]

    while cluster_name in existing_cluster_names:
        click.echo(f"Cluster already exists: {cluster_name}")
        cluster_name = _normalize_cluster_name(
            click.prompt(
                text="Please enter a name for the compute cluster", type=click.STRING
            )
        )

    click.echo(f'Creating compute cluster "{cluster_name}" using VM Size: {vm_size}')

    with click_spinner.spinner():
        backend.create_compute_cluster(
            workspace=workspace,
            name=cluster_name,
            vm_size=vm_size,
            min_nodes=min_nodes,
            max_nodes=max_nodes,
            vnet_resource_group_name=model.project.resource_group,
            vnet_name=model.project.vnet_name,
            subnet_name=model.project.subnet_name,
        )

    _update_model_properties(model=model, cluster=cluster_name, vm_size=vm_size)


def _update_model_properties(model: Model, cluster: str, vm_size: str) -> None:
    """[summary]

    Args:
        model (Model): [description]
        cluster (str): [description]
        vm_size (str): [description]
    """
    model.compute_target = cluster
    model.vm_size = vm_size
    model.save()


# -- Helper functions --------------------------------------------------------


def _get_vm_size_and_cluster_name(
    workspace: Workspace,
    specify_vm: bool,
    vm_size: str,
    cpu: str,
) -> Tuple[str, str]:
    """[summary]

    Args:
        workspace (Workspace): [description]
        specify_vm (bool): [description]
        vm_size (str): [description]
        cpu (str): [description]

    Returns:
        Tuple[str, str]: [description]
    """
    available_vm_sizes = backend.get_available_vm_sizes(workspace)
    available_vm_size_mapped = {vm["name"]: vm for vm in available_vm_sizes}

    if specify_vm is None:
        click.echo(
            "You can either specific an exact VM Size, or use a default "
            "VM Size for either CPU or GPU computation."
        )
        specify_vm = (
            click.prompt(
                text="How would you like to specify VM Size, or use a default?",
                type=click.Choice(["vmsize", "default"]),
            )
            == "vmsize"
        )

    if specify_vm:
        vm_size, cluster_name = _get_specific_vm_size(workspace, vm_size)
    else:
        vm_size, cluster_name = _get_default_vm_size(cpu)

    while vm_size not in available_vm_size_mapped:
        click.echo("VM Size unavailable: %s" % vm_size)
        vm_size = click.prompt(
            text="Please enter a VM size", type=click.Choice(available_vm_size_mapped)
        )

    return vm_size, cluster_name


def _get_specific_vm_size(workspace: Workspace, vm_size: str) -> Tuple[str, str]:
    """[summary]

    Args:
        workspace (Workspace): [description]
        vm_size (str): [description]

    Returns:
        Tuple[str, str]: [description]
    """
    available_vm_sizes = backend.get_available_vm_sizes(workspace)
    available_vm_size_mapped = {vm["name"]: vm for vm in available_vm_sizes}

    if vm_size is None:
        vm_size = click.prompt(
            text="Please enter a VM size", type=click.Choice(available_vm_size_mapped)
        )

    return vm_size, _normalize_cluster_name(vm_size)


def _get_default_vm_size(cpu: bool) -> Tuple[str, str]:
    """[summary]

    Args:
        cpu (bool): [description]

    Returns:
        Tuple[str, str]: [description]
    """
    if cpu is None:
        cpu = (
            click.prompt(
                text="Which kind of computing would you like to use?",
                type=click.Choice(["cpu", "gpu"]),
            )
            == "cpu"
        )

    if cpu:
        return DEFAULT_VM_CPU, "CPU-Cluster"
    else:
        return DEFAULT_VM_GPU, "GPU-Cluster"


def _normalize_cluster_name(cluster_name: str) -> str:
    """[summary]

    Args:
        cluster_name (str): [description]

    Returns:
        str: [description]
    """
    return cluster_name.replace("_", "-")
