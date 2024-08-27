"""Tests for json data converter module."""

import pytest
import unittest.mock
import flatdict

from typing import Any

from tel2puml.find_unique_graphs.otel_ingestion.json_data_converter import (
    _navigate_dict,
    _navigate_list,
    _extract_value_from_path,
    _extract_simple_value,
    _update_header_dict,
    _extract_nested_value,
)


class TestProcessHeaders:
    """Tests for processing headers within json data converter module."""

    @staticmethod
    def test_navigate_dict() -> None:
        """Tests the function _navigate_segment"""

        data = {"key1": {"key2": "value"}}
        segment = "key1"
        assert _navigate_dict(data, segment) == {"key2": "value"}
        # Test with an invalid key
        invalid_segment = "invalid"
        with pytest.raises(KeyError):
            _navigate_dict(data, invalid_segment)

    @staticmethod
    def test_navigate_list() -> None:
        """Tests the function _navigate_segment"""

        data = [{"key1": {"key2": "value"}}]
        assert _navigate_list(data) == {"key1": {"key2": "value"}}
        # Test with an empty list
        data = []
        with pytest.raises(IndexError):
            _navigate_list(data)

    @staticmethod
    def test_extract_simple_value() -> None:
        """Tests the function _extract_simple_value."""

        # Test returning a string value
        data = {"key1": {"key2": "value"}}
        path = "key1:key2"
        assert _extract_simple_value(data, path) == "value"

        # Test returning a dict
        data = {"key1": {"key2": "value"}}
        path = "key1"
        assert _extract_simple_value(data, path) == {"key2": "value"}

        # Test returning a list
        data2 = {
            "key1": {
                "key2": [
                    {"id": 1, "name": "item1"},
                    {"id": 2, "name": "item2"},
                ]
            }
        }
        path = "key1:key2"
        assert _extract_simple_value(data2, path) == [
            {"id": 1, "name": "item1"},
            {"id": 2, "name": "item2"},
        ]

    @staticmethod
    def test_extract_value_from_path() -> None:
        """Tests the function _extract_value_from_path"""

        with unittest.mock.patch(
            "tel2puml.find_unique_graphs.otel_ingestion.json_data_converter._extract_simple_value"
        ) as extract_simple_value, unittest.mock.patch(
            "tel2puml.find_unique_graphs.otel_ingestion.json_data_converter._extract_nested_value"
        ) as extract_nested_value:
            # Test simple path
            data = {"key1": {"key2": "value"}}
            path = "key1:key2"
            _extract_value_from_path(data, path)
            extract_simple_value.assert_called_once()
            extract_nested_value.assert_not_called()

            # Reset the mocks
            extract_simple_value.reset_mock()
            extract_nested_value.reset_mock()

            # Test complex path
            data2 = {
                "key1": [
                    {"id": 1, "name": "item1"},
                    {"id": 2, "name": "item2"},
                ]
            }
            path = "key1::id"
            _extract_value_from_path(data2, path)
            extract_simple_value.assert_not_called()
            extract_nested_value.assert_called_once()

    @staticmethod
    def test_update_header_dict() -> None:
        """Tests the function _update_header_dict"""

        # Test updating with a dict simple path
        header_dict: dict[str, Any] = {}
        path1 = "key1:key2"
        value1 = {"key3": "value"}
        _update_header_dict(header_dict, path1, value1)
        assert header_dict[path1]
        assert header_dict[path1] == flatdict.FlatterDict(value1)

        # Test updating with a dict complex path
        header_dict = {}
        path2 = "key1::key2"
        value2 = {"key3": "value"}
        _update_header_dict(header_dict, path2, value2)
        assert header_dict["key1"] == flatdict.FlatterDict(value2)

        # Test updating with a list simple path
        header_dict = {}
        path3 = "key1:key2"
        value3 = [{"key3": "value"}]
        _update_header_dict(header_dict, path3, value3)
        assert header_dict[path3]
        assert header_dict[path3] == flatdict.FlatterDict(value3)

        # Test updating with a list complex path
        header_dict = {}
        path4 = "key1::key2"
        value4 = [{"key3": "value"}]
        _update_header_dict(header_dict, path4, value4)
        assert header_dict["key1"] == flatdict.FlatterDict(value4)

        # Test updating with a string simple path
        header_dict = {}
        path5 = "key1:key2"
        value5 = "value"
        _update_header_dict(header_dict, path5, value5)
        assert header_dict[path5] == "value"

        # Test updating with a string complex path
        header_dict = {}
        path6 = "key1::key2"
        value6 = "value"
        _update_header_dict(header_dict, path6, value6)
        assert header_dict["key1"] == "value"
