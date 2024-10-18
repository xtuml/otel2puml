"""Tests for json_config.py."""
from typing import Any

import pytest
from pytest import MonkeyPatch
from pydantic import ValidationError

from tel2puml.otel_to_pv.data_sources.json_data_source.json_config import (
    JQFieldSpec,
    FieldSpec,
    field_spec_mapping_to_jq_field_spec_mapping,
    JSONDataSourceConfig,
    OTelFieldMapping,
)


class TestJQFieldSpec:
    """Tests for JQFieldSpec class."""

    @staticmethod
    def test_validate_key_values_with_key_paths() -> None:
        """Test validate_key_values_with_key_paths."""
        # test correct case
        key_paths_1: list[tuple[str | None]] = [("key1",), ("key2",)]
        key_values = [("value1",), ("value2",)]
        JQFieldSpec.validate_key_values_with_key_paths(key_paths_1, key_values)
        # test case where key values and key paths are of different lengths
        key_paths = [("key1",), ("key2",)]
        key_values = [("value1",)]
        with pytest.raises(ValueError):
            JQFieldSpec.validate_key_values_with_key_paths(
                key_paths, key_values
            )
        # test case where priority key paths and priority key values are of
        # different lengths
        key_paths_2 = list([("key1", "key2"), ("key2",)])
        key_values = [("value1",), ("value2",)]
        with pytest.raises(ValueError):
            JQFieldSpec.validate_key_values_with_key_paths(
                key_paths_2, key_values
            )

    @staticmethod
    def test_validate_value_paths_with_key_values() -> None:
        """Test validate_value_paths_with_key_values."""
        # test correct case
        value_paths: list[tuple[str | None, ...]] = [
            ("path1", None),
            ("path2", None, None),
        ]
        key_values = [("value1", None), (None, None, None)]
        JQFieldSpec.validate_value_paths_with_key_values(
            value_paths, key_values
        )
        # test case where value paths and key values are of different lengths
        value_paths = [("path1", None), ("path2", None, None)]
        key_values = [("value1", None)]
        with pytest.raises(ValueError):
            JQFieldSpec.validate_value_paths_with_key_values(
                value_paths, key_values
            )
        # test case where priority value paths and priority key values are of
        # different lengths
        value_paths = [("path1", None), ("path2", None, None)]
        key_values = [("value1", None), (None, None)]
        with pytest.raises(ValueError):
            JQFieldSpec.validate_value_paths_with_key_values(
                value_paths, key_values
            )
        # test case where a value path is None but the corresponding key value
        # is not
        value_paths = [("path1", None), (None, None, None)]
        key_values = [("value1", None), ("value2", None, None)]
        with pytest.raises(ValueError):
            JQFieldSpec.validate_value_paths_with_key_values(
                value_paths, key_values
            )

    @staticmethod
    def test_init() -> None:
        """Test __init__."""
        key_paths = [("key1",), ("key2",)]
        key_values = [("value1",), ("value2",)]
        value_paths = [("path1",), ("path2",)]
        value_type = "string"
        jq_field_spec = JQFieldSpec(
            key_paths, key_values, value_paths, value_type
        )
        assert jq_field_spec.key_paths == key_paths
        assert jq_field_spec.key_values == key_values
        assert jq_field_spec.value_paths == value_paths
        assert jq_field_spec.value_type == value_type

    @staticmethod
    def test__eq__(monkeypatch: MonkeyPatch) -> None:
        """Test __eq__."""
        monkeypatch.setattr(
            JQFieldSpec, "validate_key_values_with_key_paths", lambda *_: None
        )
        monkeypatch.setattr(
            JQFieldSpec,
            "validate_value_paths_with_key_values",
            lambda *_: None,
        )
        jq_field_spec_1 = JQFieldSpec(
            key_paths=[("key1",), ("key2",)],
            key_values=[("value1",), ("value2",)],
            value_paths=[("path1",), ("path2",)],
            value_type="string",
        )
        # test case where the two objects are equal
        jq_field_spec_2 = JQFieldSpec(
            key_paths=[("key1",), ("key2",)],
            key_values=[("value1",), ("value2",)],
            value_paths=[("path1",), ("path2",)],
            value_type="string",
        )
        assert jq_field_spec_1 == jq_field_spec_2
        # test case where the two objects are not equal
        jq_field_spec_3 = JQFieldSpec(
            key_paths=[("key1",), ("key2",)],
            key_values=[("value1",), (None,)],
            value_paths=[("path1",), ("path2",)],
            value_type="string",
        )
        assert jq_field_spec_1 != jq_field_spec_3
        # test case where the comparison object is not an instance of
        # JQFieldSpec
        assert jq_field_spec_1 != "string"

    def test_field_spec_key_path_to_jq_key_path(self) -> None:
        """Test field_spec_key_path_to_jq_key_path."""
        # test correct cases
        field_spec_key_path_1 = "key1"
        assert ("key1",) == JQFieldSpec.field_spec_key_path_to_jq_key_path(
            field_spec_key_path_1
        )
        field_spec_key_path_2 = ["key1", "key2"]
        assert (
            "key1",
            "key2",
        ) == JQFieldSpec.field_spec_key_path_to_jq_key_path(
            field_spec_key_path_2
        )
        # test case in which key path is not a string or an iterable
        field_spec_key_path_3 = 1
        with pytest.raises(TypeError):
            JQFieldSpec.field_spec_key_path_to_jq_key_path(
                field_spec_key_path_3  # type: ignore[arg-type]
            )
        # test case with an iterable in which one of the elements is not a
        # string
        field_spec_key_path_4 = ["key1", 1]
        with pytest.raises(TypeError):
            JQFieldSpec.field_spec_key_path_to_jq_key_path(
                field_spec_key_path_4  # type: ignore[arg-type]
            )

    def test_field_spec_key_paths_to_jq_field_spec_key_paths(self) -> None:
        """Test field_spec_key_paths_to_jq_field_spec_key_paths."""
        field_spec_key_paths_1 = ["key1", "key2"]
        assert [
            ("key1",),
            ("key2",),
        ] == JQFieldSpec.field_spec_key_paths_to_jq_field_spec_key_paths(
            field_spec_key_paths_1
        )
        field_spec_key_paths_2 = [["key1", "key2"], ["key3", "key4"]]
        assert [
            ("key1", "key2"),
            ("key3", "key4"),
        ] == JQFieldSpec.field_spec_key_paths_to_jq_field_spec_key_paths(
            field_spec_key_paths_2
        )

    @staticmethod
    def test_optional_list_value_to_jq_optional_list_value() -> None:
        """Test optional_list_value_to_jq_optional_list_value."""
        # test case where optional list is None
        optional_list_value_1 = None
        jq_key_path_1 = ("key1", "key2")
        assert (
            None,
            None,
        ) == JQFieldSpec.optional_list_value_to_jq_optional_list_value(
            optional_list_value_1, jq_key_path_1
        )
        # test case where optional list is a string
        optional_list_value_2 = "value1"
        jq_key_path_2 = ("key1",)
        assert (
            "value1",
        ) == JQFieldSpec.optional_list_value_to_jq_optional_list_value(
            optional_list_value_2, jq_key_path_2
        )
        # test case where key value not a string, None or an iterable
        optional_list_value_3 = 1
        jq_key_path_3 = ("key1",)
        with pytest.raises(TypeError) as e:
            JQFieldSpec.optional_list_value_to_jq_optional_list_value(
                optional_list_value_3, jq_key_path_3  # type: ignore[arg-type]
            )
            assert "Key value must be iterable or a string" in str(e)
        # test case where key value is an iterable
        optional_list_value_4 = ["value1", None]
        jq_key_path_4 = ("key1",)
        assert (
            "value1",
            None,
        ) == JQFieldSpec.optional_list_value_to_jq_optional_list_value(
            optional_list_value_4, jq_key_path_4
        )
        # test case where key value is an iterable but one of the elements is
        # not a string or None
        optional_list_value_5 = ["value1", 1]
        jq_key_path_5 = ("key1",)
        with pytest.raises(TypeError) as e:
            JQFieldSpec.optional_list_value_to_jq_optional_list_value(
                optional_list_value_5, jq_key_path_5  # type: ignore[arg-type]
            )
            assert (
                "Priority key value, within an iterable, must be a string or"
                " None" in str(e)
            )

    def test_optional_list_to_jq_optional_list(self) -> None:
        """Test field_spec_optional_list_to_jq_field_spec_optional_list."""
        # test case where optional list is None
        optional_list_1 = None
        jq_key_paths = [("key1",), ("key2",)]
        assert [
            (None,),
            (None,),
        ] == JQFieldSpec.optional_list_to_jq_optional_list(
            optional_list_1, jq_key_paths
        )
        # test case where optional list is not None
        optional_list_2 = ["value1", ["value2", "value3"]]
        jq_key_paths = [("key1",), ("key2",)]
        assert [
            ("value1",),
            ("value2", "value3"),
        ] == JQFieldSpec.optional_list_to_jq_optional_list(
            optional_list_2, jq_key_paths
        )
        # test case where key value is not a string or an iterable
        optional_list_3 = [1]
        jq_key_paths = [("key1",)]
        with pytest.raises(TypeError):
            JQFieldSpec.optional_list_to_jq_optional_list(
                optional_list_3, jq_key_paths  # type: ignore[arg-type]
            )
        # test case where key value is an iterable but one of the elements is
        # not a string
        optional_list_4 = [["value1", 1]]
        jq_key_paths = [("key1",)]
        with pytest.raises(TypeError):
            JQFieldSpec.optional_list_to_jq_optional_list(
                optional_list_4, jq_key_paths  # type: ignore[arg-type]
            )

    @staticmethod
    def test_from_field_spec() -> None:
        """Test from_field_spec class method"""
        # test case key values and value paths are not provided
        field_spec = FieldSpec(
            key_paths=["key1", "key2"],
            key_value=None,
            value_paths=None,
            value_type="string",
        )
        jq_field_spec = JQFieldSpec.from_field_spec(field_spec)
        assert jq_field_spec == JQFieldSpec(
            key_paths=[("key1",), ("key2",)],
            key_values=[(None,), (None,)],
            value_paths=[(None,), (None,)],
            value_type="string",
        )
        # test case key values and value paths are provided
        field_spec = FieldSpec(
            key_paths=["key1", "key2"],
            key_value=["value1", "value2"],
            value_paths=["path1", "path2"],
            value_type="string",
        )
        jq_field_spec = JQFieldSpec.from_field_spec(field_spec)
        assert jq_field_spec == JQFieldSpec(
            key_paths=[("key1",), ("key2",)],
            key_values=[("value1",), ("value2",)],
            value_paths=[("path1",), ("path2",)],
            value_type="string",
        )


