import json
import os

from energinetml.azure.training import AzureTrainingContext
from energinetml.core.model import Model
from tests.constants import RUN_ID


def test__should_write_metafile_correct(model):

    # Arrange
    model_meta_data = {"module_name": model.module_name, "run_id": RUN_ID}
    context = AzureTrainingContext()
    file_path = os.path.join(model.path, Model._META_FILE_NAME)

    # Act
    context.save_meta_data(model_meta_data, file_path)

    # Read file from disk
    with open(file_path) as file:
        meta_dict = json.load(file)

    # Assert
    assert meta_dict["module_name"] == model.module_name
    assert meta_dict["run_id"] == RUN_ID
