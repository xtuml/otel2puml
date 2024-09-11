"""Tests for ingest_data module."""
from pathlib import Path
from typing import Any

import yaml
import pytest

from tel2puml.otel_to_pv.ingest_otel_data import (
    IngestData,
    fetch_data_source,
    fetch_data_holder,
    ingest_data_into_dataholder
)
from tel2puml.otel_to_pv.data_holders.sql_data_holder.data_model import (
    IngestDataConfig,
    NodeModel,
    IngestTypes
)
from tel2puml.otel_to_pv.data_holders import SQLDataHolder
from tel2puml.otel_to_pv.data_sources import (
    JSONDataSource,
)


class TestIngestData:
    """Collection of tests for IngestData class."""
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

    def check_data_holder_after_load(self, data_holder: SQLDataHolder) -> None:
        """Checks the data holder after data is loaded."""
        with data_holder.session as session:
            # Check expected event ids for nodes in the database
            # Event IDs set in conftest, with 2x2x2 structure for file_no,
            # no_resource_spans and no_spans
            nodes = session.query(NodeModel).all()
            assert len(nodes) == 8

            headers = {
                "names": ["Frontend", "Backend"],
                "versions": ["1.0", "2.0"],
            }

            expected_nodes = {
                f"{i}_span_{j}_{k}": {
                    "job_name": f"{headers['names'][j]} TestJob",
                    "job_id": f"{i}_trace_id_{j} 4.8",
                    "event_type": f"namespace_{j}_{k} 200",
                    "event_id": f"{i}_span_{j}_{k}",
                    "start_timestamp": 1723544132228288000,
                    "end_timestamp": 1723544132229038947,
                    "application_name": f"service_{j}_{k}"
                    f" {headers['versions'][j]}",
                    "parent_event_id": (
                        f"{i}_span_{j}_{k-1}" if k > 0 else None
                    ),
                }
                for i in range(2)
                for j in range(2)
                for k in range(2)
            }

            for node in nodes:
                assert (
                    node.job_name
                    == expected_nodes[str(node.event_id)]["job_name"]
                )
                assert (
                    node.job_id == expected_nodes[str(node.event_id)]["job_id"]
                )
                assert (
                    node.event_type
                    == expected_nodes[str(node.event_id)]["event_type"]
                )
                assert (
                    node.event_id
                    == expected_nodes[str(node.event_id)]["event_id"]
                )
                assert (
                    node.start_timestamp
                    == expected_nodes[str(node.event_id)]["start_timestamp"]
                )
                assert (
                    node.end_timestamp
                    == expected_nodes[str(node.event_id)]["end_timestamp"]
                )
                assert (
                    node.application_name
                    == expected_nodes[str(node.event_id)]["application_name"]
                )
                assert (
                    node.parent_event_id
                    == expected_nodes[str(node.event_id)]["parent_event_id"]
                )

            # Check relationships
            event_id_to_nodes = {node.event_id: node for node in nodes}
            for node in nodes:
                if node.parent_event_id:
                    # Check child relations
                    parent_node = event_id_to_nodes[node.parent_event_id]
                    assert parent_node.children == [node]

    def test_load_data_to_data_holder(
        self,
        mock_yaml_config_string: str,
        mock_temp_dir_with_json_files: Path,
    ) -> None:
        """Integration test for IngestData class using SQLDataHolder and
        JSONDataSource classes.
        """

        # Update config to point to temp directory
        config = self.get_ingest_config(
            mock_yaml_config_string, mock_temp_dir_with_json_files
        )

        data_holder = SQLDataHolder(config["data_holders"]["sql"])
        data_source = JSONDataSource(config["data_sources"]["json"])
        with data_holder.session as session:
            # Check no nodes in the database
            assert not session.query(NodeModel).all()
        ingest_data = IngestData(data_source, data_holder)
        ingest_data.load_to_data_holder()
        self.check_data_holder_after_load(data_holder)

    def test_ingest_data_into_dataholder(
        self,
        mock_yaml_config_string: str,
        mock_temp_dir_with_json_files: Path,
    ) -> None:
        """Integration test for ingest_data_into_dataholder function."""

        # Update config to point to temp directory
        config = self.get_ingest_config(
            mock_yaml_config_string, mock_temp_dir_with_json_files
        )
        data_holder = ingest_data_into_dataholder(config)
        assert isinstance(data_holder, SQLDataHolder)
        self.check_data_holder_after_load(data_holder)


@pytest.mark.usefixtures("mock_path_exists", "mock_filepath_in_dir")
def test_fetch_data_source(mock_yaml_config_dict: dict[str, Any]) -> None:
    """Tests fetch_data_source function."""
    ingest_data_config = IngestDataConfig(
        data_sources=mock_yaml_config_dict["data_sources"],
        data_holders=mock_yaml_config_dict["data_holders"],
        ingest_data=IngestTypes(**mock_yaml_config_dict["ingest_data"]),
    )
    data_source = fetch_data_source(ingest_data_config)
    assert isinstance(data_source, JSONDataSource)
    assert data_source.dirpath == "/path/to/json/directory"
    assert data_source.filepath == "/path/to/json/file.json"

    expected_config_headers = [
        "filepath",
        "dirpath",
        "data_location",
        "header",
        "span_mapping",
        "field_mapping",
    ]
    for key in data_source.config.keys():
        assert key in expected_config_headers
        expected_config_headers.remove(key)
    assert not expected_config_headers


@pytest.mark.usefixtures("mock_path_exists", "mock_filepath_in_dir")
def test_fetch_data_holder(mock_yaml_config_dict: dict[str, Any]) -> None:
    """Tests fetch_data_holder function."""
    ingest_data_config = IngestDataConfig(
        data_sources=mock_yaml_config_dict["data_sources"],
        data_holders=mock_yaml_config_dict["data_holders"],
        ingest_data=IngestTypes(**mock_yaml_config_dict["ingest_data"]),
    )

    data_holder = fetch_data_holder(ingest_data_config)
    assert isinstance(data_holder, SQLDataHolder)
    assert data_holder.batch_size == 5
    assert data_holder.max_timestamp == 0
    assert data_holder.min_timestamp == 999999999999999999999999999999999999999
    assert not data_holder.node_models_to_save
    assert not data_holder.node_relationships_to_save
