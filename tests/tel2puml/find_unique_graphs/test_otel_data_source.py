"""Tests for otel_data_source module."""

import json
import pytest
from typing import Any

from unittest.mock import mock_open, patch

from tel2puml.find_unique_graphs.otel_ingestion.otel_data_source import (
    JSONDataSource,
)
from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    OTelEvent,
)


class TestOTELDataSource:
    """Tests for OTelDataSource class"""

    @staticmethod
    @pytest.mark.usefixtures(
        "mock_yaml_config", "mock_path_exists", "mock_filepath_in_dir"
    )
    def test_get_yaml_config() -> None:
        """Tests parsing yaml config file"""
        data_source = JSONDataSource()
        assert isinstance(data_source.yaml_config, dict)
        assert data_source.yaml_config["ingest_data"]["data_source"] == "json"

    @staticmethod
    @pytest.mark.usefixtures(
        "mock_yaml_config", "mock_path_exists", "mock_filepath_in_dir"
    )
    def test_set_data_source_valid() -> None:
        """Tests for valid file ext."""
        json_data_source = JSONDataSource()
        assert json_data_source.data_source == "json"

    @staticmethod
    def test_set_data_source_invalid(mock_yaml_config_string: str) -> None:
        """Tests invalid file extension in yaml config."""
        invalid_yaml = mock_yaml_config_string.replace("json", "invalid")
        with patch("builtins.open", mock_open(read_data=invalid_yaml)), patch(
            "os.path.isdir", return_value=True
        ), patch("os.path.isfile", return_value=True):
            with pytest.raises(ValueError, match="is not a valid data source"):
                JSONDataSource()


