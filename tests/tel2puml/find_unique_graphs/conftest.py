"""Fixtures for testing find_unique_graphs module"""

import pytest
from unittest.mock import mock_open, patch


@pytest.fixture
def mock_yaml_config_string():
    return """
            ingest_data:
                data_source: json
            data_sources:
                json:
                    dirpath: /path/to/json/directory
                    filepath: /path/to/json/file.json
            """


@pytest.fixture
def mock_yaml_config(mock_yaml_config_string):
    with patch("builtins.open", mock_open(read_data=mock_yaml_config_string)):
        yield


@pytest.fixture
def mock_path_exists():
    with patch("os.path.isdir", return_value=True), patch(
        "os.path.isfile", return_value=True
    ):
        yield
