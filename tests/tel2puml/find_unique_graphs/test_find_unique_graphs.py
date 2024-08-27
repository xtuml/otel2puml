"""Tests for the find_unique_graphs module."""

from pytest import MonkeyPatch
import pytest
import sqlalchemy as sa

from tel2puml.find_unique_graphs.find_unique_graphs import (
    get_time_window,
    create_temp_table_of_root_nodes_in_time_window,
    compute_graph_hash_from_event_ids,
    get_sql_batch_nodes,
    create_event_id_to_child_nodes_map
)
from tel2puml.find_unique_graphs.otel_ingestion.otel_data_holder import (
    DataHolder, SQLDataHolder
)
from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    NodeModel
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


def test_create_temp_table_of_root_nodes_in_time_window(
    sql_data_holder_with_otel_jobs: SQLDataHolder,
) -> None:
    """Test the create_temp_table_of_root_nodes_in_time_window function."""
    assert not sa.inspect(sql_data_holder_with_otel_jobs.engine).has_table(
        'temp_root_nodes'
    )
    time_window = (
        10**12 + 6 * 10**10, 10**12 + 54 * 10**10
    )
    table = create_temp_table_of_root_nodes_in_time_window(
        time_window, sql_data_holder_with_otel_jobs
    )
    assert sa.inspect(sql_data_holder_with_otel_jobs.engine).has_table(
        'temp_root_nodes'
    )
    assert table.columns.keys() == ['event_id']
    assert table.primary_key.columns.keys() == ['event_id']
    with sql_data_holder_with_otel_jobs.engine.connect() as connection:
        result = connection.execute(table.select())
        assert [
            (row[0],)
            for row in result.fetchall()
        ] == [(f'{i}_0',) for i in range(1, 4)]


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


def test_compute_graph_hash_from_event_ids():
    """Test the compute_graph_hash_from_event_ids function."""
    pass
