"""Tests for the module __main__.py"""

import yaml
from pathlib import Path

import pytest

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


def test_find_json_files_with_nested_directories(tmp_path: Path):
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
