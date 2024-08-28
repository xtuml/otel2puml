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
    _build_nested_dict,
    _extract_nested_value,
    process_header,
    _get_value_type,
    _add_or_append_value,
)
from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    IngestDataConfig,
    JSONDataSourceConfig,
)


class TestProcessHeaders:
    """Tests for processing headers within json data converter module."""

    @staticmethod
    def test_navigate_dict() -> None:
        """Tests the function _navigate_dict"""

        # Test valid dict
        data1 = {"key1": {"key2": "value2"}}
        segment1 = "key1"
        expected1 = {"key2": "value2"}
        assert _navigate_dict(data1, segment1) == expected1

        # Test valid string
        data2 = {"key1": "value1"}
        segment2 = "key1"
        expected2 = "value1"
        assert _navigate_dict(data2, segment2) == expected2

        # Test valid list
        data3 = {"key1": [{"key2": "value2"}, {"key3": "value3"}]}
        segment3 = "key1"
        expected3 = [{"key2": "value2"}, {"key3": "value3"}]
        assert _navigate_dict(data3, segment3) == expected3

        # Test with an invalid key
        data4 = {"key1": "value1"}
        segment4 = "invalid"
        with pytest.raises(KeyError):
            _navigate_dict(data4, segment4)

        # Test invalid type
        data5 = {"key1": 123}  # Not a dict, list, or str
        segment5 = "key1"
        with pytest.raises(TypeError):
            _navigate_dict(data5, segment5)

    @staticmethod
    def test_navigate_list() -> None:
        """Tests the function _navigate_list"""

        # Test non empty list
        data1 = [{"key1": {"key2": "value"}}]
        assert _navigate_list(data1) == {"key1": {"key2": "value"}}

        # Test list with single element
        data2 = [{"key1": "value1"}]
        expected2 = {"key1": "value1"}
        assert _navigate_list(data2) == expected2

        # Test with an empty list
        data3: list[dict[str, Any]] = []
        with pytest.raises(IndexError):
            _navigate_list(data3)

        # Test list with more than one element
        data4 = [{"key1": "value1"}, {"key2": "value2"}]
        with pytest.raises(ValueError):
            _navigate_list(data4)

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
            "tel2puml.find_unique_graphs.otel_ingestion."
            "json_data_converter._extract_simple_value"
        ) as extract_simple_value, unittest.mock.patch(
            "tel2puml.find_unique_graphs.otel_ingestion."
            "json_data_converter._extract_nested_value"
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
        assert len(header_dict) == 1
        assert header_dict[path1] == flatdict.FlatterDict(value1)

        # Test updating with a dict complex path
        header_dict = {}
        path2 = "key1::key2"
        value2 = {"key3": "value"}
        _update_header_dict(header_dict, path2, value2)
        assert len(header_dict) == 1
        assert header_dict["key1"] == flatdict.FlatterDict(value2)

        # Test updating with a list simple path
        header_dict = {}
        path3 = "key1:key2"
        value3 = [{"key3": "value"}]
        _update_header_dict(header_dict, path3, value3)
        assert len(header_dict) == 1
        assert header_dict[path3] == flatdict.FlatterDict(value3)

        # Test updating with a list complex path
        header_dict = {}
        path4 = "key1::key2"
        value4 = [{"key3": "value"}]
        _update_header_dict(header_dict, path4, value4)
        assert len(header_dict) == 1
        assert header_dict["key1"] == flatdict.FlatterDict(value4)

        # Test updating with a string simple path
        header_dict = {}
        path5 = "key1:key2"
        value5 = "value"
        _update_header_dict(header_dict, path5, value5)
        assert len(header_dict) == 1
        assert header_dict[path5] == "value"

        # Test updating with a string complex path
        header_dict = {}
        path6 = "key1::key2"
        value6 = "value"
        _update_header_dict(header_dict, path6, value6)
        assert len(header_dict) == 1
        assert header_dict["key1"] == "value"

    @staticmethod
    def test_build_nested_dict() -> None:
        """Tests the function _build_nested_dict"""

        # Test multiple segments
        path_segments1 = ["key1", "key2", "key3"]
        parsed_data1 = {"key4": "value4"}
        expected1 = {"key2": {"key3": {"key4": "value4"}}}
        assert _build_nested_dict(path_segments1, parsed_data1) == expected1

        # Test with string data
        path_segments2 = ["key1", "key2", "key3"]
        parsed_data2 = "string_value"
        expected2 = {"key2": {"key3": "string_value"}}
        assert _build_nested_dict(path_segments2, parsed_data2) == expected2

        # Test with list of dicts
        path_segments3 = ["key1", "key2", "key3"]
        parsed_data3 = [{"key4": "value4"}, {"key5": "value5"}]
        expected3 = {
            "key2": {"key3": [{"key4": "value4"}, {"key5": "value5"}]}
        }
        assert _build_nested_dict(path_segments3, parsed_data3) == expected3

        # Test error handling with one path segment. In reality there will
        # always be more than one path segment since the path requires '::'
        # for the function to be reached
        path_segments4 = ["key"]
        parsed_data4 = "string_value"
        with pytest.raises(TypeError):
            _build_nested_dict(path_segments4, parsed_data4)

    @staticmethod
    def test_extract_nested_value() -> None:
        """Tests the function _extract_nested_value"""
        sample_data = {
            "resource": {
                "attributes": [
                    {
                        "service": {"name": "frontend"},
                        "response": "200",
                        "spans": [{"trace_id": "001"}, {"span_id": "002"}],
                    }
                ]
            },
            "host": [{"provider": "receiever"}],
        }

        # Test simple case
        path = "host::provider"
        assert _extract_nested_value(sample_data, path) == {
            "provider": "receiever"
        }

        # Test nested dictionary before list
        path = "resource:attributes::response"
        assert _extract_nested_value(sample_data, path) == {"response": "200"}

        # Test nested dictionary before and after list
        path = "resource:attributes::service:name"
        assert _extract_nested_value(sample_data, path) == {
            "service:name": "frontend"
        }

        # Test larger nested data structure after list
        path = "resource:attributes::spans"
        assert _extract_nested_value(sample_data, path) == {
            "spans": [{"trace_id": "001"}, {"span_id": "002"}]
        }

    @staticmethod
    def test_process_header(
        mock_yaml_config_dict: IngestDataConfig, mock_json_data: dict[str, Any]
    ) -> None:
        """Tests for the function process_header"""
        json_config: JSONDataSourceConfig = mock_yaml_config_dict[
            "data_sources"
        ]["json"]

        # data_location within config.yaml will already have parsed json
        # resulting in the below
        mock_data = mock_json_data["resource_spans"][0]

        header_dict: dict[str, Any] = process_header(json_config, mock_data)

        assert len(header_dict) == 2
        assert header_dict["resource:attributes"] == flatdict.FlatterDict(
            [
                {
                    "key": "service.name",
                    "value": {"Value": {"StringValue": "Frontend"}},
                },
                {
                    "key": "service.version",
                    "value": {"Value": {"StringValue": "1.0"}},
                },
            ]
        )
        assert header_dict["scope_spans"] == flatdict.FlatterDict(
            {"scope": {"name": "TestJob"}}
        )


class TestProcessHeaderTags:
    """Tests for processing header tags within span field_mapping"""


def test_get_value_type() -> None:
    """Tests the function _get_value_type"""

    # Test with existing field
    field_config = {"key_paths": ["span_id"], "value_type": "string"}
    assert _get_value_type(field_config) == "string"

    # Test with non-existing field
    field_config = {"key_paths": ["span_id"]}
    with pytest.raises(KeyError):
        _get_value_type(field_config)


def test_add_or_append_value() -> None:
    """Tests the function _add_or_append_value"""

    # test adding unix nano, value int
    result = {}
    _add_or_append_value(
        "start_timestamp", 1723544132228102912, result, "unix_nano"
    )
    assert len(result) == 1
    assert result["start_timestamp"] == 1723544132228102912

    # test adding unix nano, value non-int
    result = {}
    with pytest.raises(TypeError):
        _add_or_append_value(
            "start_timestamp", "1723544132228102912", result, "unix_nano"
        )

    # test adding string
    result = {}
    _add_or_append_value("span_id", "001", result, "string")
    assert len(result) == 1
    assert result["span_id"] == "001"

    # test adding non-string
    result = {}
    _add_or_append_value("span_id", 1, result, "string")
    assert len(result) == 1
    assert result["span_id"] == "1"

    # test appending to existing field
    result = {"name": "Frontend"}
    _add_or_append_value("name", "1.0", result, "string")
    assert len(result) == 1
    assert result["name"] == "Frontend 1.0"
