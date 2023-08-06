import json
from datetime import date, datetime
from unittest.mock import Mock, patch

from energinetml.core.insight import QUERY, parse_return_json, query, query_predictions


@patch("energinetml.core.insight.subprocess.check_output")
def test__query(check_output_mock):
    """
    :param Mock check_output_mock:
    """
    app = "APP"
    resource_group = "RESOURCE-GROUP"
    subscription = "SUBSCRIPTION"
    start_date = date(2020, 1, 1)
    end_date = date(2020, 12, 31)

    expected_return_json = b'{"some": "json"}'
    expected_command = [
        "az",
        "monitor",
        "app-insights",
        "query",
        "--apps",
        app,
        "--resource-group",
        resource_group,
        "--subscription",
        subscription,
        "--start-time",
        start_date.isoformat(),
        "--end-time",
        end_date.isoformat(),
        "--analytics-query",
        QUERY,
    ]

    check_output_mock.return_value = (
        expected_return_json + b"EXTRA CHARACTERS THAT SHOULD BE REMOVED"
    )

    # Act

    returned_json = query(
        app=app,
        resource_group=resource_group,
        subscription=subscription,
        start_date=start_date,
        end_date=end_date,
    )

    # Assert

    check_output_mock.assert_called_once_with(expected_command, shell=False)

    assert returned_json == json.loads(expected_return_json)


