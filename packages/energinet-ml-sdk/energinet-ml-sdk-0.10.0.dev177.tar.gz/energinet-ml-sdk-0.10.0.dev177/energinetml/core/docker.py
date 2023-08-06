#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""

import json
import os
import subprocess
import sys
from typing import Dict

from energinetml.core.model import Model
from energinetml.core.project import WebAppProject
from energinetml.settings import (
    DEFAULT_RELATIVE_ARTIFACT_PATH,
    DOCKERFILE_PATH_ML_MODEL,
    PACKAGE_VERSION,
)


def build_prediction_api_docker_image(
    artifact_path: str, tag: str, model_version: str
) -> None:
    """TODO: Add package version when installing energinet-ml-sdk

    Args:
        path (str): [description]
        tag (str): [description]
        model_version (str): [description]

    Raises:
        ValueError: [description]
    """
    meta = _metadata_from_artifact(artifact_path)
    # Convert module path to folder path
    model_path = meta["module_name"].replace(".", "/")

    build_docker_image(
        path=artifact_path,
        tag=tag,
        dockerfile_path=DOCKERFILE_PATH_ML_MODEL,
        build_args={
            "MODEL_PATH": model_path,
            "OUTPUTS_PATH": DEFAULT_RELATIVE_ARTIFACT_PATH,
            "MODEL_VERSION": model_version,
        },
    )


def _metadata_from_artifact(artifact_path: str) -> Dict:
    """Read a meta file.

    Args:
        artifact_path (str): [description]

    Returns:
        Dict: [description]
    """
    meta_file_path = os.path.join(
        artifact_path,
        DEFAULT_RELATIVE_ARTIFACT_PATH,
        Model._META_FILE_NAME,
    )

    with open(meta_file_path, "r") as f:
        meta = json.load(f)

    return meta


def build_webapp_docker_image(project: WebAppProject, tag: str) -> None:
    """TODO: Add package version when installing energinet-ml-sdk

    Args:
        project (project.WebAppProject): [description]
        tag (str): [description]
    """
    build_docker_image(
        path=project.path, tag=tag, dockerfile_path=project.dockerfile_path
    )


def build_docker_image(
    path: str,
    tag: str,
    params: Dict[str, str] = None,
    build_args: Dict[str, str] = None,
    dockerfile_path: str = None,
):
    """Build a Docker image.

    Args:
        path (str): [description]
        tag (str): [description]
        params (Dict[str, str], optional): [description]. Defaults to None.
        build_args (Dict[str, str], optional): [description]. Defaults to None.
        dockerfile_path (str, optional): [description]. Defaults to None.
    """
    if params is None:
        params = {}
    if build_args is None:
        build_args = {}

    if dockerfile_path:
        params["--file"] = dockerfile_path

    build_args["PACKAGE_VERSION"] = str(PACKAGE_VERSION)

    # Render 'docker build' command
    command = ["docker", "build"]
    command.extend(("--tag", tag))
    for k, v in params.items():
        command.extend((k, v))
    for k, v in build_args.items():
        command.extend(("--build-arg", f"{k}={v}"))
    command.append(path)

    # Run 'docker build' command in subprocess
    subprocess.check_call(
        command, stdout=sys.stdout, stderr=subprocess.STDOUT, shell=False
    )
