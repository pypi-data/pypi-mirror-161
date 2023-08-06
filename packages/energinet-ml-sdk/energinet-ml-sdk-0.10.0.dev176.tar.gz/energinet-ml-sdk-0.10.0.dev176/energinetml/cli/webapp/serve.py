#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""
import click

from energinetml.cli.utils import discover_project
from energinetml.core.project import WebAppProject


@click.command()
@discover_project(WebAppProject)
@click.option(
    "--host",
    default="127.0.0.1",
    type=str,
    help="Host to serve on (default: 127.0.0.1)",
)
@click.option("--port", default=8080, type=int, help="Port to serve on (default: 8080)")
def serve(host: str, port: int, project: WebAppProject) -> None:
    """Serve a HTTP web API for model prediction."""
    engine = project.get_engine()
    engine.serve(project)
