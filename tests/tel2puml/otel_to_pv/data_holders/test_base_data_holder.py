"""Tests for the module base.py."""
import pytest
from pytest import MonkeyPatch

from tel2puml.otel_to_pv.data_holders.base import (
    DataHolder,
    get_time_window,
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