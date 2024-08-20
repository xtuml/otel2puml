"""Tests for OTel data holder classes."""

import pytest

from unittest.mock import patch
from sqlalchemy import text

from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    OTelEvent,
    NodeModel,
    SQLDataHolderConfig,
)
from tel2puml.find_unique_graphs.otel_ingestion.otel_data_holder import (
    SQLDataHolder,
)


class TestSQLDataHolder:
    """Tests for class SQLDataHolder."""

    @staticmethod
    def test_sql_data_holder_init(
        mock_sql_config: SQLDataHolderConfig,
    ) -> None:
        """Tests the init method."""

        holder = SQLDataHolder(mock_sql_config)
        assert holder.batch_size == 10
        assert holder.node_models_to_save == []
        assert holder.node_relationships_to_save == []
        with patch.object(holder, "create_db_tables") as mock_create_db_table:
            holder.create_db_tables()
            mock_create_db_table.assert_called_once()

    @staticmethod
    def test_create_db_tables(mock_sql_config: SQLDataHolderConfig) -> None:
        """Tests the create_db_tables method."""

        holder = SQLDataHolder(mock_sql_config)
        with patch.object(
            holder.base.metadata, "create_all"
        ) as mock_create_all:
            holder.create_db_tables()
            mock_create_all.assert_called_once_with(holder.engine)

    @staticmethod
    def test_convert_otel_event_to_node_model(
        mock_sql_config: SQLDataHolderConfig, mock_otel_event: OTelEvent
    ) -> None:
        """Tests convert_otel_event_to_node_model method."""

        holder = SQLDataHolder(mock_sql_config)
        node_model = holder.convert_otel_event_to_node_model(mock_otel_event)
        assert isinstance(node_model, NodeModel)
        assert node_model.job_name == "test_job"
        assert node_model.job_id == "123"
        assert node_model.event_type == "test_event"
        assert node_model.event_id == "456"
        assert node_model.start_timestamp == 1723544154817793024
        assert node_model.end_timestamp == 1723544154817993024
        assert node_model.application_name == "test_app"

    @staticmethod
    def test_check_otel_event_within_timeframe(
        mock_sql_config: SQLDataHolderConfig, mock_otel_event: OTelEvent
    ) -> None:
        """Tests check_otel_event_within_timeframe method."""

        holder = SQLDataHolder(mock_sql_config)
        assert holder.check_otel_event_within_timeframe(
            mock_otel_event,
            min_datetime_unix_nano=1723544154817791024,
            max_datetime_unix_nano=1723544154817795024,
        )
        assert not holder.check_otel_event_within_timeframe(
            mock_otel_event,
            min_datetime_unix_nano=1723544154817791024,
            max_datetime_unix_nano=1723544154817792024,
        )

    @staticmethod
    def test_add_node_relations(
        mock_sql_config: SQLDataHolderConfig, mock_otel_event: OTelEvent
    ) -> None:
        """Tests add_node_relations method."""

        holder = SQLDataHolder(mock_sql_config)
        holder.add_node_relations(mock_otel_event)
        assert len(holder.node_relationships_to_save) == 2
        assert holder.node_relationships_to_save[0]["parent_id"] == "456"
        assert holder.node_relationships_to_save[0]["child_id"] == "101"
        assert holder.node_relationships_to_save[1]["parent_id"] == "456"
        assert holder.node_relationships_to_save[1]["child_id"] == "102"

    @staticmethod
    def test_save_data(
        mock_sql_config: SQLDataHolderConfig, mock_otel_event: OTelEvent
    ) -> None:
        """Tests save_data method"""

        holder = SQLDataHolder(mock_sql_config)
        with patch.object(
            holder, "commit_batched_data_to_database"
        ) as mock_commit:
            for _ in range(10):
                holder.save_data(
                    mock_otel_event,
                    min_datetime_unix_nano=1023544154817793024,
                    max_datetime_unix_nano=2723544154817793024,
                )
            assert len(holder.node_models_to_save) == 10
            mock_commit.assert_called_once()

    @staticmethod
    def test_commit_batched_data_success(
        mock_sql_config: SQLDataHolderConfig,
    ) -> None:
        """Tests commit_batched_data_to_database method, with success."""

        holder = SQLDataHolder(mock_sql_config)
        with patch.object(
            holder, "batch_insert_node_models"
        ) as mock_insert_nodes, patch.object(
            holder, "batch_insert_node_associations"
        ) as mock_insert_assocs:
            holder.commit_batched_data_to_database()
            mock_insert_nodes.assert_called_once()
            mock_insert_assocs.assert_called_once()

    @staticmethod
    def test_commit_batched_data_failure(
        mock_sql_config: SQLDataHolderConfig,
    ) -> None:
        """Tests commit_batched_data_to_database method, with failure."""

        holder = SQLDataHolder(mock_sql_config)
        with patch.object(
            holder,
            "batch_insert_node_models",
            side_effect=Exception,
        ), patch.object(holder.session, "rollback") as mock_rollback:
            with pytest.raises(Exception):
                holder.commit_batched_data_to_database()
            mock_rollback.assert_called_once()

    @staticmethod
    def test_clean_up(mock_sql_config: SQLDataHolderConfig) -> None:
        """Tests clean_up method."""

        holder = SQLDataHolder(mock_sql_config)
        with patch.object(
            holder, "commit_batched_data_to_database"
        ) as mock_commit:
            holder.clean_up()
            mock_commit.assert_called_once()

    @staticmethod
    def test_integration_save_and_retrieve(
        mock_sql_config: SQLDataHolderConfig, mock_otel_event: OTelEvent
    ) -> None:
        """Integration test for converting OTelEvent to NodeModel, saving
        and retrieving it from the database."""

        child_otel_event = OTelEvent(
            job_name="test_job",
            job_id="123",
            event_type="test_event_B",
            event_id="101",
            start_timestamp=1723544154817893024,
            end_timestamp=1723544154817798024,
            application_name="test_app",
            parent_event_id="456",
        )

        holder = SQLDataHolder(mock_sql_config)
        holder.save_data(
            mock_otel_event,
            min_datetime_unix_nano=1723544144817993024,
            max_datetime_unix_nano=1723544164817993024,
        )
        holder.save_data(
            child_otel_event,
            min_datetime_unix_nano=1723544144817993024,
            max_datetime_unix_nano=1723544164817993024,
        )
        holder.clean_up()

        # Retrieve the data and check if it's correct
        with holder.session as session:
            node = session.query(NodeModel).filter_by(event_id="456").first()
            assert node is not None
            assert node.job_name == "test_job"
            assert node.job_id == "123"
            assert node.event_type == "test_event"
            assert node.event_id == "456"
            assert node.start_timestamp == 1723544154817793024
            assert node.end_timestamp == 1723544154817993024
            assert node.application_name == "test_app"

            child_node = (
                session.query(NodeModel).filter_by(event_id="101").first()
            )
            assert node.children == [child_node]

        # Check if relationships were saved
        with holder.session as session:
            stmt = text("SELECT * FROM NODE_ASSOCIATION")
            relationships = session.execute(stmt).fetchall()
            assert len(relationships) == 2
            assert relationships[0].parent_id == "456"
            assert relationships[0].child_id in ["101", "102"]
