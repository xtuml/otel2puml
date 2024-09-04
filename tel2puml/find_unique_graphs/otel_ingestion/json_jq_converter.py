"""Module to transform input JSON to a format that can be used to find unique
graphs."""
from typing import Any

import jq  # type: ignore[import-not-found]

from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    FieldSpec,
)


class JQVariableTree:
    """Class to represent a tree of variables for use in jq queries.

    :param var_num: The number of the variable, defaults to 0
    :type var_num: `int`, optional
    :param var_prefix: The prefix for the variable, defaults to "var"
    :type var_prefix: `str`, optional
    """
    def __init__(self, var_num: int = 0, var_prefix: str = "var") -> None:
        """Constructor method."""
        self.var_num: int = var_num
        self.child_var_dict: dict[str, JQVariableTree] = {}
        self.var_prefix: str = var_prefix

    def get_variable(
        self, key_path: str, var_num: int
    ) -> tuple["JQVariableTree", int]:
        """Get the variable tree for the given key path.

        :param key_path: The key path to get the variable tree for
        :type key_path: `str`
        :param var_num: The current variable number
        :type var_num: `int`
        :return: The variable tree for the given key path and the updated
        variable number
        :rtype: `tuple`[:class:`JQVariableTree`, `int`]
        """
        if key_path not in self.child_var_dict:
            var_num += 1
            self.child_var_dict[key_path] = JQVariableTree(
                var_num, self.var_prefix
            )
        return self.child_var_dict[key_path], var_num

    def __str__(self) -> str:
        """Return the string representation of the variable tree."""
        return f"${self.var_prefix}{self.var_num}"


def get_updated_path_from_key_path_key_value_and_root_var_tree(
    key_path: str,
    key_value: str | None,
    root_var_tree: JQVariableTree,
    var_num: int,
) -> tuple[str, int]:
    """Get the updated path from the key path, key value, and root variable
    tree.

    :param key_path: The key path
    :type key_path: `str`
    :param key_value: The key value
    :type key_value: `str` | `None`
    :param root_var_tree: The root variable tree
    :type root_var_tree: :class:`JQVariableTree`
    :param var_num: The current variable number
    :type var_num: `int`
    :return: The updated path and the updated variable number
    :rtype: `tuple`[:class:`str`, `int`]
    """

    split_on_array = key_path.split(".[].")
    if len(split_on_array) == 1 and key_value is not None:
        raise ValueError(
            "key_value must be None if there are no arrays in key_path."
        )
    if len(split_on_array) > 1 and key_value is not None:
        split_on_array = split_on_array[:-2] + [
            ".[].".join(split_on_array[-2:])
        ]
    variable_build_array: list[JQVariableTree | str] = [root_var_tree]
    working_var_tree = root_var_tree
    for i, path in enumerate(split_on_array):
        if i == len(split_on_array) - 1:  # and key_value is not None:
            variable_build_array.append(path)
        else:
            working_var_tree, var_num = working_var_tree.get_variable(
                path, var_num
            )
            variable_build_array[0] = working_var_tree
    return (
        ".".join(
            (
                str(variable)
                if isinstance(variable, JQVariableTree)
                else variable
            )
            for variable in variable_build_array
        )
    ), var_num


def update_field_spec_with_variables(
    field_spec: FieldSpec, root_var_tree: JQVariableTree, var_num: int = 0
) -> int:
    """Update the field spec with variables.

    :param field_spec: The field spec to update
    :type field_spec: :class:`FieldSpec`
    :param root_var_tree: The root variable tree
    :type root_var_tree: :class:`JQVariableTree`
    :param var_num: The current variable number, defaults to 0
    :type var_num: `int`, optional
    :return: The updated variable number
    :rtype: `int`
    """
    updated_key_paths: list[str] = []
    for key_path, key_value in zip(
        field_spec["key_paths"],
        (
            field_spec["key_value"]
            if field_spec["key_value"] is not None
            else [None] * len(field_spec["key_paths"])
        ),
    ):
        updated_key_path, var_num = (
            get_updated_path_from_key_path_key_value_and_root_var_tree(
                key_path, key_value, root_var_tree, var_num
            )
        )
        updated_key_paths.append(updated_key_path)
    field_spec["key_paths"] = updated_key_paths
    return var_num


def update_field_specs_with_variables(
    field_mapping: dict[str, FieldSpec],
) -> JQVariableTree:
    """Update the field specs with variables.

    :param field_mapping: The field mapping to update
    :type field_mapping: `dict`[:class:`str`, :class:`FieldSpec`]
    :return: The root variable tree
    :rtype: :class:`JQVariableTree`
    """
    root_var_tree = JQVariableTree()
    var_num = 0
    for field_spec in field_mapping.values():
        var_num = update_field_spec_with_variables(
            field_spec, root_var_tree, var_num
        )
    return root_var_tree


