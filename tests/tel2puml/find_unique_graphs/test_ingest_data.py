"""Tests for ingest_data module."""

import yaml
import pytest
from pathlib import Path

from tel2puml.find_unique_graphs.otel_ingestion.ingest_otel_data import (
    IngestData,
    fetch_data_source,
    fetch_data_holder,
)
from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    IngestDataConfig,
    NodeModel,
)
from tel2puml.find_unique_graphs.otel_ingestion.otel_data_holder import (
    SQLDataHolder,
)
from tel2puml.find_unique_graphs.otel_ingestion.otel_data_source import (
    JSONDataSource,
)


class TestIngestData:
    """Collection of tests for IngestData class."""

    @staticmethod
    def test_load_data_to_data_holder(
        mock_yaml_config_string: str,
        mock_temp_dir_with_json_files: Path,
    ) -> None:
        """Integration test for IngestData class using SQLDataHolder and
        JSONDataSource classes.
        """

        # Update config to point to temp directory
        config_yaml = mock_yaml_config_string.replace(
            "dirpath: /path/to/json/directory",
            f"dirpath: {mock_temp_dir_with_json_files}",
        ).replace("filepath: /path/to/json/file.json", "filepath: null")

        config: IngestDataConfig = yaml.safe_load(config_yaml)

        data_holder = SQLDataHolder(config["data_holders"]["sql"])
        data_source = JSONDataSource(config["data_sources"]["json"])

        with data_holder.session as session:
            # Check no nodes in the database
            assert not session.query(NodeModel).all()

            ingest_data = IngestData(data_source, data_holder)
            ingest_data.load_to_data_holder()

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
                    "application_name": f"service_{j}_{k} {headers['versions'][j]}",
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


@pytest.mark.usefixtures("mock_path_exists", "mock_filepath_in_dir")
def test_fetch_data_source(mock_yaml_config_dict: IngestDataConfig) -> None:
    """Tests fetch_data_source function."""

    data_source = fetch_data_source(mock_yaml_config_dict)
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

    mock_yaml_config_dict["ingest_data"]["data_source"] = "invalid_source"

    with pytest.raises(ValueError):
        data_source = fetch_data_source(mock_yaml_config_dict)


@pytest.mark.usefixtures("mock_path_exists", "mock_filepath_in_dir")
def test_fetch_data_holder(mock_yaml_config_dict: IngestDataConfig) -> None:
    """Tests fetch_data_holder function."""

    data_holder = fetch_data_holder(mock_yaml_config_dict)
    assert isinstance(data_holder, SQLDataHolder)
    assert data_holder.batch_size == 5
    assert data_holder.max_timestamp == 0
    assert data_holder.min_timestamp == 999999999999999999999999999999999999999
    assert not data_holder.node_models_to_save
    assert not data_holder.node_relationships_to_save

    mock_yaml_config_dict["ingest_data"]["data_holder"] = "invalid_holder"

    with pytest.raises(ValueError):
        data_holder = fetch_data_holder(mock_yaml_config_dict)
