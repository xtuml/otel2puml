"""Configuration for tests in json data source."""
import pytest

from tel2puml.otel_to_pv.config import FieldSpec
from tel2puml.otel_to_pv.data_sources.json_data_source.json_jq_converter \
    import JQVariableTree


@pytest.fixture
def field_spec_1() -> FieldSpec:
    """Fixture for FieldSpec object."""
    return FieldSpec(
        key_paths=[
            "first.[].second_1.second_2.[].third_1.third_2",
            "first.[].second_1.second_2.[].third_1.third_2",
        ],
        key_value=["value", None],
        value_paths=["value_path.next", None],
        value_type="string",
    )


@pytest.fixture
def field_spec_2() -> FieldSpec:
    """Fixture for FieldSpec object."""
    return FieldSpec(
        key_paths=["first.second.third", "first.second.third"],
        key_value=[None, None],
        value_paths=[None, None],
        value_type="string",
    )


@pytest.fixture
def field_spec_3() -> FieldSpec:
    """Fixture for FieldSpec object."""
    return FieldSpec(
        key_paths=[
            "fourth.[].fifth",
            "fourth.[].fifth",
        ],
        key_value=[None, None],
        value_paths=[None, None],
        value_type="string",
    )


@pytest.fixture
def field_mapping(
    field_spec_1: FieldSpec, field_spec_2: FieldSpec, field_spec_3: FieldSpec
) -> dict[str, FieldSpec]:
    """Fixture for field mapping using previous fiedl specs"""
    return {
        "field_1": field_spec_1,
        "field_2": field_spec_2,
        "field_3": field_spec_3,
    }


@pytest.fixture
def field_spec_with_variables_1() -> FieldSpec:
    """Fixture for 1st FieldSpec object with variables added"""
    return FieldSpec(
        key_paths=[
            "$var1.second_1.second_2.[].third_1.third_2",
            "$var2.third_1.third_2",
        ],
        key_value=["value", None],
        value_paths=["value_path.next", None],
        value_type="string",
    )


@pytest.fixture
def field_spec_with_variables_2() -> FieldSpec:
    """Fixture for 2nd FieldSpec object with variables added"""
    return FieldSpec(
        key_paths=["$var0.first.second.third", "$var0.first.second.third"],
        key_value=[None, None],
        value_paths=[None, None],
        value_type="string",
    )


@pytest.fixture
def field_spec_with_variables_3() -> FieldSpec:
    """Fixture for 3rd FieldSpec object with variables added"""
    return FieldSpec(
        key_paths=[
            "$var3.fifth",
            "$var3.fifth",
        ],
        key_value=[None, None],
        value_paths=[None, None],
        value_type="string",
    )


@pytest.fixture
def field_mapping_with_variables(
    field_spec_with_variables_1: FieldSpec,
    field_spec_with_variables_2: FieldSpec,
    field_spec_with_variables_3: FieldSpec,
) -> dict[str, FieldSpec]:
    """Fixture for field mapping using previous field specs with variables
    added"""
    return {
        "field_1": field_spec_with_variables_1,
        "field_2": field_spec_with_variables_2,
        "field_3": field_spec_with_variables_3,
    }


@pytest.fixture
def field_spec_with_variables_1_expected_jq() -> str:
    """Expected JQ query for field_spec_with_variables_1"""
    return (
        ' | ($var1.second_1.second_2.[] | select(.third_1.third_2 == "value"))'
        '.value_path.next as'
        " $out0concat0"
        " | $var2.third_1.third_2 as $out0concat1"
        ' | (($out0concat0 | tostring) + "_" + ($out0concat1 | tostring)) as'
        " $out0"
    )


@pytest.fixture
def field_spec_with_variables_2_expected_jq() -> str:
    """Expected JQ query for field_spec_with_variables_2"""
    return (
        " | $var0.first.second.third as $out1concat0"
        " | $var0.first.second.third as $out1concat1"
        ' | (($out1concat0 | tostring) + "_" + ($out1concat1 | tostring)) as'
        " $out1"
    )


@pytest.fixture
def field_spec_with_variables_3_expected_jq() -> str:
    """Expected JQ query for field_spec_with_variables_3"""
    return (
        " | $var3.fifth as $out2concat0"
        " | $var3.fifth as $out2concat1"
        ' | (($out2concat0 | tostring) + "_" + ($out2concat1 | tostring)) as'
        " $out2"
    )


@pytest.fixture
def var_tree() -> JQVariableTree:
    """Fixture for JQVariableTree object"""
    root_var_tree = JQVariableTree()
    first_child = root_var_tree.add_child("first", 1)
    first_child.add_child("second_1.second_2", 2)
    root_var_tree.add_child("fourth", 3)
    return root_var_tree


@pytest.fixture
def expected_field_mapping_query(
    field_spec_with_variables_1_expected_jq: str,
    field_spec_with_variables_2_expected_jq: str,
    field_spec_with_variables_3_expected_jq: str,
) -> str:
    """Expected JQ query for field mapping"""
    return (
        f"{field_spec_with_variables_1_expected_jq}"
        f"{field_spec_with_variables_2_expected_jq}"
        f"{field_spec_with_variables_3_expected_jq}" + " | {"
        ' "field_1": $out0,'
        ' "field_2": $out1,'
        ' "field_3": $out2'
        "}"
    )


@pytest.fixture
def expected_full_query(
    expected_field_mapping_query: str,
) -> str:
    """Expected full JQ query"""
    return (
        "["
        + ". as $var0 | $var0.first.[] as $var1 | $var1.second_1.second_2.[] "
        "as"
        " $var2 "
        "| $var0.fourth.[] as $var3" + f"{expected_field_mapping_query}" + "]"
    )


@pytest.fixture
def field_mapping_for_fixture_data() -> dict[str, FieldSpec]:
    """Fixture for field mapping using previous field specs with variables
    added"""
    return {
        "field_1": FieldSpec(
            key_paths=[
                "resource_spans.[].resource.attributes.[].key",
                "resource_spans.[].scope_spans.[].scope.name",
            ],
            key_value=["service.name", None],
            value_paths=["value.Value.StringValue", None],
            value_type="string",
        ),
        "field_2": FieldSpec(
            key_paths=[
                "resource_spans.[].scope_spans.[].spans.[].attributes.[].key",
                "resource_spans.[].scope_spans.[].spans.[].attributes.[].key",
            ],
            key_value=["coral.operation", "http.status_code"],
            value_paths=["value.Value.StringValue", "value.Value.IntValue"],
            value_type="string",
        ),
        "field_3": FieldSpec(
            key_paths=[
                "resource_spans.[].scope_spans.[].spans.[]."
                "start_time_unix_nano",
            ],
            key_value=None,
            value_paths=None,
            value_type="string",
        ),
    }


@pytest.fixture
def expected_mapped_json() -> list[dict[str, str]]:
    """Expected mapped JSON data"""
    return [
        {
            "field_1": "Frontend_TestJob",
            "field_2": "jCWhAvRzcM_500",
            "field_3": "1723544132228102912",
        },
        {
            "field_1": "Frontend_TestJob",
            "field_2": "cVh8nOperation_401",
            "field_3": "1723544132228288000",
        },
        {
            "field_1": "Backend_TestJob",
            "field_2": "2lAmnOperation_201",
            "field_3": "1723544154817766912",
        },
        {
            "field_1": "Backend_TestJob",
            "field_2": "81DznOperation_201",
            "field_3": "1723544154817793024",
        },
    ]
