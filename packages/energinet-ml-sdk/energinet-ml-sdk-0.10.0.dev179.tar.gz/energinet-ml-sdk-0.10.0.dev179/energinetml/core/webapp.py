#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]"""
from __future__ import annotations

import os
import subprocess
import sys
from typing import TYPE_CHECKING  # noqa TYP001

if TYPE_CHECKING:

    from energinetml.core.project import Project


class WebAppEngine:
    """[summary]"""

    command = None

    def serve(self, project: Project) -> None:
        """[summary]

        Args:
            project (Project): [description]

        Raises:
            NotImplementedError: [description]
        """
        os.chdir(os.path.join(project.path, "src"))

        if self.command is None:
            raise NotImplementedError

        subprocess.check_call(
            self.command, stdout=sys.stdout, stderr=subprocess.STDOUT, shell=False
        )


class WsgiWebApp(WebAppEngine):
    """
    WSGI
    """

    command = ("waitress-serve", "--listen=*:8000", "app:app")


class AsgiWebApp(WebAppEngine):
    """
    ASGI
    """

    command = ("uvicorn", "app:app")


class OpyratorWebApp(WebAppEngine):
    """[summary]"""

    def serve(self, path: str):
        """[summary]

        Args:
            path (str): [description]

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError
