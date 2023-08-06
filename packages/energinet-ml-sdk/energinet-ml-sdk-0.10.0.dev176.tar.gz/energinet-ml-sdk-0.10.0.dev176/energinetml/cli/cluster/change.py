#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""
import click

from energinetml.backend import default_backend as backend
from energinetml.cli.utils import discover_model
from energinetml.core.model import Model
from energinetml.settings import PACKAGE_NAME


@click.command()
@discover_model()
@click.option(
    "--cluster-name",
    "cluster_name",
    required=False,
    default=None,
    type=str,
    help="Name of compute cluster, if creating a new cluster",
)
def change(model: Model, cluster_name: str) -> None:
    """Switch to use another (existing) compute cluster."""

    project_meta = model.project.as_dict()
    workspace = backend.get_workspace(project_meta)

    existing_clusters = backend.get_compute_clusters(workspace)
    existing_clusters_mapped = {c.name: c for c in existing_clusters}
    existing_cluster_names = [c.name for c in existing_clusters]

    if not existing_clusters:
        click.echo('No compute clusters exists in workspace "%s".' % workspace.name)
        click.echo('Run "%s cluster create" to create a new cluster.' % PACKAGE_NAME)
        raise click.Abort()

    while cluster_name not in existing_cluster_names:
        cluster_name = click.prompt(
            text="Please enter name of compute cluster to use",
            type=click.Choice(existing_cluster_names),
            default=model.compute_target,
        )

    click.echo('Using cluster "%s" from now on.' % cluster_name)

    cluster = existing_clusters_mapped[cluster_name]

    _update_model_properties(
        model=model, cluster_name=cluster_name, vm_size=cluster.vm_size
    )


def _update_model_properties(model: Model, cluster_name: str, vm_size: str) -> None:
    """[summary]

    Args:
        model (Model): [description]
        cluster_name (str): [description]
        vm_size (str): [description]
    """
    model.compute_target = cluster_name
    model.vm_size = vm_size
    model.save()
