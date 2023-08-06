#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""
import os
import sys
from typing import List, Union

import click
import click_spinner

from energinetml.backend import default_backend as backend
from energinetml.cli.utils import discover_model
from energinetml.core.logger import ConsoleLogger
from energinetml.core.model import Model, TrainedModel
from energinetml.settings import PACKAGE_NAME, PACKAGE_VERSION

# -- CLI Command -------------------------------------------------------------


@click.command()
@discover_model()
@click.argument("parameters", nargs=-1)
@click.option(
    "--cloud-mode",
    "-c",
    "cloud_mode",
    default=False,
    is_flag=True,
    help="Run training in cloud mode (do not use locally)",
)
@click.option(
    "--force-download",
    "-f",
    "force_download",
    default=False,
    is_flag=True,
    help="Force download of datasets (ignore locally cached files)",
)
@click.option("--seed", "-s", required=False, default=None, type=str, help="Seed value")
def train(
    parameters: List[str],
    cloud_mode: bool,
    force_download: bool,
    seed: Union[int, str],
    model: Model,
):
    """Train a model locally"""

    try:
        stdout_console_logger = ConsoleLogger(name="stdout", console=sys.stdout)
        sys.stdout = stdout_console_logger
        stderr_console_logger = ConsoleLogger(name="stderr", console=sys.stderr)
        sys.stderr = stderr_console_logger

        # -- Training context ----------------------------------------------------

        if cloud_mode:
            # Training is running in the cloud
            context = backend.get_cloud_training_context()
        else:
            # Training is running locally
            context = backend.get_local_training_context(force_download)

        # -- Train Parameters ----------------------------------------------------

        params = {}
        params.update(context.get_parameters(model))
        params.update(dict(param.split(":") for param in parameters))
        params["seed"] = seed if seed is not None else model.generate_seed()

        # -- Tags ----------------------------------------------------------------

        tags = {PACKAGE_NAME: str(PACKAGE_VERSION)}
        tags.update(params)
        tags.update(context.get_tags(model))
        tags.update(model.extra_tags())

        # -- Training ------------------------------------------------------------

        print("Training model...")

        try:
            trained_model = context.train_model(model=model, tags=tags, **params)
        except NotImplementedError:
            print("Training script needs an implementation!")
            print(
                "The train() method of your model raised a NotImplementedError "
                "which indicates that you have not yet implemented it."
            )
            print("Stacktrace follows:")
            print("-" * 79)
            raise

        # -- Verify returned object ----------------------------------------------

        print("-" * 79)
        print("Training complete")
        print("Verifying trained model...")

        # Must be of type TrainedModel
        if not isinstance(trained_model, TrainedModel):
            print("-" * 79)
            print(
                "The object returned by your train()-method must be of type "
                "TrainedModel (or inherited classes). "
                f"You gave me something of type {type(trained_model)} instead."
            )
            raise click.Abort()

        # Verify object properties
        try:
            trained_model.verify()
        except trained_model.Invalid as ex:
            print("-" * 79)
            print(f"{trained_model.__class__.__name__} does not validate: {ex}")
            raise click.Abort()

        # -- Dump output to disk -------------------------------------------------

        print(f"Dumping trained model to: {model.trained_model_path}")

        trained_model.params.update(params)
        model.dump(model.trained_model_path, trained_model)

        meta_data = {"module_name": model.module_name, "run_id": context.az_run.id}

        if context.az_run:
            workspace = context.az_run.experiment.workspace
            meta_data["subscription_id"] = workspace.subscription_id
            meta_data["resource_group"] = workspace.resource_group
            meta_data["workspace_name"] = workspace.name
            meta_data["run_id"] = context.az_run.id
            meta_data["portal_url"] = context.get_portal_url()

        context.save_meta_data(
            meta_data, os.path.join(model.artifact_path, model._META_FILE_NAME)
        )

        # -- Upload output files -------------------------------------------------

        print("Uploading output files...")

        with click_spinner.spinner():
            context.save_artifacts(model)

    except Exception:
        raise
    finally:
        if context.az_run:
            # -- Print portal link ---------------------------------------------------
            print(f"Portal link: {context.get_portal_url()}")

            print("Uploading log files...")
            with click_spinner.spinner():
                context.save_logs(stdout_console_logger, stderr_console_logger)