def build_base_variable_jq_query(
    var_tree: JQVariableTree,
    parent_var_tree: JQVariableTree | None = None,
    path: str = "",
) -> str:
    """Build the base variable jq query.

    :param var_tree: The variable tree
    :type var_tree: :class:`JQVariable`
    :param parent_var_tree: The parent variable tree, defaults to None
    :type parent_var_tree: :class:`JQVariableTree` | None, optional
    :param path: The path, defaults to ""
    :type path: `str`, optional
    :return: The base variable jq query
    :rtype: `str`
    """
    if parent_var_tree is None:
        jq_query = ". as " + str(var_tree)
    else:
        insert = path if path == "" else path + "."
        jq_query = f"{str(parent_var_tree)}.{insert}[] as {str(var_tree)}"
    for key_path, child_var_tree in var_tree.child_var_dict.items():
        child_query = build_base_variable_jq_query(
            child_var_tree, var_tree, key_path
        )
        jq_query += f" | {child_query}"
    return jq_query


def get_jq_for_field_spec(field_spec: FieldSpec, out_var: str) -> str:
    """Get the jq query for the field spec.

    :param field_spec: The field spec
    :type field_spec: :class:`FieldSpec`
    :param out_var: The output variable
    :type out_var: `str`
    :return: The jq query
    :rtype: `str`
    """
    jq_query = ""
    variables: list[str] = []
    for i, key_path, key_value, value_path in zip(
        range(len(field_spec["key_paths"])),
        field_spec["key_paths"],
        (
            field_spec["key_value"]
            if field_spec["key_value"] is not None
            else [None] * len(field_spec["key_paths"])
        ),
        (
            field_spec["value_paths"]
            if field_spec["value_paths"] is not None
            else [None] * len(field_spec["key_paths"])
        ),
    ):
        variable = f"{out_var}concat{i}"
        variables.append(variable)
        if key_value is not None:
            split_on_array = key_path.split(".[].")
            if len(split_on_array) != 2:
                raise ValueError(
                    "Expecting a single array in the key_path if key_value is"
                    " not None."
                )
            if "$" not in split_on_array[0]:
                raise ValueError(
                    "Expecting a variable in the first part of the key_path."
                )
            if any("$" in part for part in split_on_array[1:]):
                raise ValueError(
                    "Expecting no variables in the rest of the key_path after "
                    "the first variable "
                )
            jq_query += (
                f" | ({split_on_array[0]}.[]"
                + f" | select(.{'.'.join(split_on_array[1:])} "
                + f'== "{key_value}")).{value_path} as {variable}'
            )
        else:
            jq_query += f" | {key_path} as {variable}"
    joined_variables = ' + "_" + '.join(
        f"({variable} | tostring)" for variable in variables
    )
    jq_query += f" | ({joined_variables}) as {out_var}"
    return jq_query


def get_jq_using_field_mapping(field_mapping: dict[str, FieldSpec]) -> str:
    """Get the jq query using the field mapping.

    :param field_mapping: The field mapping
    :type field_mapping: `dict`[:class:`str`, :class:`FieldSpec`]
    :return: The jq query
    :rtype: `str`
    """
    jq_query = ""
    var_num = 0
    map_to_var: dict[str, str] = {}
    for field, field_spec in field_mapping.items():
        out_var = f"$out{var_num}"
        var_num += 1
        map_to_var[field] = out_var
        jq_query += get_jq_for_field_spec(field_spec, out_var)
    jq_query += (
        " | {"
        + ",".join(
            f' "{field}": {out_var}' for field, out_var in map_to_var.items()
        )
        + "}"
    )
    return jq_query


def get_jq_query_from_field_mapping_with_variables_and_var_tree(
    field_mapping: dict[str, FieldSpec],
    var_tree: JQVariableTree,
) -> str:
    """Get the jq query from the field mapping with variables and variable
    tree.

    :param field_mapping: The field mapping
    :type field_mapping: `dict`[:class:`str`, :class:`FieldSpec`]
    :param var_tree: The variable tree
    :type var_tree: :class:`JQVariable`
    :return: The jq query
    :rtype: `str`
    """
    jq_query = build_base_variable_jq_query(var_tree)
    jq_query += get_jq_using_field_mapping(field_mapping)
    return f"[{jq_query}]"


def field_mapping_to_jq_query(field_mapping: dict[str, FieldSpec]) -> str:
    """Convert the field mapping to a jq query.

    :param field_mapping: The field mapping
    :type field_mapping: `dict`[:class:`str`, :class:`FieldSpec`]
    :return: The jq query
    :rtype: `str`
    """
    var_tree = update_field_specs_with_variables(field_mapping)
    return get_jq_query_from_field_mapping_with_variables_and_var_tree(
        field_mapping, var_tree
    )


def field_mapping_to_compiled_jq(field_mapping: dict[str, FieldSpec]) -> Any:
    """Convert the field mapping to a compiled jq query.

    :param field_mapping: The field mapping
    :type field_mapping: `dict`[:class:`str`, :class:`FieldSpec`]
    :return: The compiled jq query
    :rtype: `Any`
    """
    jq_query = field_mapping_to_jq_query(field_mapping)
    return jq.compile(jq_query)
