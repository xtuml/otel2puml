"""Tests for the module __main__.py"""

import yaml
import os
import tempfile
from pathlib import Path
from typing import Literal

import pytest
from pydantic import ValidationError

from tel2puml.__main__ import (
    generate_config,
    find_json_files,
    generate_component_options,
)


def test_generate_config(tmp_path: Path) -> None:
    """Tests the function generate_config."""
    config_data = {"key": "value"}
    config_file = tmp_path / "config.yaml"

    with open(config_file, "w") as file:
        yaml.dump(config_data, file)

    result = generate_config(str(config_file))

    assert result == config_data


def test_find_json_files_with_nested_directories(tmp_path: Path) -> None:
    """Tests for the function find_json_files"""
    nested_dir_1 = tmp_path / "dir1"
    nested_dir_1.mkdir()

    nested_dir_2 = nested_dir_1 / "dir2"
    nested_dir_2.mkdir()

    json_file_1 = nested_dir_1 / "file1.json"
    json_file_1.write_text("{}")

    json_file_2 = nested_dir_2 / "file2.json"
    json_file_2.write_text("{}")

    txt_file = nested_dir_1 / "file.txt"
    txt_file.write_text("This is a text file")

    result = find_json_files(str(tmp_path))

    assert sorted(result) == sorted([str(json_file_1), str(json_file_2)])


def test_generate_components_options(
    mock_yaml_config_file: Path, tmp_path: Path
) -> None:
    """Tests the function generate_component_options"""

    # Test 1: otel2puml command
    command: Literal["otel2puml", "otel2pv", "pv2puml"] = "otel2puml"
    args_dict = {
        "command": "otel2puml",
        "output_file_directory": ".",
        "config_file": str(mock_yaml_config_file),
        "ingest_data": True,
        "find_unique_graphs": False,
    }
    otel_pv_options, pv_puml_options = generate_component_options(
        command, args_dict
    )
    assert otel_pv_options
    assert otel_pv_options["config"]
    assert otel_pv_options["ingest_data"]
    assert pv_puml_options is None

    # Test 2: otel2pv command
    command = "otel2pv"
    args_dict = {
        "command": "otel2pv",
        "output_file_directory": ".",
        "config_file": str(mock_yaml_config_file),
        "ingest_data": False,
        "find_unique_graphs": False,
    }
    otel_pv_options, pv_puml_options = generate_component_options(
        command, args_dict
    )
    assert otel_pv_options
    assert otel_pv_options["config"]
    assert not otel_pv_options["ingest_data"]
    assert pv_puml_options is None

    # Test 3: pv2puml command, file_paths provided
    command = "pv2puml"
    with tempfile.NamedTemporaryFile(suffix=".json") as tmp_file:
        args_dict = {
            "command": "pv2puml",
            "output_file_directory": ".",
            "folder_path": None,
            "file_paths": [tmp_file.name],
            "job_name": "job_001",
            "group_by_job": False,
        }
        otel_pv_options, pv_puml_options = generate_component_options(
            command, args_dict
        )
        assert otel_pv_options is None
        assert pv_puml_options
        assert pv_puml_options["file_list"] == [tmp_file.name]
        assert pv_puml_options["job_name"] == "job_001"
        assert not pv_puml_options["group_by_job_id"]

    # Test 4: pv2puml command, empty file_paths provided
    command = "pv2puml"
    args_dict = {
        "command": "pv2puml",
        "output_file_directory": ".",
        "folder_path": None,
        "file_paths": [],
        "job_name": "job_001",
        "group_by_job": False,
    }
    with pytest.raises(ValidationError):
        otel_pv_options, pv_puml_options = generate_component_options(
            command, args_dict
        )

    # Test 5: pv2puml command, directory provided
    nested_dir_1 = tmp_path / "dir1"
    nested_dir_1.mkdir()

    json_file_1 = nested_dir_1 / "file1.json"
    json_file_1.write_text("{}")
    args_dict = {
        "command": "pv2puml",
        "output_file_directory": ".",
        "folder_path": nested_dir_1,
        "file_paths": None,
        "job_name": "job_002",
        "group_by_job": True,
    }
    otel_pv_options, pv_puml_options = generate_component_options(
        command, args_dict
    )
    assert otel_pv_options is None
    assert pv_puml_options
    assert pv_puml_options["file_list"] == [
        os.path.join(nested_dir_1, json_file_1)
    ]
    assert pv_puml_options["job_name"] == "job_002"
    assert pv_puml_options["group_by_job_id"]

    # Test 6: pv2puml command, empty directory provided
    nested_dir_2 = tmp_path / "dir2"
    nested_dir_2.mkdir()

    args_dict = {
        "command": "pv2puml",
        "output_file_directory": ".",
        "folder_path": nested_dir_2,
        "file_paths": None,
        "job_name": "job_003",
        "group_by_job": True,
    }
    with pytest.raises(FileNotFoundError):
        otel_pv_options, pv_puml_options = generate_component_options(
            command, args_dict
        )
