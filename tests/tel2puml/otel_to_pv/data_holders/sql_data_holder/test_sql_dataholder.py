"""Tests for sql_data_holder.py."""

import logging

import pytest
from unittest.mock import patch
from pytest import LogCaptureFixture, MonkeyPatch
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm.exc import DetachedInstanceError

from tel2puml.otel_to_pv.data_holders.sql_data_holder.data_model import (
    NodeModel,
    Base,
    NODE_ASSOCIATION,
    JobHash,
)
from tel2puml.otel_to_pv.data_holders.sql_data_holder.sql_dataholder import (
    SQLDataHolder,
    intialise_temp_table_for_root_nodes,
    get_root_nodes,
    create_temp_table_of_root_nodes_in_time_window,
    compute_graph_hash_from_event_ids,
    get_sql_batch_nodes,
    create_event_id_to_child_nodes_map,
    compute_graph_hashes_from_root_nodes,
    insert_job_hashes,
    compute_graph_hashes_for_batch,
    get_unique_graph_job_ids_per_job_name,
    find_unique_graphs,
)
from tel2puml.otel_to_pv.config import SQLDataHolderConfig
from tel2puml.otel_to_pv.otel_to_pv_types import OTelEvent


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
        caplog: LogCaptureFixture,
    ) -> None:
        """Tests node_to_otel_event method."""
        # test that the method returns the correct OTelEvent that has a child
        with sql_data_holder_with_otel_jobs.session as session:
            node = session.query(NodeModel).filter_by(event_id="0_0").first()
            assert node is not None
            assert SQLDataHolder.node_to_otel_event(node) == otel_jobs["0"][1]
        # test that a detached instance error is raised when the session the
        # node was created in is closed
        with sql_data_holder_with_otel_jobs.session as session:
            node = session.query(NodeModel).filter_by(event_id="0_0").first()
            assert node is not None
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
        otel_jobs: dict[str, list[OTelEvent]],
    ) -> None:
        """Tests get_otel_events_from_job_ids method."""

        job_ids = {"test_id_2", "test_id_3"}

        sql_data_holder = sql_data_holder_with_shuffled_otel_events
        otel_events = list(
            sql_data_holder.get_otel_events_from_job_ids(job_ids)
        )

        assert len(otel_events) == 2
        assert len(otel_events[0]) == 2
        assert len(otel_events[1]) == 2
        assert otel_events[0]["2_0"] == otel_jobs["2"][1]
        assert otel_events[0]["2_1"] == otel_jobs["2"][0]
        assert otel_events[1]["3_0"] == otel_jobs["3"][1]
        assert otel_events[1]["3_1"] == otel_jobs["3"][0]

    @staticmethod
    def test_find_unique_graphs(
        monkeypatch: MonkeyPatch, sql_data_holder_extended: SQLDataHolder
    ) -> None:
        """Tests find_unique_graphs method."""
        monkeypatch.setattr("xxhash.xxh64_hexdigest", lambda x: x)
        unique_job_ids_per_job_name = (
            sql_data_holder_extended.find_unique_graphs()
        )
        assert list(unique_job_ids_per_job_name.keys()) == [
            "test_name",
            "test_name_2",
        ]
        assert unique_job_ids_per_job_name["test_name"] == {
            "event_type_0event_type_1"
        }
        assert unique_job_ids_per_job_name["test_name_2"] == {
            str(i) for i in range(5)
        }


def test_initialise_temp_table_for_root_nodes(
    sql_data_holder_with_otel_jobs: SQLDataHolder,
) -> None:
    """Test the intialise_temp_table_for_root_nodes function."""
    assert not sa.inspect(sql_data_holder_with_otel_jobs.engine).has_table(
        "temp_root_nodes"
    )
    table = intialise_temp_table_for_root_nodes(sql_data_holder_with_otel_jobs)
    assert sa.inspect(sql_data_holder_with_otel_jobs.engine).has_table(
        "temp_root_nodes"
    )
    assert table.columns.keys() == ["event_id"]
    assert table.primary_key.columns.keys() == ["event_id"]


