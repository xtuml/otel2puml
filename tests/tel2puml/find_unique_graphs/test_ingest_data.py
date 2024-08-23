"""Tests for ingest_data module."""

import yaml
from pathlib import Path

from tel2puml.find_unique_graphs.otel_ingestion.ingest_otel_data import (
    IngestData,
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
    def test_integration_sql_json(
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
            nodes = session.query(NodeModel).all()
            assert len(nodes) == 8
            expected_event_ids = [
                f"{i}_span_{j}_{k}"
                for i in range(2)
                for j in range(2)
                for k in range(2)
            ]

            for node in nodes:
                assert node.event_id in expected_event_ids
                expected_event_ids.remove(str(node.event_id))
            assert not expected_event_ids

            # Check relationships
            node_0 = (
                session.query(NodeModel)
                .filter_by(event_id="0_span_0_0")
                .first()
            )
            node_1 = (
                session.query(NodeModel)
                .filter_by(event_id="0_span_0_1")
                .first()
            )
            assert node_0
            assert node_1
            assert node_0.children == [node_1]
