#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""
import click

from energinetml.cli.utils import discover_project
from energinetml.core.docker import build_webapp_docker_image
from energinetml.core.project import WebAppProject


@click.command()
@click.option(
    "--tag",
    "-t",
    required=True,
    help="Name and optionally a tag in the `name:tag` format",
)
@discover_project(WebAppProject)
def build(tag: str, project: WebAppProject) -> None:
    """Build web app Docker image."""
    build_webapp_docker_image(project=project, tag=tag)
