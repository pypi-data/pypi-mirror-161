#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""
import os

from packaging import version
from pkg_resources import Requirement

# -- Directories/paths -------------------------------------------------------

__current_file = os.path.abspath(__file__)
__current_folder = os.path.split(__current_file)[0]

SOURCE_DIR = os.path.abspath(__current_folder)
STATIC_DIR = os.path.join(SOURCE_DIR, "static")
EMPTY_MODEL_TEMPLATE_DIR = os.path.join(STATIC_DIR, "model_template")
DOCKERFILE_PATH_ML_MODEL = os.path.join(STATIC_DIR, "Dockerfile")
GITIGNORE_PATH = os.path.join(STATIC_DIR, "gitignore.txt")
WEB_APP_PIPELINES_TEMPLATES_PATH = os.path.join(STATIC_DIR, "webapppipelines")
DEVOPS_FOLDER_NAME = ".azuredevops"
GITIGNORE_NAME = ".gitignore"
DEFAULT_ENCODING = "utf-8"


def __read_meta(filename: str) -> str:
    with open(
        os.path.join(__current_folder, "meta", filename), encoding=DEFAULT_ENCODING
    ) as handle:
        return handle.read().strip()


# -- Local -------------------------------------------------------------------

DEFAULT_RELATIVE_ARTIFACT_PATH = "outputs"
DEFAULT_LOG_PATH = "logs"
DEFAULT_LOG_FILENAME = "log.txt"
DEFAULT_LOG_ENCODING = "utf-8"

# -- Cloud --------------------------------------------------------------------

DEFAULT_LOCATION = "westeurope"
DEFAULT_VM_CPU = "Standard_D1_v2"
DEFAULT_VM_GPU = "Standard_NV6"

CLUSTER_IDLE_SECONDS_BEFORE_SCALEDOWN = 60 * 60 * 2  # 2 hours


# -- Package details ---------------------------------------------------------

# TODO Rename "PACKAGE" to "SDK" (here and elsewhere in general)

PYTHON_VERSION = __read_meta("PYTHON_VERSION")
PACKAGE_NAME = __read_meta("PACKAGE_NAME")
COMMAND_NAME = __read_meta("COMMAND_NAME")
PACKAGE_VERSION = version.parse(__read_meta("PACKAGE_VERSION"))
PACKAGE_REQUIREMENT = Requirement.parse(f"{PACKAGE_NAME}=={PACKAGE_VERSION}")


# -- Misc --------------------------------------------------------------------

APPINSIGHTS_INSTRUMENTATIONKEY = os.environ.get("APPINSIGHTS_INSTRUMENTATIONKEY")

# Git repository containing template files
TEMPLATES_GIT_URL = "https://github.com/AnalyticsOps/templates.git"
TEMPLATES_SUBNET_WHITELIST = "/subscriptions/d252b8da-1db8-44f7-bd6e-8010cc01382b/resourceGroups/rg-AnalyticsOpsAgents-U/providers/Microsoft.Network/virtualNetworks/vnet-devops-agent-001/subnets/agent-subnet"  # noqa: E501
TEMPLATES_IP_WHITELIST = "194.239.2.0/24"
