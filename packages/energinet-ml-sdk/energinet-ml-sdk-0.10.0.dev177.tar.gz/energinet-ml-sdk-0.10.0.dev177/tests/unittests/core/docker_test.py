import os
import subprocess
import sys
from unittest.mock import patch

from energinetml.core.docker import build_prediction_api_docker_image
from energinetml.settings import (
    DEFAULT_RELATIVE_ARTIFACT_PATH,
    DOCKERFILE_PATH_ML_MODEL,
    PACKAGE_VERSION,
)


@patch("energinetml.core.docker._metadata_from_artifact")
@patch("energinetml.core.docker.subprocess.check_call")
def test__build_prediction_api_docker_image__happy_path(
    check_call_mock, _metadata_from_artifact_mock
):
    """
    :param Mock check_call_mock:
    """
    path = os.path.join("some", "arbitrary", "path")
    tag = "my-model:v1"
    model_version = "123"
    model_module_name = "myrepo.mymodel"

    _metadata_from_artifact_mock.return_value = {
        "module_name": model_module_name,
    }

    # Act

    build_prediction_api_docker_image(
        artifact_path=path,
        tag=tag,
        model_version=model_version,
    )

    # Assert

    expected_command = [
        "docker",
        "build",
        "--tag",
        tag,
        "--file",
        DOCKERFILE_PATH_ML_MODEL,
        "--build-arg",
        "MODEL_PATH=%s" % model_module_name.replace(".", "/"),
        "--build-arg",
        "OUTPUTS_PATH=%s" % DEFAULT_RELATIVE_ARTIFACT_PATH,
        "--build-arg",
        "MODEL_VERSION=%s" % model_version,
        "--build-arg",
        "PACKAGE_VERSION=%s" % PACKAGE_VERSION,
        path,
    ]

    check_call_mock.assert_called_once_with(
        expected_command, stdout=sys.stdout, stderr=subprocess.STDOUT, shell=False
    )