def test_create_temp_table_of_root_nodes_in_time_window(
    sql_data_holder_with_otel_jobs: SQLDataHolder,
) -> None:
    """Test the create_temp_table_of_root_nodes_in_time_window function."""
    time_window = (10**12 + 6 * 10**10, 10**12 + 54 * 10**10)
    table = create_temp_table_of_root_nodes_in_time_window(
        time_window, sql_data_holder_with_otel_jobs
    )
    with sql_data_holder_with_otel_jobs.engine.connect() as connection:
        result = connection.execute(table.select())
        assert [(row[0],) for row in result.fetchall()] == [
            (f"{i}_0",) for i in range(1, 4)
        ]


def test_get_root_nodes(
    sql_data_holder_with_otel_jobs: SQLDataHolder,
    table_of_root_node_event_ids: sa.Table,
    otel_jobs: dict[str, list[OTelEvent]],
) -> None:
    """Test the get_root_nodes function."""
    # test possible start rows and batch sizes
    start_row_and_batch_sizes = [
        (0, 2),
        (1, 3),
        (0, 5),
        (0, 6),
        (3, 6),
        (4, 0),
        (5, 10),
    ]
    for start_row, batch_size in start_row_and_batch_sizes:
        root_nodes = get_root_nodes(
            start_row,
            batch_size,
            table_of_root_node_event_ids,
            sql_data_holder_with_otel_jobs,
        )
        start_row = min(start_row, 5)
        end_row = min(start_row + batch_size, 5)
        size = end_row - start_row
        assert len(root_nodes) == size
        for i in range(size):
            assert root_nodes[i].job_name == "test_name"
            assert root_nodes[i].event_id == f"{i + start_row}_0"
            assert root_nodes[i].job_id == f"test_id_{i + start_row}"
            assert root_nodes[i].event_type == "event_type_0"
            assert (
                root_nodes[i].start_timestamp
                == otel_jobs[f"{i + start_row}"][1].start_timestamp
            )
            assert (
                root_nodes[i].end_timestamp
                == otel_jobs[f"{i + start_row}"][1].end_timestamp
            )
            assert root_nodes[i].application_name == "test_application_name"
            assert root_nodes[i].parent_event_id is None
    # test invalid start row and batch size
    with pytest.raises(ValueError):
        get_root_nodes(
            -1, 0, table_of_root_node_event_ids, sql_data_holder_with_otel_jobs
        )
    with pytest.raises(ValueError):
        get_root_nodes(
            0, -1, table_of_root_node_event_ids, sql_data_holder_with_otel_jobs
        )


def test_get_sql_batch_nodes(
    sql_data_holder_with_otel_jobs: SQLDataHolder,
) -> None:
    """Test the get_sql_batch_nodes function."""
    node_models = get_sql_batch_nodes(
        {f"test_id_{i}" for i in range(3)}, sql_data_holder_with_otel_jobs
    )
    assert len(node_models) == 6
    expected_job_ids = [f"test_id_{i}" for i in range(3)] * 2
    expected_event_ids = [f"{i}_{j}" for i in range(3) for j in range(2)]
    for node in node_models:
        assert node.job_id in expected_job_ids
        assert node.event_id in expected_event_ids
        expected_job_ids.remove(str(node.job_id))
        expected_event_ids.remove(str(node.event_id))
    assert not expected_job_ids
    assert not expected_event_ids


def test_create_event_id_to_child_nodes_map(
    otel_nodes_from_otel_jobs: dict[str, NodeModel],
) -> None:
    """Test the create_event_id_to_child_nodes_map function."""
    event_id_to_child_nodes_map = create_event_id_to_child_nodes_map(
        otel_nodes_from_otel_jobs.values()
    )
    assert event_id_to_child_nodes_map == {
        f"{i}_{j}": (
            [otel_nodes_from_otel_jobs[f"{i}_{j + 1}"]] if j < 1 else []
        )
        for i in range(5)
        for j in range(2)
    }


