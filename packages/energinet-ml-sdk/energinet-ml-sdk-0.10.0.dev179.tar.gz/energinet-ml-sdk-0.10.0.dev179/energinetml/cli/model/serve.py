#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""
import json
import os

import click

from energinetml.cli.utils import discover_model
from energinetml.core.http import run_predict_api
from energinetml.core.model import Model
from energinetml.settings import DEFAULT_RELATIVE_ARTIFACT_PATH


@click.command()
@discover_model()
@click.option(
    "--outputs-path",
    "outputs_path",
    default=os.path.join(DEFAULT_RELATIVE_ARTIFACT_PATH),
    type=click.Path(file_okay=True, resolve_path=True),
    help="Path to the outputs directory where the model.pkl and metadata.json exist.",
)
@click.option(
    "--host",
    default="127.0.0.1",
    type=str,
    help="Host to serve on (default: 127.0.0.1)",
)
@click.option("--port", default=8080, type=int, help="Port to serve on (default: 8080)")
@click.option(
    "--model-version",
    "model_version",
    required=False,
    type=str,
    default="Unspecified",
    help="Model version (used for logging)",
)
def serve(
    host: str,
    port: int,
    model: Model,
    outputs_path: str,
    model_version: str = None,
) -> None:
    """Serve a HTTP web API for model prediction."""
    trained_model_path = os.path.join(outputs_path, model._TRAINED_MODEL_FILE_NAME)
    trained_model = model.load(trained_model_path)

    meta_data_path = os.path.join(outputs_path, model._META_FILE_NAME)
    with open(meta_data_path) as meta_data_file:
        meta_data = json.load(meta_data_file)

    run_predict_api(
        model=model,
        trained_model=trained_model,
        meta_data=meta_data,
        model_version=model_version,
        host=host,
        port=port,
    )
