"""Tests for json data converter module."""

import pytest

from tel2puml.find_unique_graphs.otel_ingestion.json_data_converter import (
    _navigate_segment,
    _extract_value_from_path,
    _extract_simple_value,
    _update_header_dict,
    _extract_nested_value,
)


class TestProcessHeaders:
    """Tests for processing headers within json data converter module."""

    @staticmethod
    def test_navigate_segment() -> None:
        """Tests the function _navigate_segment"""

        # Test when data is a dict
        data1 = {"key1": {"key2": "value"}}
        segment = "key1"
        assert _navigate_segment(data1, segment) == {"key2": "value"}
        # Test with an invalid key
        invalid_segment = "invalid"
        with pytest.raises(KeyError):
            _navigate_segment(data1, invalid_segment)

        # Test when data is a list
        data2 = [{"key1": {"key2": "value"}}]
        segment = "key1"
        assert _navigate_segment(data2, segment) == {"key1": {"key2": "value"}}
        # Test with an empty list
        data2 = []
        with pytest.raises(IndexError):
            _navigate_segment(data2, segment)

        # Test when data is a string
        data3 = "value"
        segment = "key"
        assert _navigate_segment(data3, segment) == "value"

        # Test when data is not type dict, list, or str
        data4 = 10
        segment = "key"
        with pytest.raises(TypeError):
            _navigate_segment(data4, segment)  # type: ignore[arg-type]
