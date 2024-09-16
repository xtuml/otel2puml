"""Fixtures for testing find_unique_graphs module"""

import yaml
import json
import copy
from pathlib import Path
from unittest.mock import patch
from typing import Generator, Any

import pytest
from sqlalchemy.sql.schema import Table
import sqlalchemy as sa

from tel2puml.otel_to_pv.data_holders.sql_data_holder.data_model import (
    NodeModel,
)
from tel2puml.otel_to_pv.otel_to_pv_types import OTelEvent
from tel2puml.otel_to_pv.data_holders.sql_data_holder.sql_dataholder import (
    SQLDataHolder,
    intialise_temp_table_for_root_nodes,
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
                            key_paths: [
                            trace_id,
                            resource:attributes::key:other_key]
                            key_value: [null, test_string]
                            value_paths: [null, value:Value:StringValue]
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
def mock_path_exists() -> Generator[None, None, None]:
    """Mocks os.path.isdir and os.path.isfile functions, returning True for
    both."""
    with patch("os.path.isdir", return_value=True), patch(
        "os.path.isfile", return_value=True
    ):
        yield


@pytest.fixture
def mock_filepath_in_dir() -> Generator[None, None, None]:
    """Mocks os.listdir function, returning a custom list containing a
    json file."""
    with patch(
        "os.listdir",
        return_value=["/mock/dir/file1.json"],
    ):
        yield


@pytest.fixture
def mock_file_list() -> list[str]:
    """Mocks a list of json"""
    return ["/mock/dir/file1.json", "/mock/dir/file2.json"]


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
                                "child_span_ids": ["child1", "child2"],
                                "flags": 339,
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
                                "child_span_ids": ["child3"],
                                "flags": 395,
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
            },
            {
                "resource": {
                    "attributes": [
                        {
                            "key": "service.name",
                            "value": {"Value": {"StringValue": "Backend"}},
                        },
                        {
                            "key": "service.version",
                            "value": {"Value": {"StringValue": "1.2"}},
                        },
                    ]
                },
                "scope_spans": [
                    {
                        "scope": {"name": "TestJob"},
                        "spans": [
                            {
                                "trace_id": "trace003",
                                "span_id": "span003",
                                "parent_span_id": None,
                                "child_span_ids": [],
                                "flags": 647,
                                "name": "/delete",
                                "kind": 2,
                                "start_time_unix_nano": 1723544154817766912,
                                "end_time_unix_nano": 1723544154818599863,
                                "attributes": [
                                    {
                                        "key": "http.method",
                                        "value": {
                                            "Value": {"StringValue": "PUT"}
                                        },
                                    },
                                    {"cloudProvider": "AWS"},
                                    {
                                        "key": "http.target",
                                        "value": {
                                            "Value": {"StringValue": "/a9HDI"}
                                        },
                                    },
                                    {
                                        "key": "http.host",
                                        "value": {
                                            "Value": {
                                                "stringValue": "Abmo.com:2667"
                                            }
                                        },
                                    },
                                    {
                                        "key": "coral.operation",
                                        "value": {
                                            "Value": {
                                                "StringValue": "2lAmnOperation"
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
                                                "StringValue": "com.a58.GFkzZ"
                                            }
                                        },
                                    },
                                    {
                                        "key": "http.status_code",
                                        "value": {"Value": {"IntValue": 201}},
                                    },
                                ],
                                "status": {},
                                "resource": {
                                    "attributes": [
                                        {
                                            "key": "service.name",
                                            "value": {
                                                "Value": {
                                                    "StringValue": "D-Service"
                                                }
                                            },
                                        },
                                        {
                                            "key": "service.version",
                                            "value": {
                                                "Value": {"StringValue": "2.1"}
                                            },
                                        },
                                        {
                                            "key": {
                                                "other_key": "test_string"
                                            },
                                            "value": {
                                                "Value": {"StringValue": "2.7"}
                                            },
                                        },
                                    ]
                                },
                                "scope": {"name": "cds-o1MFqb"},
                            },
                            {
                                "trace_id": "trace004",
                                "span_id": "span004",
                                "parent_span_id": "span003",
                                "child_span_ids": ["child5"],
                                "flags": 517,
                                "name": "/read",
                                "kind": 3,
                                "start_time_unix_nano": 1723544154817793024,
                                "end_time_unix_nano": 1723544154818380443,
                                "attributes": [
                                    {
                                        "key": "http.method",
                                        "value": {
                                            "Value": {"StringValue": "PUT"}
                                        },
                                    },
                                    {"cloudProvider": "Azure"},
                                    {
                                        "key": "http.target",
                                        "value": {
                                            "Value": {"StringValue": "/KLqSb"}
                                        },
                                    },
                                    {
                                        "key": "http.host",
                                        "value": {
                                            "Value": {
                                                "stringValue": "C1DQc.com:6089"
                                            }
                                        },
                                    },
                                    {
                                        "key": "coral.operation",
                                        "value": {
                                            "Value": {
                                                "StringValue": "81DznOperation"
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
                                                "StringValue": "com.67Q.AS8pJ"
                                            }
                                        },
                                    },
                                    {
                                        "key": "http.status_code",
                                        "value": {"Value": {"IntValue": 201}},
                                    },
                                ],
                                "status": {},
                                "resource": {
                                    "attributes": [
                                        {
                                            "key": "service.name",
                                            "value": {
                                                "Value": {
                                                    "StringValue": "fx-Service"
                                                }
                                            },
                                        },
                                        {
                                            "key": "service.version",
                                            "value": {
                                                "Value": {"StringValue": "2.8"}
                                            },
                                        },
                                        {
                                            "key": {
                                                "other_key": "test_string"
                                            },
                                            "value": {
                                                "Value": {"StringValue": "1.3"}
                                            },
                                        },
                                    ]
                                },
                                "scope": {"name": "cds-XvO4xV"},
                            },
                        ],
                    }
                ],
            },
        ]
    }


