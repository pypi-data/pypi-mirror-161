#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" CLI module
"""

import click
from dotnetcore2 import runtime

# Hack OS version to avoid licencing problems in azureml
# TODO How else to get azureml Datasets working?
# TODO Move to somewhere else?
runtime.version = ("18", "10", "0")

from energinetml.settings import PACKAGE_VERSION  # noqa: E402

from .cluster import cluster_group  # noqa: E402
from .infrastructure import infrastructure_group  # noqa: E402
from .model import model_group  # noqa: E402
from .project import project_group  # noqa: E402
from .webapp import webapp_group  # noqa: E402


@click.command()
def version():
    """
    Prints SDK version.
    """
    click.echo(PACKAGE_VERSION)


@click.group()
def main():
    """
    Click main entrypoint.
    """
    pass


main.add_command(project_group, "project")
main.add_command(model_group, "model")
main.add_command(cluster_group, "cluster")
main.add_command(webapp_group, "webapp")
main.add_command(infrastructure_group, "infrastructure")
main.add_command(version)
