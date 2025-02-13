"""Tests for the module otel_to_puml"""

import os
import json
from pathlib import Path
from typing import Generator, Any
from unittest.mock import patch, MagicMock

import pytest

from tel2puml.otel_to_puml import otel_to_puml
from tel2puml.tel2puml_types import OtelPVOptions, PVPumlOptions, GlobalOptions
from tel2puml.otel_to_pv.config import load_config_from_dict
from tel2puml.otel_to_pv.data_holders.sql_data_holder.data_model import (
    NodeModel,
)
from tel2puml.otel_to_pv.data_holders.sql_data_holder.sql_dataholder import (
    SQLDataHolder,
)
from tel2puml.otel_to_pv.ingest_otel_data import fetch_data_holder


class TestOtelToPuml:
    """Tests for the otel_to_puml function"""

    @pytest.fixture
    def mock_isdir(self) -> Generator[MagicMock, None, None]:
        """Fixture to mock isdir."""
        with patch("tel2puml.otel_to_puml.os.path.isdir") as isdir_mock:
            yield isdir_mock

    @pytest.fixture
    def mock_fetch_data_holder(self) -> Generator[MagicMock, None, None]:
        """Fixture to mock fetch_data_holder."""
        with patch(
            "tel2puml.otel_to_pv.otel_to_pv.fetch_data_holder"
        ) as mock_data_holder:
            yield mock_data_holder

    @staticmethod
    def test_invalid_options_all_components_missing_otel_options(
        mock_isdir: MagicMock,
    ) -> None:
        """Test that ValueError is raised when 'otel2puml' is selected but
        otel_to_puml_options is None."""
        mock_isdir.return_value = True  # Assume directory exists

        with pytest.raises(ValueError) as exc_info:
            otel_to_puml(otel_to_pv_options=None, components="otel2puml")
        assert (
            "'otel2puml' has been selected, 'otel_to_pv_options' is required."
            in str(exc_info.value)
        )

    @staticmethod
    def test_invalid_options_otel_to_puml_components_missing_otel_options(
        mock_isdir: MagicMock,
    ) -> None:
        """Test that ValueError is raised when 'otel_to_puml' is selected
        but otel_to_puml_options is None."""
        mock_isdir.return_value = True

        with pytest.raises(ValueError) as exc_info:
            otel_to_puml(otel_to_pv_options=None, components="otel2pv")
        assert (
            "'otel2pv' has been selected, 'otel_to_pv_options' is"
            " required." in str(exc_info.value)
        )

    @staticmethod
    def test_invalid_options_pv_to_puml_components_missing_pv_options(
        mock_isdir: MagicMock,
    ) -> None:
        """Test that ValueError is raised when 'pv2puml' is
        selected but pv_to_puml_options is None."""
        mock_isdir.return_value = True

        with pytest.raises(ValueError) as exc_info:
            otel_to_puml(pv_to_puml_options=None, components="pv2puml")
        assert (
            "'pv2puml' has been selected, 'pv_to_puml_options' is required."
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
            "components should be one of 'otel2puml', 'otel2pv', 'pv2puml'"
            in str(exc_info.value)
        )

    @staticmethod
    def test_successful_all_components(
        tmp_path: Path,
        mock_yaml_config_dict: dict[str, Any],
        mock_json_data: dict[str, Any],
    ) -> None:
        """Test successful execution when components='otel2puml'."""

        output_dir = tmp_path / "puml_output"
        input_dir = tmp_path / "json_input"

        # Create the input directory
        input_dir.mkdir(parents=True, exist_ok=True)

        # Write mock_json_data to data.json in input_dir
        data_file = input_dir / "data.json"
        data_file.write_text(json.dumps(mock_json_data))

        # Configure config
        mock_yaml_config_dict["data_sources"]["json"]["dirpath"] = str(
            input_dir
        )
        mock_yaml_config_dict["data_sources"]["json"]["filepath"] = None
        config = load_config_from_dict(mock_yaml_config_dict)

        otel_options: OtelPVOptions = {
            "config": config,
            "ingest_data": True,
            "save_events": False,
            "find_unique_graphs": False,
        }

        otel_to_puml(
            otel_to_pv_options=otel_options,
            components="otel2puml",
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
            '    partition "Frontend_TestJob" {\n'
            '        group "Frontend_TestJob"\n'
            "            :com.C36.9ETRp_401;\n"
            "            :com.T2h.366Yx_500;\n"
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
        mock_yaml_config_dict["data_sources"]["json"]["dirpath"] = str(
            input_dir
        )
        mock_yaml_config_dict["data_sources"]["json"]["filepath"] = None
        mock_yaml_config_dict["data_holders"]["sql"][
            "db_uri"
        ] = f'sqlite:///{str(tmp_path / "test.db")}'
        config = load_config_from_dict(mock_yaml_config_dict)

        otel_options: OtelPVOptions = {
            "config": config,
            "ingest_data": True,
            "save_events": False,
            "find_unique_graphs": False,
        }
        # Run function
        otel_to_puml(
            otel_to_pv_options=otel_options,
            components="otel2pv",
        )
        data_holder: SQLDataHolder = fetch_data_holder(
            config  # type: ignore[assignment]
        )
        with data_holder.session as session:
            nodes = session.query(NodeModel).all()

        assert len(nodes) == 2
        assert all(isinstance(node, NodeModel) for node in nodes)
        node1 = nodes[0]
        assert node1.application_name == "Processor_1.0"
        assert node1.event_id == "span001"
        assert node1.event_type == "com.T2h.366Yx_500"
        assert node1.job_id == "job_A"
        assert node1.job_name == "Frontend_TestJob"
        assert node1.parent_event_id is None

        node2 = nodes[1]
        assert node2.application_name == "Handler_1.0"
        assert node2.event_id == "span002"
        assert node2.event_type == "com.C36.9ETRp_401"
        assert node2.job_id == "job_A"
        assert node2.job_name == "Frontend_TestJob"
        assert node2.parent_event_id == "span001"

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
        """Test successful execution when components='pv2puml'"""
        output_dir = tmp_path / "puml_output"
        input_dir = tmp_path / "job_json"

        input_dir.mkdir(parents=True, exist_ok=True)
        if group_by_job_id:
            data_files: list[str] = []
            for i, job_json in enumerate(mock_job_json_file):
                data_file = input_dir / f"file{i}.json"
                data_file.write_text(json.dumps(job_json))
                data_files.append(str(data_file))
        else:
            data_file = input_dir / "file1.json"
            data_file.write_text(json.dumps(mock_job_json_file))
            data_files = [str(data_file)]

        pv_to_puml_options: PVPumlOptions = {
            "file_list": data_files,
            "job_name": "TestName",
            "group_by_job_id": group_by_job_id,
        }

        otel_to_puml(
            pv_to_puml_options=pv_to_puml_options,
            components="pv2puml",
            output_file_directory=str(output_dir),
        )

        assert output_dir.exists()
        assert os.listdir(output_dir) == ["TestName.puml"]
        puml_file_path = output_dir / "TestName.puml"

        expected_content = (
            "@startuml\n"
            '    partition "TestName" {\n'
            '        group "TestName"\n'
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

    @staticmethod
    def test_save_events(
        tmp_path: Path,
        mock_yaml_config_dict: dict[str, Any],
        mock_json_data: dict[str, Any],
    ) -> None:
        """Test successful execution when components='otel2puml' and save
        events is True."""

        output_dir = tmp_path / "json_output"
        input_dir = tmp_path / "json_input"

        # Create the input directory
        input_dir.mkdir(parents=True, exist_ok=True)

        # Write mock_json_data to data.json in input_dir
        data_file = input_dir / "data.json"
        data_file.write_text(json.dumps(mock_json_data))

        # Configure config
        mock_yaml_config_dict["data_sources"]["json"]["dirpath"] = str(
            input_dir
        )
        mock_yaml_config_dict["data_sources"]["json"]["filepath"] = None
        config = load_config_from_dict(mock_yaml_config_dict)

        otel_options: OtelPVOptions = {
            "config": config,
            "ingest_data": True,
            "save_events": True,
            "find_unique_graphs": False,
        }

        otel_to_puml(
            otel_to_pv_options=otel_options,
            components="otel2puml",
            output_file_directory=str(output_dir),
        )

        assert os.listdir(output_dir) == ["Frontend_TestJob"]

        job_json_folder_path = output_dir / "Frontend_TestJob"
        assert os.listdir(job_json_folder_path) == [
            "pv_event_sequence_1.json",
        ]
        expected_job_json_content = [
            {
                "applicationName": "Processor_1.0",
                "eventId": "span001",
                "eventType": "com.T2h.366Yx_500",
                "jobId": "job_A",
                "jobName": "Frontend_TestJob",
                "previousEventIds": ["span002"],
                "timestamp": "2024-08-13T10:15:32.228220Z",
            },
            {
                "applicationName": "Handler_1.0",
                "eventId": "span002",
                "eventType": "com.C36.9ETRp_401",
                "jobId": "job_A",
                "jobName": "Frontend_TestJob",
                "previousEventIds": [],
                "timestamp": "2024-08-13T10:15:32.229039Z",
            },
        ]
        file_path = job_json_folder_path / "pv_event_sequence_1.json"
        assert file_path.exists()

        with file_path.open("r") as f:
            file_content = json.load(f)
            assert file_content == expected_job_json_content

    @staticmethod
    def test_find_unique_graphs(
        tmp_path: Path,
        mock_yaml_config_dict: dict[str, Any],
        mock_json_data: dict[str, Any],
        mock_fetch_data_holder: MagicMock,
        sql_data_holder_with_otel_jobs: SQLDataHolder,
    ) -> None:
        """Test successful execution when components='otel2puml' and save
        events is True."""
        mock_fetch_data_holder.return_value = sql_data_holder_with_otel_jobs

        output_dir = tmp_path / "json_output"
        input_dir = tmp_path / "json_input"

        # Create the input directory
        input_dir.mkdir(parents=True, exist_ok=True)

        # Write mock_json_data to data.json in input_dir
        data_file = input_dir / "data.json"
        data_file.write_text(json.dumps(mock_json_data))

        # Configure config
        mock_yaml_config_dict["data_sources"]["json"]["dirpath"] = str(
            input_dir
        )
        mock_yaml_config_dict["data_sources"]["json"]["filepath"] = None
        config = load_config_from_dict(mock_yaml_config_dict)

        otel_options: OtelPVOptions = {
            "config": config,
            "ingest_data": False,
            "save_events": False,
            "find_unique_graphs": True,
        }

        otel_to_puml(
            otel_to_pv_options=otel_options,
            components="otel2puml",
            output_file_directory=str(output_dir),
        )

        assert output_dir.exists()

        assert data_file.exists()
        with open(data_file, "r") as f:
            data = json.load(f)
        assert data == mock_json_data

        assert os.listdir(output_dir) == ["test_name.puml"]
        puml_file_path = output_dir / "test_name.puml"
        expected_content = (
            "@startuml\n"
            '    partition "test_name" {\n'
            '        group "test_name"\n'
            "            :event_type_1;\n"
            "            :event_type_0;\n"
            "        end group\n"
            "    }\n"
            "@enduml"
        )
        with open(puml_file_path, "r") as f:
            content = f.read()
            content = content.strip()
            print(content)
            expected_content = expected_content.strip()
            assert content == expected_content

    @staticmethod
    @pytest.mark.parametrize(
        "output_puml_models", [True, False]
    )
    def test_otel2puml_input_puml_models(
        tmp_path: Path,
        mock_yaml_config_dict: dict[str, Any],
        mock_json_data: dict[str, Any],
        mock_event_model: dict[str, Any],
        output_puml_models: bool,
        expected_model_output: list[dict[str, Any]],
    ) -> None:
        """Test successful execution when components='otel2puml'."""

        output_dir = tmp_path / "puml_output"
        input_dir = tmp_path / "json_input"

        # Create the input directory
        input_dir.mkdir(parents=True, exist_ok=True)

        # Write mock_json_data to data.json in input_dir
        data_file = input_dir / "data.json"
        data_file.write_text(json.dumps(mock_json_data))

        # Configure config
        mock_yaml_config_dict["data_sources"]["json"]["dirpath"] = str(
            input_dir
        )
        mock_yaml_config_dict["data_sources"]["json"]["filepath"] = None
        config = load_config_from_dict(mock_yaml_config_dict)

        otel_options: OtelPVOptions = {
            "config": config,
            "ingest_data": True,
            "save_events": False,
            "find_unique_graphs": False,
        }
        input_puml_models_file = tmp_path / "input_puml_models.json"
        input_puml_models_file.write_text(json.dumps(mock_event_model))
        global_options: GlobalOptions = {
            "input_puml_models": [str(input_puml_models_file)],
            "output_puml_models": output_puml_models,
        }

        otel_to_puml(
            otel_to_pv_options=otel_options,
            global_options=global_options,
            components="otel2puml",
            output_file_directory=str(output_dir),
        )

        assert output_dir.exists()

        assert data_file.exists()
        with open(data_file, "r") as f:
            data = json.load(f)
        assert data == mock_json_data

        assert "Frontend_TestJob.puml" in os.listdir(output_dir)
        puml_file_path = output_dir / "Frontend_TestJob.puml"
        expected_content = (
            "@startuml\n"
            '    partition "Frontend_TestJob" {\n'
            '        group "Frontend_TestJob"\n'
            "            :com.C36.9ETRp_401;\n"
            "            :com.T2h.366Yx_500;\n"
            "            :TestEvent;\n"
            "        end group\n"
            "    }\n"
            "@enduml"
        )
        with open(puml_file_path, "r") as f:
            content = f.read()
            content = content.strip()
            expected_content = expected_content.strip()
            assert content == expected_content
        if output_puml_models:
            save_model_path = output_dir / "Frontend_TestJob_model.json"
            assert os.path.exists(save_model_path)
            with open(save_model_path, "r") as f:
                model_content = json.load(f)
                assert "job_name" in model_content
                assert model_content["job_name"] == "Frontend_TestJob"
                assert "events" in model_content
                assert (
                    sorted(
                        model_content["events"],
                        key=lambda x: x["eventType"],
                    )
                    == expected_model_output
                )

    @staticmethod
    @pytest.mark.parametrize(
        "output_puml_models", [True, False]
    )
    def test_pv_to_puml_input_puml_models(
        mock_job_json_file_for_event_model: list[dict[str, Any]],
        tmp_path: Path,
        mock_event_model: dict[str, Any],
        output_puml_models: bool,
        expected_model_output: list[dict[str, Any]],
    ) -> None:
        """Test successful execution when components='pv2puml'"""
        output_dir = tmp_path / "puml_output"
        input_dir = tmp_path / "job_json"

        input_dir.mkdir(parents=True, exist_ok=True)
        data_file = input_dir / "file1.json"
        data_file.write_text(json.dumps(mock_job_json_file_for_event_model))
        data_files = [str(data_file)]

        pv_to_puml_options: PVPumlOptions = {
            "file_list": data_files,
            "job_name": "Frontend_TestJob",
        }
        input_puml_models_file = tmp_path / "input_puml_models.json"
        input_puml_models_file.write_text(json.dumps(mock_event_model))
        global_options: GlobalOptions = {
            "input_puml_models": [str(input_puml_models_file)],
            "output_puml_models": output_puml_models,
        }

        otel_to_puml(
            pv_to_puml_options=pv_to_puml_options,
            global_options=global_options,
            components="pv2puml",
            output_file_directory=str(output_dir),
        )

        assert output_dir.exists()
        assert "Frontend_TestJob.puml" in os.listdir(output_dir)
        puml_file_path = output_dir / "Frontend_TestJob.puml"

        expected_content = (
            "@startuml\n"
            '    partition "Frontend_TestJob" {\n'
            '        group "Frontend_TestJob"\n'
            "            :com.C36.9ETRp_401;\n"
            "            :com.T2h.366Yx_500;\n"
            "            :TestEvent;\n"
            "        end group\n"
            "    }\n"
            "@enduml"
        )
        with open(puml_file_path, "r") as f:
            content = f.read()
            content = content.strip()
            expected_content = expected_content.strip()
            assert content == expected_content
        if output_puml_models:
            save_model_path = output_dir / "Frontend_TestJob_model.json"
            assert os.path.exists(save_model_path)
            with open(save_model_path, "r") as f:
                model_content = json.load(f)
                assert "job_name" in model_content
                assert model_content["job_name"] == "Frontend_TestJob"
                assert "events" in model_content
                assert (
                    sorted(
                        model_content["events"], key=lambda x: x["eventType"]
                    )
                    == expected_model_output
                )
