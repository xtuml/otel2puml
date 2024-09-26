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
from tel2puml.otel_to_pv.data_holders.sql_data_holder.data_model import (
    NodeModel,
)
from tel2puml.otel_to_pv.data_holders.sql_data_holder.sql_dataholder import (
    SQLDataHolder,
)


class TestOtelToPuml:
    """Tests for the otel_to_puml function"""

    @pytest.fixture
    def mock_isdir(self) -> Generator[MagicMock, None, None]:
        with patch("tel2puml.otel_to_puml.os.path.isdir") as isdir_mock:
            yield isdir_mock

    @pytest.fixture
    def mock_fetch_data_holder(self) -> Generator[MagicMock, None, None]:
        with patch(
            "tel2puml.otel_to_pv.sequence_otel_v2.fetch_data_holder"
        ) as fetch_data_hoder_mock:
            yield fetch_data_hoder_mock

    @staticmethod
    def test_invalid_options_all_components_missing_otel_options(
        mock_isdir: MagicMock,
    ) -> None:
        """Test that ValueError is raised when 'all' is selected but otel_to_puml_options is None."""
        mock_isdir.return_value = True  # Assume directory exists

        with pytest.raises(ValueError) as exc_info:
            otel_to_puml(otel_to_puml_options=None, components="all")
        assert (
            "'all' has been selected, 'otel_to_puml_options' is required."
            in str(exc_info.value)
        )

    @staticmethod
    def test_invalid_options_otel_to_puml_components_missing_otel_options(
        mock_isdir: MagicMock,
    ) -> None:
        """Test that ValueError is raised when 'otel_to_puml' is selected but otel_to_puml_options is None."""
        mock_isdir.return_value = True

        with pytest.raises(ValueError) as exc_info:
            otel_to_puml(otel_to_puml_options=None, components="otel_to_puml")
        assert (
            "'otel_to_puml' has been selected, 'otel_to_puml_options' is required."
            in str(exc_info.value)
        )

    @staticmethod
    def test_invalid_options_pv_to_puml_components_missing_pv_options(
        mock_isdir: MagicMock,
    ) -> None:
        """Test that ValueError is raised when 'pv_to_puml' is selected but pv_to_puml_options is None."""
        mock_isdir.return_value = True

        with pytest.raises(ValueError) as exc_info:
            otel_to_puml(pv_to_puml_options=None, components="pv_to_puml")
        assert (
            "'pv_to_puml' has been selected, 'pv_to_puml_options' is required."
            in str(exc_info.value)
        )

    @staticmethod
    def test_invalid_components_value(mock_isdir: MagicMock) -> None:
        """Test that ValueError is raised when an invalid component is
        selected."""
        mock_isdir.return_value = True

        with pytest.raises(ValueError) as exc_info:
            otel_to_puml(
                components="invalid_component"  # type: ignore[arg-type]
            )
        assert (
            "components should be one of 'all', 'otel_to_puml', 'pv_to_puml'"
            in str(exc_info.value)
        )

    @staticmethod
    def test_successful_all_components(
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
        config["data_sources"]["json"]["dirpath"] = str(input_dir)
        config["data_sources"]["json"]["filepath"] = None

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

    @staticmethod
    def test_successful_otel_to_puml_components_ingest_only(
        tmp_path: Path,
        mock_json_data: dict[str, Any],
        mock_yaml_config_dict: dict[str, Any],
    ) -> None:
        """Test successful execution when components='otel_to_puml' and ingest
        data is set True."""
        input_dir = tmp_path / "json_input"

        # Create the input directory
        input_dir.mkdir(parents=True, exist_ok=True)

        # Write mock_json_data to data.json in input_dir
        data_file = input_dir / "data.json"
        data_file.write_text(json.dumps(mock_json_data))

        # Configure config
        config = load_config_from_dict(mock_yaml_config_dict)
        config["data_sources"]["json"]["dirpath"] = str(input_dir)
        config["data_sources"]["json"]["filepath"] = None

        otel_options: OtelPumlOptions = {
            "config": load_config_from_dict(mock_yaml_config_dict),
            "ingest_data": True,
        }
        # Run function
        data_holder = otel_to_puml(
            otel_to_puml_options=otel_options,
            components="otel_to_puml",
        )
        assert isinstance(data_holder, SQLDataHolder)
        with data_holder.session as session:
            nodes = session.query(NodeModel).all()

        assert len(nodes) == 2
        assert all(isinstance(node, NodeModel) for node in nodes)
        node1 = nodes[0]
        assert node1.application_name == "Processor 1.0"
        assert node1.event_id == "span001"
        assert node1.event_type == "com.T2h.366Yx 500"
        assert node1.job_id == "job_A"
        assert node1.job_name == "Frontend TestJob"
        assert node1.parent_event_id is None

        node2 = nodes[1]
        assert node2.application_name == "Handler 1.0"
        assert node2.event_id == "span002"
        assert node2.event_type == "com.C36.9ETRp 401"
        assert node2.job_id == "job_A"
        assert node2.job_name == "Frontend TestJob"
        assert node2.parent_event_id == "span001"

    @staticmethod
    def test_successful_otel_to_puml_components_stream_data(
        tmp_path: Path,
        sql_data_holder_with_otel_jobs: SQLDataHolder,
        mock_fetch_data_holder: MagicMock,
        mock_yaml_config_dict: dict[str, Any],
    ) -> None:
        """Test successful execution when components='otel_to_puml' and ingest
        data is set False. This tests streaming data from the data holder
        and generating puml files.
        """
        mock_fetch_data_holder.return_value = sql_data_holder_with_otel_jobs

        output_dir = tmp_path / "puml_output"

        otel_options: OtelPumlOptions = {
            "config": load_config_from_dict(mock_yaml_config_dict),
            "ingest_data": False,
        }
        # Run function
        otel_to_puml(
            otel_to_puml_options=otel_options,
            components="otel_to_puml",
            output_file_directory=str(output_dir),
        )

        assert output_dir.exists()
        assert os.listdir(output_dir) == ["test_name.puml"]
        puml_file_path = output_dir / "test_name.puml"

        expected_content = (
            "@startuml\n"
            '    partition "default_name" {\n'
            '        group "default_name"\n'
            "            :event_type_1;\n"
            "            :event_type_0;\n"
            "        end group\n"
            "    }\n"
            "@enduml"
        )
        with open(puml_file_path, "r") as f:
            content = f.read()
            content = content.strip()
            expected_content = expected_content.strip()
            assert content == expected_content

    @staticmethod
    @pytest.mark.parametrize(
        "group_by_job_id",
        [False, True],
    )
    def test_successful_pv_to_puml_components(
        mock_job_json_file: list[dict[str, Any]],
        tmp_path: Path,
        group_by_job_id: bool,
    ) -> None:
        """Test successful execution when components='pv_to_puml'"""
        output_dir = tmp_path / "puml_output"
        input_dir = tmp_path / "job_json"

        input_dir.mkdir(parents=True, exist_ok=True)

        data_file = input_dir / "file1.json"
        data_file.write_text(json.dumps(mock_job_json_file))

        pv_to_puml_options: PVPumlOptions = {
            "file_directory": str(input_dir),
            "job_name": "TestName",
            "group_by_job_id": group_by_job_id,
        }

        otel_to_puml(
            pv_to_puml_options=pv_to_puml_options,
            components="pv_to_puml",
            output_file_directory=str(output_dir),
        )

        assert output_dir.exists()
        assert os.listdir(output_dir) == ["TestName.puml"]
        puml_file_path = output_dir / "TestName.puml"

        expected_content = (
            "@startuml\n"
            '    partition "default_name" {\n'
            '        group "default_name"\n'
            "            :START;\n"
            "            :A;\n"
            "            :END;\n"
            "        end group\n"
            "    }\n"
            "@enduml"
        )
        with open(puml_file_path, "r") as f:
            content = f.read()
            content = content.strip()
            expected_content = expected_content.strip()
            assert content == expected_content
