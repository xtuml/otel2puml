"""Tests for otel_data_source module."""

import pytest
from typing import Generator

from unittest.mock import mock_open, patch

from tel2puml.find_unique_graphs.otel_ingestion.otel_data_source import (
    JSONDataSource,
)


class TestOTELDataSource:
    """Tests for OTelDataSource class"""

    def test_get_yaml_config(
        self,
        mock_yaml_config: Generator[None, None, None],
        mock_path_exists: Generator[None, None, None],
    ) -> None:
        """Tests parsing yaml config file"""
        data_source = JSONDataSource()
        assert isinstance(data_source.yaml_config, dict)
        assert data_source.yaml_config["ingest_data"]["data_source"] == "json"

    def test_set_file_ext_valid(
        self,
        mock_yaml_config: Generator[None, None, None],
        mock_path_exists: Generator[None, None, None],
    ) -> None:
        """Tests for valid file ext within the data source object."""
        data_source = JSONDataSource()
        assert data_source.file_ext == "json"

    def test_set_file_ext_invalid(self, mock_yaml_config_string: str) -> None:
        """Tests invalid file extension in yaml config."""
        invalid_yaml = mock_yaml_config_string.replace("json", "invalid")
        with patch("builtins.open", mock_open(read_data=invalid_yaml)), patch(
            "os.path.isdir", return_value=True
        ), patch("os.path.isfile", return_value=True):
            with pytest.raises(ValueError, match="is not a valid file ext"):
                JSONDataSource()

    def test_set_dirpath_valid(
        self,
        mock_yaml_config: Generator[None, None, None],
        mock_path_exists: Generator[None, None, None],
    ) -> None:
        """Tests set_dirpath method."""
        data_source = JSONDataSource()
        assert data_source.dirpath == "/path/to/json/directory"

    def test_set_dirpath_invalid(
        self, mock_yaml_config: Generator[None, None, None]
    ) -> None:
        """Tests the set_dirpath method with a non-existant directory."""
        with patch("os.path.isdir", return_value=False), patch(
            "os.path.isfile", return_value=True
        ):
            with pytest.raises(ValueError, match="directory does not exist"):
                JSONDataSource()

    def test_set_filepath_valid(
        self,
        mock_yaml_config: Generator[None, None, None],
        mock_path_exists: Generator[None, None, None],
    ) -> None:
        """Tests the set_filepath method."""
        data_source = JSONDataSource()
        assert data_source.filepath == "/path/to/json/file.json"

    def test_set_filepath_invalid(
        self, mock_yaml_config: Generator[None, None, None]
    ) -> None:
        """Tests the set_filepath method with an non-existant file."""
        with patch("os.path.isdir", return_value=True), patch(
            "os.path.isfile", return_value=False
        ):
            with pytest.raises(ValueError, match="does not exist"):
                JSONDataSource()

    def test_initialisation_no_dirpath_no_filepath(
        self, mock_yaml_config_string: str
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
