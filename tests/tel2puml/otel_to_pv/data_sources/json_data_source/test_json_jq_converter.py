"""Tests for the json_jq_converter module."""
from typing import Any
import pytest

import jq  # type: ignore[import-not-found]

from tel2puml.otel_to_pv.data_sources.json_data_source.json_config \
    import JQFieldSpec, FieldSpec
from tel2puml.otel_to_pv.data_sources.json_data_source.json_jq_converter \
    import (
        JQVariableTree,
        get_updated_path_from_key_path_key_value_and_root_var_tree,
        update_field_spec_with_variables,
        update_field_specs_with_variables,
        build_base_variable_jq_query,
        get_jq_for_field_spec,
        get_jq_using_field_mapping,
        get_jq_query_from_field_mapping_with_variables_and_var_tree,
        jq_field_mapping_to_jq_query,
        jq_field_mapping_to_compiled_jq,
        field_mapping_to_compiled_jq,
        generate_records_from_compiled_jq
    )


class TestJQVariableTree:
    """Tests for the JQVariableTree class."""
    @staticmethod
    def test__init__() -> None:
        """Test the __init__ method of the JQVariableTree class."""
        # test with defaults
        var_tree = JQVariableTree()
        assert var_tree.var_num == 0
        assert var_tree.var_prefix == "var"
        assert len(var_tree.child_var_dict) == 0
        # test with custom values
        var_tree = JQVariableTree(var_num=1, var_prefix="variable")
        assert var_tree.var_num == 1
        assert var_tree.var_prefix == "variable"
        assert len(var_tree.child_var_dict) == 0

    @staticmethod
    def test_add_child() -> None:
        """Test the add_child method of the JQVariableTree class."""
        var_tree = JQVariableTree(var_num=0, var_prefix="test")
        # test case with no children
        first_child = var_tree.add_child("first", 1)
        assert len(var_tree.child_var_dict) == 1
        assert "first" in var_tree.child_var_dict
        assert var_tree.child_var_dict["first"] == first_child
        assert first_child.var_num == 1
        assert first_child.var_prefix == "test"
        # test case with another child
        second_child = var_tree.add_child("second", 2)
        assert len(var_tree.child_var_dict) == 2
        assert (
            "second" in var_tree.child_var_dict
            and "first" in var_tree.child_var_dict
        )
        assert var_tree.child_var_dict["second"] == second_child
        assert second_child.var_num == 2
        assert second_child.var_prefix == "test"
        # test case with a child that already exists
        with pytest.raises(ValueError):
            var_tree.add_child("first", 3)

    @staticmethod
    def test_has_child() -> None:
        """Test the has_child method of the JQVariableTree class."""
        var_tree = JQVariableTree(var_num=0, var_prefix="test")
        assert not var_tree.has_child("first")
        var_tree.add_child("first", 1)
        assert var_tree.has_child("first")

    @staticmethod
    def test_get_child() -> None:
        """Test the get_variable method of the JQVariableTree class."""
        var_tree = JQVariableTree(var_num=0, var_prefix="test")
        # test case with no children
        with pytest.raises(KeyError):
            var_tree.get_child("first")
        # test case with a single child
        first_child = var_tree.add_child("first", 1)
        assert var_tree.get_child("first") == first_child
        with pytest.raises(KeyError):
            var_tree.get_child("second")
        # test case with multiple children
        second_child = var_tree.add_child("second", 2)
        assert var_tree.get_child("second") == second_child

    @staticmethod
    def test__str__() -> None:
        """Test the __str__ method of the JQVariableTree class."""
        var_tree = JQVariableTree(var_num=0, var_prefix="test")
        assert str(var_tree) == "$test0"
        var_tree = JQVariableTree(var_num=1, var_prefix="variable")
        assert str(var_tree) == "$variable1"


