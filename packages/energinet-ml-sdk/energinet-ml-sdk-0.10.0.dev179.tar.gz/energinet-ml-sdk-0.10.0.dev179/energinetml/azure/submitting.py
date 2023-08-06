#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""

from typing import TYPE_CHECKING

import azureml

if TYPE_CHECKING:
    from energinetml.core.model import Model


class AzureSubmitContext:
    """[summary]"""

    class SubmitError(Exception):
        """[summary]"""

        pass

    class FailedToWait(SubmitError):
        """[summary]"""

        pass

    class FailedToDownload(SubmitError):
        """[summary]"""

        pass

    def __init__(self, model: "Model", az_run: azureml.core.Run):
        """[summary]

        Args:
            model (Model): [description]
            az_run (azureml.core.Run): [description]
        """
        self.model = model
        self.az_run = az_run

    def wait_for_completion(self):
        """[summary]

        Raises:
            AzureSubmitContext.FailedToWait: [description]
        """
        try:
            self.az_run.wait_for_completion(show_output=True)
        except azureml.exceptions._azureml_exception.ActivityFailedException as e:
            raise self.FailedToWait(e.message)

    def download_files(self):
        """Wrapper function for Azure Run-class download_files-function."""
        self.az_run.download_files(output_directory=self.model.path)
