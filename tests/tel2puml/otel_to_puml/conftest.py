"""Fixtures for testing otel_to_puml module"""

import yaml
from typing import Any, Generator

import pytest
import sqlalchemy as sa

from tel2puml.otel_to_pv.otel_to_pv_types import OTelEvent
from tel2puml.otel_to_pv.data_holders.sql_data_holder.sql_dataholder import (
    SQLDataHolder,
)
from tel2puml.otel_to_pv.config import SQLDataHolderConfig


@pytest.fixture
def mock_yaml_config_string() -> str:
    """String to mock yaml config file."""
    return """
            ingest_data:
                data_source: json
                data_holder: sql
            data_holders:
                sql:
                    db_uri: 'sqlite:///:memory:'
                    batch_size: 5
                    time_buffer: 0
            data_sources:
                json:
                    dirpath: /path/to/json/directory
                    filepath: /path/to/json/file.json
                    json_per_line: false
                    field_mapping:
                        job_name:
                            key_paths: [
                            "resource_spans.[].resource.attributes.[].key",
                            "resource_spans.[].scope_spans.[].scope.name"]
                            key_value: ["service.name", null]
                            value_paths: ["value.Value.StringValue", null]
                            value_type: string
                        job_id:
                            key_paths: [
                            "resource_spans.[].scope_spans.[].spans.[].job_id"]
                            value_type: string
                        event_type:
                            key_paths: [
                            "resource_spans.[].scope_spans.[].spans.[].attributes.[].key",
                            "resource_spans.[].scope_spans.[].spans.[].attributes.[].key"]
                            key_value: [app.namespace, http.status_code]
                            value_paths: [
                            value.Value.StringValue,
                            value.Value.IntValue]
                            value_type: string
                        event_id:
                            key_paths: [
                                "resource_spans.[].scope_spans.[].spans.[].span_id"
                            ]
                            value_type: string
                        start_timestamp:
                            key_paths: [
                            "resource_spans.[].scope_spans.[].spans.[].start_time_unix_nano"]
                            value_type: string
                        end_timestamp:
                            key_paths: [
                            "resource_spans.[].scope_spans.[].spans.[].end_time_unix_nano"]
                            value_type: string
                        application_name:
                            key_paths: [
                            "resource_spans.[].scope_spans.[].spans.[].attributes.[].key",
                            "resource_spans.[].resource.attributes.[].key"]
                            key_value: [app.service, service.version]
                            value_paths: [
                            value.Value.StringValue,
                            value.Value.StringValue]
                            value_type: string
                        parent_event_id:
                            key_paths: [
                            "resource_spans.[].scope_spans.[].spans.[].parent_span_id"]
                            value_type: string
                        child_event_ids:
                            key_paths: [
                            "resource_spans.[].scope_spans.[].spans.[].child_span_ids"]
                            value_type: array
            """


@pytest.fixture
def mock_yaml_config_dict(mock_yaml_config_string: str) -> dict[str, Any]:
    """Mocks a dict when reading the yaml config."""
    config_dict: dict[str, Any] = yaml.safe_load(mock_yaml_config_string)
    return config_dict


