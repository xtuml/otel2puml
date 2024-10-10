"""Test the tel2puml.otel_to_pv.otel_to_pv module."""

import os
import json
from pathlib import Path
from typing import Any, Generator

import yaml
import pytest
import sqlalchemy as sa
from pytest import MonkeyPatch

from tel2puml.otel_to_pv.otel_to_pv import (
    otel_to_pv,
    handle_save_events,
    save_pv_event_stream_to_file,
)
from tel2puml.otel_to_pv.data_holders.sql_data_holder.sql_dataholder import (
    SQLDataHolder,
)
from tel2puml.otel_to_pv.config import (
    IngestDataConfig,
    IngestTypes,
    SequenceModelConfig,
)
from tel2puml.otel_to_pv.otel_to_pv_types import OTelEventTypeMap
from tel2puml.otel_to_pv.data_holders.sql_data_holder.data_model import (
    NodeModel,
)
from tel2puml.tel2puml_types import PVEvent


class TestOtelToPV:
    """Tests for the otel_to_pv function."""

    def get_ingest_config(
        self, config_yaml: str, new_dirpath: Path
    ) -> IngestDataConfig:
        """Updates the dirpath in the config yaml string."""
        update_config_yaml_string = config_yaml.replace(
            "dirpath: /path/to/json/directory", f"dirpath: {new_dirpath}"
        ).replace("filepath: /path/to/json/file.json", "filepath: null")
        config_dict: dict[str, Any] = yaml.safe_load(update_config_yaml_string)
        config = IngestDataConfig(
            data_sources=config_dict["data_sources"],
            data_holders=config_dict["data_holders"],
            ingest_data=IngestTypes(**config_dict["ingest_data"]),
        )
        return config

    def test_otel_to_pv(
        self,
        monkeypatch: MonkeyPatch,
        mock_yaml_config_dict: dict[str, Any],
        sql_data_holder_with_otel_jobs: SQLDataHolder,
        mock_yaml_config_string: str,
        mock_temp_dir_with_json_files: Path,
        event_to_async_group_map: dict[str, dict[str, str]],
    ) -> None:
        """Tests for the function otel_to_pv."""
        time_buffer = 0

        # Test 1: Default parameters
        def mock_fetch_data_holder(config: IngestDataConfig) -> SQLDataHolder:
            sql_data_holder = sql_data_holder_with_otel_jobs
            sql_data_holder.time_buffer = time_buffer
            return sql_data_holder

        ingest_data_config = IngestDataConfig(
            data_sources=mock_yaml_config_dict["data_sources"],
            data_holders=mock_yaml_config_dict["data_holders"],
            ingest_data=IngestTypes(**mock_yaml_config_dict["ingest_data"]),
        )
        monkeypatch.setattr(
            "tel2puml.otel_to_pv.otel_to_pv.fetch_data_holder",
            mock_fetch_data_holder,
        )
        # make the time buffer 0 to retrieve all events
        result = otel_to_pv(ingest_data_config)

        events = []
        valid_event_ids = [f"{i}_{j}" for i in range(5) for j in range(2)]
        valid_job_ids = {f"test_id_{i}" for i in range(5)}
        job_id_count: dict[str, int] = {}
        for job_name, pv_event_streams in result:
            assert job_name == "test_name"
            for pv_event_gen in pv_event_streams:
                for pv_event in pv_event_gen:
                    job_id_count.setdefault(pv_event["jobId"], 0)
                    job_id_count[pv_event["jobId"]] += 1
                    events.append(pv_event)
                    assert pv_event["eventId"] in valid_event_ids
                    assert pv_event["jobId"] in valid_job_ids
                    valid_event_ids.remove(pv_event["eventId"])

        assert len(events) == 10
        assert all(job_id_count[job_id] == 2 for job_id in valid_job_ids)
        assert len(valid_event_ids) == 0

        # Test 2: ingest_data = True
        config = self.get_ingest_config(
            mock_yaml_config_string, mock_temp_dir_with_json_files
        )
        result = otel_to_pv(config, ingest_data=True)

        events = []
        valid_job_names = ["Backend_TestJob", "Frontend_TestJob"]
        valid_job_ids = {
            "0_trace_id_1_4.8",
            "1_trace_id_1_4.8",
            "0_trace_id_0_4.8",
            "1_trace_id_0_4.8",
        }
        valid_event_ids = [
            f"{i}_span_{j}_{k}"
            for i in range(2)
            for j in range(2)
            for k in range(2)
        ]
        job_id_count = {}
        for i, (job_name, pv_event_streams) in enumerate(result):
            assert job_name == valid_job_names[i]
            for pv_event_gen in pv_event_streams:
                for pv_event in pv_event_gen:
                    job_id_count.setdefault(pv_event["jobId"], 0)
                    job_id_count[pv_event["jobId"]] += 1
                    events.append(pv_event)
                    assert pv_event["eventId"] in valid_event_ids
                    assert pv_event["jobId"] in valid_job_ids
                    valid_event_ids.remove(pv_event["eventId"])

        assert len(events) == 8
        assert all(job_id_count[job_id] == 2 for job_id in valid_job_ids)
        assert len(valid_event_ids) == 0

        # Test 3: find_unique_graphs = True
        time_buffer = 0
        result = otel_to_pv(ingest_data_config, find_unique_graphs=True)
        num_events = 0
        # job id test_id_0 is outside the config time buffer window, therefore
        # it is not included, reducing total events streamed to 8
        valid_event_ids = ["0_1", "0_0"]
        for job_name, pv_event_streams in result:
            assert job_name == "test_name"
            for pv_event_gen in pv_event_streams:
                for pv_event in pv_event_gen:
                    assert pv_event["jobId"] == "test_id_0"
                    num_events += 1
                    assert pv_event["eventId"] in valid_event_ids
                    valid_event_ids.remove(pv_event["eventId"])

        assert num_events == 2
        assert len(valid_event_ids) == 0

        # Test 4: async_flag = True
        # time_buffer = 0
        ingest_config_copy = ingest_data_config.copy()
        ingest_config_copy["sequencer"] = SequenceModelConfig(async_flag=True)
        result = otel_to_pv(ingest_config_copy)
        events = []
        valid_event_ids = [f"{i}_{j}" for i in range(5) for j in range(2)]
        valid_job_ids = {f"test_id_{i}" for i in range(5)}
        job_id_count = {}
        for job_name, pv_event_streams in result:
            assert job_name == "test_name"
            for pv_event_gen in pv_event_streams:
                for pv_event in pv_event_gen:
                    job_id_count.setdefault(pv_event["jobId"], 0)
                    job_id_count[pv_event["jobId"]] += 1
                    events.append(pv_event)
                    assert pv_event["eventId"] in valid_event_ids
                    assert pv_event["jobId"] in valid_job_ids
                    valid_event_ids.remove(pv_event["eventId"])

        assert len(events) == 10
        assert all(job_id_count[job_id] == 2 for job_id in valid_job_ids)
        assert len(valid_event_ids) == 0

        # Test 5: event_to_async_group_map provided in config
        ingest_data_config["sequencer"] = SequenceModelConfig(
            async_event_groups={
                "test_name": event_to_async_group_map,
            }
        )
        result = otel_to_pv(
            ingest_data_config,
        )
        events = []
        valid_event_ids = [f"{i}_{j}" for i in range(5) for j in range(2)]
        valid_job_ids = {f"test_id_{i}" for i in range(5)}
        job_id_count = {}
        for job_name, pv_event_streams in result:
            assert job_name == "test_name"
            for pv_event_gen in pv_event_streams:
                for pv_event in pv_event_gen:
                    job_id_count.setdefault(pv_event["jobId"], 0)
                    job_id_count[pv_event["jobId"]] += 1
                    events.append(pv_event)
                    assert pv_event["eventId"] in valid_event_ids
                    assert pv_event["jobId"] in valid_job_ids
                    valid_event_ids.remove(pv_event["eventId"])

        assert len(events) == 10
        assert all(job_id_count[job_id] == 2 for job_id in valid_job_ids)
        assert len(valid_event_ids) == 0
        # Test 6: event_name_map_information provided in config
        ingest_data_config["sequencer"] = SequenceModelConfig(
            event_name_map_information={
                "test_name": {
                    "event_type_0": OTelEventTypeMap(
                        mapped_event_type="test_event_type",
                        child_event_types={"event_type_1"},
                    )
                }
            }
        )
        result = otel_to_pv(
            ingest_data_config,
        )
        events = []
        valid_event_ids = [f"{i}_{j}" for i in range(5) for j in range(2)]
        valid_job_ids = {f"test_id_{i}" for i in range(5)}
        job_id_count = {}
        for job_name, pv_event_streams in result:
            assert job_name == "test_name"
            for pv_event_gen in pv_event_streams:
                for pv_event in pv_event_gen:
                    job_id_count.setdefault(pv_event["jobId"], 0)
                    job_id_count[pv_event["jobId"]] += 1
                    events.append(pv_event)
                    assert pv_event["eventId"] in valid_event_ids
                    assert pv_event["jobId"] in valid_job_ids
                    valid_event_ids.remove(pv_event["eventId"])
                    if pv_event["eventId"] in {f"{i}_0" for i in range(5)}:
                        assert pv_event["eventType"] == "test_event_type"
                    else:
                        assert pv_event["eventType"] == "event_type_1"

        # Test 7: Remove disconnected spans
        def mock_fetch_data_holder_disconnected_spans(
            config: IngestDataConfig,
        ) -> SQLDataHolder:
            """Remove root span to create disconnected data within NodeModel
            table"""
            sql_data_holder = sql_data_holder_with_otel_jobs
            sql_data_holder.time_buffer = time_buffer
            with sql_data_holder.session as session:
                stmt = sa.delete(NodeModel).where(NodeModel.event_id == "4_0")
                session.execute(stmt)
                session.commit()
            return sql_data_holder

        ingest_data_config = IngestDataConfig(
            data_sources=mock_yaml_config_dict["data_sources"],
            data_holders=mock_yaml_config_dict["data_holders"],
            ingest_data=IngestTypes(**mock_yaml_config_dict["ingest_data"]),
        )
        monkeypatch.setattr(
            "tel2puml.otel_to_pv.otel_to_pv.fetch_data_holder",
            mock_fetch_data_holder_disconnected_spans,
        )

        result = otel_to_pv(ingest_data_config)
        events = []
        valid_event_ids = [f"{i}_{j}" for i in range(4) for j in range(2)]
        valid_job_ids = {f"test_id_{i}" for i in range(4)}
        job_id_count = {}
        for job_name, pv_event_streams in result:
            assert job_name == "test_name"
            for pv_event_gen in pv_event_streams:
                for pv_event in pv_event_gen:
                    job_id_count.setdefault(pv_event["jobId"], 0)
                    job_id_count[pv_event["jobId"]] += 1
                    events.append(pv_event)
                    assert pv_event["eventId"] in valid_event_ids
                    assert pv_event["jobId"] in valid_job_ids
                    valid_event_ids.remove(pv_event["eventId"])

        assert len(events) == 8
        assert all(job_id_count[job_id] == 2 for job_id in valid_job_ids)
        assert len(valid_event_ids) == 0

        # Test 8: Remove jobs outside of time window
        # (accounting for already removed jobs)
        time_buffer = 1
        result = otel_to_pv(ingest_data_config)

        events = []
        valid_event_ids = [f"{i}_{j}" for i in range(1, 4) for j in range(2)]
        valid_job_ids = {f"test_id_{i}" for i in range(1, 4)}
        job_id_count = {}
        for job_name, pv_event_streams in result:
            assert job_name == "test_name"
            for pv_event_gen in pv_event_streams:
                for pv_event in pv_event_gen:
                    job_id_count.setdefault(pv_event["jobId"], 0)
                    job_id_count[pv_event["jobId"]] += 1
                    events.append(pv_event)
                    assert pv_event["eventId"] in valid_event_ids
                    assert pv_event["jobId"] in valid_job_ids
                    valid_event_ids.remove(pv_event["eventId"])

        assert len(events) == 6
        assert all(job_id_count[job_id] == 2 for job_id in valid_job_ids)
        assert len(valid_event_ids) == 0

    def test_otel_to_pv_save_events(
        self,
        monkeypatch: MonkeyPatch,
        mock_yaml_config_dict: dict[str, Any],
        sql_data_holder_with_otel_jobs: SQLDataHolder,
        tmp_path: Path,
        expected_job_json_content: list[dict[str, Any]],
    ) -> None:
        """Tests the save_events flag for the function otel_to_pv."""

        def mock_fetch_data_holder(config: IngestDataConfig) -> SQLDataHolder:
            sql_data_holder = sql_data_holder_with_otel_jobs
            sql_data_holder.time_buffer = 1
            return sql_data_holder

        output_dir = tmp_path / "json_output"
        ingest_data_config = IngestDataConfig(
            data_sources=mock_yaml_config_dict["data_sources"],
            data_holders=mock_yaml_config_dict["data_holders"],
            ingest_data=IngestTypes(**mock_yaml_config_dict["ingest_data"]),
        )
        monkeypatch.setattr(
            "tel2puml.otel_to_pv.otel_to_pv.fetch_data_holder",
            mock_fetch_data_holder,
        )

        result_gen = otel_to_pv(
            ingest_data_config,
            save_events=True,
            output_file_directory=str(output_dir),
        )
        # check pv_event_gen is exhausted
        assert list(result_gen) == []

        json_file_dir = tmp_path / "json_output" / "test_name"
        assert json_file_dir.exists()
        files = list(json_file_dir.iterdir())
        assert len(files) == 4

        # 4 files, each with an array of 2 jobs
        for i in range(4):
            file_path = json_file_dir / f"pv_event_sequence_{i+1}.json"

            assert file_path.exists()

            with file_path.open("r") as f:
                file_content = json.load(f)
                assert (
                    file_content
                    == expected_job_json_content[(2 * i): (2 * i) + 2]
                )


