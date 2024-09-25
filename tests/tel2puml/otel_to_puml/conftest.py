"""Fixtures for testing otel_to_puml module"""

import yaml
from typing import Any

import pytest


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
                    time_buffer: 30
            data_sources:
                json:
                    dirpath: /path/to/json/directory
                    filepath: /path/to/json/file.json
                    data_location: resource_spans
                    header:
                        paths: [resource:attributes, scope_spans::scope:name]
                    span_mapping:
                        spans:
                            key_paths: [scope_spans::spans]
                    field_mapping:
                        job_name:
                            key_paths: [HEADER:resource:attributes::key,
                            HEADER:scope_spans::scope:name]
                            key_value: [service.name, null]
                            value_paths: [value:Value:StringValue, null]
                            value_type: string
                        job_id:
                            key_paths: [job_id]
                            value_type: string
                        event_type:
                            key_paths: [attributes::key, attributes::key]
                            key_value: [coral.namespace, http.status_code]
                            value_paths: [
                            value:Value:StringValue,
                            value:Value:IntValue]
                            value_type: string
                        event_id:
                            key_paths: [span_id]
                            value_type: string
                        start_timestamp:
                            key_paths: [start_time_unix_nano]
                            value_type: unix_nano
                        end_timestamp:
                            key_paths: [end_time_unix_nano]
                            value_type: unix_nano
                        application_name:
                            key_paths: [
                            attributes::key,
                            HEADER:resource:attributes::key]
                            key_value: [coral.service, service.version]
                            value_paths: [
                            value:Value:StringValue,
                            value:Value:StringValue]
                            value_type: string
                        parent_event_id:
                            key_paths: [parent_span_id]
                            value_type: string
                        child_event_ids:
                            key_paths: [child_span_ids]
                            value_type: string
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
                                        "key": "coral.operation",
                                        "value": {
                                            "Value": {
                                                "StringValue": "jCWhAvRzcM"
                                            }
                                        },
                                    },
                                    {
                                        "key": "coral.service",
                                        "value": {
                                            "Value": {
                                                "StringValue": "Processor"
                                            }
                                        },
                                    },
                                    {
                                        "key": "coral.namespace",
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
                                        "key": "coral.operation",
                                        "value": {
                                            "Value": {
                                                "StringValue": "cVh8nOperation"
                                            }
                                        },
                                    },
                                    {
                                        "key": "coral.service",
                                        "value": {
                                            "Value": {"StringValue": "Handler"}
                                        },
                                    },
                                    {
                                        "key": "coral.namespace",
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
