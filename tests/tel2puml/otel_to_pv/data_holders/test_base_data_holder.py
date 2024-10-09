"""Tests for the module base.py."""
import pytest
from pytest import MonkeyPatch

from tel2puml.otel_to_pv.data_holders.base import (
    DataHolder,
    get_time_window,
)


class TestDataHolder:
    """Tests for the DataHolder class."""
    @staticmethod
    @pytest.fixture(autouse=True)
    def _remove_abstract_methods(monkeypatch: MonkeyPatch) -> None:
        """Remove abstract methods from the DataHolder class."""
        monkeypatch.setattr(DataHolder, "__abstractmethods__", set())

    @staticmethod
    def test__init__() -> None:
        """Test the __init__ method."""
        data_holder = DataHolder()
        assert data_holder._max_timestamp == 0
        assert data_holder._min_timestamp == 9223372036854775807

    @staticmethod
    def test_max_timestamp() -> None:
        """Test the max_timestamp property."""
        data_holder = DataHolder()
        assert data_holder.max_timestamp == 9223372036854775807
        data_holder._max_timestamp = 10**12
        assert data_holder.max_timestamp == 9223372036854775807
        data_holder._min_timestamp = 0
        assert data_holder.max_timestamp == 10**12

    @staticmethod
    def test_min_timestamp() -> None:
        """Test the min_timestamp property."""
        data_holder = DataHolder()
        assert data_holder.min_timestamp == 0
        data_holder._min_timestamp = 10**12
        assert data_holder.min_timestamp == 0
        data_holder._max_timestamp = 2 * 10**12
        assert data_holder.min_timestamp == 10**12


def test_get_time_window(monkeypatch: MonkeyPatch) -> None:
    """Test the get_time_window function."""
    monkeypatch.setattr(DataHolder, "__abstractmethods__", set())
    data_holder = DataHolder()  # type: ignore[abstract]
    data_holder._min_timestamp = 10**12
    data_holder._max_timestamp = 2 * 10**12
    time_buffer = 1
    expected_result = (1060000000000, 1940000000000)
    assert get_time_window(time_buffer, data_holder) == expected_result
    with pytest.raises(ValueError):
        get_time_window(10, data_holder)
