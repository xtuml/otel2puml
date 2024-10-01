"""Tests for the module config.py."""

from typing import Any
from copy import deepcopy

import pytest
from pydantic import ValidationError

from tel2puml.otel_to_pv.config import (
    load_config_from_dict,
    SequenceModelConfig,
)


def test_load_config_from_dict(mock_yaml_config_dict: dict[str, Any]) -> None:
    """Test load_config_from_yaml_string."""
    otel_to_pv_config = load_config_from_dict(mock_yaml_config_dict)
    # check sequencer default is set
    assert otel_to_pv_config["sequencer"] == SequenceModelConfig(
        async_event_groups={}
    )
    # check case where sequencer is provided
    temp_config = deepcopy(mock_yaml_config_dict)
    temp_config["sequencer"] = {
        "async_event_groups": {
            "job_1": {
                "event_1": {},
                "event_2": {"event_3": "group_1"}
            }
        }
    }
    otel_to_pv_config = load_config_from_dict(temp_config)
    assert otel_to_pv_config["sequencer"] == SequenceModelConfig(
        async_event_groups={
            "job_1": {
                "event_1": {},
                "event_2": {"event_3": "group_1"}
            }
        }
    )
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


def test_sequence_model_config() -> None:
    """Test the sequence model config."""
    # test empy dict
    SequenceModelConfig(
        async_event_groups={}
    )
    # test correct usage possibilities
    SequenceModelConfig(
        async_event_groups={
            "job_1": {},
            "job_2": {
                "event_1": {},
                "event_2": {"event_3": "group_1"}
            }
        }
    )
    # test incorrect usage possibilities
    with pytest.raises(ValidationError):
        SequenceModelConfig(
            async_event_groups={
                "job_1": 1,
            }
        )
    with pytest.raises(ValidationError):
        SequenceModelConfig(
            async_event_groups={
                "job_1": {
                    "event_1": 1,
                }
            }
        )
    with pytest.raises(ValidationError):
        SequenceModelConfig(
            async_event_groups={
                "job_1": {
                    "event_1": {
                        "event_2": 1
                    }
                }
            }
        )
