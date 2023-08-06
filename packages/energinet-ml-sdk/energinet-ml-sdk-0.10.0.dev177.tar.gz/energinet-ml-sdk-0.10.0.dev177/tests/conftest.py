import tempfile
from random import random

import pytest

from energinetml.core.model import Model, TrainedModel, import_model_class
from energinetml.core.project import MachineLearningProject
from tests.constants import (
    COMPUTE_TARGET,
    DATASETS,
    DATASETS_CLOUD,
    DATASETS_LOCAL,
    EXPERIMENT,
    FEATURES,
    FILES_INCLUDE,
    MODEL_NAME,
    PARAMETERS,
    PROJECT_NAME,
    RESOURCE_GROUP,
    SUBNET,
    SUBSCRIPTION_ID,
    VM_SIZE,
    VNET,
    WORKSPACE_NAME,
)


def create_model(path: str, files_include=FILES_INCLUDE):
    return Model.create(
        path=f"{path}/user_model_{int(random()*100000)}",
        name=MODEL_NAME,
        experiment=EXPERIMENT,
        compute_target=COMPUTE_TARGET,
        vm_size=VM_SIZE,
        datasets=DATASETS,
        datasets_local=DATASETS_LOCAL,
        datasets_cloud=DATASETS_CLOUD,
        features=FEATURES,
        parameters=PARAMETERS,
        files_include=files_include,
    )


def create_project(path: str):
    return MachineLearningProject.create(
        path=path + "/user_model_test",
        name=PROJECT_NAME,
        subscription_id=SUBSCRIPTION_ID,
        resource_group=RESOURCE_GROUP,
        workspace_name=WORKSPACE_NAME,
        vnet_name=VNET,
        subnet_name=SUBNET,
    )


@pytest.fixture
def model_path():
    with tempfile.TemporaryDirectory() as path:
        project = create_project(path)

        model = create_model(path=project.default_model_path(MODEL_NAME))

        trained_model = TrainedModel(
            model="123", params={"asd": 123}, features=FEATURES
        )
        Model.dump(model.trained_model_path, trained_model)

        yield model.path


@pytest.fixture
def user_model():
    with tempfile.TemporaryDirectory() as path:
        model = create_model(path)
        model_class = import_model_class(model.path, model.parent_levels)
        yield model_class.from_directory(model.path)


@pytest.fixture
def model():
    with tempfile.TemporaryDirectory() as path:
        yield create_model(path)


@pytest.fixture
def model_with_project():
    with tempfile.TemporaryDirectory() as path:
        project = create_project(path)
        yield create_model(project.default_model_path(MODEL_NAME))


# -- Smoketest command-line options ------------------------------------------


def pytest_addoption(parser):
    """
    Adds command-line options to "pytest" command which will
    become available when running tests. Used for smoke testing.
    """
    parser.addoption("--path", action="store", default=None)
    parser.addoption("--subscription-id", action="store", default=None)
    parser.addoption("--subscription-name", action="store", default=None)
    parser.addoption("--resource-group", action="store", default=None)
    parser.addoption("--service-connection", action="store", default=None)
    parser.addoption("--workspace-name", action="store", default=None)
    parser.addoption("--project-name", action="store", default=None)
    parser.addoption("--model-name", action="store", default=None)
    parser.addoption("--deployment-base-url", action="store", default=None)
    parser.addoption("--sdk-version", action="store", default=None)


@pytest.fixture
def path(pytestconfig):
    """
    Used by ML smoketests.
    """
    return pytestconfig.getoption("--path")


@pytest.fixture
def subscription_id(pytestconfig):
    """
    Used by ML smoketests.
    """
    return pytestconfig.getoption("--subscription-id")


@pytest.fixture
def subscription_name(pytestconfig):
    """
    Used by ML smoketests.
    """
    return pytestconfig.getoption("--subscription-name")


@pytest.fixture
def resource_group(pytestconfig):
    """
    Used by ML AND Web-App smoketests.
    """
    return pytestconfig.getoption("--resource-group")


@pytest.fixture
def service_connection(pytestconfig):
    """
    Used by Web-App smoketests.
    """
    return pytestconfig.getoption("--service-connection")


@pytest.fixture
def workspace_name(pytestconfig):
    """
    Used by ML smoketests.
    """
    return pytestconfig.getoption("--workspace-name")


@pytest.fixture
def project_name(pytestconfig):
    """
    Used by ML AND Web-App smoketests.
    """
    return pytestconfig.getoption("--project-name")


@pytest.fixture
def model_name(pytestconfig):
    """
    Used by ML smoketests.
    """
    return pytestconfig.getoption("--model-name")


@pytest.fixture
def deployment_base_url(pytestconfig):
    """
    Used by ML smoketests.
    """
    return pytestconfig.getoption("--deployment-base-url")


@pytest.fixture
def sdk_version(pytestconfig):
    """
    Used by ML smoketests.
    """
    return pytestconfig.getoption("--sdk-version")


@pytest.fixture
def prediction_input():
    """
    Used by ML smoketests.
    """
    return {"inputs": [{"features": {"age": 20}}, {"features": {"age": 40}}]}


@pytest.fixture
def prediction_output():
    """
    Used by ML smoketests.
    """
    return ["no", "yes"]