def test_compute_graph_hash_from_event_ids(
    monkeypatch: MonkeyPatch,
    otel_linked_nodes_and_nodes: tuple[
        dict[str, list[NodeModel]], dict[int, NodeModel]
    ],
) -> None:
    """Test the compute_graph_hash_from_event_ids function."""
    # test that order for string output is correct and the function is
    # performing correctly recursively and sorting correctly
    node_links, nodes = otel_linked_nodes_and_nodes
    mock_hash = {
        "1MNP": "MNPZ",
        "2": "P",
        "3": "M",
        "4": "N",
        "5": "MNPY",
        "0MNPYMNPZ": "complete",
    }
    monkeypatch.setattr("xxhash.xxh64_hexdigest", lambda x: mock_hash[x])
    compute_graph_hash_from_event_ids(nodes[0], node_links) == "complete"
    # remove patch and test that hashing function is correct for a single node
    # and is deterministic
    monkeypatch.undo()
    assert (
        compute_graph_hash_from_event_ids(nodes[5], node_links)
        == "6a81b47405b648ed"  # pragma: allowlist secret
    )


def test_compute_graph_hash_from_root_nodes(
    otel_simple_linked_nodes_and_nodes: tuple[
        dict[str, list[NodeModel]], dict[str, NodeModel]
    ],
) -> None:
    """Test the compute_graph_hashes_from_root_nodes function."""
    node_links, nodes = otel_simple_linked_nodes_and_nodes
    hashes = compute_graph_hashes_from_root_nodes(
        [nodes["0_0"], nodes["1_0"]], node_links
    )
    expected_hashes = {
        ("0", "0a0d678d03e9644c"),  # pragma: allowlist secret
        ("1", "6cb8df24661bf2e6"),  # pragma: allowlist secret
    }
    assert {
        (str(node.job_id), str(node.job_hash)) for node in hashes
    } == expected_hashes
    # test that the order of the root nodes does not affect the output
    hashes = compute_graph_hashes_from_root_nodes(
        [nodes["1_0"], nodes["0_0"]], node_links
    )
    assert {
        (str(node.job_id), str(node.job_hash)) for node in hashes
    } == expected_hashes


def test_insert_job_hashes(mock_sql_config: SQLDataHolderConfig) -> None:
    """Test the insert_job_hashes function."""
    sql_data_holder = SQLDataHolder(mock_sql_config)
    # check for integrity error if job_ids are not unique
    job_hashes = [
        JobHash(job_id="1", job_hash="1", job_name="test_name"),
        JobHash(job_id="1", job_hash="2", job_name="test_name"),
    ]
    with pytest.raises(IntegrityError):
        insert_job_hashes(job_hashes, sql_data_holder)
    # check normal use
    job_hashes = [
        JobHash(job_id="1", job_hash="1", job_name="test_name"),
        JobHash(job_id="2", job_hash="2", job_name="test_name"),
    ]
    insert_job_hashes(job_hashes, sql_data_holder)
    with sql_data_holder.engine.connect() as connection:
        result = connection.execute(JobHash.__table__.select())
        assert [(row[0], row[1], row[2]) for row in result.fetchall()] == [
            ("1", "test_name", "1"),
            ("2", "test_name", "2"),
        ]


def test_compute_graph_hashes_for_batch(
    sql_data_holder_with_otel_jobs: SQLDataHolder,
    otel_jobs: dict[str, list[OTelEvent]],
) -> None:
    """Test the compute_graph_hashes_for_batch function."""
    root_nodes = [
        SQLDataHolder.convert_otel_event_to_node_model(otel_event)
        for value in otel_jobs.values()
        for otel_event in value
        if otel_event.event_id.endswith("_0")
    ]
    compute_graph_hashes_for_batch(root_nodes, sql_data_holder_with_otel_jobs)
    with sql_data_holder_with_otel_jobs.engine.connect() as connection:
        result = connection.execute(JobHash.__table__.select())
        assert [(row[0], row[1], row[2]) for row in result.fetchall()] == [
            (
                f"test_id_{i}",
                "test_name",
                "7b03569ba77bbcdc",  # pragma: allowlist secret
            )
            for i in range(5)
        ]


