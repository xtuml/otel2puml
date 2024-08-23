"""Tests for the find_unique_graphs module."""

from pytest import MonkeyPatch
import pytest
import sqlalchemy as sa


from tel2puml.find_unique_graphs.find_unique_graphs import (
    get_time_window,
    create_temp_table_of_root_nodes_in_time_window,
)
from tel2puml.find_unique_graphs.otel_ingestion.otel_data_holder import (
    DataHolder, SQLDataHolder
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
