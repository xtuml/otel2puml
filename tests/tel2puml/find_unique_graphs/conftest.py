"""Fixtures for testing find_unique_graphs module"""

import pytest
import yaml

from unittest.mock import patch
from typing import Generator, Any

from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    OTelEvent,
    SQLDataHolderConfig,
    NodeModel
)
from tel2puml.find_unique_graphs.otel_ingestion.otel_data_holder import (
    SQLDataHolder,
)


@pytest.fixture
def mock_yaml_config_string() -> str:
    """String to mock yaml config file."""
    return """
            ingest_data:
                data_source: json
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
                            resource:attributes::key]
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
def mock_yaml_config_dict(mock_yaml_config_string: str) -> Any:
    """Returns a dict to mock a dict when reading the yaml config."""
    return yaml.safe_load(mock_yaml_config_string)["data_sources"]["json"]


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
def otel_jobs() -> dict[str, list[OTelEvent]]:
    """Dict of 5 OTelEvents lists."""
    timestamp_choices = [
        tuple(10**12 + boundary for boundary in addition)
        for addition in [
            (0, 3 * 10 ** 10),
            (10 ** 11, 2 * 10 ** 11),
            (57 * 10 ** 10, 60 * 10 ** 10)
        ]
    ]
    cases = [
        (timestamp_choices[0], timestamp_choices[0]),
        (timestamp_choices[0], timestamp_choices[1]),
        (timestamp_choices[1], timestamp_choices[1]),
        (timestamp_choices[1], timestamp_choices[2]),
        (timestamp_choices[2], timestamp_choices[2])
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
def sql_data_holder_with_otel_jobs(
    otel_jobs: dict[str, list[OTelEvent]],
    mock_sql_config: SQLDataHolderConfig
) -> SQLDataHolder:
    mock_sql_config["time_buffer"] = 1
    sql_data_holder = SQLDataHolder(
        config=mock_sql_config,
    )
    for otel_job in otel_jobs.values():
        with sql_data_holder.session as session:
            session.add_all(
                NodeModel(
                    job_name=otel_event.job_name,
                    job_id=otel_event.job_id,
                    event_type=otel_event.event_type,
                    event_id=otel_event.event_id,
                    start_timestamp=otel_event.start_timestamp,
                    end_timestamp=otel_event.end_timestamp,
                    application_name=otel_event.application_name,
                    parent_event_id=otel_event.parent_event_id,
                )
                for otel_event in otel_job
            )
            session.commit()
    return sql_data_holder
