import pytest

from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    FieldSpec, JSONDataSourceConfig
)
from tel2puml.find_unique_graphs.otel_ingestion.json_jq_converter import (
    JQVariableTree,
)


@pytest.fixture
def field_spec_1() -> FieldSpec:
    return FieldSpec(
        key_paths=[
            "first.[].second_1.second_2.[].third_1.third_2",
            "first.[].second_1.second_2.[].third_1.third_2",
        ],
        key_value=["value", None],
        value_paths=["value_path.next", None],
    )


@pytest.fixture
def field_spec_2() -> FieldSpec:
    return FieldSpec(
        key_paths=["first.second.third", "first.second.third"],
        key_value=[None, None],
    )


@pytest.fixture
def field_spec_3() -> FieldSpec:
    return FieldSpec(
        key_paths=[
            "fourth.[].fifth",
            "fourth.[].fifth",
        ],
        key_value=[None, None],
    )


@pytest.fixture
def field_mapping(
    field_spec_1: FieldSpec, field_spec_2: FieldSpec, field_spec_3: FieldSpec
) -> dict[str, FieldSpec]:
    return {
        "field_1": field_spec_1,
        "field_2": field_spec_2,
        "field_3": field_spec_3,
    }


@pytest.fixture
def field_spec_with_variables_1() -> FieldSpec:
    return FieldSpec(
            key_paths=["$var2.third_1.third_2", "$var2.third_1.third_2"],
            key_value=["value", None],
            value_paths=["value_path.next", None],
        )


@pytest.fixture
def field_spec_with_variables_2() -> FieldSpec:
    return FieldSpec(
        key_paths=["$var0.first.second.third", "$var0.first.second.third"],
        key_value=[None, None],
    )


@pytest.fixture
def field_spec_with_variables_3() -> FieldSpec:
    return FieldSpec(
        key_paths=[
            "$var3.fifth",
            "$var3.fifth",
        ],
        key_value=[None, None],
    )


@pytest.fixture
def field_mapping_with_variables(
    field_spec_with_variables_1: FieldSpec,
    field_spec_with_variables_2: FieldSpec,
    field_spec_with_variables_3: FieldSpec,
) -> dict[str, FieldSpec]:
    return {
        "field_1": field_spec_with_variables_1,
        "field_2": field_spec_with_variables_2,
        "field_3": field_spec_with_variables_3,
    }


@pytest.fixture
def field_spec_with_variables_1_expected_jq() -> str:
    return (
        " | ($var2 | select(.third_1.third_2 == value)).value_path.next as"
        " $out0concat0"
        " | $var2.third_1.third_2 as $out0concat1"
        ' | ($out0concat0 | tostring) + "_" + ($out0concat1 | tostring) as'
        " $out0"
    )


@pytest.fixture
def field_spec_with_variables_2_expected_jq() -> str:
    return (
        " | $var0.first.second.third as $out1concat0"
        " | $var0.first.second.third as $out1concat1"
        ' | ($out1concat0 | tostring) + "_" + ($out1concat1 | tostring) as'
        " $out1"
    )


@pytest.fixture
def field_spec_with_variables_3_expected_jq() -> str:
    return (
        " | $var3.fifth as $out2concat0"
        " | $var3.fifth as $out2concat1"
        ' | ($out2concat0 | tostring) + "_" + ($out2concat1 | tostring) as'
        " $out2"
    )


@pytest.fixture
def var_tree() -> JQVariableTree:
    root_var_tree = JQVariableTree()
    var_num = 0
    first_child = root_var_tree.get_variable("first", var_num)
    var_num = first_child.var_num
    first_grand_child = first_child.get_variable("second_1.second_2", var_num)
    var_num = first_grand_child.var_num
    second_child = root_var_tree.get_variable("fourth", var_num)
    var_num = second_child.var_num
    return root_var_tree


@pytest.fixture
def expected_field_mapping_query(
    field_spec_with_variables_1_expected_jq: str,
    field_spec_with_variables_2_expected_jq: str,
    field_spec_with_variables_3_expected_jq: str
) -> str:
    return (
        f"{field_spec_with_variables_1_expected_jq}"
        f"{field_spec_with_variables_2_expected_jq}"
        f"{field_spec_with_variables_3_expected_jq}" +
        ' | {'
        ' "field_1": $out0,'
        ' "field_2": $out1,'
        ' "field_3": $out2'
        "}"
    )


@pytest.fixture
def expected_full_query(
    expected_field_mapping_query: str,
) -> str:
    return (
        "[" +
        ". as $var0 | $var0.first.[] as $var1 | $var1.second_1.second_2.[] as"
        " $var2 "
        "| $var0.fourth.[] as $var3" +
        f"{expected_field_mapping_query}" +
        "]"
    )


@pytest.fixture
def config_with_jq_type_field_mapping(
    field_mapping: dict[str, FieldSpec]
) -> JSONDataSourceConfig:
    return JSONDataSourceConfig(
        filepath="file_path",
        dirpath="dir_path",
        data_location="data_location",
        header={},
        span_mapping={},
        field_mapping=field_mapping,
    )