class TestFieldMappingToCompiledJQ:
    """Tests for the field_mapping_to_compiled_jq function and related
    functions."""
    @staticmethod
    def check_first_child(
        first_child: JQVariableTree, second_child: bool = False
    ) -> None:
        """Check the first child of the root variable tree and its children."""
        assert first_child.var_num == 1
        if second_child:
            assert len(first_child.child_var_dict) == 1
            assert "second_1.second_2" in first_child.child_var_dict
            second_child_var = first_child.child_var_dict["second_1.second_2"]
            assert second_child_var.var_num == 2
            assert len(second_child_var.child_var_dict) == 0
        else:
            assert len(first_child.child_var_dict) == 0

    def check_root_var_tree(
        self,
        root_var_tree: JQVariableTree,
        second_child: bool = False,
    ) -> None:
        """Check the root variable tree and its children."""
        assert len(root_var_tree.child_var_dict) == 1
        assert "first" in root_var_tree.child_var_dict
        first_child = root_var_tree.child_var_dict["first"]
        self.check_first_child(first_child, second_child=second_child)

    def check_root_var_tree_for_no_arrays(
        self, root_var_tree: JQVariableTree
    ) -> None:
        """Check the root variable tree and its children when there are no
        arrays in the key path."""
        assert len(root_var_tree.child_var_dict) == 0

    def test_get_updated_path_from_key_path_key_value_and_root_var_tree(
        self,
    ) -> None:
        """Test the get_updated_path_from_key_path_key_value_and_root_var_tree
        function."""
        root_var_tree = JQVariableTree()
        # test case with key value
        key_path = "first.[].second_1.second_2.[].third_1.third_2"
        key_value = "value"
        expected_key_path = "$var1.second_1.second_2.[].third_1.third_2"
        updated_key_path, var_num = (
            get_updated_path_from_key_path_key_value_and_root_var_tree(
                key_path, key_value, root_var_tree, var_num=0
            )
        )
        assert updated_key_path == expected_key_path
        assert var_num == 1

        self.check_root_var_tree(root_var_tree)
        # test case without key value
        root_var_tree = JQVariableTree()
        expected_key_path = "$var2.third_1.third_2"
        updated_key_path, var_num = (
            get_updated_path_from_key_path_key_value_and_root_var_tree(
                key_path, None, root_var_tree, var_num=0
            )
        )
        assert updated_key_path == expected_key_path
        assert var_num == 2
        self.check_root_var_tree(root_var_tree, second_child=True)
        # test case with no arrays in key path
        root_var_tree = JQVariableTree()
        key_path = "first.second.third"
        expected_key_path = "$var0." + key_path
        updated_key_path, var_num = (
            get_updated_path_from_key_path_key_value_and_root_var_tree(
                key_path, None, root_var_tree, var_num=0
            )
        )
        assert updated_key_path == expected_key_path
        assert var_num == 0
        self.check_root_var_tree_for_no_arrays(root_var_tree)
        # test case with key value and no arrays in key path
        root_var_tree = JQVariableTree()
        key_path = "first.second.third"
        key_value = "value"
        with pytest.raises(ValueError):
            get_updated_path_from_key_path_key_value_and_root_var_tree(
                key_path, key_value, root_var_tree, var_num=0
            )

    def test_update_field_spec_with_variables(
        self, field_spec_1: JQFieldSpec, field_spec_2: JQFieldSpec,
        field_spec_4: JQFieldSpec
    ) -> None:
        """Test the update_field_spec_with_variables function."""
        field_spec = field_spec_1
        root_var_tree = JQVariableTree()
        var_num = update_field_spec_with_variables(field_spec, root_var_tree)
        assert var_num == 2
        assert field_spec.key_paths == [
            ("$var1.second_1.second_2.[].third_1.third_2",),
            ("$var2.third_1.third_2",),
        ]
        self.check_root_var_tree(root_var_tree, second_child=True)
        field_spec = field_spec_2
        root_var_tree = JQVariableTree()
        var_num = update_field_spec_with_variables(field_spec, root_var_tree)
        assert var_num == 0
        assert field_spec.key_paths == [
            ("$var0.first.second.third",),
            ("$var0.first.second.third",),
        ]
        self.check_root_var_tree_for_no_arrays(root_var_tree)
        # check case with tuples containing multiple values
        field_spec = field_spec_4
        root_var_tree = JQVariableTree()
        var_num = update_field_spec_with_variables(field_spec, root_var_tree)
        assert var_num == 2
        assert field_spec.key_paths == [
            (
                "$var1.second_1.second_2.[].third_1.third_2",
                "$var2.third_1.third_2",
            ),
        ]
        self.check_root_var_tree(root_var_tree, second_child=True)

    def test_update_field_specs_with_variables(
        self,
        field_mapping: dict[str, JQFieldSpec],
        field_mapping_with_variables: dict[str, JQFieldSpec],
    ) -> None:
        """Test the update_field_specs_with_variables function."""
        root_var_tree = update_field_specs_with_variables(field_mapping)
        assert len(field_mapping) == 3
        assert len(root_var_tree.child_var_dict) == 2
        assert "first" in root_var_tree.child_var_dict
        assert "fourth" in root_var_tree.child_var_dict
        first_child = root_var_tree.child_var_dict["first"]
        self.check_first_child(first_child, second_child=True)
        second_child = root_var_tree.child_var_dict["fourth"]
        self.check_root_var_tree_for_no_arrays(second_child)
        assert field_mapping == field_mapping_with_variables

    @staticmethod
    def test_build_base_variable_jq_query() -> None:
        """Test the build_base_variable_jq_query function."""
        # test root var with no children
        for path in ["", "first", "first.second"]:
            root_var_tree = JQVariableTree()
            assert (
                build_base_variable_jq_query(root_var_tree, path=path)
                == ". as $var0"
            )
        # test root var with one child
        root_var_tree = JQVariableTree()
        first_child = root_var_tree.add_child("first", 1)
        assert build_base_variable_jq_query(root_var_tree) == (
            ". as $var0 | (try $var0.first.[] catch null) as $var1"
        )
        # test case with grandchild
        grand_child = first_child.add_child("grand_child", 2)
        assert build_base_variable_jq_query(root_var_tree) == (
            ". as $var0 | (try $var0.first.[] catch null) as $var1 "
            "| (try $var1.grand_child.[] catch null) as"
            " $var2"
        )
        # test case with great grandchild
        grand_child.add_child("great_grand_child", 3)
        assert build_base_variable_jq_query(root_var_tree) == (
            ". as $var0 | (try $var0.first.[] catch null) as $var1 "
            "| (try $var1.grand_child.[] catch null) as"
            " $var2 "
            "| (try $var2.great_grand_child.[] catch null) as $var3"
        )
        # test case with a sibling of the first child
        root_var_tree.add_child("second", 4)
        assert build_base_variable_jq_query(root_var_tree) == (
            ". as $var0 | (try $var0.first.[] catch null) as $var1 "
            "| (try $var1.grand_child.[] catch null) as"
            " $var2 "
            "| (try $var2.great_grand_child.[] catch null) as $var3"
            " | (try $var0.second.[] catch null) as $var4"
        )
        # test case with a sibling of the first child grandchild
        first_child.add_child("grand_child_2", 5)
        assert build_base_variable_jq_query(root_var_tree) == (
            ". as $var0 | (try $var0.first.[] catch null) as $var1 "
            "| (try $var1.grand_child.[] catch null) as"
            " $var2 "
            "| (try $var2.great_grand_child.[] catch null) as $var3"
            " | (try $var1.grand_child_2.[] catch null) as $var5"
            " | (try $var0.second.[] catch null) as $var4"
        )

    @staticmethod
    def test_get_jq_for_field_spec(
        field_spec_with_variables_1: JQFieldSpec,
        field_spec_with_variables_2: JQFieldSpec,
        field_spec_with_variables_4: JQFieldSpec,
        field_spec_with_variables_1_expected_jq: str,
        field_spec_with_variables_2_expected_jq: str,
        field_spec_with_variables_4_expected_jq: str,
    ) -> None:
        """Test the get_jq_for_field_spec function."""
        field_spec = field_spec_with_variables_1
        assert get_jq_for_field_spec(field_spec, "$out0") == (
            field_spec_with_variables_1_expected_jq
        )
        field_spec = field_spec_with_variables_2
        assert get_jq_for_field_spec(field_spec, "$out1") == (
            field_spec_with_variables_2_expected_jq
        )
        # check case with variable not in the first part of the key path
        field_spec = JQFieldSpec(
            key_paths=[("first.[].second.third",), ("first.second.third",)],
            key_values=[("value",), (None,)],
            value_paths=[("value_path.next",), (None,)],
            value_type="string",
        )
        with pytest.raises(ValueError):
            get_jq_for_field_spec(field_spec, "$out0")
        # check case with variable in the first part of the key path and
        # variable in the rest of the key path
        field_spec = JQFieldSpec(
            key_paths=[
                ("$var0.[].$var1.second.third",),
                ("$var0.first.second.third",),
            ],
            key_values=[("value",), (None,)],
            value_paths=[("value_path.next",), (None,)],
            value_type="string",
        )
        with pytest.raises(ValueError):
            get_jq_for_field_spec(field_spec, "$out0")
        # check case with no arrays in the key path
        field_spec = JQFieldSpec(
            key_paths=[("first.second.third",), ("first.second.third",)],
            key_values=[("value",), (None,)],
            value_paths=[("value_path.next",), (None,)],
            value_type="string",
        )
        with pytest.raises(ValueError):
            get_jq_for_field_spec(field_spec, "$out0")
        # check case with more than one array in the key path
        field_spec = JQFieldSpec(
            key_paths=[
                ("first.[].second.[].third",), ("first.[].second.third",)
            ],
            key_values=[("value",), (None,)],
            value_paths=[("value_path.next",), (None,)],
            value_type="string",
        )
        with pytest.raises(ValueError):
            get_jq_for_field_spec(field_spec, "$out0")
        # check case with multiple values in a single key path signifying
        # priority order
        assert get_jq_for_field_spec(
            field_spec_with_variables_4, "$out3"
        ) == field_spec_with_variables_4_expected_jq

    @staticmethod
    def test_get_jq_using_field_mapping(
        field_mapping_with_variables: dict[str, JQFieldSpec],
        expected_field_mapping_query: str,
    ) -> None:
        """Test the get_jq_using_field_mapping function."""
        field_mapping = field_mapping_with_variables
        assert get_jq_using_field_mapping(field_mapping) == (
            expected_field_mapping_query
        )

    @staticmethod
    def test_get_jq_query_from_field_mapping_with_variables_and_var_tree(
        field_mapping_with_variables: dict[str, JQFieldSpec],
        var_tree: JQVariableTree,
        expected_full_query: str,
    ) -> None:
        """Test the get_jq_query_from_field_mapping_with_variables_and_var_tree
        function."""
        jq_query = get_jq_query_from_field_mapping_with_variables_and_var_tree(
            field_mapping_with_variables, var_tree
        )
        assert jq_query == (expected_full_query)

    @staticmethod
    def test_jq_field_mapping_to_jq_query(
        field_mapping: dict[str, JQFieldSpec],
        expected_full_query: str,
    ) -> None:
        """Test the field_mapping_to_jq_query function."""
        jq_query = jq_field_mapping_to_jq_query(field_mapping)
        assert jq_query == (expected_full_query)

    @staticmethod
    def test_jq_field_mapping_to_compiled_jq(
        jq_field_mapping_for_fixture_data: dict[str, JQFieldSpec],
        mock_json_data: dict[str, Any],
        expected_mapped_json: list[dict[str, str]],
    ) -> None:
        """Test the field_mapping_to_compiled_jq function."""
        compiled_jq = jq_field_mapping_to_compiled_jq(
            jq_field_mapping_for_fixture_data
        )
        output = list(iter(compiled_jq.input_value(mock_json_data)))
        assert output == expected_mapped_json

    @staticmethod
    def test_field_mapping_to_compiled_jq(
        field_mapping_for_fixture_data: dict[str, FieldSpec],
        mock_json_data: dict[str, Any],
        expected_mapped_json: list[dict[str, str]],
    ) -> None:
        """Test the field_mapping_to_compiled_jq function."""
        compiled_jq = field_mapping_to_compiled_jq(
            field_mapping_for_fixture_data
        )
        output = list(iter(compiled_jq.input_value(mock_json_data)))
        assert output == expected_mapped_json

    @staticmethod
    def test_generate_records_from_compiled_jq() -> None:
        """Test the generate_records_from_compiled_jq function."""
        # test case with multiple records
        data = {
            "records": [
                {"first": "value1", "second": "value2"},
                {"first": "value3", "second": "value4"},
            ]
        }
        compiled_jq = jq.compile(".records[]")
        output = list(generate_records_from_compiled_jq(data, compiled_jq))
        assert output == [
            {"first": "value1", "second": "value2"},
            {"first": "value3", "second": "value4"},
        ]
        # test case where the record is a list
        compiled_jq = jq.compile("[.records[]]")
        output = list(generate_records_from_compiled_jq(data, compiled_jq))
        assert output == [
            {"first": "value1", "second": "value2"},
            {"first": "value3", "second": "value4"},
        ]
