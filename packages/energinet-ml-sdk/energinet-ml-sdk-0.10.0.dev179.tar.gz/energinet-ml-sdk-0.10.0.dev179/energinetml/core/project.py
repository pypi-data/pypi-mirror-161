#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from functools import cached_property
from typing import Any, Dict

from energinetml.core.templates import WebAppTemplateResolver
from energinetml.core.webapp import WebAppEngine
from energinetml.settings import (
    DEFAULT_ENCODING,
    DEFAULT_LOCATION,
    PACKAGE_NAME,
    PACKAGE_VERSION,
)

from .configurable import Configurable
from .requirements import RequirementList
from .templates import ASGIWebAppTemplates, WSGIWebAppTemplates
from .webapp import AsgiWebApp, WsgiWebApp


@dataclass
class Project(Configurable):
    """[summary]"""

    _CONFIG_FILE_NAME = "project.json"
    _REQUIREMENTS_FILE_NAME = "requirements.txt"

    name: str

    @classmethod
    def create(cls, *args: Any, **kwargs: Dict[str, Any]) -> Project:
        """[summary]

        Returns:
            [type]: [description]
        """
        project = super().create(*args, **kwargs)

        # Create requirements.txt file
        with open(project.requirements_file_path, "w", encoding=DEFAULT_ENCODING) as f:
            f.write(f"{PACKAGE_NAME}=={PACKAGE_VERSION}\n")

        return project

    @property
    def requirements_file_path(self) -> str:
        """Absolute path to requirements.txt file.

        Returns:
            str: [description]
        """
        return self.get_file_path(self._REQUIREMENTS_FILE_NAME)

    @cached_property
    def requirements(self) -> RequirementList:
        """Returns a list of project requirements from requirements.txt.

        Returns:
            RequirementList: [description]
        """
        if os.path.isfile(self.requirements_file_path):
            return RequirementList.from_file(self.requirements_file_path)
        else:
            return RequirementList()


# -- Machine Learning --------------------------------------------------------


@dataclass
class MachineLearningProject(Project):
    """[summary]"""

    subscription_id: str
    resource_group: str
    workspace_name: str
    vnet_name: str
    subnet_name: str
    location: str = field(default=DEFAULT_LOCATION)

    @property
    def vnet_resourcegroup_name(self) -> str:
        """The resource group where the VNET is located, typically
        the same as the workspace.

        Returns:
            str: [description]
        """
        return self.resource_group

    def default_model_path(self, model_name: str) -> str:
        """Returns default absolute path to folder where new models
        should be created at.

        Args:
            model_name (str): [description]

        Returns:
            str: [description]
        """
        return self.get_file_path(model_name)


# -- Web Apps ----------------------------------------------------------------


class WebAppProjectKind(str, Enum):
    """[summary]"""

    ASGI = "ASGI"
    WSGI = "WSGI"


@dataclass
class WebAppProject(Project):
    """[summary]"""

    kind: WebAppProjectKind

    RESOLVERS = {
        WebAppProjectKind.ASGI: ASGIWebAppTemplates(),
        WebAppProjectKind.WSGI: WSGIWebAppTemplates(),
    }

    ENGINES = {
        WebAppProjectKind.ASGI: AsgiWebApp(),
        WebAppProjectKind.WSGI: WsgiWebApp(),
    }

    def get_template_resolver(self) -> WebAppTemplateResolver:
        """[summary]

        Raises:
            RuntimeError: [description]

        Returns:
            WebAppTemplateResolver: [description]
        """
        if self.kind in self.RESOLVERS:
            return self.RESOLVERS[self.kind]
        raise RuntimeError

    def get_engine(self) -> WebAppEngine:
        """[summary]

        Raises:
            RuntimeError: [description]

        Returns:
            WebAppEngine: [description]
        """
        if self.kind in self.ENGINES:
            return self.ENGINES[self.kind]
        raise RuntimeError

    @property
    def dockerfile_path(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return os.path.join(self.path, "Dockerfile")
