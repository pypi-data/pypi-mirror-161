import os
import tempfile
from unittest.mock import Mock, patch

import pytest
from azureml import exceptions

from energinetml.azure.datasets import AzureMLDataStore, MLDataSet


class TestMLDataSet:
    def test__path(self):
        with tempfile.TemporaryDirectory() as path:
            uut = MLDataSet(name="NAME", mount_path=path)

            assert uut.path("some", "folder") == os.path.join(path, "some", "folder")

    @patch("energinetml.azure.datasets.open")
    def test__open(self, open_mock):
        """
        :param Mock open_mock:
        """
        file_object = Mock()
        open_mock.return_value = file_object

        with tempfile.TemporaryDirectory() as path:
            uut = MLDataSet(name="NAME", mount_path=path)

            return_value = uut.open(["some", "path"])

            assert return_value is file_object

    @patch("energinetml.azure.datasets.os.path.exists")
    def test__contains(self, exists_mock):
        """
        :param Mock exists_mock:
        """
        exists_mock.return_value = True

        with tempfile.TemporaryDirectory() as path:
            uut = MLDataSet(name="NAME", mount_path=path)

            return_value = uut.contains("some", "path")

            assert return_value is True


class TestAzureMLDataStore:
    @patch("energinetml.azure.datasets.AzureMLDataStore.load_azureml_dataset")
    @patch("energinetml.azure.datasets.AzureMLDataStore.mount")
    def test__from_model(self, mount_mock, load_azureml_dataset_mock):
        """
        :param Mock mount_mock:
        :param Mock load_azureml_dataset_mock:
        """
        workspace = Mock()
        force_download = True
        model = Mock()

        mount1 = Mock()
        mount2 = Mock()
        mount_mock.side_effect = (mount1, mount2)

        # Act
        instance = AzureMLDataStore.from_model(
            model=model,
            datasets=[("dataset1", "123"), ("dataset2", "321")],
            workspace=workspace,
            force_download=force_download,
        )

        # Assert
        assert isinstance(instance, AzureMLDataStore)

        assert load_azureml_dataset_mock.call_count == 2
        load_azureml_dataset_mock.assert_any_call(
            workspace=workspace, dataset_name="dataset1", dataset_version="123"
        )

        load_azureml_dataset_mock.assert_any_call(
            workspace=workspace, dataset_name="dataset2", dataset_version="321"
        )

        assert instance["dataset1"] is mount1
        assert instance["dataset2"] is mount2

    @patch("energinetml.azure.datasets.Dataset.get_by_name")
    @pytest.mark.parametrize(
        "dataset_version, actual_dataset_version", (("123", "123"), (None, "latest"))
    )
    def test__load_azureml_dataset__dataset_exists__should_return_dataset(
        self, get_by_name_mock, dataset_version, actual_dataset_version
    ):
        """
        :param Mock get_by_name_mock:
        :param str dataset_version:
        :param str actual_dataset_version:
        """
        dataset = Mock()
        get_by_name_mock.return_value = dataset
        workspace = Mock()

        # Act
        returned_value = AzureMLDataStore.load_azureml_dataset(
            workspace=workspace,
            dataset_name="datasetname",
            dataset_version=dataset_version,
        )

        # Assert
        assert returned_value is dataset

        get_by_name_mock.assert_called_once_with(
            workspace=workspace, name="datasetname", version=actual_dataset_version
        )

    @patch("energinetml.azure.datasets.Dataset.get_by_name")
    def test__load_azureml_dataset__azure_raise_user_error_exception__should_raise_data_set_not_found(  # noqa: E501
        self, get_by_name_mock
    ):
        """
        :param Mock get_by_name_mock:
        """
        get_by_name_mock.side_effect = exceptions._azureml_exception.UserErrorException(
            "x"
        )

        # Act + Assert
        with pytest.raises(AzureMLDataStore.DataSetNotFound):
            AzureMLDataStore.load_azureml_dataset(
                workspace=Mock(), dataset_name="datasetname", dataset_version="123"
            )

    def test__mount(self):
        with pytest.raises(NotImplementedError):
            AzureMLDataStore.mount(
                model=Mock(), azureml_dataset=Mock(), force_download=Mock()
            )
