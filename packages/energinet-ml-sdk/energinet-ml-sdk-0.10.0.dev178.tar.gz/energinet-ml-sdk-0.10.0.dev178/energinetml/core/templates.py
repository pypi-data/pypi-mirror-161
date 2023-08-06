#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""

import os
import subprocess
import sys
import tempfile
import typing

from jinja2 import Template

from energinetml.settings import (
    DEFAULT_ENCODING,
    DEVOPS_FOLDER_NAME,
    GITIGNORE_NAME,
    TEMPLATES_GIT_URL,
    TEMPLATES_IP_WHITELIST,
    TEMPLATES_SUBNET_WHITELIST,
)


class TemplateResolver:
    """[summary]"""

    class TemplateResolverError(Exception):
        """[summary]"""

        pass

    def get_default_env(self) -> typing.Dict[str, typing.Any]:
        """[summary]

        Returns:
            typing.Dict[str, typing.Any]: [description]
        """
        return {}

    def clone_and_render(
        self,
        project_root_path: str,
        files: typing.Iterable[typing.Tuple[str, str]],
        env: typing.Dict[str, typing.Any],
    ):
        """Clones Git repository and renders templates using the provided
        environment variables.

        Args:
            project_root_path (str): [description]
            files (typing.Iterable[typing.Tuple[str, str]]): This argument is an
            iterable of (src, dst) where 'src' is file path relative to Git repository
            root, and 'dst' is file path relative.
        to project root.
            env (typing.Dict[str, typing.Any]): [description]
        """
        actual_env = self.get_default_env()
        actual_env.update(env)

        with tempfile.TemporaryDirectory() as clone_path:
            self.clone(clone_path)

            for src, dst in files:
                self.render(
                    src=os.path.join(clone_path, src),
                    dst=os.path.join(project_root_path, dst),
                    env=actual_env,
                )

    def clone(self, clone_path: str) -> None:
        """[summary]

        Args:
            clone_path (str): [description]

        Raises:
            self.TemplateResolverError: [description]
        """
        try:
            subprocess.check_call(
                args=["git", "clone", TEMPLATES_GIT_URL, clone_path],
                stdout=sys.stdout,
                stderr=subprocess.STDOUT,
                shell=False,
            )
        except subprocess.CalledProcessError:
            raise self.TemplateResolverError(
                f"Failed to clone Git repo: {TEMPLATES_GIT_URL}"
            )

    def render(self, src: str, dst: str, env: typing.Dict[str, str]) -> None:
        """Renders Jinja2 template file at 'src' and writes it to 'dst' using the
        provided environment variables. Creates directories if necessary.

        Args:
            src (str): [description]
            dst (str): [description]
            env (typing.Dict[str, str]): [description]
        """
        dst_folder = os.path.split(dst)[0]

        with open(src, encoding=DEFAULT_ENCODING) as f:
            template = Template(f.read())
            rendered = template.render(**env)

        if not os.path.isdir(dst_folder):
            os.makedirs(dst_folder)

        with open(dst, "w", encoding=DEFAULT_ENCODING) as f:
            f.write(rendered)


class DataSciencePlatformTemplates(TemplateResolver):
    """
    Templates specific for Data Science Platform.
    """

    def get_default_env(self) -> typing.Dict[str, typing.Any]:
        """[summary]

        Returns:
            typing.Dict[str, typing.Any]: [description]
        """
        return {
            "subnetWhitelist": TEMPLATES_SUBNET_WHITELIST,
            "ipWhitelist": TEMPLATES_IP_WHITELIST,
        }

    def resolve(
        self,
        project_root_path: str,
        project_name: str,
        service_connection: str,
        resource_group: str,
    ):
        """[summary]

        Args:
            project_root_path (str): [description]
            project_name (str): [description]
            service_connection (str): DevOps Service Connection for deploying to
            resource group.
            resource_group (str): Azure Resource Group to deploy webapp to.
        """
        files = (
            (GITIGNORE_NAME, GITIGNORE_NAME),
            (
                os.path.join(DEVOPS_FOLDER_NAME, "infrastructure.yml"),
                os.path.join(DEVOPS_FOLDER_NAME, "infrastructure.yml"),
            ),
            (
                os.path.join("terraform", "datascienceplatform", "dev", "main.tf"),
                os.path.join("terraform", "dev", "datascienceplatform.tf"),
            ),
        )

        env = {
            "serviceConnection": service_connection,
            "resourceGroup": resource_group,
            "projectName": project_name,
        }

        self.clone_and_render(project_root_path=project_root_path, files=files, env=env)