@pytest.fixture
def mock_json_data() -> dict[str, Any]:
    """Mock OTel JSON data."""
    return {
        "resource_spans": [
            {
                "resource": {
                    "attributes": [
                        {
                            "key": "service.name",
                            "value": {"Value": {"StringValue": "Frontend"}},
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
                                "trace_id": "trace001",
                                "span_id": "span001",
                                "parent_span_id": None,
                                "child_span_ids": ["span002"],
                                "job_id": "job_A",
                                "name": "/delete",
                                "kind": 5,
                                "start_time_unix_nano": 1723544132228102912,
                                "end_time_unix_nano": 1723544132228219285,
                                "attributes": [
                                    {
                                        "key": "http.method",
                                        "value": {
                                            "Value": {"StringValue": "GET"}
                                        },
                                    },
                                    {"cloudProvider": "Azure"},
                                    {
                                        "key": "http.target",
                                        "value": {
                                            "Value": {"StringValue": "/XNJJo"}
                                        },
                                    },
                                    {
                                        "key": "http.host",
                                        "value": {
                                            "Value": {
                                                "stringValue": "GqsdsjtJsK.com"
                                            }
                                        },
                                    },
                                    {
                                        "key": "app.operation",
                                        "value": {
                                            "Value": {
                                                "StringValue": "jCWhAvRzcM"
                                            }
                                        },
                                    },
                                    {
                                        "key": "app.service",
                                        "value": {
                                            "Value": {
                                                "StringValue": "Processor"
                                            }
                                        },
                                    },
                                    {
                                        "key": "app.namespace",
                                        "value": {
                                            "Value": {
                                                "StringValue": "com.T2h.366Yx"
                                            }
                                        },
                                    },
                                    {
                                        "key": "http.status_code",
                                        "value": {"Value": {"IntValue": 500}},
                                    },
                                ],
                                "status": {},
                                "resource": {
                                    "attributes": [
                                        {
                                            "key": "service.name",
                                            "value": {
                                                "Value": {
                                                    "StringValue": "OvATmm04"
                                                }
                                            },
                                        },
                                        {
                                            "key": "service.version",
                                            "value": {
                                                "Value": {"StringValue": "1.2"}
                                            },
                                        },
                                        {
                                            "key": {
                                                "other_key": "test_string"
                                            },
                                            "value": {
                                                "Value": {"StringValue": "4.8"}
                                            },
                                        },
                                    ]
                                },
                                "scope": {"name": "cds-T5gHfy"},
                            },
                            {
                                "trace_id": "trace002",
                                "span_id": "span002",
                                "parent_span_id": "span001",
                                "child_span_ids": [],
                                "job_id": "job_A",
                                "name": "/update",
                                "kind": 4,
                                "start_time_unix_nano": 1723544132228288000,
                                "end_time_unix_nano": 1723544132229038947,
                                "attributes": [
                                    {
                                        "key": "http.method",
                                        "value": {
                                            "Value": {"StringValue": "DELETE"}
                                        },
                                    },
                                    {"cloudProvider": "AWS"},
                                    {
                                        "key": "http.target",
                                        "value": {
                                            "Value": {"StringValue": "/Ze2bE"}
                                        },
                                    },
                                    {
                                        "key": "http.host",
                                        "value": {
                                            "Value": {
                                                "stringValue": "lhD6.com:7631"
                                            }
                                        },
                                    },
                                    {
                                        "key": "app.operation",
                                        "value": {
                                            "Value": {
                                                "StringValue": "cVh8nOperation"
                                            }
                                        },
                                    },
                                    {
                                        "key": "app.service",
                                        "value": {
                                            "Value": {"StringValue": "Handler"}
                                        },
                                    },
                                    {
                                        "key": "app.namespace",
                                        "value": {
                                            "Value": {
                                                "StringValue": "com.C36.9ETRp"
                                            }
                                        },
                                    },
                                    {
                                        "key": "http.status_code",
                                        "value": {"Value": {"IntValue": 401}},
                                    },
                                ],
                                "status": {},
                                "resource": {
                                    "attributes": [
                                        {
                                            "key": "service.name",
                                            "value": {
                                                "Value": {
                                                    "StringValue": "Ih-Service"
                                                }
                                            },
                                        },
                                        {
                                            "key": "service.version",
                                            "value": {
                                                "Value": {"StringValue": "2.9"}
                                            },
                                        },
                                        {
                                            "key": {
                                                "other_key": "test_string"
                                            },
                                            "value": {
                                                "Value": {"StringValue": "2.0"}
                                            },
                                        },
                                    ]
                                },
                                "scope": {"name": "cds-NgdScW"},
                            },
                        ],
                    }
                ],
            }
        ]
    }


@pytest.fixture
def otel_jobs() -> dict[str, list[OTelEvent]]:
    """Dict of 5 OTelEvents lists."""
    timestamp_choices = [
        tuple(10**12 + boundary for boundary in addition)
        for addition in [
            (0, 3 * 10**10),
            (10**11, 2 * 10**11),
            (57 * 10**10, 60 * 10**10),
        ]
    ]
    cases = [
        (timestamp_choices[0], timestamp_choices[0]),
        (timestamp_choices[0], timestamp_choices[1]),
        (timestamp_choices[1], timestamp_choices[1]),
        (timestamp_choices[1], timestamp_choices[2]),
        (timestamp_choices[2], timestamp_choices[2]),
    ]

    otel_jobs: dict[str, list[OTelEvent]] = {}
    for i, case in enumerate(cases):
        prev_parent_event_id = None
        otel_jobs[f"{i}"] = []
        for j, timestamps in enumerate(reversed(case)):
            event_id = f"{i}_{j}"
            next_event_id = [f"{i}_{j+1}"] if j < 1 else []
            otel_jobs[f"{i}"].append(
                OTelEvent(
                    job_name="test_name",
                    job_id=f"test_id_{i}",
                    event_type=f"event_type_{j}",
                    event_id=event_id,
                    start_timestamp=timestamps[0],
                    end_timestamp=timestamps[1],
                    application_name="test_application_name",
                    parent_event_id=prev_parent_event_id,
                    child_event_ids=next_event_id,
                )
            )
            prev_parent_event_id = event_id
        otel_jobs[f"{i}"] = list(reversed(otel_jobs[f"{i}"]))
    return otel_jobs


