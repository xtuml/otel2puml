"""Fixtures for test_pv_to_tel"""

import pytest

from tel2puml.tel2puml_types import OtelSpan, PVEvent


sample_pv_event_1 = {
    "jobId": "8077a248-95e9-4687-8d96-e2ca2638cfab",
    "jobName": "simple_sequence",
    "eventType": "A",
    "eventId": "31185642-eee0-4ab4-8aac-43f94a0bb1b7",
    "timestamp": "2023-09-25T10:58:06.059959Z",
    "applicationName": "test_file_simple_sequence",
}

sample_pv_event_2 = {
    "jobId": "8077a248-95e9-4687-8d96-e2ca2638cfab",
    "jobName": "simple_sequence",
    "eventType": "B",
    "eventId": "721897bf-48f4-499d-a7a3-0a8bff783b66",
    "timestamp": "2023-09-25T10:58:06.059993Z",
    "applicationName": "test_file_simple_sequence",
    "previousEventIds": ["31185642-eee0-4ab4-8aac-43f94a0bb1b7"],
}

sample_pv_event_3 = {
    "jobId": "8077a248-95e9-4687-8d96-e2ca2638cfab",
    "jobName": "simple_sequence",
    "eventType": "C",
    "eventId": "91943012-02d4-478c-bcfa-e12c5d6dc880",
    "timestamp": "2023-09-25T10:58:06.060022Z",
    "applicationName": "test_file_simple_sequence",
    "previousEventIds": ["721897bf-48f4-499d-a7a3-0a8bff783b66"],
}

# Expected OtelSpan for testing
expected_otel_span_1 = OtelSpan(
    name="test_file_simple_sequence",
    span_id="31185642-eee0-4ab4-8aac-43f94a0bb1b7",
    parent_span_id=None,
    trace_id="8077a248-95e9-4687-8d96-e2ca2638cfab",
    start_time_unix_nano=1695639486119918080,
    end_time_unix_nano=1695639486119918080,
    attributes=[
        {
            "key": "coral.operation",
            "value": {"Value": {"StringValue": "A"}},
        }
    ],
)

expected_otel_span_2 = OtelSpan(
    name="test_file_simple_sequence",
    span_id="721897bf-48f4-499d-a7a3-0a8bff783b66",
    parent_span_id=["31185642-eee0-4ab4-8aac-43f94a0bb1b7"],
    trace_id="8077a248-95e9-4687-8d96-e2ca2638cfab",
    start_time_unix_nano=1695639486119986176,
    end_time_unix_nano=1695639486119986176,
    attributes=[
        {
            "key": "coral.operation",
            "value": {"Value": {"StringValue": "B"}},
        }
    ],
)

expected_otel_span_3 = OtelSpan(
    name="test_file_simple_sequence",
    span_id="91943012-02d4-478c-bcfa-e12c5d6dc880",
    parent_span_id=["721897bf-48f4-499d-a7a3-0a8bff783b66"],
    trace_id="8077a248-95e9-4687-8d96-e2ca2638cfab",
    start_time_unix_nano=1695639486120044032,
    end_time_unix_nano=1695639486120044032,
    attributes=[
        {
            "key": "coral.operation",
            "value": {"Value": {"StringValue": "C"}},
        }
    ],
)


@pytest.fixture
def sample_pv_events() -> list[PVEvent]:
    """Fixture for pv sample events"""
    return [sample_pv_event_1, sample_pv_event_2, sample_pv_event_3]


@pytest.fixture
def expected_otel_span_events() -> list[OtelSpan]:
    """Fixture for expected otel span events"""
    return [expected_otel_span_1, expected_otel_span_2, expected_otel_span_3]


@pytest.fixture
def expected_otel_json_output_sample_test_1() -> dict[OtelSpan]:
    """Fixture for expected Otel json output"""
    return {
        "resource_spans": [
            {
                "resource": {
                    "attributes": [
                        {
                            "key": "service.name",
                            "value": {"Value": {"StringValue": "TestApp"}},
                        },
                        {
                            "key": "service.version",
                            "value": {"Value": {"StringValue": "1.0"}},
                        },
                    ]
                },
                "scope_spans": [
                    {
                        "scope": {"name": "TestJob"},
                        "spans": [
                            {
                                "name": "test_file_simple_sequence",
                                "span_id": (
                                    "31185642-eee0-4ab4-8aac-43f94a0bb1b7"),
                                "parent_span_id": None,
                                "trace_id": (
                                    "8077a248-95e9-4687-8d96-e2ca2638cfab"),
                                "start_time_unix_nano": 1695639486119918080,
                                "end_time_unix_nano": 1695639486119918080,
                                "attributes": [
                                    {
                                        "key": "coral.operation",
                                        "value": {
                                            "Value": {"StringValue": "A"}
                                        },
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        ]
    }
