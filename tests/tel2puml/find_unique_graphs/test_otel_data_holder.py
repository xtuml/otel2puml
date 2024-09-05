"""Tests for OTel data holder classes."""
import logging

import pytest
from unittest.mock import patch
from pytest import LogCaptureFixture
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm.exc import DetachedInstanceError

from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    OTelEvent,
    NodeModel,
    SQLDataHolderConfig,
    Base,
    NODE_ASSOCIATION,
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

        with patch.object(
            SQLDataHolder, "create_db_tables"
        ) as mock_create_db_tables:
            holder = SQLDataHolder(mock_sql_config)
            # Test the super().__init__() method
            assert (
                holder.min_timestamp == 999999999999999999999999999999999999999
            )
            assert holder.max_timestamp == 0
            # Test attributes set correctly
            assert holder.batch_size == 10
            assert holder.node_models_to_save == []
            assert holder.node_relationships_to_save == []
            assert isinstance(holder.engine, Engine)
            assert holder.engine.url.drivername == "sqlite"
            assert holder.engine.url.database == ":memory:"
            assert isinstance(holder.session, Session)
            assert isinstance(holder.base, Base)
            mock_create_db_tables.assert_called_once()

    @staticmethod
    def test_create_db_tables(mock_sql_config: SQLDataHolderConfig) -> None:
        """Tests the create_db_tables method."""

        holder = SQLDataHolder(mock_sql_config)
        inspector = inspect(holder.engine)
        # Test column names in nodes table
        columns = inspector.get_columns("nodes")
        column_names = [column["name"] for column in columns]
        expected_column_names = [
            "id",
            "job_name",
            "job_id",
            "event_type",
            "event_id",
            "start_timestamp",
            "end_timestamp",
            "application_name",
            "parent_event_id",
        ]
        assert column_names == expected_column_names

        # Test column names in node association table
        columns = inspector.get_columns("NODE_ASSOCIATION")
        column_names = [column["name"] for column in columns]

        assert column_names == ["parent_id", "child_id"]

        # Test get column names in job hash table
        columns = inspector.get_columns("job_hashes")
        column_names = [column["name"] for column in columns]

        assert column_names == ["job_id", "job_name", "job_hash"]

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
        mock_sql_config: SQLDataHolderConfig, mock_otel_events: list[OTelEvent]
    ) -> None:
        """Tests save_data method"""

        holder = SQLDataHolder(mock_sql_config)
        for otel_event in mock_otel_events:
            holder.save_data(otel_event)

        assert holder.min_timestamp == 1695639486119918080
        assert holder.max_timestamp == 1695639486119918093

        nodes = holder.session.query(NodeModel).all()
        assert len(nodes) == len(mock_otel_events)

        node_0 = (
            holder.session.query(NodeModel).filter_by(event_id="0").first()
        )
        assert isinstance(node_0, NodeModel)
        assert node_0.job_name == "test_name"
        assert node_0.job_id == "test_id"
        assert node_0.event_id == "0"
        assert node_0.start_timestamp == 1695639486119918080
        assert node_0.end_timestamp == 1695639486119918084
        assert node_0.application_name == "test_application_name"
        assert node_0.parent_event_id == "None"

        # Test parent-child relationship
        node_1 = (
            holder.session.query(NodeModel).filter_by(event_id="1").first()
        )
        assert node_0.children == [node_1]

    @staticmethod
    def test_commit_batched_data_success(
        mock_sql_config: SQLDataHolderConfig,
    ) -> None:
        """Tests commit_batched_data_to_database method, with success."""

        holder = SQLDataHolder(mock_sql_config)
        parent_node_model = NodeModel(
            job_name="test_job_name",
            job_id="test_job_id",
            event_type="test_event",
            event_id="100",
            start_timestamp=1723544154817893024,
            end_timestamp=1723544154817798024,
            application_name="test_app",
            parent_event_id=None,
        )
        child_node_model = NodeModel(
            job_name="test_job_name",
            job_id="test_job_id",
            event_type="test_event",
            event_id="101",
            start_timestamp=1723544154817893024,
            end_timestamp=1723544154817798024,
            application_name="test_app",
            parent_event_id="100",
        )

        holder.node_relationships_to_save.append(
            {"parent_id": "100", "child_id": "101"}
        )
        holder.node_models_to_save.append(parent_node_model)
        holder.node_models_to_save.append(child_node_model)

        # Test reset batch
        assert len(holder.node_models_to_save) == 2
        assert len(holder.node_relationships_to_save) == 1

        holder.commit_batched_data_to_database()

        assert len(holder.node_models_to_save) == 0
        assert len(holder.node_relationships_to_save) == 0

        # Test NodeModels are correctly stored in the database
        node_0 = (
            holder.session.query(NodeModel).filter_by(event_id="100").first()
        )
        node_1 = (
            holder.session.query(NodeModel).filter_by(event_id="101").first()
        )

        assert isinstance(node_0, NodeModel)
        assert not node_0.parent_event_id

        assert isinstance(node_1, NodeModel)
        assert node_1 in node_0.children
        assert node_1.parent_event_id == "100"

        # Test attributes between parent and child are the same
        for attr in [
            "job_name",
            "job_id",
            "application_name",
            "event_type",
            "start_timestamp",
            "end_timestamp",
        ]:
            assert getattr(node_0, attr) == getattr(node_1, attr)

        # Test node relationships are correctly stored in the database
        node_relationship = holder.session.query(NODE_ASSOCIATION).all()

        assert len(node_relationship) == 1
        assert node_relationship[0].parent_id == "100"
        assert node_relationship[0].child_id == "101"

    @staticmethod
    def test_commit_batched_data_failure(
        mock_sql_config: SQLDataHolderConfig,
    ) -> None:
        """Tests commit_batched_data_to_database method, with failure."""

        holder = SQLDataHolder(mock_sql_config)

        # Test the IntegrityError case
        with patch.object(
            holder,
            "batch_insert_node_models",
            side_effect=IntegrityError(
                "IntegrityError", None, Exception("IntegrityError")
            ),
        ), patch.object(holder.session, "rollback") as mock_rollback:
            with pytest.raises(Exception) as context:
                holder.commit_batched_data_to_database()
            mock_rollback.assert_called_once()
            assert "IntegrityError" in str(context.value)

        # Test the OperationalError case
        with patch.object(
            holder,
            "batch_insert_node_models",
            side_effect=OperationalError(
                "OperationalError", None, Exception("OperationalError")
            ),
        ), patch.object(holder.session, "rollback") as mock_rollback:
            with pytest.raises(Exception) as context:
                holder.commit_batched_data_to_database()
            mock_rollback.assert_called_once()
            assert "OperationalError" in str(context.value)

        # Test the unexpected error case
        with patch.object(
            holder,
            "batch_insert_node_models",
            side_effect=Exception("Unexpected Error"),
        ), patch.object(holder.session, "rollback") as mock_rollback:
            with pytest.raises(Exception) as context:
                holder.commit_batched_data_to_database()
            mock_rollback.assert_called_once()
            assert "Unexpected Error" in str(context.value)

    @staticmethod
    def test_sql_data_holder_exit_method(
        mock_sql_config: SQLDataHolderConfig, mock_otel_event: OTelEvent
    ) -> None:
        """Tests the __exit__ method using a context manager."""

        with SQLDataHolder(mock_sql_config) as holder:
            holder.save_data(mock_otel_event)
            assert len(holder.session.query(NodeModel).all()) == 0

        # Rest of the batch is commited on __exit__
        assert len(holder.session.query(NodeModel).all()) == 1

        node = (
            holder.session.query(NodeModel).filter_by(event_id="456").first()
        )
        assert isinstance(node, NodeModel)
        assert node.job_name == "test_job"

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
            end_timestamp=1823544154817798024,
            application_name="test_app",
            parent_event_id="456",
        )

        with SQLDataHolder(mock_sql_config) as holder:
            holder.save_data(mock_otel_event)
            holder.save_data(child_otel_event)

        assert holder.min_timestamp == 1723544154817793024
        assert holder.max_timestamp == 1823544154817798024

        # Retrieve the data and check if it's correct
        node = (
            holder.session.query(NodeModel).filter_by(event_id="456").first()
        )
        assert node is not None
        assert isinstance(node, NodeModel)
        assert node.job_name == "test_job"
        assert node.job_id == "123"
        assert node.event_type == "test_event"
        assert node.event_id == "456"
        assert node.start_timestamp == 1723544154817793024
        assert node.end_timestamp == 1723544154817993024
        assert node.application_name == "test_app"

        child_node = (
            holder.session.query(NodeModel).filter_by(event_id="101").first()
        )
        assert node.children == [child_node]

        # Check if relationships were saved
        relationships = holder.session.query(NODE_ASSOCIATION).all()
        assert len(relationships) == 2
        assert relationships[0].parent_id == "456"
        assert relationships[0].child_id in ["101", "102"]

    @staticmethod
    def test_node_to_otel_event(
        sql_data_holder_with_otel_jobs: SQLDataHolder,
        otel_jobs: dict[str, list[OTelEvent]],
        caplog: LogCaptureFixture
    ) -> None:
        """Tests node_to_otel_event method."""
        # test that the method returns the correct OTelEvent that has a child
        with sql_data_holder_with_otel_jobs.session as session:
            node = session.query(NodeModel).filter_by(event_id="0_0").first()
            assert SQLDataHolder.node_to_otel_event(node) == otel_jobs["0"][1]
        # test that a detached instance error is raised when the session the
        # node was created in is closed
        with sql_data_holder_with_otel_jobs.session as session:
            node = session.query(NodeModel).filter_by(event_id="0_0").first()
        caplog.clear()
        caplog.set_level(logging.ERROR)
        with pytest.raises(DetachedInstanceError):
            SQLDataHolder.node_to_otel_event(node)
        assert (
            "Likely not within a session so cannot access children."
            in caplog.text
        )

    @staticmethod
    def test_get_otel_events_from_job_ids(
        sql_data_holder_with_shuffled_otel_events: SQLDataHolder,
        otel_jobs: dict[str, list[OTelEvent]]
    ) -> None:
        """Tests get_otel_events_from_job_ids method."""

        job_ids = {"test_id_2", "test_id_3"}

        otel_events = list(
            sql_data_holder_with_shuffled_otel_events.
            get_otel_events_from_job_ids(
                job_ids
            )
        )

        assert len(otel_events) == 2
        assert len(otel_events[0]) == 2
        assert len(otel_events[1]) == 2
        assert otel_events[0]["2_0"] == otel_jobs["2"][1]
        assert otel_events[0]["2_1"] == otel_jobs["2"][0]
        assert otel_events[1]["3_0"] == otel_jobs["3"][1]
        assert otel_events[1]["3_1"] == otel_jobs["3"][0]