class TestSavePVEventStreamsToFile:
    """Tests for the save_pv_event_stream_to_file function."""

    def test_save_pv_event_stream_to_file_success(
        self, tmp_path: Path
    ) -> None:
        """Test that PVEvents are saved correctly to a file."""
        job_name = "test_job"
        pv_event: PVEvent = {
            "jobId": "test_job_id",
            "eventId": "1",
            "timestamp": "2024-10-08T12:00:00Z",
            "applicationName": "test_app",
            "jobName": "test_job",
            "eventType": "test_event_A",
        }
        pv_event_2: PVEvent = {
            "jobId": "test_job_id",
            "eventId": "2",
            "timestamp": "2024-10-08T12:00:00Z",
            "previousEventIds": ["1"],
            "applicationName": "test_app",
            "jobName": "test_job",
            "eventType": "test_event_B",
        }
        pv_stream = (pv_event for pv_event in [pv_event, pv_event_2])
        output_dir = tmp_path
        count = 1

        job_dir = output_dir / job_name
        job_dir.mkdir(parents=True, exist_ok=True)

        save_pv_event_stream_to_file(
            job_name,
            pv_stream,
            str(output_dir),
            count,
        )

        expected_file = job_dir / f"pv_event_sequence_{count}.json"
        assert expected_file.exists()

        with expected_file.open("r") as f:
            file_content = json.load(f)
            assert file_content == [pv_event, pv_event_2]

    def test_save_pv_event_to_file_io_error(self, tmp_path: Path) -> None:
        """Test that IOError is handled correctly when writing the file."""
        job_name = "test_job"
        pv_event: PVEvent = {
            "jobId": "test_job_id",
            "eventId": "3",
            "timestamp": "2024-10-08T12:10:00Z",
            "applicationName": "test_app",
            "jobName": "test_job",
            "eventType": "test_event_error",
        }
        pv_stream = (pv_event for pv_event in [pv_event])
        output_dir = tmp_path
        count = 3

        # Create a directory and make it read-only to simulate IOError
        job_dir = output_dir / job_name
        job_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(job_dir, 0o400)

        try:
            with pytest.raises(IOError):
                save_pv_event_stream_to_file(
                    job_name,
                    pv_stream,
                    str(output_dir),
                    count,
                )
        finally:
            # Restore permissions to delete the temp directory
            os.chmod(job_dir, 0o700)


