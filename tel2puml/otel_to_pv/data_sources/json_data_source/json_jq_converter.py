"""Module to transform input JSON to a format that can be ingested into a
DataHolder."""

from typing import Any, Generator

import jq  # type: ignore[import-not-found]

from tel2puml.otel_to_pv.config import (
    JQFieldSpec,
    field_spec_mapping_to_jq_field_spec_mapping,
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

    def has_child(self, key_path: str) -> bool:
        """Check if the key path is a child of the variable tree.

        :param key_path: The key path to check
        :type key_path: `str`
        :return: True if the key path is a child of the variable tree, False
        otherwise
        :rtype: `bool`
        """
        return key_path in self.child_var_dict

    def add_child(self, key_path: str, var_num: int) -> "JQVariableTree":
        """Add a child to the variable tree.

        :param key_path: The key path to add
        :type key_path: `str`
        :param var_num: The variable number to assign to the child
        :type var_num: `int`
        :return: The child variable tree
        :rtype: :class:`JQVariable
        """
        if key_path in self.child_var_dict:
            raise ValueError(
                f"Key path {key_path} already exists in the variable tree."
            )
        self.child_var_dict[key_path] = JQVariableTree(
            var_num, self.var_prefix
        )
        return self.child_var_dict[key_path]

    def get_child(self, key_path: str) -> "JQVariableTree":
        """Get the variable tree for the given key path. Raise a ValueError if
        the key path does not exist in the variable tree.

        :param key_path: The key path to get the variable tree for
        :type key_path: `str`
        :return: The variable tree for the given key path
        :rtype: :class:`JQVariableTree
        """
        if not self.has_child(key_path):
            raise KeyError(
                f"Key path {key_path} does not exist in the variable tree."
            )
        return self.child_var_dict[key_path]

    def __str__(self) -> str:
        """Return the string representation of the variable tree."""
        return f"${self.var_prefix}{self.var_num}"

    def __iter__(self) -> Generator[tuple[str, "JQVariableTree"], Any, None]:
        """Iterate over the variable tree.

        :return: A generator of key path and variable tree pairs
        :rtype: `Generator`[`tuple`[`str`, :class:`JQVariableTree`], `Any`,
        `None`]
        """
        yield from self.child_var_dict.items()


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
        if i == len(split_on_array) - 1:
            variable_build_array.append(path)
        else:
            if not working_var_tree.has_child(path):
                var_num += 1
                working_var_tree = working_var_tree.add_child(path, var_num)
            else:
                working_var_tree = working_var_tree.get_child(path)
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
    field_spec: JQFieldSpec, root_var_tree: JQVariableTree, var_num: int = 0
) -> int:
    """Update the field spec with variables.

    :param field_spec: The field spec to update
    :type field_spec: :class:`JQFieldSpec`
    :param root_var_tree: The root variable tree
    :type root_var_tree: :class:`JQVariableTree`
    :param var_num: The current variable number, defaults to 0
    :type var_num: `int`, optional
    :return: The updated variable number
    :rtype: `int`
    """
    updated_key_paths: list[tuple[str, ...]] = []
    for priority_key_paths, priority_key_values in zip(
        field_spec.key_paths,
        field_spec.key_values,
    ):
        updated_priority_key_paths: list[str] = []
        for key_path, key_value in zip(
            priority_key_paths, priority_key_values
        ):
            updated_key_path, var_num = (
                get_updated_path_from_key_path_key_value_and_root_var_tree(
                    key_path, key_value, root_var_tree, var_num
                )
            )
            updated_priority_key_paths.append(updated_key_path)
        updated_key_paths.append(tuple(updated_priority_key_paths))
    field_spec.key_paths = updated_key_paths
    return var_num


