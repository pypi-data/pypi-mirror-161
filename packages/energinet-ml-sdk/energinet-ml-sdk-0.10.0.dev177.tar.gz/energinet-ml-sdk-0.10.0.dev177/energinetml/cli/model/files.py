#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""
import click

from energinetml.cli.utils import discover_model
from energinetml.core.model import Model


@click.command()
@discover_model()
def files(model: Model) -> None:
    """List files that are copied to the cloud when submitting."""
    for file_path in sorted(model.files):
        click.echo(file_path)
