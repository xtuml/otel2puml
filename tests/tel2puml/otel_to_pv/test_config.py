"""Tests for the module config.py."""
from typing import Any
from copy import deepcopy

import pytest
from pydantic import ValidationError

from tel2puml.otel_to_pv.config import load_config_from_dict


def test_load_config_from_dict(
    mock_yaml_config_dict: dict[str, Any]
) -> None:
    """Test load_config_from_yaml_string."""
    _ = load_config_from_dict(mock_yaml_config_dict)
    # test cases in which some required fields are missing
    for field in ["data_sources", "data_holders", "ingest_data"]:
        temp_config = deepcopy(mock_yaml_config_dict)
        temp_config.pop(field)
        with pytest.raises(AssertionError):
            load_config_from_dict(temp_config)
    # test case where an fields are not present for ingest_data
    for field in ["data_source", "data_holder"]:
        temp_config = deepcopy(mock_yaml_config_dict)
        temp_config["ingest_data"].pop(field)
        with pytest.raises(ValidationError):
            load_config_from_dict(temp_config)
    # test case of incorrect data source and data holder
    for field in ["data_source", "data_holder"]:
        temp_config = deepcopy(mock_yaml_config_dict)
        temp_config["ingest_data"][field] = "incorrect"
        with pytest.raises(ValidationError):
            load_config_from_dict(temp_config)
    # test case where an extra field is supplied to ingest_data
    temp_config = deepcopy(mock_yaml_config_dict)
    temp_config["ingest_data"]["extra"] = "extra"
    with pytest.raises(ValidationError):
        load_config_from_dict(temp_config)
