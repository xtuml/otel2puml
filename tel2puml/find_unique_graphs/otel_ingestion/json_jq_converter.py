from typing import Any

import jq

from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    FieldSpec,
)


class JQVariableTree:
    def __init__(self, var_num: int = 0, var_prefix: str = "var") -> None:
        self.var_num: int = var_num
        self.child_var_dict: dict[str, JQVariableTree] = {}
        self.var_prefix: str = var_prefix

    def get_variable(
        self, key_path: str, var_num: int
    ) -> tuple["JQVariableTree", int]:
        if key_path not in self.child_var_dict:
            var_num += 1
            self.child_var_dict[key_path] = JQVariableTree(
                var_num, self.var_prefix
            )
        return self.child_var_dict[key_path], var_num

    def __str__(self) -> str:
        return f"${self.var_prefix}{self.var_num}"

    def __repr__(self) -> str:
        return f"JQVariableTree({self.var_num}, {self.var_prefix})"


def get_updated_path_from_key_path_key_value_and_root_var_tree(
    key_path: str,
    key_value: str | None,
    root_var_tree: JQVariableTree,
    var_num: int,
) -> tuple[str, int]:
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
    updated_key_paths: list[str] = []
    for key_path, key_value in zip(
        field_spec["key_paths"],
        (
            field_spec["key_value"]
            if "key_value" in field_spec
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
    jq_query = ""
    variables: list[str] = []
    for i, key_path, key_value, value_path in zip(
        range(len(field_spec["key_paths"])),
        field_spec["key_paths"],
        (
            field_spec["key_value"]
            if "key_value" in field_spec
            else [None] * len(field_spec["key_paths"])
        ),
        (
            field_spec["value_paths"]
            if "value_paths" in field_spec
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
    jq_query = build_base_variable_jq_query(var_tree)
    jq_query += get_jq_using_field_mapping(field_mapping)
    return f"[{jq_query}]"


def field_mapping_to_jq_query(field_mapping: dict[str, FieldSpec]) -> str:
    var_tree = update_field_specs_with_variables(field_mapping)
    return get_jq_query_from_field_mapping_with_variables_and_var_tree(
        field_mapping, var_tree
    )


def field_mapping_to_compiled_jq(field_mapping: dict[str, FieldSpec]) -> Any:
    jq_query = field_mapping_to_jq_query(field_mapping)
    return jq.compile(jq_query)
