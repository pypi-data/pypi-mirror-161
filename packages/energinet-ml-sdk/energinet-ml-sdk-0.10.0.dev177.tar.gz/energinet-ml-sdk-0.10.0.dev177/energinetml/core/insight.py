#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[summary]
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Iterable  # noqa TYP001

if TYPE_CHECKING:
    import pandas as pd

QUERY = """
    requests
        | where name == "prediction"
        | order by timestamp
        | project timestamp,
                  identifiers = customDimensions["identifiers"],
                  features = customDimensions["features"],
                  predictions = customDimensions["predictions"],
                  model_name = customDimensions["model_name"],
                  model_version = customDimensions["model_version"]
        | where features != ""
"""


def query(
    app: str,
    resource_group: str,
    subscription: str,
    start_date: datetime.date,
    end_date: datetime.date,
) -> Dict[str, Any]:
    """Query Application Insights for model predictions.

    Args:
        app (str): Azure Application Insight app name
        resource_group (str): Azure resource group
        subscription (str): Azure subscription
        start_date (datetime.date): Start date (included)
        end_date (datetime.date): End date (included)

    Returns:
        Dict[str, Any]: [description]
    """
    command = ["az", "monitor", "app-insights", "query"]
    command.extend(("--apps", app))
    command.extend(("--resource-group", resource_group))
    command.extend(("--subscription", subscription))
    command.extend(("--start-time", start_date.isoformat()))
    command.extend(("--end-time", end_date.isoformat()))
    command.extend(("--analytics-query", QUERY))

    output_bytes = subprocess.check_output(command, shell=False)
    output_string = output_bytes.decode("utf-8")
    # String may contain trailing characters, not part of the JSON document
    output_string = output_string[: output_string.rfind("}") + 1]

    return json.loads(output_string)


def parse_return_json(return_json: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    """[summary]

    Args:
        return_json (Dict[str, Any]): [description]

    Returns:
        Iterable[Dict[str, Any]]: [description]

    Yields:
        Iterator[Iterable[Dict[str, Any]]]: [description]
    """
    columns = [c["name"] for c in return_json["tables"][0]["columns"]]

    for row in return_json["tables"][0]["rows"]:
        entity = dict(zip(columns, row))

        t = datetime.strptime(entity["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(
            microsecond=0
        )

        z = zip(
            json.loads(entity["identifiers"]),
            json.loads(entity["features"]),
            json.loads(entity["predictions"]),
        )

        for identifier, features, prediction in z:
            yield {
                "timestamp": t,
                "model_name": entity["model_name"],
                "model_version": entity["model_version"],
                "identifier": identifier,
                "features": features,
                "prediction": prediction,
            }


def query_predictions(**kwargs) -> Iterable[Dict[str, Any]]:
    """Perform an Application Insight query to get inputs with their respective
    predictions from a deployed model. These are the entries logged by models
    when deployed in Azure using the SDK.

    Example usage:

        from datetime import date
        from energinetml import query_predictions

        entries = query_predictions(
            app='MyApplicationInsightAppName',
            resource_group='MyAzureResourceGroup',
            subscription='MyAzureSubscription',
            start_date=date(2021, 1, 1),
            end_date=date(2021, 12, 31),
        )

    Returns:
        Iterable[Dict[str, Any]]: [description]
    """
    return parse_return_json(query(**kwargs))


def query_predictions_as_dataframe(**kwargs) -> pd.DataFrame:
    """Shortcut for query_predictions() but returns a Pandas DataFrame
    instead of a list of dicts.
    Any kwargs: Keyword args for query_predictions() method

    Raises:
        RuntimeError: [description]

    Returns:
        pd.DataFrame: [description]
    """

    try:
        import pandas as pd
    except ImportError:
        raise RuntimeError(
            "Failed to import pandas. Make sure to add "
            "pandas to your requirements.txt file"
        )

    return pd.DataFrame(query_predictions(**kwargs))
