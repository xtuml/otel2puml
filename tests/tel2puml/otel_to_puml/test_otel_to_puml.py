"""Tests for the module otel_to_puml"""

import os
import json
from unittest.mock import patch, MagicMock
from typing import Generator, Any
from pathlib import Path

import pytest

from tel2puml.otel_to_puml import otel_to_puml
from tel2puml.tel2puml_types import OtelPumlOptions, PVPumlOptions
from tel2puml.otel_to_pv.config import load_config_from_dict


class TestOtelToPuml:
    """Tests for the otel_to_puml function"""

    @pytest.fixture
    def mock_mkdir(self) -> Generator[MagicMock, None, None]:
        with patch("tel2puml.otel_to_puml.os.mkdir") as mkdir_mock:
            yield mkdir_mock

    @pytest.fixture
    def mock_isdir(self) -> Generator[MagicMock, None, None]:
        with patch("tel2puml.otel_to_puml.os.path.isdir") as isdir_mock:
            yield isdir_mock

    def test_invalid_options_all_components_missing_otel_options(
        self, mock_isdir: MagicMock
    ) -> None:
        """Test that ValueError is raised when 'all' is selected but otel_to_puml_options is None."""
        mock_isdir.return_value = True  # Assume directory exists

        with pytest.raises(ValueError) as exc_info:
            otel_to_puml(otel_to_puml_options=None, components="all")
        assert (
            "'all' has been selected, 'otel_to_puml_options' is required."
            in str(exc_info.value)
        )

    def test_invalid_options_otel_to_puml_components_missing_otel_options(
        self, mock_isdir: MagicMock
    ) -> None:
        """Test that ValueError is raised when 'otel_to_puml' is selected but otel_to_puml_options is None."""
        mock_isdir.return_value = True

        with pytest.raises(ValueError) as exc_info:
            otel_to_puml(otel_to_puml_options=None, components="otel_to_puml")
        assert (
            "'otel_to_puml' has been selected, 'otel_to_puml_options' is required."
            in str(exc_info.value)
        )

    def test_invalid_options_pv_to_puml_components_missing_pv_options(
        self, mock_isdir: MagicMock
    ) -> None:
        """Test that ValueError is raised when 'pv_to_puml' is selected but pv_to_puml_options is None."""
        mock_isdir.return_value = True

        with pytest.raises(ValueError) as exc_info:
            otel_to_puml(pv_to_puml_options=None, components="pv_to_puml")
        assert (
            "'pv_to_puml' has been selected, 'pv_to_puml_options' is required."
            in str(exc_info.value)
        )

    def test_invalid_components_value(self, mock_isdir: MagicMock) -> None:
        """Test that ValueError is raised when an invalid component is
        selected."""
        mock_isdir.return_value = True

        with pytest.raises(ValueError) as exc_info:
            otel_to_puml(components="invalid_component")
        assert (
            "components should be one of 'all', 'otel_to_puml', 'pv_to_puml'"
            in str(exc_info.value)
        )

    def test_successful_all_components(
        self,
        tmp_path: Path,
        mock_yaml_config_dict: dict[str, Any],
        mock_json_data: dict[str, Any],
    ) -> None:
        """Test successful execution when components='all'."""

        output_dir = tmp_path / "puml_output"
        input_dir = tmp_path / "json_input"

        # Create the input directory
        input_dir.mkdir(parents=True, exist_ok=True)

        # Write mock_json_data to data.json in input_dir
        data_file = input_dir / "data.json"
        data_file.write_text(json.dumps(mock_json_data))

        # Configure config
        config = load_config_from_dict(mock_yaml_config_dict)
        config["data_sources"]["json"]["filepath"] = None
        config["data_sources"]["json"]["dirpath"] = str(input_dir)

        otel_options: OtelPumlOptions = {
            "config": load_config_from_dict(mock_yaml_config_dict),
            "ingest_data": True,
        }
        # Run function
        otel_to_puml(
            otel_to_puml_options=otel_options,
            components="all",
            output_file_directory=str(output_dir),
        )

        assert output_dir.exists()

        assert data_file.exists()
        with open(data_file, "r") as f:
            data = json.load(f)
        assert data == mock_json_data

        assert os.listdir(output_dir) == ["Frontend_TestJob.puml"]
        puml_file_path = output_dir / "Frontend_TestJob.puml"
        expected_content = (
            "@startuml\n"
            '    partition "default_name" {\n'
            '        group "default_name"\n'
            "            :com.C36.9ETRp 401;\n"
            "            :com.T2h.366Yx 500;\n"
            "        end group\n"
            "    }\n"
            "@enduml"
        )
        with open(puml_file_path, "r") as f:
            content = f.read()
            content = content.strip()
            expected_content = expected_content.strip()
            assert content == expected_content
