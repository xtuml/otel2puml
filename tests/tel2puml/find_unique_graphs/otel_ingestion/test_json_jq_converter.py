"""Tests for the json_jq_converter module."""
from typing import Any
import pytest

from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    FieldSpec,
)
from tel2puml.find_unique_graphs.otel_ingestion.json_jq_converter import (
    JQVariableTree,
    get_updated_path_from_key_path_key_value_and_root_var_tree,
    update_field_spec_with_variables,
    update_field_specs_with_variables,
    build_base_variable_jq_query,
    get_jq_for_field_spec,
    get_jq_using_field_mapping,
    get_jq_query_from_field_mapping_with_variables_and_var_tree,
    field_mapping_to_jq_query,
    field_mapping_to_compiled_jq,
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
    def test_get_variable() -> None:
        """Test the get_variable method of the JQVariableTree class."""
        var_tree = JQVariableTree(var_num=0, var_prefix="test")
        # test case with no children
        first_child, var_num = var_tree.get_variable("first", 0)
        assert first_child.var_num == 1
        assert first_child.var_prefix == "test"
        assert var_num == 1
        assert len(var_tree.child_var_dict) == 1
        assert "first" in var_tree.child_var_dict
        assert first_child.child_var_dict == {}
        # test case when key path already exists
        first_child_again, var_num = var_tree.get_variable("first", 2)
        assert first_child_again == first_child
        assert var_num == 2
        assert first_child.child_var_dict == {}
        # test case with another child
        second_child, var_num = var_tree.get_variable("second", 3)
        assert second_child.var_num == 4
        assert second_child.var_prefix == "test"
        assert var_num == 4
        assert len(var_tree.child_var_dict) == 2
        assert (
            "second" in var_tree.child_var_dict
            and "first" in var_tree.child_var_dict
        )
        assert second_child.child_var_dict == {}

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
        first_child: JQVariableTree, second_child=False
    ) -> None:
        """Check the first child of the root variable tree and its children."""
        assert first_child.var_num == 1
        if second_child:
            assert len(first_child.child_var_dict) == 1
            assert "second_1.second_2" in first_child.child_var_dict
            second_child = first_child.child_var_dict["second_1.second_2"]
            assert second_child.var_num == 2
            assert len(second_child.child_var_dict) == 0
        else:
            assert len(first_child.child_var_dict) == 0

    def check_root_var_tree(
        self,
        root_var_tree: JQVariableTree,
        second_child=False,
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
        self, field_spec_1: FieldSpec, field_spec_2: FieldSpec
    ) -> None:
        """Test the update_field_spec_with_variables function."""
        field_spec = field_spec_1
        root_var_tree = JQVariableTree()
        var_num = update_field_spec_with_variables(field_spec, root_var_tree)
        assert var_num == 2
        assert field_spec["key_paths"] == [
            "$var1.second_1.second_2.[].third_1.third_2",
            "$var2.third_1.third_2",
        ]
        self.check_root_var_tree(root_var_tree, second_child=True)
        field_spec = field_spec_2
        root_var_tree = JQVariableTree()
        var_num = update_field_spec_with_variables(field_spec, root_var_tree)
        assert var_num == 0
        assert field_spec["key_paths"] == [
            "$var0.first.second.third",
            "$var0.first.second.third",
        ]
        self.check_root_var_tree_for_no_arrays(root_var_tree)

    def test_update_field_specs_with_variables(
        self,
        field_mapping: dict[str, FieldSpec],
        field_mapping_with_variables: dict[str, FieldSpec],
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
        var_num = 0
        first_child, var_num = root_var_tree.get_variable("first", var_num)
        assert build_base_variable_jq_query(root_var_tree) == (
            ". as $var0 | $var0.first.[] as $var1"
        )
        # test case with grandchild
        grand_child, var_num = first_child.get_variable("grand_child", var_num)
        assert build_base_variable_jq_query(root_var_tree) == (
            ". as $var0 | $var0.first.[] as $var1 | $var1.grand_child.[] as"
            " $var2"
        )
        # test case with great grandchild
        _, var_num = grand_child.get_variable("great_grand_child", var_num)
        assert build_base_variable_jq_query(root_var_tree) == (
            ". as $var0 | $var0.first.[] as $var1 | $var1.grand_child.[] as"
            " $var2 "
            "| $var2.great_grand_child.[] as $var3"
        )
        # test case with a sibling of the first child
        _, var_num = root_var_tree.get_variable("second", var_num)
        assert build_base_variable_jq_query(root_var_tree) == (
            ". as $var0 | $var0.first.[] as $var1 | $var1.grand_child.[] as"
            " $var2 "
            "| $var2.great_grand_child.[] as $var3"
            " | $var0.second.[] as $var4"
        )
        # test case with a sibling of the first child grandchild
        _, var_num = first_child.get_variable("grand_child_2", var_num)
        assert build_base_variable_jq_query(root_var_tree) == (
            ". as $var0 | $var0.first.[] as $var1 | $var1.grand_child.[] as"
            " $var2 "
            "| $var2.great_grand_child.[] as $var3"
            " | $var1.grand_child_2.[] as $var5"
            " | $var0.second.[] as $var4"
        )

    @staticmethod
    def test_get_jq_for_field_spec(
        field_spec_with_variables_1: FieldSpec,
        field_spec_with_variables_2: FieldSpec,
        field_spec_with_variables_1_expected_jq: str,
        field_spec_with_variables_2_expected_jq: str,
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
        field_spec = FieldSpec(
            key_paths=["first.[].second.third", "first.second.third"],
            key_value=["value", None],
            value_paths=["value_path.next", None],
        )
        with pytest.raises(ValueError):
            get_jq_for_field_spec(field_spec, "$out0")
        # check case with variable in the first part of the key path and
        # variable in the rest of the key path
        field_spec = FieldSpec(
            key_paths=[
                "$var0.[].$var1.second.third",
                "$var0.first.second.third",
            ],
            key_value=["value", None],
            value_paths=["value_path.next", None],
        )
        with pytest.raises(ValueError):
            get_jq_for_field_spec(field_spec, "$out0")
        # check case with no arrays in the key path
        field_spec = FieldSpec(
            key_paths=["first.second.third", "first.second.third"],
            key_value=["value", None],
            value_paths=["value_path.next", None],
        )
        with pytest.raises(ValueError):
            get_jq_for_field_spec(field_spec, "$out0")
        # check case with more than one array in the key path
        field_spec = FieldSpec(
            key_paths=["first.[].second.[].third", "first.[].second.third"],
            key_value=["value", None],
            value_paths=["value_path.next", None],
        )
        with pytest.raises(ValueError):
            get_jq_for_field_spec(field_spec, "$out0")

    @staticmethod
    def test_get_jq_using_field_mapping(
        field_mapping_with_variables: dict[str, FieldSpec],
        expected_field_mapping_query: str,
    ) -> None:
        """Test the get_jq_using_field_mapping function."""
        field_mapping = field_mapping_with_variables
        assert get_jq_using_field_mapping(field_mapping) == (
            expected_field_mapping_query
        )

    @staticmethod
    def test_get_jq_query_from_field_mapping_with_variables_and_var_tree(
        field_mapping_with_variables: dict[str, FieldSpec],
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
    def test_field_mapping_to_jq_query(
        field_mapping: dict[str, FieldSpec],
        expected_full_query: str,
    ) -> None:
        """Test the field_mapping_to_jq_query function."""
        jq_query = field_mapping_to_jq_query(field_mapping)
        assert jq_query == (expected_full_query)

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
        output = compiled_jq.input_value(mock_json_data).first()
        assert output == expected_mapped_json
