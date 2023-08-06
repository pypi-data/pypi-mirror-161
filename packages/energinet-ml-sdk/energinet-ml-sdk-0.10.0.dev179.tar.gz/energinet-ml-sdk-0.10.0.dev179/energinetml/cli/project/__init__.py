#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Manage machine learning projects.
"""
import click

from .init import init_project


@click.group()
def project_group() -> None:
    """Manage machine learning projects."""
    pass


project_group.add_command(init_project, "init")