@pytest.fixture
def mock_sql_config() -> SQLDataHolderConfig:
    """Mocks config for SQLDataHolder."""

    return SQLDataHolderConfig(
        db_uri="sqlite:///:memory:", batch_size=10, time_buffer=30
    )


@pytest.fixture
def sql_data_holder_with_otel_jobs(
    otel_jobs: dict[str, list[OTelEvent]],
    mock_sql_config: SQLDataHolderConfig,
) -> Generator[SQLDataHolder, Any, None]:
    """Creates a SQLDataHolder object with 5 jobs, each with 2 events."""
    sql_data_holder = SQLDataHolder(
        config=mock_sql_config,
    )
    sql_data_holder.time_buffer = 1
    sql_data_holder.batch_size = 2
    sql_data_holder._min_timestamp = 10**12
    sql_data_holder._max_timestamp = 2 * 10**12
    with sql_data_holder:
        for otel_events in otel_jobs.values():
            for otel_event in otel_events:
                sql_data_holder.save_data(otel_event)
    yield sql_data_holder
    with sql_data_holder.session as session:
        if sa.inspect(sql_data_holder.engine).has_table("temp_root_nodes"):
            session.execute(sa.text("DROP TABLE temp_root_nodes"))
    sql_data_holder.base.metadata._remove_table("temp_root_nodes", None)


@pytest.fixture
def mock_job_json_file() -> list[dict[str, Any]]:
    """Fixture to mock job json file."""
    return [
        {
            "eventId": "evt_001",
            "eventType": "START",
            "jobId": "job_id_001",
            "timestamp": "2024-09-01T07:45:00Z",
            "applicationName": "BackupService",
            "jobName": "TempFilesCleanup",
        },
        {
            "eventId": "evt_002",
            "eventType": "A",
            "jobId": "job_id_001",
            "timestamp": "2024-09-01T08:15:00Z",
            "applicationName": "BackupService",
            "jobName": "TempFilesCleanup",
            "previousEventIds": ["evt_001"],
        },
        {
            "eventId": "evt_003",
            "eventType": "END",
            "jobId": "job_id_001",
            "timestamp": "2024-09-02T09:00:00Z",
            "applicationName": "CleanupService",
            "jobName": "TempFilesCleanup",
            "previousEventIds": ["evt_002"],
        },
    ]


@pytest.fixture
def mock_event_model() -> dict[str, Any]:
    """Fixture to mock event model."""
    return {
        "job_name": "Frontend_TestJob",
        "events": [
            {
                "eventType": "TestEvent",
                "outgoingEventSets": [],
                "incomingEventSets": [
                    [{"eventType": "com.T2h.366Yx_500", "count": 1}]
                ],
            },
            {
                "eventType": "com.T2h.366Yx_500",
                "outgoingEventSets": [
                    [{"eventType": "TestEvent", "count": 1}]
                ],
                "incomingEventSets": [],
            },
        ],
    }


@pytest.fixture
def mock_job_json_file_for_event_model() -> list[dict[str, Any]]:
    """Fixture to mock job json file for event model."""
    return [
        {
            "eventId": "evt_001",
            "eventType": "com.C36.9ETRp_401",
            "jobId": "job_id_001",
            "timestamp": "2024-09-01T07:45:00Z",
            "applicationName": "BackupService",
            "jobName": "Frontend_TestJob",
        },
        {
            "eventId": "evt_002",
            "eventType": "com.T2h.366Yx_500",
            "jobId": "job_id_001",
            "timestamp": "2024-09-01T08:15:00Z",
            "applicationName": "BackupService",
            "jobName": "Frontend_TestJob",
            "previousEventIds": ["evt_001"],
        },
    ]


@pytest.fixture
def expected_model_output() -> list[dict[str, Any]]:
    """Fixture for expected model output."""
    return sorted([
        {
            "eventType": "|||START|||",
            "outgoingEventSets": [
                [{"eventType": "com.C36.9ETRp_401", "count": 1}]
            ],
            "incomingEventSets": [],
        },
        {
            "eventType": "com.C36.9ETRp_401",
            "outgoingEventSets": [
                [{"eventType": "com.T2h.366Yx_500", "count": 1}]
            ],
            "incomingEventSets": [
                [{"eventType": "|||START|||", "count": 1}]
            ],
        },
        {
            "eventType": "com.T2h.366Yx_500",
            "outgoingEventSets": [
                [{"eventType": "TestEvent", "count": 1}]
            ],
            "incomingEventSets": [
                [{"eventType": "com.C36.9ETRp_401", "count": 1}]
            ],
        },
        {
            "eventType": "TestEvent",
            "outgoingEventSets": [],
            "incomingEventSets": [
                [{"eventType": "com.T2h.366Yx_500", "count": 1}]
            ],
        },
    ], key=lambda x: x["eventType"])
