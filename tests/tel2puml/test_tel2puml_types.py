"""Tests for the pydantic models within tel2puml_types.py"""

import tempfile
from typing import Any

import pytest
from pydantic import ValidationError

from tel2puml.tel2puml_types import OtelToPVArgs, PvToPumlArgs, PVEventModel


@pytest.mark.parametrize("command", ["otel2pv", "otel2puml"])
def test_otel_to_pv_args(command: str) -> None:
    """Tests for the pydantic model OtelToPVArgs"""

    # Test 1: Valid inputs for otel2pv
    with tempfile.NamedTemporaryFile(suffix=".yaml") as tmp_file:
        args = OtelToPVArgs(config_file=tmp_file.name, command=command)
        assert str(args.config_file) == tmp_file.name
        assert args.ingest_data is True
        assert args.find_unique_graphs is False
        assert args.save_events is False

    # Test 2: Incorrect file extension for config file
    with tempfile.NamedTemporaryFile(suffix=".incorrect") as tmp_file:
        with pytest.raises(ValidationError):
            args = OtelToPVArgs(config_file=tmp_file.name, command=command)

    # Test 3: Check error handling with save_events=True, command=otel2puml
    if command == "otel2puml":
        with tempfile.NamedTemporaryFile(suffix=".yaml") as tmp_file:
            with pytest.raises(ValidationError):
                args = OtelToPVArgs(
                    config_file=tmp_file.name,
                    command="otel2puml",
                    save_events=True,
                )

    # Test 4: Non-existant file
    with pytest.raises(ValidationError):
        OtelToPVArgs(config_file="nonexistent.yaml", command="otel2puml")

    # Test 5: Test config file not a filepath
    with pytest.raises(ValidationError):
        OtelToPVArgs(config_file=123, command=command)

    # Test 6: Test with non-boolean values
    with pytest.raises(ValidationError):
        with tempfile.NamedTemporaryFile(suffix=".yaml") as tmp_file:
            args = OtelToPVArgs(
                config_file=tmp_file.name,
                command="otel2puml",
                save_events=0,
                find_unique_graphs=0,
            )


def test_pv_to_puml_args() -> None:
    """Tests for the pydantic model PvToPumlArgs"""

    # Test 1: Valid filepaths
    with tempfile.NamedTemporaryFile(
        suffix=".txt"
    ) as tmp_file1, tempfile.NamedTemporaryFile(suffix=".json") as tmp_file2:
        file_paths = [tmp_file1.name, tmp_file2.name]
        args = PvToPumlArgs(file_paths=file_paths)
        assert args.file_paths is not None
        assert [str(filepath) for filepath in args.file_paths] == file_paths
        assert args.folder_path is None
        assert args.job_name == "default_name"
        assert args.group_by_job is False

    # Test 2: Valid folderpath
    with tempfile.TemporaryDirectory() as tmp_dir:
        args = PvToPumlArgs(folder_path=tmp_dir)
        assert str(args.folder_path) == tmp_dir
        assert args.file_paths is None
        assert args.job_name == "default_name"
        assert args.group_by_job is False

    # Test 3: Invalid folderpath
    with pytest.raises(ValidationError):
        PvToPumlArgs(folder_path="nonexistent_directory")

    # Test 4: Filepath and Folderpath provided
    with tempfile.NamedTemporaryFile(
        suffix=".json"
    ) as tmp_file1, tempfile.TemporaryDirectory() as tmp_dir:
        file_paths = [tmp_file1.name]
        with pytest.raises(ValidationError):
            args = PvToPumlArgs(file_paths=file_paths, folder_path=tmp_dir)

    # Test 5: Filepath and Folderpath not provided
    with pytest.raises(ValidationError):
        args = PvToPumlArgs(file_paths=None, folder_path=None)

    # Test 6: Test invalid job name
    with pytest.raises(ValidationError):
        with tempfile.NamedTemporaryFile(suffix=".json") as tmp_file2:
            args = PvToPumlArgs(
                file_paths=[tmp_file2.name], folder_path=None, job_name=123
            )

    # Test 7: Test with non-boolean values
    with pytest.raises(ValidationError):
        with tempfile.NamedTemporaryFile(suffix=".json") as tmp_file3:
            args = PvToPumlArgs(
                file_paths=[tmp_file3.name], folder_path=None, group_by_job=0
            )


def test_pv_event_model() -> None:
    """Test for the pydantic model PVEventModel"""

    # Test 1: Valid PVEventModel
    event_data: dict[str, Any] = {
        "jobId": "job123",
        "eventId": "event123",
        "timestamp": "2023-01-01T00:00:00Z",
        "applicationName": "app",
        "jobName": "job",
        "eventType": "type",
    }
    event = PVEventModel(**event_data)
    assert event.jobId == "job123"
    assert event.eventId == "event123"
    assert event.timestamp == "2023-01-01T00:00:00Z"
    assert event.previousEventIds == []
    assert event.applicationName == "app"
    assert event.jobName == "job"
    assert event.eventType == "type"

    # Test 2: Invalid PVEventModel - incorrect type for previousEventIds
    with pytest.raises(ValidationError):
        PVEventModel(
            jobId="job123",
            eventId="event123",
            timestamp="2023-01-01T00:00:00Z",
            applicationName="app",
            jobName="job",
            eventType="type",
            previousEventIds=123,
        )

    # Test 3: Valid PVEventModel with previousEventIds as a string
    event_data["previousEventIds"] = "prev_event"
    event = PVEventModel(**event_data)
    assert event.previousEventIds == ["prev_event"]

    # Test 4: Valid PVEventModel with previousEventIds as a list
    event_data["previousEventIds"] = ["prev_event1", "prev_event2"]
    event = PVEventModel(**event_data)
    assert event.previousEventIds == ["prev_event1", "prev_event2"]
