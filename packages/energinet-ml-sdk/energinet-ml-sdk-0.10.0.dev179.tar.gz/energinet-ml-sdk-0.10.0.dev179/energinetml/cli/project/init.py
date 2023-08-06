#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""

import os

import click

from energinetml.backend import default_backend as backend
from energinetml.cli.utils import (
    parse_input_path,
    parse_input_project_name,
    parse_input_resource_group,
    parse_input_subscription_id,
    parse_input_workspace_name,
)
from energinetml.core.project import MachineLearningProject
from energinetml.settings import COMMAND_NAME, DEFAULT_LOCATION

PROJECT_FILES = ("project.json", "requirements.txt")


# -- CLI Command -------------------------------------------------------------


@click.command()
@click.option(
    "--path",
    "-p",
    default=None,
    type=click.Path(dir_okay=True, resolve_path=True),
    callback=parse_input_path(PROJECT_FILES),
    help="Project path (default to current)",
)
@click.option(
    "--name",
    "-n",
    required=False,
    default=None,
    type=str,
    callback=parse_input_project_name(),
    help="Project name",
)
@click.option(
    "--subscription",
    "-s",
    "subscription_id",
    required=False,
    default=None,
    type=str,
    callback=parse_input_subscription_id(),
    help="Azure subscription name",
)
@click.option(
    "--resource-group",
    "-r",
    "resource_group",
    required=False,
    default=None,
    type=str,
    callback=parse_input_resource_group(),
    help="Azure Resource Group",
)
@click.option(
    "--workspace",
    "-w",
    "workspace_name",
    required=False,
    default=None,
    type=str,
    callback=parse_input_workspace_name(),
    help="AzureML Workspace name",
)
@click.option(
    "--location",
    "-l",
    "location",
    default=DEFAULT_LOCATION,
    required=False,
    type=str,
    help=f"Azure location (default: {DEFAULT_LOCATION})",
)
def init_project(
    path: str,
    name: str,
    subscription_id: str,
    resource_group: str,
    workspace_name: str,
    location: str,
):
    """Create a new, empty machine learning project."""
    if not os.path.isdir(path):
        os.makedirs(path)

    project_meta = {
        "subscription_id": subscription_id,
        "resource_group": resource_group,
        "workspace_name": workspace_name,
    }
    workspace = backend.get_workspace(project_meta)

    MachineLearningProject.create(
        path=path,
        name=name,
        subscription_id=subscription_id,
        resource_group=resource_group,
        workspace_name=workspace_name,
        location=location,
        vnet_name=workspace.tags["vnet_name"],
        subnet_name=workspace.tags["subnet_name"],
    )

    click.echo("-" * 79)
    click.echo(f"Initialized the project at: {path}")
    click.echo(f"Type '{COMMAND_NAME} model init' to add a new model to the project.")
    click.echo("-" * 79)
