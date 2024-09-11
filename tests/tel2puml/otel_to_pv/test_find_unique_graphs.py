"""Tests for the find_unique_graphs module."""

from pytest import MonkeyPatch
import pytest
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError

from tel2puml.otel_to_pv.find_unique_graphs import (
    get_time_window,
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
    find_unique_graphs
)
from tel2puml.otel_to_pv.data_holders import (
    DataHolder, SQLDataHolder
)
from tel2puml.otel_to_pv.otel_ingestion.otel_data_model import (
    NodeModel,
    SQLDataHolderConfig,
    JobHash,
    OTelEvent
)


def test_get_time_window(monkeypatch: MonkeyPatch) -> None:
    """Test the get_time_window function."""
    monkeypatch.setattr(DataHolder, "__abstractmethods__", set())
    data_holder = DataHolder()  # type: ignore[abstract]
    data_holder.min_timestamp = 10**12
    data_holder.max_timestamp = 2 * 10**12
    time_buffer = 1
    expected_result = (1060000000000, 1940000000000)
    assert get_time_window(time_buffer, data_holder) == expected_result
    with pytest.raises(ValueError):
        get_time_window(10, data_holder)


def test_initialise_temp_table_for_root_nodes(
    sql_data_holder_with_otel_jobs: SQLDataHolder,
) -> None:
    """Test the intialise_temp_table_for_root_nodes function."""
    assert not sa.inspect(sql_data_holder_with_otel_jobs.engine).has_table(
        'temp_root_nodes'
    )
    table = intialise_temp_table_for_root_nodes(
        sql_data_holder_with_otel_jobs
    )
    assert sa.inspect(sql_data_holder_with_otel_jobs.engine).has_table(
        'temp_root_nodes'
    )
    assert table.columns.keys() == ['event_id']
    assert table.primary_key.columns.keys() == ['event_id']


def test_create_temp_table_of_root_nodes_in_time_window(
    sql_data_holder_with_otel_jobs: SQLDataHolder,
) -> None:
    """Test the create_temp_table_of_root_nodes_in_time_window function."""
    time_window = (
        10**12 + 6 * 10**10, 10**12 + 54 * 10**10
    )
    table = create_temp_table_of_root_nodes_in_time_window(
        time_window, sql_data_holder_with_otel_jobs
    )
    with sql_data_holder_with_otel_jobs.engine.connect() as connection:
        result = connection.execute(table.select())
        assert [
            (row[0],)
            for row in result.fetchall()
        ] == [(f'{i}_0',) for i in range(1, 4)]


def test_get_root_nodes(
    sql_data_holder_with_otel_jobs: SQLDataHolder,
    table_of_root_node_event_ids: sa.Table,
    otel_jobs: dict[str, list[OTelEvent]]
) -> None:
    """Test the get_root_nodes function."""
    # test possible start rows and batch sizes
    start_row_and_batch_sizes = [
        (0, 2), (1, 3), (0, 5), (0, 6), (3, 6),
        (4, 0), (5, 10)
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
        {f"test_id_{i}" for i in range(3)},
        sql_data_holder_with_otel_jobs
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
    otel_nodes_from_otel_jobs: dict[str, NodeModel]
) -> None:
    """Test the create_event_id_to_child_nodes_map function."""
    event_id_to_child_nodes_map = create_event_id_to_child_nodes_map(
        otel_nodes_from_otel_jobs.values()
    )
    assert event_id_to_child_nodes_map == {
        f"{i}_{j}": (
            [otel_nodes_from_otel_jobs[f"{i}_{j + 1}"]]
            if j < 1
            else []
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
        "1MNP": "MNPZ", "2": "P", "3": "M", "4": "N", "5": "MNPY",
        "0MNPYMNPZ": "complete"
    }
    monkeypatch.setattr("xxhash.xxh64_hexdigest", lambda x: mock_hash[x])
    compute_graph_hash_from_event_ids(
        nodes[0],
        node_links
    ) == "complete"
    # remove patch and test that hashing function is correct for a single node
    # and is deterministic
    monkeypatch.undo()
    assert compute_graph_hash_from_event_ids(
        nodes[5],
        node_links
    ) == '6a81b47405b648ed'  # pragma: allowlist secret


def test_compute_graph_hash_from_root_nodes(
    otel_simple_linked_nodes_and_nodes: tuple[
        dict[str, list[NodeModel]], dict[str, NodeModel]
    ],
) -> None:
    """Test the compute_graph_hashes_from_root_nodes function."""
    node_links, nodes = otel_simple_linked_nodes_and_nodes
    hashes = compute_graph_hashes_from_root_nodes(
        [nodes["0_0"], nodes["1_0"]],
        node_links
    )
    expected_hashes = {
        ("0", "0a0d678d03e9644c"),  # pragma: allowlist secret
        ("1", "6cb8df24661bf2e6")  # pragma: allowlist secret
    }
    assert {
        (str(node.job_id), str(node.job_hash)) for node in hashes
    } == expected_hashes
    # test that the order of the root nodes does not affect the output
    hashes = compute_graph_hashes_from_root_nodes(
        [nodes["1_0"], nodes["0_0"]],
        node_links
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
        assert [
            (row[0], row[1], row[2])
            for row in result.fetchall()
        ] == [("1", "test_name", "1"), ("2", "test_name", "2")]


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
    compute_graph_hashes_for_batch(
        root_nodes, sql_data_holder_with_otel_jobs
    )
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
                        job_name=f"test_name_{j}"
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
