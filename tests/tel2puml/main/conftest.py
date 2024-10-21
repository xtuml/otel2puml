"""Fixtures for testing __main__ module"""

import yaml
from pathlib import Path

import pytest


@pytest.fixture
def mock_yaml_config_file(tmp_path: Path) -> Path:
    """Create a temporary YAML config file."""
    config_content = {
        "ingest_data": {"data_source": "json", "data_holder": "sql"},
        "data_holders": {
            "sql": {
                "db_uri": "sqlite:///:memory:",
                "batch_size": 5,
                "time_buffer": 30,
            }
        },
        "data_sources": {
            "json": {
                "dirpath": "/path/to/json/directory",
                "filepath": "/path/to/json/file.json",
                "json_per_line": False,
                "field_mapping": {
                    "job_name": {
                        "key_paths": [
                            "resource_spans.[].resource.attributes.[].key",
                            "resource_spans.[].scope_spans.[].scope.name",
                        ],
                        "key_value": ["service.name", None],
                        "value_paths": ["value.Value.StringValue", None],
                        "value_type": "string",
                    },
                    "job_id": {
                        "key_paths": [
                            "resource_spans.[].scope_spans.[].spans.[]."
                            "trace_id",
                            "resource_spans.[].scope_spans.[].spans.[]."
                            "resource.attributes.[].key.other_key",
                        ],
                        "key_value": [None, "test_string"],
                        "value_paths": [None, "value.Value.StringValue"],
                        "value_type": "string",
                    },
                    "event_type": {
                        "key_paths": [
                            "resource_spans.[].scope_spans.[].spans.[]."
                            "attributes.[].key",
                            "resource_spans.[].scope_spans.[].spans.[]."
                            "attributes.[].key",
                        ],
                        "key_value": ["app.namespace", "http.status_code"],
                        "value_paths": [
                            "value.Value.StringValue",
                            "value.Value.IntValue",
                        ],
                        "value_type": "string",
                    },
                    "event_id": {
                        "key_paths": [
                            "resource_spans.[].scope_spans.[].spans.[].span_id"
                        ],
                        "value_type": "string",
                    },
                    "start_timestamp": {
                        "key_paths": [
                            "resource_spans.[].scope_spans.[].spans.[]."
                            "start_time_unix_nano"
                        ],
                        "value_type": "string",
                    },
                    "end_timestamp": {
                        "key_paths": [
                            "resource_spans.[].scope_spans.[].spans.[]."
                            "end_time_unix_nano"
                        ],
                        "value_type": "string",
                    },
                    "application_name": {
                        "key_paths": [
                            "resource_spans.[].scope_spans.[].spans.[]."
                            "attributes.[].key",
                            "resource_spans.[].resource.attributes.[].key",
                        ],
                        "key_value": ["app.service", "service.version"],
                        "value_paths": [
                            "value.Value.StringValue",
                            "value.Value.StringValue",
                        ],
                        "value_type": "string",
                    },
                    "parent_event_id": {
                        "key_paths": [
                            "resource_spans.[].scope_spans.[].spans.[]."
                            "parent_span_id"
                        ],
                        "value_type": "string",
                    },
                    "child_event_ids": {
                        "key_paths": [
                            "resource_spans.[].scope_spans.[].spans.[]."
                            "child_span_ids"
                        ],
                        "value_type": "array",
                    },
                },
            }
        },
    }

    config_file = tmp_path / "config.yaml"
    with config_file.open("w") as f:
        yaml.dump(config_content, f)

    return config_file
