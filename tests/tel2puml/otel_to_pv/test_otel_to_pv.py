"""Test the tel2puml.otel_to_pv.otel_to_pv module."""

from pathlib import Path
from typing import Any

import yaml
import sqlalchemy as sa
from pytest import MonkeyPatch

from tel2puml.otel_to_pv.otel_to_pv import otel_to_pv
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

        # Test 1: Default parameters
        def mock_fetch_data_holder(config: IngestDataConfig) -> SQLDataHolder:
            return sql_data_holder_with_otel_jobs

        ingest_data_config = IngestDataConfig(
            data_sources=mock_yaml_config_dict["data_sources"],
            data_holders=mock_yaml_config_dict["data_holders"],
            ingest_data=IngestTypes(**mock_yaml_config_dict["ingest_data"]),
        )
        monkeypatch.setattr(
            "tel2puml.otel_to_pv.otel_to_pv.fetch_data_holder",
            mock_fetch_data_holder,
        )

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
        result = otel_to_pv(ingest_data_config, find_unique_graphs=True)

        num_events = 0
        # job id test_id_0 is outside the config time buffer window, therefore
        # it is not included, reducing total events streamed to 8
        valid_event_ids = ["1_1", "1_0"]
        for job_name, pv_event_streams in result:
            assert job_name == "test_name"
            for pv_event_gen in pv_event_streams:
                for pv_event in pv_event_gen:
                    assert pv_event["jobId"] == "test_id_1"
                    num_events += 1
                    assert pv_event["eventId"] in valid_event_ids
                    valid_event_ids.remove(pv_event["eventId"])

        assert num_events == 2
        assert len(valid_event_ids) == 0

        # Test 4: async_flag = True
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
            with sql_data_holder.session as session:
                stmt = sa.delete(NodeModel).where(NodeModel.event_id == "0_0")
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
        valid_event_ids = [f"{i}_{j}" for i in range(1, 5) for j in range(2)]
        valid_job_ids = {f"test_id_{i}" for i in range(1, 5)}
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
