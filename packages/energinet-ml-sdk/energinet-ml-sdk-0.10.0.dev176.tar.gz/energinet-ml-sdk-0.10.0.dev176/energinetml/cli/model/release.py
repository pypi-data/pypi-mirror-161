#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""
import click
import click_spinner
from azureml.core import Experiment as AzExperiment
from azureml.core import Run as AzRun
from azureml.core import Workspace

from energinetml.backend import default_backend as backend
from energinetml.cli.utils import discover_model
from energinetml.core.model import Model, ModelArtifact

# -- CLI Command -------------------------------------------------------------
# TODO: Remove Azure-related things out in backend


@click.command()
@discover_model()
@click.option(
    "--run-id",
    "-r",
    "run_id",
    type=str,
    required=False,
    default=None,
    help="Run ID to release",
)
def release(run_id: str, model: Model) -> None:
    """Release a model."""

    project_meta = model.project.as_dict()

    workspace = backend.get_workspace(project_meta)

    if run_id is None:
        run_id = _get_run_id_if_omitted(workspace, model)

    # -- Download files ------------------------------------------------------

    click.echo("Releasing model using Run ID: %s" % run_id)

    with ModelArtifact.from_cloud(
        model.experiment, run_id, project_meta=project_meta
    ) as artifact:

        run = AzRun.get(workspace, run_id)
        # Can not use run.register_model() here, as its only able to copy
        # files from the Run's output folder, and we also want to package
        # the project files (from the restored snapshot).
        with click_spinner.spinner():
            model_tags = {k: v for k, v in run.tags.items() if not k.startswith("_")}
            model_tags.update({"run_id": run_id})

            model = backend.release_model(
                workspace=workspace,
                model_path=artifact.path,
                model_name=model.name,
                properties=run.properties,
                description="TODO Describe me!",
                run_id=run_id,
                tags=model_tags,
            )

            click.echo(f"Released new model {model.name} version {model.version}")


# -- Helper functions --------------------------------------------------------


def _get_run_id_if_omitted(workspace: Workspace, model: Model) -> str:
    """[summary]

    Args:
        workspace (Workspace): [description]
        model (Model): [description]

    Raises:
        click.Abort: [description]

    Returns:
        str: [description]
    """
    experiment = AzExperiment(workspace=workspace, name=model.experiment)

    latest_runs = list(AzRun.list(experiment=experiment))

    if not latest_runs:
        click.echo(f"No runs exists for experiment {model.experiment}")
        raise click.Abort()

    latest_run_id = latest_runs[0].id

    use_latest_run = click.confirm(
        (
            "You did not provide me with a Run ID. "
            f"Would you like to use the latest (Run ID: {latest_run_id})?"
        )
    )

    if use_latest_run is False:
        click.echo(
            "I do not know which run to release. Provide me with a "
            "Run ID using the -r/--run-id parameter."
        )
        raise click.Abort()

    return latest_run_id
