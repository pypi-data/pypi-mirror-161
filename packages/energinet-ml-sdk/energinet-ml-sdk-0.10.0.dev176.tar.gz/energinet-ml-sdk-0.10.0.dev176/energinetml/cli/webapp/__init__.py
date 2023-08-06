#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Manage Python Web Apps.
"""

import click

from .build import build as build_webapp
from .init import init as init_webapp
from .serve import serve as serve_webapp


@click.group()
def webapp_group():
    """Manage Python Web Apps."""
    pass


webapp_group.add_command(init_webapp)
webapp_group.add_command(build_webapp)
webapp_group.add_command(serve_webapp)