class TestJSONDataSource:
    """Tests for JSONDataSource class."""

    @staticmethod
    @pytest.mark.usefixtures(
        "mock_yaml_config", "mock_path_exists", "mock_filepath_in_dir"
    )
    def test_set_dirpath_valid() -> None:
        """Tests set_dirpath method."""
        json_data_source = JSONDataSource()
        assert json_data_source.dirpath == "/path/to/json/directory"

    @staticmethod
    @pytest.mark.usefixtures("mock_yaml_config")
    def test_set_dirpath_invalid() -> None:
        """Tests the set_dirpath method with a non-existant directory."""
        with patch("os.path.isdir", return_value=False), patch(
            "os.path.isfile", return_value=True
        ):
            with pytest.raises(ValueError, match="directory does not exist"):
                JSONDataSource()

    @staticmethod
    @pytest.mark.usefixtures(
        "mock_yaml_config", "mock_path_exists", "mock_filepath_in_dir"
    )
    def test_set_filepath_valid() -> None:
        """Tests the set_filepath method."""
        jsond_data_source = JSONDataSource()
        assert jsond_data_source.filepath == "/path/to/json/file.json"

    @staticmethod
    @pytest.mark.usefixtures("mock_yaml_config")
    def test_set_filepath_invalid() -> None:
        """Tests the set_filepath method with an non-existant file."""
        with patch("os.path.isdir", return_value=True), patch(
            "os.path.isfile", return_value=False
        ):
            with pytest.raises(ValueError, match="does not exist"):
                JSONDataSource()

    @staticmethod
    def test_initialisation_no_dirpath_no_filepath(
        mock_yaml_config_string: str,
    ) -> None:
        """Tests error handling for case with no directory or file found."""
        invalid_yaml = mock_yaml_config_string.replace(
            "dirpath: /path/to/json/directory", 'dirpath: ""'
        ).replace("filepath: /path/to/json/file.json", 'filepath: ""')

        with patch("builtins.open", mock_open(read_data=invalid_yaml)), patch(
            "os.path.isdir", return_value=False
        ), patch("os.path.isfile", return_value=False):
            with pytest.raises(
                FileNotFoundError, match="No directory or files found"
            ):
                JSONDataSource()

    @staticmethod
    @pytest.mark.usefixtures(
        "mock_yaml_config", "mock_path_exists", "mock_filepath_in_dir"
    )
    def test_init() -> None:
        """Tests the classes init method."""
        json_data_source = JSONDataSource()
        assert json_data_source.data_source == "json"
        assert json_data_source.dirpath == "/path/to/json/directory"
        assert json_data_source.filepath == "/path/to/json/file.json"

    @staticmethod
    @pytest.mark.usefixtures("mock_path_exists")
    def test_get_file_list_filepath(
        mock_yaml_config_string: str,
    ) -> None:
        """Tests getting the json filepath if directory is not specified."""
        no_dir_path_yaml = mock_yaml_config_string.replace(
            "dirpath: /path/to/json/directory", 'dirpath: ""'
        )
        with patch("builtins.open", mock_open(read_data=no_dir_path_yaml)):
            json_data_source = JSONDataSource()
            assert json_data_source.get_file_list() == [
                "/path/to/json/file.json"
            ]

    @staticmethod
    @pytest.mark.usefixtures("mock_yaml_config", "mock_path_exists")
    def test_get_file_list_dirpath(
        mock_file_list: list[str],
    ) -> None:
        """Tests getting the json filepaths if the directory is specified."""
        with patch(
            "os.listdir",
            return_value=["/mock/dir/file1.json", "/mock/dir/file2.json"],
        ):
            json_data_source = JSONDataSource()
            assert json_data_source.get_file_list() == mock_file_list

    @staticmethod
    @pytest.mark.usefixtures("mock_path_exists")
    def test_parse_json_stream(
        mock_json_data: list[dict[str, Any]],
        mock_yaml_config_string: str,
    ) -> None:
        """Tests parsing a json file."""
        no_dir_path_yaml = mock_yaml_config_string.replace(
            "dirpath: /path/to/json/directory", 'dirpath: ""'
        )
        with patch("builtins.open", mock_open(read_data=no_dir_path_yaml)):
            json_data_source = JSONDataSource()
            mock_file_content = json.dumps(mock_json_data)

            with patch(
                "builtins.open", mock_open(read_data=mock_file_content)
            ):
                events = list(
                    json_data_source.parse_json_stream("mock_file.json")
                )

            assert len(events) == 2
            assert isinstance(events[0], OTelEvent)
            assert events[0].event_id == "event1"
            assert events[1].event_id == "event2"

    @staticmethod
    @pytest.mark.usefixtures(
        "mock_yaml_config", "mock_path_exists", "mock_filepath_in_dir"
    )
    def test_create_otel_object(
        mock_json_data: list[dict[str, Any]],
    ) -> None:
        """Tests creating an OTelEvent object."""
        json_data_source = JSONDataSource()
        otel_event = json_data_source.create_otel_object(mock_json_data[0])

        assert isinstance(otel_event, OTelEvent)
        assert otel_event.job_name == "job1"
        assert otel_event.job_id == "id1"
        assert otel_event.event_type == "type1"
        assert otel_event.event_id == "event1"
        assert otel_event.start_timestamp == "2023-01-01T00:00:00"
        assert otel_event.end_timestamp == "2023-01-01T00:01:00"
        assert otel_event.application_name == "app1"
        assert otel_event.parent_event_id is None
        assert otel_event.child_event_ids == ["event2"]

    @staticmethod
    @pytest.mark.usefixtures("mock_path_exists", "mock_filepath_in_dir")
    def test_iter_next(
        mock_yaml_config_string: str,
        mock_json_data: list[dict[str, Any]],
    ) -> None:
        """Tests the __iter__ method."""
        with patch(
            "builtins.open", mock_open(read_data=mock_yaml_config_string)
        ):
            json_data_source = JSONDataSource()
            mock_file_content = json.dumps(mock_json_data)

            with patch(
                "builtins.open", mock_open(read_data=mock_file_content)
            ):
                events = list(json_data_source)

        assert len(events) == 2
        assert isinstance(events[0], OTelEvent)
        assert events[0].event_id == "event1"
        assert events[1].event_id == "event2"
