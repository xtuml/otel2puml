"""Tests for otel_data_source module."""

import json
import os
import shutil
from typing import Literal, Any
from logging import WARNING

import yaml
import pytest
from pytest import FixtureRequest, LogCaptureFixture
from pathlib import Path
from unittest.mock import mock_open, patch

from tel2puml.otel_to_pv.data_sources.json_data_source.json_datasource import (
    JSONDataSource,
)
from tel2puml.otel_to_pv.data_sources.json_data_source.json_config import (
    JSONDataSourceConfig
)
from tel2puml.otel_to_pv.otel_to_pv_types import OTelEvent
from tel2puml.otel_to_pv.config import IngestDataConfig


class TestJSONDataSource:
    """Tests for JSONDataSource class."""

    @staticmethod
    @pytest.mark.usefixtures("mock_path_exists")
    def test_get_yaml_config(
        mock_ingest_config: IngestDataConfig,
    ) -> None:
        """Tests parsing yaml config file and setting config attribute."""
        json_data_source = JSONDataSource(
            mock_ingest_config.data_sources["json"]
        )
        config = json_data_source.config

        # Check if config is a dictionary
        assert isinstance(config, JSONDataSourceConfig)

        # Check string values
        assert config.dirpath == "/path/to/json/directory"
        assert config.filepath == "/path/to/json/file.json"
        assert not config.json_per_line
        assert config.field_mapping is not None

    @staticmethod
    @pytest.mark.usefixtures("mock_path_exists")
    def test_set_dirpath_valid(
        mock_ingest_config: IngestDataConfig,
    ) -> None:
        """Tests set_dirpath method."""
        json_data_source = JSONDataSource(
            mock_ingest_config.data_sources["json"]
        )
        assert json_data_source.dirpath == "/path/to/json/directory"

    @staticmethod
    def test_set_dirpath_invalid(
        mock_ingest_config: IngestDataConfig,
    ) -> None:
        """Tests the set_dirpath method with a non-existant directory."""
        with patch("os.path.isdir", return_value=False), patch(
            "os.path.isfile", return_value=True
        ):
            with pytest.raises(ValueError, match="directory does not exist"):
                JSONDataSource(mock_ingest_config.data_sources["json"])

    @staticmethod
    @pytest.mark.usefixtures("mock_path_exists")
    def test_set_filepath_valid(
        mock_ingest_config: IngestDataConfig,
    ) -> None:
        """Tests the set_filepath method."""
        json_data_source = JSONDataSource(
            mock_ingest_config.data_sources["json"]
        )
        assert json_data_source.filepath == "/path/to/json/file.json"

    @staticmethod
    def test_set_filepath_invalid(
        mock_ingest_config: IngestDataConfig,
    ) -> None:
        """Tests the set_filepath method with an non-existant file."""
        with patch("os.path.isdir", return_value=True), patch(
            "os.path.isfile", return_value=False
        ):
            with pytest.raises(ValueError, match="does not exist"):
                JSONDataSource(mock_ingest_config.data_sources["json"])

    @staticmethod
    @pytest.mark.usefixtures("mock_path_exists")
    def test_get_file_list(
        mock_ingest_config: IngestDataConfig, tmp_path: Path
    ) -> None:
        """Tests the get_file_list method."""

        json_data_source = JSONDataSource(
            mock_ingest_config.data_sources["json"]
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
        json_data_source.dirpath = str(temp_dir)
        json_data_source.filepath = None  # Ensure filepath is not set
        file_list = json_data_source.get_file_list()

        expected_files = {
            os.path.join(temp_dir, "json_file1.json"),
            os.path.join(temp_dir, sub_temp_dir, "json_file2.json"),
            os.path.join(temp_dir, "text_file.txt"),
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
        json_data_source_config = JSONDataSourceConfig(**config)

        with pytest.raises(
            FileNotFoundError, match="No directory or files found"
        ):
            JSONDataSource(json_data_source_config)

    @staticmethod
    @pytest.mark.usefixtures("mock_path_exists", "mock_filepath_in_dir")
    def test_parse_json_stream(
        mock_ingest_config: IngestDataConfig,
        mock_json_data: dict[str, Any],
        caplog: LogCaptureFixture,
    ) -> None:
        """Tests the parse_json_stream method."""
        mock_file_content = json.dumps(mock_json_data).encode("utf-8")
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            json_data_source = JSONDataSource(
                mock_ingest_config.data_sources["json"]
            )
            otel_events = json_data_source.parse_json_stream(
                "/mock/dir/file1.json"
            )
            otel_event = next(otel_events)
            assert otel_event.job_name == "Frontend_TestJob"
            assert otel_event.job_id == "trace001_4.8"
            assert otel_event.event_id == "span001"
            assert otel_event.event_type == "com.T2h.366Yx_500"
            assert otel_event.application_name == "Processor_1.0"
            assert otel_event.start_timestamp == 1723544132228102912
            assert otel_event.end_timestamp == 1723544132228219285
            assert otel_event.parent_event_id is None
            assert otel_event.child_event_ids == ["child1", "child2"]
        # test case with a validation error
        json_data = {"resource_spans": [
            {"scope_spans": [{"spans": [{"span_id": "span001"}]}]}
        ]}
        mock_file_content = json.dumps(json_data).encode("utf-8")
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            json_data_source = JSONDataSource(
                mock_ingest_config.data_sources["json"]
            )
            caplog.clear()
            caplog.set_level(WARNING)
            otel_events = json_data_source.parse_json_stream(
                "/mock/dir/file1.json"
            )
            with pytest.raises(StopIteration):
                otel_event = next(otel_events)
            assert (
                "Error coercing data in"
                " file: "
                "/mock/dir/file1.json\n"
                "Validation Error: 6 validation errors for OTelEvent\n"
                "job_name\n"
                "  Input should be a valid string [type=string_type, "
                "input_value=None, input_type=NoneType]\n"
                "    For further information visit "
                "https://errors.pydantic.dev/2.9/v/string_type\n"
                "job_id\n"
                "  Input should be a valid string [type=string_type, "
                "input_value=None, input_type=NoneType]\n"
                "    For further information visit "
                "https://errors.pydantic.dev/2.9/v/string_type\n"
                "event_type\n"
                "  Input should be a valid string [type=string_type, "
                "input_value=None, input_type=NoneType]\n"
                "    For further information visit "
                "https://errors.pydantic.dev/2.9/v/string_type\n"
                "start_timestamp\n"
                "  Input should be a valid integer [type=int_type, "
                "input_value=None, input_type=NoneType]\n"
                "    For further information visit "
                "https://errors.pydantic.dev/2.9/v/int_type\n"
                "end_timestamp\n"
                "  Input should be a valid integer [type=int_type, "
                "input_value=None, input_type=NoneType]\n"
                "    For further information visit "
                "https://errors.pydantic.dev/2.9/v/int_type\n"
                "application_name\n"
                "  Input should be a valid string [type=string_type, "
                "input_value=None, input_type=NoneType]\n"
                "    For further information visit "
                "https://errors.pydantic.dev/2.9/v/string_type\n"
                "Record: {'job_name': None, 'job_id': None, "
                "'event_type': None, 'event_id': 'span001', "
                "'start_timestamp': None, 'end_timestamp': None, "
                "'application_name': None, 'parent_event_id': None, "
                "'child_event_ids': None}\n"
                "Skipping record - if this is a persistent error, "
                "please check the field mapping or jq query in the"
                " input config.yaml."
            ) in caplog.text

    @staticmethod
    @pytest.mark.usefixtures("mock_path_exists", "mock_filepath_in_dir")
    @pytest.mark.parametrize(
        "mock_data, mock_yaml_config",
        [
            ("mock_json_data", "mock_ingest_config"),
            (
                "mock_json_data_without_list",
                "mock_ingest_config_without_list",
            ),
            ("mock_json_data", "mock_ingest_config_json_per_line"),
        ],
    )
    def test_end_to_end_json_parsing(
        mock_data: str,
        mock_yaml_config: str,
        request: FixtureRequest,
    ) -> None:
        """Tests parsing a json file for both json data that has spans
        within a list and as a dictionary.
        """
        mock_file_content = json.dumps(
            request.getfixturevalue(mock_data)
        ).encode("utf-8")
        mock_file_content = (
            mock_file_content[:1]
            + b'"injected_error": "\x1b", '
            + mock_file_content[1:]
        )
        mock_ingest_config: IngestDataConfig = request.getfixturevalue(
            mock_yaml_config
        )
        if mock_ingest_config.data_sources["json"].json_per_line:
            mock_file_content = mock_file_content + b"\n" + mock_file_content

        with patch(
            "builtins.open", mock_open(read_data=mock_file_content)
        ), patch.object(
            JSONDataSource,
            "get_file_list",
            return_value=["/mock/dir/file1.json"],
        ):
            json_data_source = JSONDataSource(
                mock_ingest_config.data_sources["json"]
            )
            json_data_source.config.dirpath = ""

            otel_events: list[OTelEvent] = []
            for data in json_data_source:
                otel_events.append(data)

        def check_otel_events(
            otel_events: list[OTelEvent], n_check: Literal[2, 4]
        ) -> None:
            """Check the otel events."""
            otel_event = otel_events[0]
            assert otel_event.job_name == "Frontend_TestJob"
            assert otel_event.job_id == "trace001_4.8"
            assert otel_event.event_id == "span001"
            assert otel_event.event_type == "com.T2h.366Yx_500"
            assert otel_event.application_name == "Processor_1.0"
            assert otel_event.start_timestamp == 1723544132228102912
            assert otel_event.end_timestamp == 1723544132228219285
            assert otel_event.parent_event_id is None
            assert otel_event.child_event_ids == ["child1", "child2"]

            otel_event2 = otel_events[1]
            assert otel_event2.job_name == "Frontend_TestJob"
            assert otel_event2.job_id == "trace002_2.0"
            assert otel_event2.event_id == "span002"
            assert otel_event2.event_type == "com.C36.9ETRp_401"
            assert otel_event2.application_name == "Handler_1.0"
            assert otel_event2.start_timestamp == 1723544132228288000
            assert otel_event2.end_timestamp == 1723544132229038947
            assert otel_event2.parent_event_id == "span001"
            assert otel_event2.child_event_ids == ["child3"]

            if n_check == 2:
                return
            otel_event3 = otel_events[2]
            assert otel_event3.job_name == "Backend_TestJob"
            assert otel_event3.job_id == "trace003_2.7"
            assert otel_event3.event_id == "span003"
            assert otel_event3.event_type == "com.a58.GFkzZ_201"
            assert otel_event3.application_name == "Processor_1.2"
            assert otel_event3.start_timestamp == 1723544154817766912
            assert otel_event3.end_timestamp == 1723544154818599863
            assert otel_event3.parent_event_id is None
            assert otel_event3.child_event_ids == []

            otel_event4 = otel_events[3]
            assert otel_event4.job_name == "Backend_TestJob"
            assert otel_event4.job_id == "trace004_1.3"
            assert otel_event4.event_id == "span004"
            assert otel_event4.event_type == "com.67Q.AS8pJ_201"
            assert otel_event4.application_name == "Processor_1.2"
            assert otel_event4.start_timestamp == 1723544154817793024
            assert otel_event4.end_timestamp == 1723544154818380443
            assert otel_event4.parent_event_id == "span003"
            assert otel_event4.child_event_ids is None

        # without list
        if mock_yaml_config == "mock_ingest_config_without_list":
            assert len(otel_events) == 2
            check_otel_events(otel_events, 2)
        # json on each line of file
        elif mock_yaml_config == "mock_ingest_config_json_per_line":
            assert len(otel_events) == 8
            check_otel_events(otel_events[:4], 4)
            check_otel_events(otel_events[4:], 4)
        # with list
        else:
            assert len(otel_events) == 4
            check_otel_events(otel_events, 4)
