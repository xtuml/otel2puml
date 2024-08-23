"""Tests for ingest_data module."""

import json
import yaml
from pathlib import Path
from typing import Any

from tel2puml.find_unique_graphs.otel_ingestion.ingest_otel_data import (
    IngestData,
)
from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    IngestDataConfig,
    NodeModel
)
from tel2puml.find_unique_graphs.otel_ingestion.otel_data_holder import (
    SQLDataHolder,
    DataHolder,
)
from tel2puml.find_unique_graphs.otel_ingestion.otel_data_source import (
    JSONDataSource,
    OTELDataSource,
)

from utils import generate_resource_spans


class TestIngestData:
    """Collection of tests for IngestData class."""

    @staticmethod
    def create_temp_directory_with_json_file(tmp_path: Path):
        # Create temp directory
        temp_dir = tmp_path / "temp_dir"
        temp_dir.mkdir()

        # Create 2 json files in the temp directory
        for file_no in range(2):
            json_file = temp_dir / "json_file1.json"

            with json_file.open("w") as f:
                json.dump(generate_resource_spans(file_no, 2, 2), f)

        return temp_dir

    @staticmethod
    def test_integration_sql_json(
        mock_yaml_config_string: str,
        tmp_path: Path,
    ):
        # Create temp directory with 2 json files in
        temp_dir = TestIngestData.create_temp_directory_with_json_file(
            tmp_path
        )
        # Update config to point to temp directory
        config_yaml = mock_yaml_config_string.replace(
            "dirpath: /path/to/json/directory", f"dirpath: {temp_dir}"
        ).replace("filepath: /path/to/json/file.json", "filepath: null")

        config: IngestDataConfig = yaml.safe_load(config_yaml)

        data_holder: DataHolder = SQLDataHolder(config["data_holders"]["sql"])
        data_source: OTELDataSource = JSONDataSource(
            config["data_sources"]["json"]
        )
        # Assert nothing in the database
        ingest_data = IngestData(data_source, data_holder)
        ingest_data.load_to_data_holder()

        with data_holder.session as session:
            nodes = session.query(NodeModel).all()
        
        assert nodes
        # Assert things in the database