def test__parse_return_json():
    input_features = '[{"sepal_length": 1, "sepal_width": 2, "petal_length": 3, "petal_width": 4}, {"sepal_length": 10, "sepal_width": 20, "petal_length": 30, "petal_width": 40}]'  # noqa: E501
    model_name = "d-tree"
    predictions = '["Iris-versicolor", "Iris-virginica"]'
    indentifiers = "[null, null]"
    model_version = "456"

    return_json = {
        "tables": [
            {
                "columns": [
                    {"name": "timestamp", "type": "datetime"},
                    {"name": "identifiers", "type": "dynamic"},
                    {"name": "features", "type": "dynamic"},
                    {"name": "predictions", "type": "dynamic"},
                    {"name": "model_name", "type": "dynamic"},
                    {"name": "model_version", "type": "dynamic"},
                ],
                "name": "PrimaryResult",
                "rows": [
                    [
                        "2021-03-15T11:15:55.986Z",
                        indentifiers,
                        input_features,
                        predictions,
                        model_name,
                        model_version,
                    ],
                    [
                        "2021-03-15T11:15:55.854Z",
                        indentifiers,
                        input_features,
                        predictions,
                        model_name,
                        model_version,
                    ],
                    [
                        "2021-03-15T11:15:55.709Z",
                        indentifiers,
                        input_features,
                        predictions,
                        model_name,
                        model_version,
                    ],
                    [
                        "2021-03-15T11:15:55.563Z",
                        indentifiers,
                        input_features,
                        predictions,
                        model_name,
                        model_version,
                    ],
                    [
                        "2021-03-15T11:15:55.463Z",
                        indentifiers,
                        input_features,
                        predictions,
                        model_name,
                        model_version,
                    ],
                    [
                        "2021-03-15T11:15:52.904Z",
                        indentifiers,
                        input_features,
                        predictions,
                        model_name,
                        model_version,
                    ],
                    [
                        "2021-03-15T11:15:52.739Z",
                        indentifiers,
                        input_features,
                        predictions,
                        model_name,
                        model_version,
                    ],
                    [
                        "2021-03-15T11:15:40.224Z",
                        indentifiers,
                        input_features,
                        predictions,
                        model_name,
                        model_version,
                    ],
                    [
                        "2021-03-15T11:13:49.717Z",
                        indentifiers,
                        input_features,
                        predictions,
                        model_name,
                        model_version,
                    ],
                ],
            }
        ]
    }

    # Act

    result = list(parse_return_json(return_json))

    # Assert

    assert result == [
        {
            "timestamp": datetime(2021, 3, 15, 11, 15, 55),
            "model_name": model_name,
            "model_version": model_version,
            "identifier": None,
            "features": {
                "sepal_length": 1,
                "sepal_width": 2,
                "petal_length": 3,
                "petal_width": 4,
            },
            "prediction": "Iris-versicolor",
        },
        {
            "timestamp": datetime(2021, 3, 15, 11, 15, 55),
            "model_name": model_name,
            "model_version": model_version,
            "identifier": None,
            "features": {
                "sepal_length": 10,
                "sepal_width": 20,
                "petal_length": 30,
                "petal_width": 40,
            },
            "prediction": "Iris-virginica",
        },
        {
            "timestamp": datetime(2021, 3, 15, 11, 15, 55),
            "model_name": model_name,
            "model_version": model_version,
            "identifier": None,
            "features": {
                "sepal_length": 1,
                "sepal_width": 2,
                "petal_length": 3,
                "petal_width": 4,
            },
            "prediction": "Iris-versicolor",
        },
        {
            "timestamp": datetime(2021, 3, 15, 11, 15, 55),
            "model_name": model_name,
            "model_version": model_version,
            "identifier": None,
            "features": {
                "sepal_length": 10,
                "sepal_width": 20,
                "petal_length": 30,
                "petal_width": 40,
            },
            "prediction": "Iris-virginica",
        },
        {
            "timestamp": datetime(2021, 3, 15, 11, 15, 55),
            "model_name": model_name,
            "model_version": model_version,
            "identifier": None,
            "features": {
                "sepal_length": 1,
                "sepal_width": 2,
                "petal_length": 3,
                "petal_width": 4,
            },
            "prediction": "Iris-versicolor",
        },
        {
            "timestamp": datetime(2021, 3, 15, 11, 15, 55),
            "model_name": model_name,
            "model_version": model_version,
            "identifier": None,
            "features": {
                "sepal_length": 10,
                "sepal_width": 20,
                "petal_length": 30,
                "petal_width": 40,
            },
            "prediction": "Iris-virginica",
        },
        {
            "timestamp": datetime(2021, 3, 15, 11, 15, 55),
            "model_name": model_name,
            "model_version": model_version,
            "identifier": None,
            "features": {
                "sepal_length": 1,
                "sepal_width": 2,
                "petal_length": 3,
                "petal_width": 4,
            },
            "prediction": "Iris-versicolor",
        },
        {
            "timestamp": datetime(2021, 3, 15, 11, 15, 55),
            "model_name": model_name,
            "model_version": model_version,
            "identifier": None,
            "features": {
                "sepal_length": 10,
                "sepal_width": 20,
                "petal_length": 30,
                "petal_width": 40,
            },
            "prediction": "Iris-virginica",
        },
        {
            "timestamp": datetime(2021, 3, 15, 11, 15, 55),
            "model_name": model_name,
            "model_version": model_version,
            "identifier": None,
            "features": {
                "sepal_length": 1,
                "sepal_width": 2,
                "petal_length": 3,
                "petal_width": 4,
            },
            "prediction": "Iris-versicolor",
        },
        {
            "timestamp": datetime(2021, 3, 15, 11, 15, 55),
            "model_name": model_name,
            "model_version": model_version,
            "identifier": None,
            "features": {
                "sepal_length": 10,
                "sepal_width": 20,
                "petal_length": 30,
                "petal_width": 40,
            },
            "prediction": "Iris-virginica",
        },
        {
            "timestamp": datetime(2021, 3, 15, 11, 15, 52),
            "model_name": model_name,
            "model_version": model_version,
            "identifier": None,
            "features": {
                "sepal_length": 1,
                "sepal_width": 2,
                "petal_length": 3,
                "petal_width": 4,
            },
            "prediction": "Iris-versicolor",
        },
        {
            "timestamp": datetime(2021, 3, 15, 11, 15, 52),
            "model_name": model_name,
            "model_version": model_version,
            "identifier": None,
            "features": {
                "sepal_length": 10,
                "sepal_width": 20,
                "petal_length": 30,
                "petal_width": 40,
            },
            "prediction": "Iris-virginica",
        },
        {
            "timestamp": datetime(2021, 3, 15, 11, 15, 52),
            "model_name": model_name,
            "model_version": model_version,
            "identifier": None,
            "features": {
                "sepal_length": 1,
                "sepal_width": 2,
                "petal_length": 3,
                "petal_width": 4,
            },
            "prediction": "Iris-versicolor",
        },
        {
            "timestamp": datetime(2021, 3, 15, 11, 15, 52),
            "model_name": model_name,
            "model_version": model_version,
            "identifier": None,
            "features": {
                "sepal_length": 10,
                "sepal_width": 20,
                "petal_length": 30,
                "petal_width": 40,
            },
            "prediction": "Iris-virginica",
        },
        {
            "timestamp": datetime(2021, 3, 15, 11, 15, 40),
            "model_name": model_name,
            "model_version": model_version,
            "identifier": None,
            "features": {
                "sepal_length": 1,
                "sepal_width": 2,
                "petal_length": 3,
                "petal_width": 4,
            },
            "prediction": "Iris-versicolor",
        },
        {
            "timestamp": datetime(2021, 3, 15, 11, 15, 40),
            "model_name": model_name,
            "model_version": model_version,
            "identifier": None,
            "features": {
                "sepal_length": 10,
                "sepal_width": 20,
                "petal_length": 30,
                "petal_width": 40,
            },
            "prediction": "Iris-virginica",
        },
        {
            "timestamp": datetime(2021, 3, 15, 11, 13, 49),
            "model_name": model_name,
            "model_version": model_version,
            "identifier": None,
            "features": {
                "sepal_length": 1,
                "sepal_width": 2,
                "petal_length": 3,
                "petal_width": 4,
            },
            "prediction": "Iris-versicolor",
        },
        {
            "timestamp": datetime(2021, 3, 15, 11, 13, 49),
            "model_name": model_name,
            "model_version": model_version,
            "identifier": None,
            "features": {
                "sepal_length": 10,
                "sepal_width": 20,
                "petal_length": 30,
                "petal_width": 40,
            },
            "prediction": "Iris-virginica",
        },
    ]


@patch("energinetml.core.insight.query")
@patch("energinetml.core.insight.parse_return_json")
def test__query_predictions(parse_return_json_mock, query_mock):
    """
    :param Mock parse_return_json_mock:
    :param Mock query_mock:
    """
    query_return_value = Mock()
    parse_return_json_return_value = Mock()

    query_mock.return_value = query_return_value
    parse_return_json_mock.return_value = parse_return_json_return_value

    # Act
    return_value = query_predictions(some="args", foobar=1234)

    # Assert
    query_mock.assert_called_once_with(some="args", foobar=1234)
    parse_return_json_mock.assert_called_once_with(query_return_value)
    assert return_value is parse_return_json_return_value