def test_get_unique_graph_job_ids_per_job_name(
    sql_data_holder_with_otel_jobs: SQLDataHolder,
) -> None:
    """Test the get_unique_graph_job_ids_per_job_name function."""
    with sql_data_holder_with_otel_jobs.session as session:
        for j in range(2):
            session.add_all(
                [
                    JobHash(
                        job_id=f"test_id_{j}{i}",
                        job_hash=f"{i % 2}",
                        job_name=f"test_name_{j}",
                    )
                    for i in range(4)
                ]
            )
        session.commit()
    """Test the get_unique_graph_job_ids_per_job_name function."""
    unique_job_ids_per_job_name = get_unique_graph_job_ids_per_job_name(
        sql_data_holder_with_otel_jobs
    )
    assert list(unique_job_ids_per_job_name.keys()) == [
        "test_name_0",
        "test_name_1",
    ]
    assert unique_job_ids_per_job_name["test_name_0"] == {"0", "1"}
    assert unique_job_ids_per_job_name["test_name_1"] == {"0", "1"}


def test_find_unique_graphs(
    monkeypatch: MonkeyPatch,
    sql_data_holder_extended: SQLDataHolder,
) -> None:
    """Test the find_unique_graphs function."""
    # test that the function is working correctly with a simple graph
    monkeypatch.setattr("xxhash.xxh64_hexdigest", lambda x: x)
    unique_job_ids_per_job_name = find_unique_graphs(
        1, 2, sql_data_holder_extended
    )
    assert list(unique_job_ids_per_job_name.keys()) == [
        "test_name",
        "test_name_2",
    ]
    assert unique_job_ids_per_job_name["test_name"] == {
        "event_type_0event_type_1"
    }
    assert unique_job_ids_per_job_name["test_name_2"] == {
        str(i) for i in range(5)
    }


def test_stream_data(
    sql_data_holder_with_multiple_otel_job_names: SQLDataHolder,
) -> None:
    """Test the stream_data function"""
    sql_data_holder = sql_data_holder_with_multiple_otel_job_names

    # Test 1: Stream all data
    # Prep expected events
    expected_events = {}
    with sql_data_holder.session as session:
        nodes = session.query(NodeModel).all()
        for node in nodes:
            otel_event = sql_data_holder.node_to_otel_event(node)
            expected_events[otel_event.event_id] = otel_event

    # Stream data and collect events
    result = sql_data_holder.stream_data()
    streamed_events = {}
    for job_name, otel_event_gen in result:
        for otel_event in otel_event_gen:
            streamed_events[otel_event.event_id] = otel_event

    # Compare the expected and streamed data
    assert len(expected_events) == len(streamed_events)

    for event_id, expected_event in expected_events.items():
        assert event_id in streamed_events
        assert expected_event == streamed_events[event_id]

    # Test 2: Stream from empty database
    empty_sql_data_holder = SQLDataHolder(
        config=SQLDataHolderConfig(
            db_uri="sqlite:///:memory:", batch_size=10, time_buffer=30
        )
    )

    with empty_sql_data_holder:
        result = empty_sql_data_holder.stream_data()

        all_events = []
        for job_name, otel_event_gen in result:
            for otel_event in otel_event_gen:
                all_events.append(otel_event)

        assert len(all_events) == 0

    # Test 3: Stream from large dataset
    large_sql_data_holder = SQLDataHolder(
        config=SQLDataHolderConfig(
            db_uri="sqlite:///:memory:", batch_size=1000, time_buffer=30
        )
    )

    num_jobs = 10
    events_per_job = 10000  # Total of 100,000 events

    with large_sql_data_holder:
        for job_index in range(num_jobs):
            job_name = f"job_{job_index}"
            job_id = f"job_id_{job_index}"
            for event_index in range(events_per_job):
                otel_event = OTelEvent(
                    job_name=job_name,
                    job_id=job_id,
                    event_type=f"event_type_{event_index}",
                    event_id=f"event_{job_index}_{event_index}",
                    start_timestamp=1723544132228288000 + event_index,
                    end_timestamp=1723544132228288000 + event_index + 10,
                    application_name="test_application",
                    parent_event_id=None,
                    child_event_ids=[],
                )
                large_sql_data_holder.save_data(otel_event)

    # Stream data and verify counts
    total_events_streamed = 0
    with large_sql_data_holder:
        result = large_sql_data_holder.stream_data()
        for job_name, otel_event_gen in result:
            event_count = 0
            for otel_event in otel_event_gen:
                event_count += 1
            assert event_count == events_per_job
            total_events_streamed += event_count

    assert total_events_streamed == num_jobs * events_per_job


