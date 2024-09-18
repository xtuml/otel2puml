"""Tests for otel_to_pv types."""

import pytest
from pydantic import ValidationError

from tel2puml.otel_to_pv.otel_to_pv_types import OTelEvent


def test_otel_event() -> None:
    """Test OTelEvent."""
    # test that setting with correct types works does not raise an error
    input_dict = {
        "job_name": "job_name",
        "job_id": "job_id",
        "event_type": "event_type",
        "event_id": "event_id",
        "start_timestamp": 1,
        "end_timestamp": 2,
        "application_name": "application_name",
        "parent_event_id": "parent_event_id",
        "child_event_ids": ["child_event_id"],
    }
    OTelEvent(**input_dict)
    # test that setting with incorrect types raises a validation error
    input_dict = {
        "job_name": 1,
        "job_id": 1,
        "event_type": 1,
        "event_id": 1,
        "start_timestamp": "1",
        "end_timestamp": "2",
        "application_name": 1,
        "parent_event_id": 1,
        "child_event_ids": [1],
    }
    with pytest.raises(ValidationError):
        OTelEvent(**input_dict)
    # test that setting timestamp fields with a type that can be coerced works
    input_dict = {
        "job_name": "job_name",
        "job_id": "job_id",
        "event_type": "event_type",
        "event_id": "event_id",
        "start_timestamp": "1",
        "end_timestamp": "2",
        "application_name": "application_name",
        "parent_event_id": "parent_event_id",
        "child_event_ids": ["child_event_id"],
    }
    OTelEvent(**input_dict)
    # test that setting timestamp fields with a type that cannot be coerced
    # raises a validation error
    input_dict = {
        "job_name": "job_name",
        "job_id": "job_id",
        "event_type": "event_type",
        "event_id": "event_id",
        "start_timestamp": "a",
        "end_timestamp": "b",
        "application_name": "application_name",
        "parent_event_id": "parent_event_id",
        "child_event_ids": ["child_event_id"],
    }
    with pytest.raises(ValidationError):
        OTelEvent(**input_dict)
