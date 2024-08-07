"""Fixtures for testing find_unique_graphs module"""

import pytest
from unittest.mock import mock_open, patch
from typing import Generator, Any


@pytest.fixture
def mock_yaml_config_string() -> str:
    return """
            ingest_data:
                data_source: json
            data_sources:
                json:
                    dirpath: /path/to/json/directory
                    filepath: /path/to/json/file.json
            """


@pytest.fixture
def mock_yaml_config(
    mock_yaml_config_string: str,
) -> Generator[None, None, None]:
    with patch("builtins.open", mock_open(read_data=mock_yaml_config_string)):
        yield


@pytest.fixture
def mock_path_exists() -> Generator[None, None, None]:
    with patch("os.path.isdir", return_value=True), patch(
        "os.path.isfile", return_value=True
    ):
        yield


@pytest.fixture
def mock_filepath_in_dir() -> Generator[None, None, None]:
    with patch(
        "os.listdir",
        return_value=["/mock/dir/file1.json"],
    ):
        yield


@pytest.fixture
def mock_json_data() -> list[dict[str, Any]]:
    return [
        {
            "job_name": "job1",
            "job_id": "id1",
            "event_type": "type1",
            "event_id": "event1",
            "start_timestamp": "2023-01-01T00:00:00",
            "end_timestamp": "2023-01-01T00:01:00",
            "application_name": "app1",
            "parent_event_id": None,
            "child_event_ids": ["event2"],
        },
        {
            "job_name": "job1",
            "job_id": "id2",
            "event_type": "type2",
            "event_id": "event2",
            "start_timestamp": "2023-01-01T00:02:00",
            "end_timestamp": "2023-01-01T00:03:00",
            "application_name": "app1",
            "parent_event_id": "event1",
            "child_event_ids": None,
        },
    ]


@pytest.fixture
def mock_file_list() -> list[str]:
    return ["/mock/dir/file1.json", "/mock/dir/file2.json"]
