#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""
import os
import subprocess
import sys

import click

from energinetml.cli.utils import (
    parse_input_path,
    parse_input_project_name,
    parse_input_resource_group,
    parse_input_service_connection,
    parse_input_webapp_kind,
)
from energinetml.core.project import WebAppProject, WebAppProjectKind

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
    "--service-connection",
    "-s",
    "service_connection",
    required=False,
    default=None,
    type=str,
    callback=parse_input_service_connection(),
    help="Azure DevOps Service Connection name",
)
@click.option(
    "--pipelines/--no-pipelines",
    default=None,
    help="Whether or not to setup DevOps pipelines",
)
@click.option(
    "--kind",
    "-k",
    "kind",
    required=False,
    default=None,
    type=click.Choice(["ASGI", "WSGI"]),
    callback=parse_input_webapp_kind(),
    help=(
        "Kind of web server to use (ASGI or WSGI). "
        "ASGI for flask, Django, or Falcon. "
        "WSGI for fastapi."
    ),
)
def init(
    path: str,
    name: str,
    resource_group: str,
    service_connection: str,
    kind: WebAppProjectKind,
    pipelines: bool,
) -> None:
    """Create a new, empty web app project."""

    # -- Create project ------------------------------------------------------

    project = WebAppProject.create(path=path, name=name, kind=kind)

    click.echo("Initialized the project at: %s" % path)
    click.echo("-" * 79)

    # -- Clone repo ----------------------------------------------------------

    click.echo("-" * 79)
    click.echo(
        "NOTICE: We need to clone a Git repository containing the "
        "necessary template files. This requires Git to be "
        "installed on your system."
    )
    click.echo("-" * 79)

    project.get_template_resolver().resolve(
        project_root_path=path,
        project_name=name,
        service_connection=service_connection or "ENTER SERVICE CONNECTION NAME",
        resource_group=resource_group or "ENTER RESOURCE GROUP",
    )

    click.echo("-" * 79)

    # -- Create DevOps pipelines ---------------------------------------------

    click.echo("Creating Azure DevOps pipelines")

    if pipelines:
        repo = _get_git_repository_name(project)

        _create_pipeline(
            name=f"{project.name} infrastructure",
            yaml_path=".azuredevops/infrastructure.yml",
            repo=repo,
        )

        _create_pipeline(
            name=f"{project.name} deploy",
            yaml_path=".azuredevops/deploy.yml",
            repo=repo,
        )


def _get_git_repository_name(project: WebAppProject) -> str:
    """[summary]

    Args:
        project (WebAppProject): [description]

    Returns:
        str: [description]
    """
    path = os.getcwd()
    os.chdir(project.path)
    command = ("git", "config", "--get", "remote.origin.url")
    output = subprocess.check_output(command, universal_newlines=True)
    os.chdir(path)
    return output.rsplit("/")[-1].strip()


def _create_pipeline(name: str, yaml_path: str, repo: str):
    """[summary]

    Args:
        name (str): [description]
        yaml_path (str): [description]
        repo (str): [description]
    """
    click.echo(f"Setting up DevOps pipeline: {name}")

    command = [
        "az",
        "pipelines",
        "create",
        "--name",
        f"{name}",
        "--branch",
        "master",
        "--org",
        "https://dev.azure.com/energinet/",
        "--project",
        "AnalyticsOps",
        "--repository",
        repo,
        "--yaml-path",
        yaml_path,
        "--repository-type",
        "tfsgit",
        "--skip-first-run",
        "true",
    ]

    subprocess.check_call(command, stdout=sys.stdout, stderr=subprocess.STDOUT)
