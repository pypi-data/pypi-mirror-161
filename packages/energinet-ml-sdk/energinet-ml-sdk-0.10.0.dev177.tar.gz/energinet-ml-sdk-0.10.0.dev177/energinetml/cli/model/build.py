#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""
import click

from energinetml.core.docker import build_prediction_api_docker_image


@click.command()
@click.option(
    "--tag",
    "-t",
    required=True,
    help="Name and optionally a tag in the `name:tag` format",
)
@click.option(
    "--model-version",
    "model_version",
    required=True,
    type=str,
    help="Model version (used for logging)",
)
@click.option(
    "--artifact-path",
    "artifact_path",
    required=True,
    type=str,
    help="Path to model artifact",
)
def build(tag: str, model_version: str, artifact_path: str) -> None:
    """Build a Docker image with a HTTP web API for model prediction."""

    build_prediction_api_docker_image(
        artifact_path=artifact_path,
        model_version=model_version,
        tag=tag,
    )