@pytest.fixture
def mock_json_data_without_list() -> dict[str, Any]:
    """Mock OTel JSON data without spans being in a list."""
    return {
        "resource_spans": {
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
                            "child_span_ids": ["child1", "child2"],
                            "flags": 339,
                            "name": "/delete",
                            "kind": 5,
                            "start_time_unix_nano": 1723544132228102912,
                            "end_time_unix_nano": 1723544132228219285,
                            "attributes": [
                                {
                                    "key": "http.method",
                                    "value": {"Value": {"StringValue": "GET"}},
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
                                            "stringValue": "GqsdJsK.com:7167"
                                        }
                                    },
                                },
                                {
                                    "key": "coral.operation",
                                    "value": {
                                        "Value": {
                                            "StringValue": "jCWhcMOperation"
                                        }
                                    },
                                },
                                {
                                    "key": "coral.service",
                                    "value": {
                                        "Value": {"StringValue": "Processor"}
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
                                                "StringValue": "Ovm04-Service"
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
                                        "key": {"other_key": "test_string"},
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
                            "child_span_ids": ["child3"],
                            "flags": 395,
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
                                            "stringValue": "lhD61AC.com:7631"
                                        }
                                    },
                                },
                                {
                                    "key": "coral.operation",
                                    "value": {
                                        "Value": {
                                            "StringValue": "cVh8f6JOperation"
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
                                                "StringValue": "Ihj-Service"
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
                                        "key": {"other_key": "test_string"},
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
        },
    }


@pytest.fixture
def mock_otel_event() -> OTelEvent:
    """Mocks an OTelEvent object."""

    return OTelEvent(
        job_name="test_job",
        job_id="123",
        event_type="test_event",
        event_id="456",
        start_timestamp=1723544154817793024,
        end_timestamp=1723544154817993024,
        application_name="test_app",
        parent_event_id="789",
        child_event_ids=["101", "102"],
    )


@pytest.fixture
def mock_sql_config() -> SQLDataHolderConfig:
    """Mocks config for SQLDataHolder."""

    return SQLDataHolderConfig(
        db_uri="sqlite:///:memory:", batch_size=10, time_buffer=30
    )


@pytest.fixture
def mock_otel_events() -> list[OTelEvent]:
    """Mocks a list of 10 OTelEvents"""

    otel_events = []
    prev_parent_event_id = None
    start_timestamp = 1695639486119918080
    end_timestamp = 1695639486119918084
    for index in range(10):
        event_id = index
        next_event_id = index + 1
        otel_events.append(
            OTelEvent(
                job_name="test_name",
                job_id="test_id",
                event_type=f"event_type_{index}",
                event_id=str(event_id),
                start_timestamp=start_timestamp + index,
                end_timestamp=end_timestamp + index,
                application_name="test_application_name",
                parent_event_id=str(prev_parent_event_id),
                child_event_ids=[str(next_event_id)],
            )
        )
        prev_parent_event_id = event_id

    return otel_events


@pytest.fixture
def mock_temp_dir_with_json_files(tmp_path: Path) -> Path:
    """
    Mock a temporary directory with 2 json files.

    :param tmp_path: Pytest fixture providing a temporary directory path
    :type tmp_path: :class:`pathlib.Path`
    :return: Path to the created temporary directory containing JSON files
    :rtype: `Path`
    """

    # Create temp directory
    temp_dir = tmp_path / "temp_dir"
    temp_dir.mkdir()

    no_files = 2
    no_resouce_spans = 2
    no_spans = 2

    # Create 2 json files in the temp directory
    for file_no in range(no_files):
        json_file = temp_dir / f"json_file_{file_no}.json"

        with json_file.open("w") as f:
            json.dump(
                _generate_resource_spans(file_no, no_resouce_spans, no_spans),
                f,
            )

    return temp_dir


def _create_span(
    file_no: int, i: int, j: int, no_spans: int
) -> dict[str, Any]:
    """
    Create a single span dictionary with various attributes.

    :param file_no: The file number
    :type file_no: `int`
    :param i: The resource span index
    :type i: `int`
    :param j: The span index within the resource span
    :type j: `int`
    :param no_spans: The total number of spans in the resource span
    :type no_spans: `int`
    :return: A dictionary representing a span
    :rtype: `dict`[`str`, `Any`]
    """
    return {
        "trace_id": f"{file_no}_trace_id_{i}",
        "span_id": f"{file_no}_span_{i}_{j}",
        "parent_span_id": f"{file_no}_span_{i}_{j-1}" if j > 0 else None,
        "child_span_ids": (
            [f"{file_no}_span_{i}_{j+1}"] if j < no_spans - 1 else []
        ),
        "name": "/update",
        "start_time_unix_nano": 1723544132228288000,
        "end_time_unix_nano": 1723544132229038947,
        "attributes": [
            {
                "key": "http.method",
                "value": {"Value": {"StringValue": f"method_{i}_{j}"}},
            },
            {
                "key": "http.target",
                "value": {"Value": {"StringValue": f"target_{i}_{j}"}},
            },
            {
                "key": "http.host",
                "value": {"Value": {"StringValue": f"host_{i}_{j}"}},
            },
            {
                "key": "coral.operation",
                "value": {"Value": {"StringValue": f"operation_{i}_{j}"}},
            },
            {
                "key": "coral.service",
                "value": {"Value": {"StringValue": f"service_{i}_{j}"}},
            },
            {
                "key": "coral.namespace",
                "value": {"Value": {"StringValue": f"namespace_{i}_{j}"}},
            },
            {"key": "http.status_code", "value": {"Value": {"IntValue": 200}}},
        ],
        "status": {},
        "resource": {
            "attributes": [
                {
                    "key": "service.name",
                    "value": {"Value": {"StringValue": f"name_{i}_{j}"}},
                },
                {
                    "key": "service.version",
                    "value": {"Value": {"StringValue": f"version_{i}_{j}"}},
                },
                {
                    "key": {"other_key": "test_string"},
                    "value": {"Value": {"StringValue": "4.8"}},
                },
            ]
        },
        "scope": {"name": f"{file_no}_name_{j}"},
    }


def _create_header(
    service_name: str, service_version: str
) -> list[dict[str, Any]]:
    """
    Create a header list containing service name and version.

    :param service_name: The name of the service
    :type service_name: `str`
    :param service_version: The version of the service
    :type service_version: `str`
    :return: A list of dictionaries representing the header
    :rtype: `list`[`dict`[`str`, `Any`]]
    """
    return [
        {
            "key": "service.name",
            "value": {"Value": {"StringValue": service_name}},
        },
        {
            "key": "service.version",
            "value": {"Value": {"StringValue": service_version}},
        },
    ]


def _create_resource_span(
    header: list[dict[str, Any]], spans: list[dict[str, Any]]
) -> dict[str, Any]:
    """
    Combine a header and a list of spans into a resource span dictionary.

    :param header: The header information for the resource span
    :type header: `list`[`dict`[`str`, `Any`]]
    :param spans: A list of span dictionaries
    :type spans: `list`[`dict`[`str`, `Any`]]
    :return: A dictionary representing a resource span
    :rtype: `dict`[`str`, `Any`]
    """
    return {
        "resource": {"attributes": header},
        "scope_spans": [
            {
                "scope": {"name": "TestJob"},
                "spans": spans,
            }
        ],
    }


def _generate_resource_spans(
    file_no: int, no_resource_spans: int, no_spans: int
) -> dict[str, Any]:
    """
    Combine a header and a list of spans into a resource span dictionary.

    :param header: The header information for the resource span
    :type header: `list`[`dict`[`str`, `Any`]]
    :param spans: A list of span dictionaries
    :type spans: `list`[`dict`[`str`, `Any`]]
    :return: A dictionary representing a resource span
    :rtype: `dict`[`str`, `Any`]
    """
    headers = {
        "service_name": ["Frontend", "Backend", "Cloud", "Docker", "DB"],
        "service_version": ["1.0", "2.0", "3.0", "4.0", "5.0"],
    }
    resource_spans: dict[str, Any] = {"resource_spans": []}

    for i in range(no_resource_spans):
        header = _create_header(
            headers["service_name"][i], headers["service_version"][i]
        )
        spans = []
        for j in range(no_spans):
            span = _create_span(file_no, i, j, no_spans)
            spans.append(span)
        resource_spans["resource_spans"].append(
            _create_resource_span(header, spans)
        )

    return resource_spans


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
def otel_jobs_multiple_job_names(
    otel_jobs: dict[str, list[OTelEvent]],
) -> dict[str, list[OTelEvent]]:
    """Dict of 2x job names with 5 OTelEvents lists."""

    otel_jobs_copy = copy.deepcopy(otel_jobs)
    otel_jobs_updated_name = {}

    for i, otel_events in enumerate(otel_jobs.values()):
        otel_jobs_updated_name[f"{i+5}"] = []
        for j, event in enumerate(reversed(otel_events)):
            event = event._replace(job_name="test_name_1")._replace(
                job_id=f"test_id_{i+5}"
            )._replace(event_id = f"{i+5}_{j}")
            if j == 0:
                event = event._replace(child_event_ids = [f"{i+5}_{j+1}"])
            else:
                event = event._replace(parent_event_id=f"{i+5}_{j-1}")
            otel_jobs_updated_name[f"{i+5}"].append(event)

    updated_otel_jobs = dict(otel_jobs_copy, **otel_jobs_updated_name)

    return updated_otel_jobs


@pytest.fixture
def otel_nodes_from_otel_jobs(
    otel_jobs: dict[str, list[OTelEvent]],
) -> dict[str, NodeModel]:
    """Creates a dict of event id mapped to NodeModel from the otel_jobs
    fixture.
    """
    otel_nodes: dict[str, NodeModel] = {}
    for otel_job in otel_jobs.values():
        for otel_event in otel_job:
            otel_nodes[otel_event.event_id] = NodeModel(
                job_name=otel_event.job_name,
                job_id=otel_event.job_id,
                event_type=otel_event.event_type,
                event_id=otel_event.event_id,
                start_timestamp=otel_event.start_timestamp,
                end_timestamp=otel_event.end_timestamp,
                application_name=otel_event.application_name,
                parent_event_id=otel_event.parent_event_id,
            )
    return otel_nodes


@pytest.fixture
def sql_data_holder_with_otel_jobs(
    otel_jobs: dict[str, list[OTelEvent]],
    mock_sql_config: SQLDataHolderConfig,
) -> Generator[SQLDataHolder, Any, None]:
    """Creates a SQLDataHolder object with 5 jobs, each with 2 events."""
    mock_sql_config["time_buffer"] = 1
    mock_sql_config["batch_size"] = 2
    sql_data_holder = SQLDataHolder(
        config=mock_sql_config,
    )
    sql_data_holder.min_timestamp = 10**12
    sql_data_holder.max_timestamp = 2 * 10**12
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
def sql_data_holder_with_multiple_otel_job_names(
    otel_jobs_multiple_job_names: dict[str, list[OTelEvent]],
    mock_sql_config: SQLDataHolderConfig,
) -> Generator[SQLDataHolder, Any, None]:
    """Creates a SQLDataHolder object with 10 jobs consisting of 2 job names,
    each with 2 events."""
    mock_sql_config["time_buffer"] = 1
    mock_sql_config["batch_size"] = 2
    sql_data_holder = SQLDataHolder(
        config=mock_sql_config,
    )
    sql_data_holder.min_timestamp = 10**12
    sql_data_holder.max_timestamp = 2 * 10**12
    with sql_data_holder:
        for otel_events in otel_jobs_multiple_job_names.values():
            for otel_event in otel_events:
                sql_data_holder.save_data(otel_event)
    yield sql_data_holder
    with sql_data_holder.session as session:
        if sa.inspect(sql_data_holder.engine).has_table("temp_root_nodes"):
            session.execute(sa.text("DROP TABLE temp_root_nodes"))
    sql_data_holder.base.metadata._remove_table("temp_root_nodes", None)


@pytest.fixture
def sql_data_holder_with_shuffled_otel_events(
    otel_jobs: dict[str, list[OTelEvent]],
    mock_sql_config: SQLDataHolderConfig,
) -> Generator[SQLDataHolder, Any, None]:
    """Creates a SQLDataHolder object with 5 jobs, each with 2 events."""
    mock_sql_config["time_buffer"] = 1
    sql_data_holder = SQLDataHolder(
        config=mock_sql_config,
    )
    sql_data_holder.min_timestamp = 10**12
    sql_data_holder.max_timestamp = 2 * 10**12
    with sql_data_holder:
        shuffled_tuples = [
            ("1", 0),
            ("0", 0),
            ("3", 1),
            ("0", 1),
            ("1", 1),
            ("2", 1),
            ("2", 0),
            ("3", 0),
            ("4", 1),
            ("4", 0),
        ]
        for shuffled_tuple in shuffled_tuples:
            sql_data_holder.save_data(
                otel_jobs[shuffled_tuple[0]][shuffled_tuple[1]]
            )
    yield sql_data_holder
    with sql_data_holder.session as session:
        if sa.inspect(sql_data_holder.engine).has_table("temp_root_nodes"):
            session.execute(sa.text("DROP TABLE temp_root_nodes"))
    sql_data_holder.base.metadata._remove_table("temp_root_nodes", None)


@pytest.fixture
def table_of_root_node_event_ids(
    sql_data_holder_with_otel_jobs: SQLDataHolder,
) -> Table:
    """Creates a temporary table of root nodes."""
    table = intialise_temp_table_for_root_nodes(sql_data_holder_with_otel_jobs)
    with sql_data_holder_with_otel_jobs.session as session:
        session.execute(
            table.insert(),
            [{"event_id": f"{i}_0"} for i in range(5)],
        )
        session.commit()
    return table


@pytest.fixture
def otel_linked_nodes_and_nodes() -> (
    tuple[dict[str, list[NodeModel]], dict[int, NodeModel]]
):
    """Dict of 5 OTelEvents lists."""
    nodes = {
        i: NodeModel(
            job_name="test_name",
            job_id=f"{i}",
            event_type=f"{i}",
            event_id=f"{i}",
            start_timestamp=10**12 + 10**10 * i,
            end_timestamp=10**12 + 10**10 * i + 10**10,
            application_name="test_application_name",
            parent_event_id=None,
        )
        for i in range(6)
    }
    linked_nodes = {
        "0": [nodes[1], nodes[5]],
        "1": [nodes[2], nodes[3], nodes[4]],
    }
    return linked_nodes, nodes


@pytest.fixture
def otel_nodes_under_separate_job_name() -> list[NodeModel]:
    """Creates a list of 5 nodes, each from a different job."""
    nodes = [
        NodeModel(
            job_name="test_name_2",
            job_id=f"{i}{j}",
            event_type=f"{i}",
            event_id=f"{i}{j}",
            start_timestamp=10**12 + 10**11,
            end_timestamp=10**12 + 2 * 10**11,
            application_name="test_application_name",
            parent_event_id=None,
        )
        for i in range(5)
        for j in range(2)
    ]
    # add one outside the time window in tests to see it is not included
    nodes.append(
        NodeModel(
            job_name="test_name_2",
            job_id="xvgyt",
            event_type="xvgyt",
            event_id="xvgyt",
            start_timestamp=10**12,
            end_timestamp=10**12 + 10**10,
            application_name="test_application_name",
            parent_event_id=None,
        )
    )
    return nodes


@pytest.fixture
def sql_data_holder_extended(
    sql_data_holder_with_otel_jobs: SQLDataHolder,
    otel_nodes_under_separate_job_name: list[NodeModel],
) -> SQLDataHolder:
    """Creates a SQLDataHolder object with 5 jobs, each with 2 events."""

    with sql_data_holder_with_otel_jobs.session as session:
        session.add_all(
            otel_node for otel_node in otel_nodes_under_separate_job_name
        )
        session.commit()
    return sql_data_holder_with_otel_jobs


@pytest.fixture
def otel_simple_linked_nodes_and_nodes() -> (
    tuple[dict[str, list[NodeModel]], dict[str, NodeModel]]
):
    """Dict of 4 nodes, 2 nodes per job"""
    nodes = {
        f"{i}_{j}": NodeModel(
            job_name="test_name",
            job_id=f"{i}",
            event_type=f"{i * 2 + j}",
            event_id=f"{i}_{j}",
            start_timestamp=10**12 + 10**10 * j,
            end_timestamp=10**12 + 10**10 * j + 10**10,
            application_name="test_application_name",
            parent_event_id=None,
        )
        for i in range(2)
        for j in range(2)
    }
    linked_nodes = {
        "0_0": [nodes["0_1"]],
        "1_0": [nodes["1_1"]],
    }
    return linked_nodes, nodes
