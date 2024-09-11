"""Tests for otel_data_source module."""

import json
import os
import yaml
import pytest
import shutil

from pytest import FixtureRequest
from pathlib import Path
from unittest.mock import mock_open, patch

from tel2puml.otel_to_pv.data_sources.otel_data_source import (
    JSONDataSource,
)
from tel2puml.otel_to_pv.otel_ingestion.otel_data_model import (
    IngestDataConfig,
    OTelEvent,
)


class TestJSONDataSource:
    """Tests for JSONDataSource class."""

    @staticmethod
    @pytest.mark.usefixtures("mock_path_exists")
    def test_get_yaml_config(
        mock_yaml_config_dict: IngestDataConfig,
    ) -> None:
        """Tests parsing yaml config file and setting config attribute."""
        json_data_source = JSONDataSource(
            mock_yaml_config_dict["data_sources"]["json"]
        )
        config = json_data_source.config

        # Check if config is a dictionary
        assert isinstance(config, dict)

        # Check main config keys
        expected_keys = {
            "dirpath",
            "filepath",
            "data_location",
            "header",
            "span_mapping",
            "field_mapping",
        }
        assert set(config.keys()) == expected_keys

        # Check string values
        assert config["dirpath"] == "/path/to/json/directory"
        assert config["filepath"] == "/path/to/json/file.json"
        assert config["data_location"] == "resource_spans"

        # Check expected field mapping keys
        expected_field_mapping_keys = {
            "job_name",
            "job_id",
            "event_type",
            "event_id",
            "start_timestamp",
            "end_timestamp",
            "application_name",
            "parent_event_id",
            "child_event_ids",
        }
        assert (
            set(config["field_mapping"].keys()) == expected_field_mapping_keys
        )

    @staticmethod
    @pytest.mark.usefixtures("mock_path_exists")
    def test_set_dirpath_valid(
        mock_yaml_config_dict: IngestDataConfig,
    ) -> None:
        """Tests set_dirpath method."""
        json_data_source = JSONDataSource(
            mock_yaml_config_dict["data_sources"]["json"]
        )
        assert json_data_source.dirpath == "/path/to/json/directory"

    @staticmethod
    def test_set_dirpath_invalid(
        mock_yaml_config_dict: IngestDataConfig,
    ) -> None:
        """Tests the set_dirpath method with a non-existant directory."""
        with patch("os.path.isdir", return_value=False), patch(
            "os.path.isfile", return_value=True
        ):
            with pytest.raises(ValueError, match="directory does not exist"):
                JSONDataSource(mock_yaml_config_dict["data_sources"]["json"])

    @staticmethod
    @pytest.mark.usefixtures("mock_path_exists")
    def test_set_filepath_valid(
        mock_yaml_config_dict: IngestDataConfig,
    ) -> None:
        """Tests the set_filepath method."""
        json_data_source = JSONDataSource(
            mock_yaml_config_dict["data_sources"]["json"]
        )
        assert json_data_source.filepath == "/path/to/json/file.json"

    @staticmethod
    def test_set_filepath_invalid(
        mock_yaml_config_dict: IngestDataConfig,
    ) -> None:
        """Tests the set_filepath method with an non-existant file."""
        with patch("os.path.isdir", return_value=True), patch(
            "os.path.isfile", return_value=False
        ):
            with pytest.raises(ValueError, match="does not exist"):
                JSONDataSource(mock_yaml_config_dict["data_sources"]["json"])

    @staticmethod
    @pytest.mark.usefixtures("mock_path_exists")
    def test_get_file_list(
        mock_yaml_config_dict: IngestDataConfig, tmp_path: Path
    ) -> None:
        """Tests the get_file_list method."""

        json_data_source = JSONDataSource(
            mock_yaml_config_dict["data_sources"]["json"]
        )
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
        mock_yaml_config_dict: IngestDataConfig,
        request: FixtureRequest,
    ) -> None:
        """Tests parsing a json file for both json data that has spans
        within a list and as a dictionary.
        """
        mock_file_content = json.dumps(request.getfixturevalue(mock_data))

        with patch(
            "builtins.open", mock_open(read_data=mock_file_content)
        ), patch.object(
            JSONDataSource,
            "get_file_list",
            return_value=["/mock/dir/file1.json"],
        ):
            json_data_source = JSONDataSource(
                mock_yaml_config_dict["data_sources"]["json"]
            )
            json_data_source.config["dirpath"] = ""

            otel_events: list[OTelEvent] = []
            for data in json_data_source:
                otel_events.append(data)

        otel_event = otel_events[0]
        assert otel_event.job_name == "Frontend TestJob"
        assert otel_event.job_id == "trace001 4.8"
        assert otel_event.event_id == "span001"
        assert otel_event.event_type == "com.T2h.366Yx 500"
        assert otel_event.application_name == "Processor 1.0"
        assert otel_event.start_timestamp == 1723544132228102912
        assert otel_event.end_timestamp == 1723544132228219285
        assert otel_event.parent_event_id is None
        assert otel_event.child_event_ids == ["child1", "child2"]

        otel_event2 = otel_events[1]
        assert otel_event2.job_name == "Frontend TestJob"
        assert otel_event2.job_id == "trace002 2.0"
        assert otel_event2.event_id == "span002"
        assert otel_event2.event_type == "com.C36.9ETRp 401"
        assert otel_event2.application_name == "Handler 1.0"
        assert otel_event2.start_timestamp == 1723544132228288000
        assert otel_event2.end_timestamp == 1723544132229038947
        assert otel_event2.parent_event_id == "span001"
        assert otel_event2.child_event_ids == ["child3"]

        if mock_data == "mock_json_data_without_list":
            assert len(otel_events) == 2
        else:
            assert len(otel_events) == 4

            otel_event3 = otel_events[2]
            assert otel_event3.job_name == "Backend TestJob"
            assert otel_event3.job_id == "trace003 2.7"
            assert otel_event3.event_id == "span003"
            assert otel_event3.event_type == "com.a58.GFkzZ 201"
            assert otel_event3.application_name == "Processor 1.2"
            assert otel_event3.start_timestamp == 1723544154817766912
            assert otel_event3.end_timestamp == 1723544154818599863
            assert otel_event3.parent_event_id is None
            assert otel_event3.child_event_ids is None

            otel_event4 = otel_events[3]
            assert otel_event4.job_name == "Backend TestJob"
            assert otel_event4.job_id == "trace004 1.3"
            assert otel_event4.event_id == "span004"
            assert otel_event4.event_type == "com.67Q.AS8pJ 201"
            assert otel_event4.application_name == "Processor 1.2"
            assert otel_event4.start_timestamp == 1723544154817793024
            assert otel_event4.end_timestamp == 1723544154818380443
            assert otel_event4.parent_event_id == "span003"
            assert otel_event4.child_event_ids == ["child5"]