def update_field_specs_with_variables(
    field_mapping: dict[str, JQFieldSpec],
) -> JQVariableTree:
    """Update the field specs with variables.

    :param field_mapping: The field mapping to update
    :type field_mapping: `dict`[:class:`str`, :class:`JQFieldSpec`]
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
        jq_query = (
            f"(try {str(parent_var_tree)}.{insert}[] catch null) "
            f"as {str(var_tree)}"
        )
    for key_path, child_var_tree in var_tree:
        child_query = build_base_variable_jq_query(
            child_var_tree, var_tree, key_path
        )
        jq_query += f" | {child_query}"
    return jq_query


def get_jq_for_field_spec(
    field_spec: JQFieldSpec,
    out_var: str,
) -> str:
    """Get the jq query for the field spec.

    :param field_spec: The field spec
    :type field_spec: :class:`JQFieldSpec`
    :param out_var: The output variable
    :type out_var: `str`
    :return: The jq query
    :rtype: `str`
    """
    jq_query = ""
    variables: list[list[str]] = []
    for (
        i,
        priority_key_paths,
        priority_key_values,
        priority_value_paths,
    ) in zip(
        range(len(field_spec.key_paths)),
        field_spec.key_paths,
        field_spec.key_values,
        field_spec.value_paths,
    ):
        priority_variables: list[str] = []
        for j, key_path, key_value, value_path in zip(
            range(len(priority_key_paths)),
            priority_key_paths,
            priority_key_values,
            priority_value_paths,
        ):
            variable = f"{out_var}concat{i}{j}"
            priority_variables.append(variable)
            if key_value is not None:
                split_on_array = key_path.split(".[].")
                if len(split_on_array) != 2:
                    raise ValueError(
                        "Expecting a single array in the key_path if key_value"
                        " is"
                        " not None."
                    )
                if "$" not in split_on_array[0]:
                    raise ValueError(
                        "Expecting a variable in the first part of the "
                        "key_path."
                    )
                if any("$" in part for part in split_on_array[1:]):
                    raise ValueError(
                        "Expecting no variables in the rest of the key_path "
                        "after "
                        "the first variable "
                    )
                jq_query += (
                    f" | ({split_on_array[0]}.[]"
                    + f" | select((try .{'.'.join(split_on_array[1:])} catch "
                    "null) "
                    + f'== "{key_value}")).{value_path} as {variable}'
                )
            else:
                jq_query += f" | (try {key_path} catch null) as {variable}"
        variables.append(priority_variables)
    if field_spec.value_type == "string":
        joined_variables = ' + "_" + '.join(
            "("
            + " // ".join(f"{variable}" for variable in priority_variables)
            + " | (if . == null then null else (. | tostring) end))"
            for priority_variables in variables
        )
    elif field_spec.value_type == "array":
        joined_variables = (
            "("
            + " + ".join(
                f"[{'//'.join(priority_variables)}]"
                for priority_variables in variables
            )
            + ") | flatten | (if (. | all(. == null)) and . != [] then null "
            "else . end)"
        )
    else:
        raise ValueError(f"Invalid value_type: {field_spec.value_type}")
    jq_query += f" | ({joined_variables}) as {out_var}"
    return jq_query


def get_jq_using_field_mapping(field_mapping: dict[str, JQFieldSpec]) -> str:
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
    field_mapping: dict[str, JQFieldSpec],
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
    return f"{jq_query}"


def jq_field_mapping_to_jq_query(field_mapping: dict[str, JQFieldSpec]) -> str:
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


def jq_field_mapping_to_compiled_jq(
    field_mapping: dict[str, JQFieldSpec],
) -> Any:
    """Convert the field mapping to a compiled jq query.

    :param field_mapping: The field mapping
    :type field_mapping: `dict`[:class:`str`, :class:`FieldSpec`]
    :return: The compiled jq query
    :rtype: `Any`
    """
    jq_query = jq_field_mapping_to_jq_query(field_mapping)
    return jq.compile(jq_query)


def field_mapping_to_compiled_jq(field_mapping: dict[str, FieldSpec]) -> Any:
    """Convert the field mapping to a compiled jq query.

    :param field_mapping: The field mapping
    :type field_mapping: `dict`[:class:`str`, :class:`FieldSpec`]
    :return: The compiled jq query
    :rtype: `Any`
    """
    jq_field_mapping = field_spec_mapping_to_jq_field_spec_mapping(
        field_mapping
    )
    return jq_field_mapping_to_compiled_jq(jq_field_mapping)


def generate_records_from_compiled_jq(
    input_data: Any, compiled_jq: Any
) -> Generator[Any, None, None]:
    """Generate records from compiled jq.

    :param input: The input data
    :type input: `Any`
    :param compiled_jq: The compiled jq query
    :type compiled_jq: `Any`
    :return: A generator of records
    :rtype: `Generator`[`Any`, `None`, `None`]
    """
    records = iter(compiled_jq.input_value(input_data))
    for record in records:
        if isinstance(record, list):
            yield from record
        else:
            yield record
