#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Manage machine learning models.
"""
import click

from .build import build as build_model
from .files import files as model_files
from .init import init_model
from .release import release as release_model
from .serve import serve as serve_model
from .submit import submit as submit_model
from .train import train as train_model


@click.group()
def model_group():
    """Manage machine learning models."""
    pass


model_group.add_command(init_model, "init")
model_group.add_command(train_model)
model_group.add_command(build_model)
model_group.add_command(serve_model)
model_group.add_command(submit_model)
model_group.add_command(release_model)
model_group.add_command(model_files)