def test_field_spec_mapping_to_jq_field_spec_mapping(
    field_mapping_for_fixture_data: dict[str, FieldSpec],
    jq_field_mapping_for_fixture_data: dict[str, JQFieldSpec],
) -> None:
    """Test field_spec_mapping_to_jq_field_spec_mapping."""
    assert (
        jq_field_mapping_for_fixture_data
        == field_spec_mapping_to_jq_field_spec_mapping(
            field_mapping_for_fixture_data
        )
    )


class TestJSONDataSourceConfig:
    """Tests for JSONDataSourceConfig class."""
    @staticmethod
    def valid_field_spec() -> dict[str, str]:
        """Return a valid field spec."""
        return dict(key_paths="key1", value_type="string")

    @staticmethod
    def invalid_field_spec() -> dict[str, str]:
        """Return an invalid field spec."""
        return dict(
            key_paths="key1",
        )

    def otel_field_mapping(
        self, valid: bool = True, with_child: bool = False
    ) -> dict[str, dict[str, str]]:
        """Return an otel field mapping dictionary"""
        field_mapping = {
            "job_name": self.valid_field_spec(),
            "job_id": self.valid_field_spec(),
            "event_type": self.valid_field_spec(),
            "event_id": self.valid_field_spec(),
            "start_timestamp": self.valid_field_spec(),
            "end_timestamp": self.valid_field_spec(),
            "application_name": self.valid_field_spec(),
            "parent_event_id": (
                self.valid_field_spec() if valid else self.invalid_field_spec()
            ),
        }
        if with_child:
            field_mapping["child_event_ids"] = self.valid_field_spec()
        return field_mapping

    def test_otel_field_mapping(self) -> None:
        """Test otel_field_mapping."""
        # test case where all field specs are valid and no child event ids
        # field

        def check_fields(otel_mapping_model: OTelFieldMapping) -> None:
            assert otel_mapping_model.job_name == self.valid_field_spec()
            assert otel_mapping_model.event_type == self.valid_field_spec()
            assert otel_mapping_model.event_id == self.valid_field_spec()
            assert otel_mapping_model.job_id == self.valid_field_spec()
            assert (
                otel_mapping_model.start_timestamp == self.valid_field_spec()
            )
            assert otel_mapping_model.end_timestamp == self.valid_field_spec()
            assert (
                otel_mapping_model.application_name == self.valid_field_spec()
            )
            assert (
                otel_mapping_model.parent_event_id == self.valid_field_spec()
            )

        model = OTelFieldMapping(**self.otel_field_mapping())
        check_fields(model)
        assert model.child_event_ids is None
        # test case where all field specs are valid and there is a child event
        # ids field
        model = OTelFieldMapping(**self.otel_field_mapping(with_child=True))
        check_fields(model)
        assert model.child_event_ids == self.valid_field_spec()
        # test case where one of the field specs is invalid
        with pytest.raises(ValidationError):
            OTelFieldMapping(**self.otel_field_mapping(valid=False))

    def test_json_data_source_config(self) -> None:
        """Test JSONDataSourceConfig."""
        # test cases where input config should be valid
        field_mapping = self.otel_field_mapping()
        # case with all cases of valid combinations of filepath and dirpath
        for case_1 in [("filepath", None), (None, "dirpath")]:
            config_dict: dict[str, Any] = dict(
                field_mapping=field_mapping,
                filepath=case_1[0],
                dirpath=case_1[1],
                json_per_line=True,
            )
            config = JSONDataSourceConfig(
                **config_dict
            )
            assert config.field_mapping == OTelFieldMapping(**field_mapping)
            assert config.filepath == case_1[0]
            assert config.dirpath == case_1[1]
            assert config.json_per_line
        # case with all valid combinations of field mapping and jq query
        for case_2 in [(field_mapping, None), (None, "jq_query")]:
            config_dict = dict(
                field_mapping=case_2[0],
                filepath="filepath",
                dirpath=None,
                json_per_line=False,
                jq_query=case_2[1],
            )
            config = JSONDataSourceConfig(
                **config_dict
            )
            assert config.field_mapping == (
                OTelFieldMapping(**field_mapping)
                if (case_2[0] is not None)
                else None
            )
            assert config.jq_query == case_2[1]
            assert not config.json_per_line
            assert config.filepath == "filepath"
            assert config.dirpath is None
        # test case negative cases of incorrect types
        for case_3 in [
            "field_mapping",
            "filepath",
            "dirpath",
            "jq_query",
            "json_per_line",
        ]:
            input_dict: dict[str, Any] = dict(
                field_mapping=field_mapping,
                filepath="filepath",
                dirpath=None,
                json_per_line=True,
                jq_query=None,
            )
            input_dict[case_3] = 1
            with pytest.raises(ValidationError):
                JSONDataSourceConfig(**input_dict)
        # test case where both field_mapping and jq_query are None
        with pytest.raises(ValidationError):
            JSONDataSourceConfig(
                field_mapping=None,
                filepath="filepath",
                dirpath=None,
                json_per_line=True,
                jq_query=None,
            )
        # test case where both field mapping and jq query are provided
        with pytest.raises(ValidationError):
            config_dict = dict(
                field_mapping=field_mapping,
                filepath="filepath",
                dirpath=None,
                json_per_line=True,
                jq_query="jq_query",
            )
            JSONDataSourceConfig(
                **config_dict
            )
        # test case where file path and dir path are both None
        with pytest.raises(ValidationError):
            config_dict = dict(
                field_mapping=field_mapping,
                filepath=None,
                dirpath=None,
                json_per_line=True,
                jq_query=None,
            )
            JSONDataSourceConfig(
                **config_dict
            )
        # test case where both file path and dir path are provided
        with pytest.raises(ValidationError):
            config_dict = dict(
                field_mapping=field_mapping,
                filepath="filepath",
                dirpath="dirpath",
                json_per_line=True,
                jq_query=None,
            )
            JSONDataSourceConfig(
                **config_dict
            )
