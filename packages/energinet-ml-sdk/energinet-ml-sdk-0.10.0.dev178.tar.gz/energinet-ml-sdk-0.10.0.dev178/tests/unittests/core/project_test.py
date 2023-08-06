import json
import os
import tempfile

import pytest

from energinetml.core.project import MachineLearningProject
from energinetml.settings import PACKAGE_NAME, PACKAGE_VERSION

NAME = "NAME"
SUBSCRIPTION_ID = "SUBSCRIPTION-ID"
RESOURCE_GROUP = "RESOURCE-GROUP"
WORKSPACE_NAME = "WORKSPACE-NAME"
VNET = "VNET"
SUBNET = "SUBNET"


@pytest.fixture
def project():
    with tempfile.TemporaryDirectory() as path:
        yield MachineLearningProject(
            path=path,
            name=NAME,
            subscription_id=SUBSCRIPTION_ID,
            resource_group=RESOURCE_GROUP,
            workspace_name=WORKSPACE_NAME,
            vnet_name=VNET,
            subnet_name=SUBNET,
        )


class TestProject:
    def test__vnet_resourcegroup_name(self, project):
        """
        :param Project project:
        """
        assert project.vnet_resourcegroup_name == RESOURCE_GROUP

    def test__vnet_name(self, project):
        """
        :param Project project:
        """
        assert project.vnet_name == VNET

    def test__subnet_name(self, project):
        """
        :param Project project:
        """
        assert project.subnet_name == SUBNET

    def test__requirements_file_path(self, project):
        """
        :param Project project:
        """
        assert project.requirements_file_path == os.path.join(
            project.path, "requirements.txt"
        )

    def test__default_model_path(self, project):
        """
        :param Project project:
        """
        model_name = "my-model"

        assert project.default_model_path(model_name) == os.path.join(
            project.path, model_name
        )

    def test__create__should_create_project_files(self):
        with tempfile.TemporaryDirectory() as path:
            project = MachineLearningProject.create(
                path=path,
                name=NAME,
                subscription_id=SUBSCRIPTION_ID,
                resource_group=RESOURCE_GROUP,
                workspace_name=WORKSPACE_NAME,
                vnet_name=VNET,
                subnet_name=SUBNET,
            )

            assert os.path.isfile(os.path.join(project.path, "project.json"))
            assert os.path.isfile(os.path.join(project.path, "requirements.txt"))

            # requirements.txt
            assert PACKAGE_NAME in project.requirements
            assert project.requirements.get(PACKAGE_NAME).specs == [
                ("==", str(PACKAGE_VERSION))
            ]  # noqa: E501

            # project.json
            with open(os.path.join(project.path, "project.json")) as f:
                config = json.load(f)
                assert config["name"] == NAME
                assert config["subscription_id"] == SUBSCRIPTION_ID
                assert config["resource_group"] == RESOURCE_GROUP
                assert config["workspace_name"] == WORKSPACE_NAME
