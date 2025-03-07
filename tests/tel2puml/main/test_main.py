"""Tests for the module __main__.py"""

import yaml
import os
import tempfile
from pathlib import Path
from typing import Literal, Any
from unittest.mock import Mock, patch
from json import JSONDecodeError

import pytest
from pydantic import ValidationError
from pytest import MonkeyPatch, CaptureFixture

from tel2puml.__main__ import (
    generate_config,
    find_files,
    generate_component_options,
    handle_exception,
    main_handler,
)
from tel2puml.otel_to_pv.data_sources.json_data_source.json_jq_converter \
    import JQCompileError, JQExtractionError
from tel2puml.tel2puml_types import GlobalOptions


def test_generate_config(tmp_path: Path) -> None:
    """Tests the function generate_config."""
    config_data = {"key": "value"}
    config_file = tmp_path / "config.yaml"

    with open(config_file, "w") as file:
        yaml.dump(config_data, file)

    result = generate_config(str(config_file))

    assert result == config_data


def test_find_files_with_nested_directories(tmp_path: Path) -> None:
    """Tests for the function find_files"""
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

    result = find_files(str(tmp_path))

    assert sorted(result) == sorted(
        [str(json_file_1), str(json_file_2), str(txt_file)]
    )


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
    otel_pv_options, pv_puml_options, global_options = (
        generate_component_options(command, args_dict)
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
    otel_pv_options, pv_puml_options, global_options = (
        generate_component_options(command, args_dict)
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
        otel_pv_options, pv_puml_options, global_options = (
            generate_component_options(command, args_dict)
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
        generate_component_options(
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
    otel_pv_options, pv_puml_options, global_options = (
        generate_component_options(command, args_dict)
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
        generate_component_options(
            command, args_dict
        )

    # Test 7: pv2puml, otel2puml, otel2pv command, with input_puml_models and
    # output_puml_models provided
    commands: list[Literal["pv2puml", "otel2puml", "otel2pv"]] = [
        "pv2puml",
        "otel2puml",
        "otel2pv",
    ]
    tmp_model_path = tmp_path / "file1.puml"
    tmp_model_path.write_text("")
    global_options_combinations: list[dict[str, Any]] = [
        {"input_puml_models": [tmp_model_path], "output_puml_models": True},
        {"input_puml_models": [tmp_model_path]},
        {"output_puml_models": True},
    ]
    for command_out in commands:
        for global_options_combo in global_options_combinations:
            args_dict = {
                "command": command_out,
                "folder_path": nested_dir_1,
                "config_file": str(mock_yaml_config_file),
                **global_options_combo,
            }
            if command_out == "otel2pv":
                with pytest.raises(ValidationError):
                    _ = generate_component_options(command_out, args_dict)
            else:
                otel_pv_options, pv_puml_options, global_options = (
                    generate_component_options(command_out, args_dict)
                )
                assert global_options is not None
                assert global_options == GlobalOptions(
                    input_puml_models=global_options_combo.get(
                        "input_puml_models", []
                    ),
                    output_puml_models=global_options_combo.get(
                        "output_puml_models", False
                    ),
                )


def test_handle_exception(
    monkeypatch: MonkeyPatch,
    capfd: CaptureFixture[str],
) -> None:
    """Tests the function handle_exception."""
    # Mock the exit function so that the test does not exit the test suite
    monkeypatch.setattr("builtins.exit", Mock())

    # Test 1: debug = True
    # Raises an exception with traceback
    try:
        raise Exception("Test exception")
    except Exception as e:
        handle_exception(e, debug=True)

    captured = capfd.readouterr()
    assert "DEBUG:" in captured.out
    assert "Traceback" in captured.out

    # Test 2: user error, debug = False
    try:
        raise Exception("User test error")
    except Exception as e:
        handle_exception(
            e, debug=False, user_error=True, custom_message="Custom error."
        )

    captured = capfd.readouterr()
    assert (
        "ERROR: Use the -d flag for more detailed information." in captured.out
    )
    assert "User error: Custom error." in captured.out

    # Test 3: no user error, debug = False
    try:
        raise Exception("Unexpected test error")
    except Exception as e:
        handle_exception(
            e,
            debug=False,
            user_error=False,
        )

    captured = capfd.readouterr()
    assert (
        "ERROR: Use the -d flag for more detailed information." in captured.out
    )
    assert (
        "Please raise an issue at https://github.com/xtuml/otel2puml"
        in captured.out
    )


def test_main_handler_error_handling(
    monkeypatch: MonkeyPatch,
    capfd: CaptureFixture[str],
) -> None:
    """Tests the main function"""
    # Mock the exit function so that the test does not exit the test suite
    monkeypatch.setattr("builtins.exit", Mock())
    args_dict = {
        "command": "otel2puml",
        "config_file": "invalid_config.yaml",
        "ingest_data": True,
        "find_unique_graphs": False,
        "output_file_directory": ".",
        "debug": False,
    }

    errors_lookup = {
        JQCompileError: "Error occurred during JQ compiling.",
        JQExtractionError: "Error occurred during JQ extraction.",
        JSONDecodeError: "Invalid JSON format detected. Please check your"
        " JSON files.",
        ValidationError: "Input validation failed. Please check the input"
        " data."
    }

    # Test 1: JQCompileError
    with patch(
        "tel2puml.__main__.generate_component_options"
    ) as mock_generate_options:
        mock_generate_options.side_effect = JQCompileError("Test error")

        main_handler(args_dict, errors_lookup)
        captured = capfd.readouterr()
        # Check if the correct error message was printed
        assert (
            "\nERROR: Use the -d flag for more detailed information."
        ) in captured.out
        assert (
            "User error: Error occurred during JQ compiling."
        ) in captured.out

    # Test 2: JQExtractionError
    with patch(
        "tel2puml.__main__.generate_component_options"
    ) as mock_generate_options:
        mock_generate_options.side_effect = JQExtractionError("Test error")

        main_handler(args_dict, errors_lookup)
        captured = capfd.readouterr()
        # Check if the correct error message was printed
        assert (
            "\nERROR: Use the -d flag for more detailed information."
        ) in captured.out
        assert (
            "User error: Error occurred during JQ extraction."
        ) in captured.out

    # Test 3: JSONDecodeError
    with patch(
        "tel2puml.__main__.generate_component_options"
    ) as mock_generate_options:
        mock_generate_options.side_effect = JSONDecodeError(
            "JSONDecodeError", "", 0
        )

        main_handler(args_dict, errors_lookup)
        captured = capfd.readouterr()
        # Check if the correct error message was printed
        assert (
            "\nERROR: Use the -d flag for more detailed information."
        ) in captured.out
        assert (
            "User error: Invalid JSON format detected. Please check your"
            " JSON files."
        ) in captured.out

    # Test 4: ValidationError
    with patch(
        "tel2puml.__main__.generate_component_options"
    ) as mock_generate_options:
        # Written like this as ValidationError in pydantic does not have a
        # constructor
        mock_generate_options.side_effect = (
            ValidationError.from_exception_data("Invalid data", line_errors=[])
        )

        main_handler(args_dict, errors_lookup)
        captured = capfd.readouterr()
        # Check if the correct error message was printed
        assert (
            "\nERROR: Use the -d flag for more detailed information."
        ) in captured.out
        assert (
            "User error: Input validation failed. Please check the input"
            " data."
        ) in captured.out

    # Test 5: Unexpected Exception
    with patch(
        "tel2puml.__main__.generate_component_options"
    ) as mock_generate_options:
        mock_generate_options.side_effect = Exception("Unexpected error")

        main_handler(args_dict, errors_lookup)
        captured = capfd.readouterr()
        # Check if the correct error message was printed
        assert (
            "\nERROR: Use the -d flag for more detailed information."
        ) in captured.out
        assert (
            "Please raise an issue at https://github.com/xtuml/otel2puml."
        ) in captured.out
