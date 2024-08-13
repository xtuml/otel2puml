"""Fixtures for testing find_unique_graphs module"""

import pytest
import yaml
from unittest.mock import mock_open, patch
from typing import Generator, Any


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
                    header_mapping:
                        header:
                            key_paths: [resource:attributes::key, resource:attributes::key]
                            key_value: [service.name, service.version]
                            value_paths: [value:Value:StringValue, value:Value:StringValue]
                            value_type: string
                    span_mapping:
                        spans:
                            key_paths: [scope_spans::spans]
                    field_mapping:
                        job_name:
                            key_paths: [attributes::cloudProvider]
                            value_type: string
                        job_id:
                            key_paths: [trace_id, resource:attributes::key:other_key]
                            key_value: [null, test_string]
                            value_paths: [null, value:Value:StringValue]
                            value_type: string
                        event_type:
                            key_paths: [attributes::key, attributes::key]
                            key_value: [coral.namespace, http.status_code]
                            value_paths: [value:Value:StringValue, value:Value:IntValue]
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
                            key_paths: [attributes::key, resource:attributes::key]
                            key_value: [coral.service, service.version]
                            value_paths: [value:Value:StringValue, value:Value:StringValue]
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
    """Returns a dict to mock a dict when reading the yaml config."""
    return yaml.safe_load(mock_yaml_config_string)


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
                                "trace_id": "B4MQWcR6iByyOq4EMSs5Nn==",
                                "span_id": "F1Vp3ypcQfU==",
                                "parent_span_id": "NzWDkmlAnji==",
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
                                                "stringValue": "GqsdsjtJsK.com:7167"
                                            }
                                        },
                                    },
                                    {
                                        "key": "coral.operation",
                                        "value": {
                                            "Value": {
                                                "StringValue": "jCWhAvRzcMOperation"
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
                                                    "StringValue": "OvATmm04-Service"
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
                                "trace_id": "Js7TGf4OJROjbISB1BvOOb==",
                                "span_id": "Jv6moYFCoLK==",
                                "parent_span_id": "0u4wIXKIZ2t==",
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
                                                "stringValue": "lhD61W2zAC.com:7631"
                                            }
                                        },
                                    },
                                    {
                                        "key": "coral.operation",
                                        "value": {
                                            "Value": {
                                                "StringValue": "cVh8n0sf6JOperation"
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
                                                    "StringValue": "IhjobAPC-Service"
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
                                "trace_id": "ig0YZJI4VfTAXKDZl7Rxf0==",
                                "span_id": "Z6EwUDfGeiG==",
                                "parent_span_id": "JH12Q4s/0C6==",
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
                                                "stringValue": "Abmoyw1N2R.com:2667"
                                            }
                                        },
                                    },
                                    {
                                        "key": "coral.operation",
                                        "value": {
                                            "Value": {
                                                "StringValue": "2lAmnidMXzOperation"
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
                                                    "StringValue": "DpueAKK0-Service"
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
                                "trace_id": "U2xB3xqOvelpIHiS6wDlAb==",
                                "span_id": "SkZoa3pRvr9==",
                                "parent_span_id": "Rm3JfwVgeMq==",
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
                                                "stringValue": "C1nsCFcDQc.com:6089"
                                            }
                                        },
                                    },
                                    {
                                        "key": "coral.operation",
                                        "value": {
                                            "Value": {
                                                "StringValue": "81DTBhHRznOperation"
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
                                                    "StringValue": "fxoOxHYJ-Service"
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
                            "trace_id": "B4MQWcR6iByyOq4EMSs5Nn==",
                            "span_id": "F1Vp3ypcQfU==",
                            "parent_span_id": "NzWDkmlAnji==",
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
                                            "stringValue": "GqsdsjtJsK.com:7167"
                                        }
                                    },
                                },
                                {
                                    "key": "coral.operation",
                                    "value": {
                                        "Value": {
                                            "StringValue": "jCWhAvRzcMOperation"
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
                                                "StringValue": "OvATmm04-Service"
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
                            "trace_id": "Js7TGf4OJROjbISB1BvOOb==",
                            "span_id": "Jv6moYFCoLK==",
                            "parent_span_id": "0u4wIXKIZ2t==",
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
                                            "stringValue": "lhD61W2zAC.com:7631"
                                        }
                                    },
                                },
                                {
                                    "key": "coral.operation",
                                    "value": {
                                        "Value": {
                                            "StringValue": "cVh8n0sf6JOperation"
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
                                                "StringValue": "IhjobAPC-Service"
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
def mock_file_list() -> list[str]:
    """Mocks a list of json"""
    return ["/mock/dir/file1.json", "/mock/dir/file2.json"]