def test_stream_job_name_batches(
    sql_data_holder_with_multiple_otel_job_names: SQLDataHolder,
) -> None:
    """Test stream_job_name_batches method."""
    # Test 1: Stream all data
    sql_data_holder = sql_data_holder_with_multiple_otel_job_names
    with sql_data_holder.session as session:
        otel_event_gen = sql_data_holder.stream_job_name_batches(session)
        all_events = list(otel_event_gen)

    assert len(all_events) == 20

    # Test 2: Stream data, filtered by job name
    with sql_data_holder.session as session:
        otel_event_gen = sql_data_holder.stream_job_name_batches(
            session, filter_job_names={"test_name"}
        )
        all_events = list(otel_event_gen)

    assert all(otel_event.job_name == "test_name" for otel_event in all_events)
    assert len(all_events) == 10

    expected_job_ids = [f"test_id_{i}" for i in range(5)]
    expected_event_ids = [f"{i}_{j}" for i in range(5) for j in range(2)]
    job_id_count: dict[str, int] = {}
    for event in all_events:
        job_id_count.setdefault(event.job_id, 0)
        job_id_count[event.job_id] += 1
        assert event.job_id in expected_job_ids
        assert event.event_id in expected_event_ids
        expected_event_ids.remove(event.event_id)
    assert all(value == 2 for value in job_id_count.values())
    assert len(expected_event_ids) == 0

    # Test 3: Stream data, filtered using map
    with sql_data_holder.session as session:
        otel_event_gen = sql_data_holder.stream_job_name_batches(
            session,
            job_name_to_job_ids_map={
                "test_name": {"test_id_0", "test_id_1"},
            },
        )
        all_events = list(otel_event_gen)

    assert len(all_events) == 4
    job_id_count = {}
    expected_event_ids = ["0_0", "0_1", "1_0", "1_1"]
    for otel_event in all_events:
        job_id_count.setdefault(otel_event.job_id, 0)
        job_id_count[otel_event.job_id] += 1
        assert otel_event.job_name == "test_name"
        assert otel_event.job_id in {
            "test_id_0",
            "test_id_1",
        }
        assert otel_event.event_id in expected_event_ids
        expected_event_ids.remove(otel_event.event_id)
    assert all(value == 2 for value in job_id_count.values())
    assert len(expected_event_ids) == 0

    # Test 4: Stream data, filtering with name and map
    filter_job_names = {"test_name", "test_name_1"}
    job_name_to_job_ids_map = {
        "test_name": {"test_id_0", "test_id_1"},
        "test_name_1": {"test_id_5"},
    }

    with sql_data_holder.session as session:
        otel_event_gen = sql_data_holder.stream_job_name_batches(
            session,
            filter_job_names=filter_job_names,
            job_name_to_job_ids_map=job_name_to_job_ids_map,
        )
        all_events = list(otel_event_gen)

    assert len(all_events) == 6

    valid_job_ids = {"test_id_0", "test_id_1", "test_id_5"}
    valid_job_names = {"test_name", "test_name_1"}
    job_id_count = {}
    for otel_event in all_events:
        job_id_count.setdefault(otel_event.job_id, 0)
        job_id_count[otel_event.job_id] += 1
        assert otel_event.job_name in valid_job_names
        assert otel_event.job_id in valid_job_ids
    assert all(value == 2 for value in job_id_count.values())

    # Test 5: Stream data with non-existant job name
    with sql_data_holder.session as session:
        otel_event_gen = sql_data_holder.stream_job_name_batches(
            session, filter_job_names={"invalid_job_name"}
        )
        all_events = list(otel_event_gen)

    assert len(all_events) == 0

    # Test 6: Stream data with non-existant job name in map
    with sql_data_holder.session as session:
        otel_event_gen = sql_data_holder.stream_job_name_batches(
            session,
            job_name_to_job_ids_map={"invalid_job_name": {"test_id_0"}},
        )
        all_events = list(otel_event_gen)

    assert len(all_events) == 0
