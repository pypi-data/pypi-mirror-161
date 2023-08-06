#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""
import io
import os
from typing import TYPE_CHECKING, Dict, Iterable, List, Tuple, Union

from azureml import exceptions
from azureml.core import Dataset, Workspace
from azureml.data import FileDataset, TabularDataset
from pandas import DataFrame

from energinetml.settings import DEFAULT_ENCODING

if TYPE_CHECKING:
    from energinetml.core.model import Model


class MLDataSet:
    """[summary]"""

    def __init__(
        self, name: str, mount_path: str = None, dataframe: DataFrame = None
    ) -> None:
        """[summary]

        Args:
            name (str): [description]
            mount_path (str): [description]
            dataframe (DataFrame, optional): Dataframe of the dataset.
            This is set if the dataset is tabular. Defaults to None.
        """
        self.name = name
        self.mount_path = mount_path
        self.dataframe = dataframe

    def __str__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return f"{self.__class__.__name__}<{self.name}>"

    def path(self, *relative_path: Union[List[str], str]) -> str:
        """[summary]

        Args:
            *relative_path (Union[List[str], str]): [description]

        Returns:
            str: [description]
        """
        return os.path.join(self.mount_path, *relative_path)

    def open(self, relative_path: List[str], *args, **kwargs) -> io.TextIOWrapper:
        """
        :param list[str] relative_path:
        :param args: *args for open()
        :param kwargs: **kwargs for open()
        :rtype: typing.IO
        """
        return open(
            self.path(*relative_path), *args, encoding=DEFAULT_ENCODING, **kwargs
        )

    def contains(self, *relative_path: Union[List[str], str]) -> bool:
        """[summary]

        Args:
            *relative_path (Union[List[str], str]): [description]

        Returns:
            bool: [description]
        """
        return os.path.exists(self.path(*relative_path))


class MLDataStore(Dict[str, "MLDataSet"]):
    """A class

    Args:
        Dict (str, MLDataSet): A dictionary of datasets
    """

    class DataSetNotFound(Exception):
        """[summary]"""

        pass


class AzureMLDataStore(MLDataStore):
    """[summary]"""

    @classmethod
    def from_model(
        cls,
        model: "Model",
        datasets: Iterable[Tuple[str, str]],
        workspace: Workspace,
        force_download: bool = False,
    ) -> "AzureMLDataStore":
        """[summary]

        Args:
            model (Model): [description]
            datasets (Iterable[Tuple[str, str]]): [description]
            workspace (Workspace): [description]
            force_download (bool, optional): [description]. Defaults to False.

        Returns:
            Description
        """
        mounted_datasets = {}

        for dataset_name, dataset_version in datasets:
            azureml_dataset = cls.load_azureml_dataset(
                workspace=workspace,
                dataset_name=dataset_name,
                dataset_version=dataset_version,
            )

            mounted_datasets[dataset_name] = cls.mount(
                model=model,
                azureml_dataset=azureml_dataset,
                force_download=force_download,
            )

        return cls(**mounted_datasets)

    @classmethod
    def load_azureml_dataset(
        cls, workspace: Workspace, dataset_name: str, dataset_version: str = None
    ) -> Union[TabularDataset, FileDataset]:
        """[summary]

        Args:
            workspace (Workspace): [description]
            dataset_name (str): [description]
            dataset_version (str, optional): [description]. Defaults to None.

        Raises:
            cls.DataSetNotFound: [description]

        Returns:
            Union[TabularDataset, FileDataset]: [description]
        """

        # azureml wants 'latest'
        if dataset_version is None:
            dataset_version = "latest"

        try:
            return Dataset.get_by_name(
                workspace=workspace, name=dataset_name, version=dataset_version
            )
        except exceptions._azureml_exception.UserErrorException:
            raise cls.DataSetNotFound(dataset_name)

    @classmethod
    def mount(
        cls,
        model: "Model",
        azureml_dataset: Union[TabularDataset, FileDataset],
        force_download: bool,
    ) -> MLDataSet:
        """[summary]

        Args:
            model (Model): [description]
            azureml_dataset (Union[TabularDataset, FileDataset]): [description]
            force_download (bool): [description]

        Raises:
            NotImplementedError: [description]

        Returns:
            MLDataSet: [description]
        """
        raise NotImplementedError


class MountedAzureMLDataStore(AzureMLDataStore):
    """[summary]"""

    @classmethod
    def mount(cls, model: "Model", azureml_dataset, force_download: bool) -> MLDataSet:
        """[summary]

        Args:
            model (Model): [description]
            azureml_dataset ([type]): [description]
            force_download (bool): [description]

        Returns:
            MLDataSet: [description]
        """
        # We don't need to download tabular datasets because we already know the schema.
        if isinstance(azureml_dataset, TabularDataset):
            df = azureml_dataset.to_pandas_dataframe()
            return MLDataSet(name=azureml_dataset.name, dataframe=df)

        else:
            mount_context = azureml_dataset.mount()
            mount_point = mount_context.mount_point
            mount_context.start()
            return MLDataSet(name=azureml_dataset.name, mount_path=mount_point)


class DownloadedAzureMLDataStore(AzureMLDataStore):
    """[summary]"""

    @classmethod
    def mount(
        cls, model: "Model", azureml_dataset: TabularDataset, force_download: bool
    ) -> MLDataSet:
        """[summary]

        Args:
            model (Model): [description]
            azureml_dataset (TabularDataset): [description]
            force_download (bool): [description]

        Returns:
            MLDataSet: [description]
        """

        # We don't need to download tabular datasets because we already know the schema.
        if isinstance(azureml_dataset, TabularDataset):
            df = azureml_dataset.to_pandas_dataframe()
            return MLDataSet(name=azureml_dataset.name, dataframe=df)

        mount_point = os.path.join(model.data_folder_path, azureml_dataset.name)
        try:
            azureml_dataset.download(mount_point, overwrite=force_download)
        except exceptions._azureml_exception.UserErrorException:
            # Dataset already exists on filesystem
            # TODO Rethink this solution
            print("NOTICE: Using cached dataset (from filesystem)")
        return MLDataSet(name=azureml_dataset.name, mount_path=mount_point)