class TestHandleSaveEvents:
    """Tests for the handle_save_events function."""

    def test_handle_save_events_success(self, tmp_path: Path) -> None:
        """Test that handle_save_events saves all PVEvents correctly."""
        job_name = "test_job"
        output_dir = tmp_path

        pv_event_streams: list[list[PVEvent]] = [
            [
                {
                    "jobId": "test_job_id",
                    "eventId": "1",
                    "timestamp": "2024-10-08T12:00:00Z",
                    "applicationName": "test_app",
                    "jobName": "test_job",
                    "eventType": "test_event",
                },
                {
                    "jobId": "test_job_id",
                    "eventId": "2",
                    "timestamp": "2024-10-08T12:05:00Z",
                    "previousEventIds": ["1"],
                    "applicationName": "test_app",
                    "jobName": "test_job",
                    "eventType": "test_event_followup",
                },
            ],
            [
                {
                    "jobId": "test_job_id",
                    "eventId": "3",
                    "timestamp": "2024-10-08T12:10:00Z",
                    "applicationName": "test_app",
                    "jobName": "test_job",
                    "eventType": "test_event_second_followup",
                }
            ],
        ]

        def event_streams_gen() -> (
            Generator[Generator[PVEvent, Any, None], Any, None]
        ):
            for stream in pv_event_streams:
                yield (event for event in stream)

        handle_save_events(job_name, event_streams_gen(), str(output_dir))

        job_dir = output_dir / job_name
        assert job_dir.exists() and job_dir.is_dir()

        for i, expected_pv_event in enumerate(
            [events for events in pv_event_streams],
            start=1,
        ):
            file_path = job_dir / f"pv_event_sequence_{i}.json"
            assert file_path.exists()
            with file_path.open("r") as f:
                file_content = json.load(f)
                assert file_content == expected_pv_event

    def test_handle_save_events_os_error(self, tmp_path: Path) -> None:
        """
        Test that handle_save_events handles OSError when creating directories
        by making the output directory non-writable.
        """
        job_name = "test_job"

        non_writable_dir = tmp_path / "non_writable_dir"
        non_writable_dir.mkdir(parents=True, exist_ok=True)

        # Remove write permissions from the output directory
        non_writable_dir.chmod(0o555)

        try:
            pv_event_streams: list[list[PVEvent]] = []

            def event_streams_gen() -> (
                Generator[Generator[PVEvent, Any, None], Any, None]
            ):
                for stream in pv_event_streams:
                    yield (event for event in stream)

            with pytest.raises(OSError):
                handle_save_events(
                    job_name, event_streams_gen(), str(non_writable_dir)
                )

        finally:
            # Restore write permissions to allow pytest to clean up the
            # temporary directory
            non_writable_dir.chmod(0o755)

    def test_handle_save_events_empty_stream(self, tmp_path: Path) -> None:
        """Test that handle_save_events works correctly with an empty
        PVEvent stream."""
        job_name = "test_job"
        output_dir = tmp_path

        pv_event_streams: list[list[PVEvent]] = []

        def event_streams_gen() -> (
            Generator[Generator[PVEvent, Any, None], Any, None]
        ):
            for stream in pv_event_streams:
                yield (event for event in stream)

        handle_save_events(job_name, event_streams_gen(), str(output_dir))

        job_dir = output_dir / job_name
        assert job_dir.exists() and job_dir.is_dir()

        assert not any(job_dir.iterdir())
