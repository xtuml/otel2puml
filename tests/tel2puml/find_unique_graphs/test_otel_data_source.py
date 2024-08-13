"""Tests for otel_data_source module."""

import json
import yaml
import pytest
from typing import Any
from pytest import FixtureRequest
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
        """Tests parsing yaml config file"""
        json_data_source = JSONDataSource(mock_yaml_config_dict)
        assert isinstance(json_data_source.config, dict)
        assert json_data_source.config["data_location"] == "resource_spans"
        assert isinstance(
            json_data_source.config["header_mapping"]["header"]["key_paths"],
            list,
        )
        assert (
            json_data_source.config["header_mapping"]["header"]["key_paths"][0]
            == "resource:attributes::key"
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
        jsond_data_source = JSONDataSource(mock_yaml_config_dict)
        assert jsond_data_source.filepath == "/path/to/json/file.json"

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
    @pytest.mark.usefixtures("mock_path_exists")
    def test_init(
        mock_yaml_config_dict: JSONDataSourceConfig,
    ) -> None:
        """Tests the classes init method."""
        json_data_source = JSONDataSource(mock_yaml_config_dict)
        assert json_data_source.dirpath == "/path/to/json/directory"
        assert json_data_source.filepath == "/path/to/json/file.json"

    @staticmethod
    @pytest.mark.usefixtures("mock_path_exists")
    def test_get_file_list_filepath(
        mock_yaml_config_dict: JSONDataSourceConfig,
    ) -> None:
        """Tests getting the json filepath if directory is not specified."""
        json_data_source = JSONDataSource(mock_yaml_config_dict)
        json_data_source.dirpath = ""
        assert json_data_source.get_file_list() == ["/path/to/json/file.json"]

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
