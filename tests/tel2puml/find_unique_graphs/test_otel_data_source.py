"""Tests for otel_data_source module."""

import json
import os
import yaml
import pytest
import shutil
from typing import Any
from pytest import FixtureRequest
from pathlib import Path
from unittest.mock import mock_open, patch

from tel2puml.find_unique_graphs.otel_ingestion.otel_data_source import (
    JSONDataSource,
)
from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    JSONDataSourceConfig,
)


class TestJSONDataSource:
    """Tests for JSONDataSource class."""

    @staticmethod
    @pytest.mark.usefixtures("mock_path_exists")
    def test_get_yaml_config(
        mock_yaml_config_dict: JSONDataSourceConfig,
    ) -> None:
        """Tests parsing yaml config file and setting config attribute."""
        json_data_source = JSONDataSource(mock_yaml_config_dict)
        config = json_data_source.config

        # Check if config is a dictionary
        assert isinstance(config, dict)

        # Check main config keys
        expected_keys = {
            "dirpath",
            "filepath",
            "data_location",
            "header_mapping",
            "span_mapping",
            "field_mapping",
        }
        assert set(config.keys()) == expected_keys

        # Check string values
        assert config["dirpath"] == "/path/to/json/directory"
        assert config["filepath"] == "/path/to/json/file.json"
        assert config["data_location"] == "resource_spans"

        # Check expected header keys
        expected_header_keys = {
            "key_paths",
            "key_value",
            "value_paths",
            "value_type",
        }
        assert (
            set(config["header_mapping"]["header"].keys())
            == expected_header_keys
        )

    @staticmethod
    @pytest.mark.usefixtures("mock_path_exists")
    def test_set_dirpath_valid(
        mock_yaml_config_dict: JSONDataSourceConfig,
    ) -> None:
        """Tests set_dirpath method."""
        json_data_source = JSONDataSource(mock_yaml_config_dict)
        assert json_data_source.dirpath == "/path/to/json/directory"

    @staticmethod
    def test_set_dirpath_invalid(
        mock_yaml_config_dict: JSONDataSourceConfig,
    ) -> None:
        """Tests the set_dirpath method with a non-existant directory."""
        with patch("os.path.isdir", return_value=False), patch(
            "os.path.isfile", return_value=True
        ):
            with pytest.raises(ValueError, match="directory does not exist"):
                JSONDataSource(mock_yaml_config_dict)

    @staticmethod
    @pytest.mark.usefixtures("mock_path_exists")
    def test_set_filepath_valid(
        mock_yaml_config_dict: JSONDataSourceConfig,
    ) -> None:
        """Tests the set_filepath method."""
        json_data_source = JSONDataSource(mock_yaml_config_dict)
        assert json_data_source.filepath == "/path/to/json/file.json"

    @staticmethod
    def test_set_filepath_invalid(
        mock_yaml_config_dict: JSONDataSourceConfig,
    ) -> None:
        """Tests the set_filepath method with an non-existant file."""
        with patch("os.path.isdir", return_value=True), patch(
            "os.path.isfile", return_value=False
        ):
            with pytest.raises(ValueError, match="does not exist"):
                JSONDataSource(mock_yaml_config_dict)

    @staticmethod
    @pytest.mark.usefixtures("mock_path_exists")
    def test_get_file_list(
        mock_yaml_config_dict: JSONDataSourceConfig, tmp_path: Path
    ) -> None:
        """Tests the get_file_list method."""

        json_data_source = JSONDataSource(mock_yaml_config_dict)
        # Create temp directory
        temp_dir = tmp_path / "temp_dir"
        temp_dir.mkdir()
        sub_temp_dir = temp_dir / "sub_temp_dir"
        sub_temp_dir.mkdir()

        # Create files
        json_file1 = temp_dir / "json_file1.json"
        json_file2 = sub_temp_dir / "json_file2.json"
        text_file = temp_dir / "text_file.txt"

        for file in [json_file1, json_file2]:
            with file.open("w") as f:
                json.dump({"sample": "json"}, f)

        with text_file.open("w") as f:
            f.write("Sample text")

        # Test 1: Directory mode
        json_data_source.config["dirpath"] = str(temp_dir)
        json_data_source.filepath = None  # Ensure filepath is not set
        file_list = json_data_source.get_file_list()

        expected_files = {
            os.path.join(temp_dir, "json_file1.json"),
            os.path.join(temp_dir, sub_temp_dir, "json_file2.json"),
        }
        assert set(file_list) == expected_files

        # Test 2: Single file mode
        single_file = temp_dir / "single_file.json"
        with single_file.open("w") as f:
            json.dump({"single": "file"}, f)

        json_data_source.dirpath = None

        json_data_source.filepath = str(single_file)
        assert json_data_source.get_file_list() == [str(single_file)]

        # Test 3: Error case (neither dirpath nor filepath set)
        json_data_source.dirpath = None
        json_data_source.filepath = None
        with pytest.raises(ValueError, match="Directory/Filepath not set."):
            json_data_source.get_file_list()

        # Remove temp directory
        shutil.rmtree(temp_dir)

        # Test 4: Empty directory
        empty_dir = tmp_path / "empty_dir"
        empty_dir.mkdir()
        json_data_source.dirpath = str(empty_dir)
        json_data_source.filepath = None
        assert json_data_source.get_file_list() == []

    @staticmethod
    def test_initialisation_no_dirpath_no_filepath(
        mock_yaml_config_string: str,
    ) -> None:
        """Tests error handling for case with no directory or file found."""
        invalid_yaml = mock_yaml_config_string.replace(
            "dirpath: /path/to/json/directory", 'dirpath: ""'
        ).replace("filepath: /path/to/json/file.json", 'filepath: ""')

        config = yaml.safe_load(invalid_yaml)["data_sources"]["json"]

        with pytest.raises(
            FileNotFoundError, match="No directory or files found"
        ):
            JSONDataSource(config)

    @staticmethod
    @pytest.mark.usefixtures("mock_path_exists", "mock_filepath_in_dir")
    @pytest.mark.parametrize(
        "mock_data",
        [
            "mock_json_data",
            "mock_json_data_without_list",
        ],
    )
    def test_end_to_end_json_parsing(
        mock_data: str,
        mock_yaml_config_dict: JSONDataSourceConfig,
        request: FixtureRequest,
    ) -> None:
        """Tests parsing a json file."""
        mock_file_content = json.dumps(request.getfixturevalue(mock_data))

        with patch(
            "builtins.open", mock_open(read_data=mock_file_content)
        ), patch.object(
            JSONDataSource,
            "get_file_list",
            return_value=["/mock/dir/file1.json"],
        ):
            json_data_source = JSONDataSource(mock_yaml_config_dict)
            json_data_source.config["dirpath"] = ""

            grouped_spans: dict[str, Any] = dict()
            for data, header in json_data_source:
                grouped_spans.setdefault(header, [])
                grouped_spans[header].append(data)

        if mock_data == "mock_json_data":
            assert len(grouped_spans) == 2
            assert grouped_spans["Frontend 1.0"]
            assert grouped_spans["Backend 1.2"]
        else:
            assert len(grouped_spans) == 1
            assert grouped_spans["Frontend 1.0"]

        otel_event = grouped_spans["Frontend 1.0"][0]
        assert otel_event.job_name == "Azure"
        assert otel_event.job_id == "B4MQWcR6iByyOq4EMSs5Nn== 4.8"
        assert otel_event.event_id == "F1Vp3ypcQfU=="
        assert otel_event.event_type == "com.T2h.366Yx 500"
        assert otel_event.application_name == "Processor 1.2"
        assert otel_event.start_timestamp == "2024-08-13 10:15:32"
        assert otel_event.end_timestamp == "2024-08-13 10:15:32"
        assert otel_event.parent_event_id == "NzWDkmlAnji=="
        assert otel_event.child_event_ids == ["child1", "child2"]

        otel_event2 = grouped_spans["Frontend 1.0"][1]
        assert otel_event2.job_name == "AWS"
        assert otel_event2.job_id == "Js7TGf4OJROjbISB1BvOOb== 2.0"
        assert otel_event2.event_id == "Jv6moYFCoLK=="
        assert otel_event2.event_type == "com.C36.9ETRp 401"
        assert otel_event2.application_name == "Handler 2.9"
        assert otel_event2.start_timestamp == "2024-08-13 10:15:32"
        assert otel_event2.end_timestamp == "2024-08-13 10:15:32"
        assert otel_event2.parent_event_id == "0u4wIXKIZ2t=="
        assert otel_event2.child_event_ids == ["child3"]