class WebAppTemplateResolver(TemplateResolver):
    """
    Templates specific for Web Apps.
    """

    def resolve_web_app(
        self, project_root_path: str, kind: str, env: typing.Dict[str, typing.Any]
    ):
        """[summary]

        Args:
            project_root_path (str): [description]
            kind (str): [description]
            env (typing.Dict[str, typing.Any]): [description]
        """
        files = (
            (GITIGNORE_NAME, GITIGNORE_NAME),
            (
                os.path.join(DEVOPS_FOLDER_NAME, "infrastructure.yml"),
                os.path.join(DEVOPS_FOLDER_NAME, "infrastructure.yml"),
            ),
            (
                os.path.join(DEVOPS_FOLDER_NAME, "deploy-webapp.yml"),
                os.path.join(DEVOPS_FOLDER_NAME, "deploy.yml"),
            ),
            (
                os.path.join("webapp", "terraform", "dev", "main.tf"),
                os.path.join("terraform", "dev", "webapp.tf"),
            ),
            (os.path.join("webapp", kind, "Dockerfile"), os.path.join("Dockerfile")),
            (
                os.path.join("webapp", kind, "src", "app.py"),
                os.path.join("src", "app.py"),
            ),
            (
                os.path.join("webapp", kind, "src", "__init__.py"),
                os.path.join("src", "__init__.py"),
            ),
            (
                os.path.join("webapp", kind, "src", "requirements.txt"),
                os.path.join("src", "requirements.txt"),
            ),
        )

        self.clone_and_render(project_root_path=project_root_path, files=files, env=env)

    def resolve(
        self,
        project_root_path: str,
        project_name: str,
        service_connection: str,
        resource_group: str,
    ):
        """[summary]

        Args:
            project_root_path (str): [description]
            project_name (str): [description]
            service_connection (str): DevOps Service Connection for deploying to
            resource group.
            resource_group (str): Azure Resource Group to deploy webapp to.

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError


class ASGIWebAppTemplates(WebAppTemplateResolver):
    """
    Templates specific for ASGI Web Apps.
    """

    def resolve(
        self,
        project_root_path: str,
        project_name: str,
        service_connection: str,
        resource_group: str,
    ):
        """[summary]

        Args:
            project_root_path (str): [description]
            project_name (str): [description]
            service_connection (str): DevOps Service Connection for deploying to
            resource group.
            resource_group (str): Azure Resource Group to deploy webapp to.
        """
        self.resolve_web_app(
            project_root_path=project_root_path,
            kind="ASGI",
            env={
                "serviceConnection": service_connection,
                "resourceGroup": resource_group,
                "projectName": project_name,
            },
        )


class WSGIWebAppTemplates(WebAppTemplateResolver):
    """
    Templates specific for ASGI Web Apps.
    """

    def resolve(
        self,
        project_root_path: str,
        project_name: str,
        service_connection: str,
        resource_group: str,
    ):
        """[summary]

        Args:
            project_root_path (str): [description]
            project_name (str): [description]
            service_connection (str): DevOps Service Connection for deploying to
            resource group.
            resource_group (str): Azure Resource Group to deploy webapp to.
        """
        self.resolve_web_app(
            project_root_path=project_root_path,
            kind="WSGI",
            env={
                "serviceConnection": service_connection,
                "resourceGroup": resource_group,
                "projectName": project_name,
            },
        )
