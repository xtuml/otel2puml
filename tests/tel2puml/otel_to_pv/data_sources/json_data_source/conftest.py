"""Configuration for tests in json data source."""

import pytest

from tel2puml.otel_to_pv.config import JQFieldSpec, FieldSpec
from tel2puml.otel_to_pv.data_sources.json_data_source.json_jq_converter \
    import (
        JQVariableTree,
    )


@pytest.fixture
def field_spec_1() -> JQFieldSpec:
    """Fixture for JQFieldSpec object."""
    return JQFieldSpec(
        key_paths=[
            ("first.[].second_1.second_2.[].third_1.third_2",),
            ("first.[].second_1.second_2.[].third_1.third_2",),
        ],
        key_values=[("value",), (None,)],
        value_paths=[("value_path.next",), (None,)],
        value_type="string",
    )


@pytest.fixture
def field_spec_2() -> JQFieldSpec:
    """Fixture for JQFieldSpec object."""
    return JQFieldSpec(
        key_paths=[("first.second.third",), ("first.second.third",)],
        key_values=[(None,), (None,)],
        value_paths=[(None,), (None,)],
        value_type="string",
    )


@pytest.fixture
def field_spec_3() -> JQFieldSpec:
    """Fixture for JQFieldSpec object."""
    return JQFieldSpec(
        key_paths=[
            ("fourth.[].fifth",),
            ("fourth.[].fifth",),
        ],
        key_values=[(None,), (None,)],
        value_paths=[(None,), (None,)],
        value_type="string",
    )


@pytest.fixture
def field_spec_4() -> JQFieldSpec:
    """Fixture for JQFieldSpec object."""
    return JQFieldSpec(
        key_paths=[
            tuple(["first.[].second_1.second_2.[].third_1.third_2"] * 2)
        ],
        key_values=[("value", None)],
        value_paths=[("value_path.next", None)],
        value_type="string",
    )


@pytest.fixture
def field_mapping(
    field_spec_1: JQFieldSpec,
    field_spec_2: JQFieldSpec,
    field_spec_3: JQFieldSpec,
) -> dict[str, JQFieldSpec]:
    """Fixture for field mapping using previous fiedl specs"""
    return {
        "field_1": field_spec_1,
        "field_2": field_spec_2,
        "field_3": field_spec_3,
    }


@pytest.fixture
def field_spec_with_variables_1() -> JQFieldSpec:
    """Fixture for 1st JQFieldSpec object with variables added"""
    return JQFieldSpec(
        key_paths=[
            ("$var1.second_1.second_2.[].third_1.third_2",),
            ("$var2.third_1.third_2",),
        ],
        key_values=[("value",), (None,)],
        value_paths=[("value_path.next",), (None,)],
        value_type="string",
    )


@pytest.fixture
def field_spec_with_variables_2() -> JQFieldSpec:
    """Fixture for 2nd JQFieldSpec object with variables added"""
    return JQFieldSpec(
        key_paths=[
            ("$var0.first.second.third",),
            ("$var0.first.second.third",),
        ],
        key_values=[(None,), (None,)],
        value_paths=[(None,), (None,)],
        value_type="string",
    )


@pytest.fixture
def field_spec_with_variables_3() -> JQFieldSpec:
    """Fixture for 3rd JQFieldSpec object with variables added"""
    return JQFieldSpec(
        key_paths=[
            ("$var3.fifth",),
            ("$var3.fifth",),
        ],
        key_values=[(None,), (None,)],
        value_paths=[(None,), (None,)],
        value_type="string",
    )


@pytest.fixture
def field_spec_with_variables_4() -> JQFieldSpec:
    """Fixture for 4th JQFieldSpec object with variables added"""
    return JQFieldSpec(
        key_paths=[
            (
                "$var1.second_1.second_2.[].third_1.third_2",
                "$var2.third_1.third_2",
            ),
        ],
        key_values=[("value", None)],
        value_paths=[("value_path.next", None)],
        value_type="string",
    )


@pytest.fixture
def field_mapping_with_variables(
    field_spec_with_variables_1: JQFieldSpec,
    field_spec_with_variables_2: JQFieldSpec,
    field_spec_with_variables_3: JQFieldSpec,
) -> dict[str, JQFieldSpec]:
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
        ' | ($var1.second_1.second_2.[] | select((try .third_1.third_2 catch '
        'null) == "value"))'
        ".value_path.next as"
        " $out0concat00"
        " | (try $var2.third_1.third_2 catch null) as $out0concat10"
        ' | (($out0concat00 | (if . == null then null else (. | tostring) '
        'end)) + "_" + ($out0concat10 | (if . == null then null else (. | '
        'tostring) end)))'
        " as"
        " $out0"
    )


@pytest.fixture
def field_spec_with_variables_2_expected_jq() -> str:
    """Expected JQ query for field_spec_with_variables_2"""
    return (
        " | (try $var0.first.second.third catch null) as $out1concat00"
        " | (try $var0.first.second.third catch null) as $out1concat10"
        ' | (($out1concat00 | (if . == null then null else (. | tostring) '
        'end)) + "_" + ($out1concat10 | (if . == null then null else (. | '
        'tostring) end)))'
        " as"
        " $out1"
    )


@pytest.fixture
def field_spec_with_variables_3_expected_jq() -> str:
    """Expected JQ query for field_spec_with_variables_3"""
    return (
        " | (try $var3.fifth catch null) as $out2concat00"
        " | (try $var3.fifth catch null) as $out2concat10"
        ' | (($out2concat00 | (if . == null then null else (. | tostring) '
        'end)) + "_" + ($out2concat10 | (if . == null then null else (. | '
        'tostring) end)))'
        " as"
        " $out2"
    )


@pytest.fixture
def field_spec_with_variables_4_expected_jq() -> str:
    """Expected JQ query for field_spec_with_variables_4"""
    return (
        ' | ($var1.second_1.second_2.[] | select((try .third_1.third_2 catch '
        'null) == "value"))'
        ".value_path.next as"
        " $out3concat00"
        " | (try $var2.third_1.third_2 catch null) as $out3concat01"
        " | (($out3concat00 // $out3concat01 | (if . == null then null else "
        "(. | tostring) end)))"
        " as"
        " $out3"
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
        ". as $var0 | (try $var0.first.[] catch null) as $var1 "
        "| (try $var1.second_1.second_2.[] catch null) "
        "as"
        " $var2 "
        "| (try $var0.fourth.[] catch null) as $var3"
        + f"{expected_field_mapping_query}"
    )


@pytest.fixture
def jq_field_mapping_for_fixture_data() -> dict[str, JQFieldSpec]:
    """Fixture for field mapping using previous field specs with variables
    added"""
    return {
        "field_1": JQFieldSpec(
            key_paths=[
                ("resource_spans.[].resource.attributes.[].key",),
                ("resource_spans.[].scope_spans.[].scope.name",),
            ],
            key_values=[("service.name",), (None,)],
            value_paths=[("value.Value.StringValue",), (None,)],
            value_type="string",
        ),
        "field_2": JQFieldSpec(
            key_paths=[
                (
                    "resource_spans.[].scope_spans.[].spans.[].attributes.[]"
                    ".key",
                ),
                (
                    "resource_spans.[].scope_spans.[].spans.[].attributes.[]"
                    ".key",
                ),
            ],
            key_values=[("coral.operation",), ("http.status_code",)],
            value_paths=[
                ("value.Value.StringValue",),
                ("value.Value.IntValue",),
            ],
            value_type="string",
        ),
        "field_3": JQFieldSpec(
            key_paths=[
                (
                    "resource_spans.[].scope_spans.[].spans.[]."
                    "start_time_unix_nano",
                ),
            ],
            key_values=[(None,)],
            value_paths=[(None,)],
            value_type="string",
        ),
        "field_4": JQFieldSpec(
            key_paths=[
                (
                    "resource_spans.[].scope_spans.[].spans.[]."
                    "does_not_exist",
                    "resource_spans.[].does_not_exist.[].spans.[]."
                    "end_time_unix_nano",
                    "resource_spans.[].scope_spans.[].spans.[]."
                    "end_time_unix_nano",
                ),
            ],
            key_values=[(None, None, None)],
            value_paths=[(None, None, None)],
            value_type="string",
        ),
    }


@pytest.fixture
def field_mapping_for_fixture_data(
    jq_field_mapping_for_fixture_data: dict[str, JQFieldSpec],
) -> dict[str, JQFieldSpec]:
    """Fixture for field mapping using previous field specs with variables
    added"""
    return {
        f"field_{i}": FieldSpec(
            key_paths=jq_field_mapping_for_fixture_data[
                f"field_{i}"
            ].key_paths,
            key_value=jq_field_mapping_for_fixture_data[
                f"field_{i}"
            ].key_values,
            value_paths=jq_field_mapping_for_fixture_data[
                f"field_{i}"
            ].value_paths,
            value_type=jq_field_mapping_for_fixture_data[
                f"field_{i}"
            ].value_type,
        )
        for i in range(1, 5)
    }


@pytest.fixture
def expected_mapped_json() -> list[dict[str, str]]:
    """Expected mapped JSON data"""
    return [
        {
            "field_1": "Frontend_TestJob",
            "field_2": "jCWhAvRzcM_500",
            "field_3": "1723544132228102912",
            "field_4": "1723544132228219285",
        },
        {
            "field_1": "Frontend_TestJob",
            "field_2": "cVh8nOperation_401",
            "field_3": "1723544132228288000",
            "field_4": "1723544132229038947",
        },
        {
            "field_1": "Backend_TestJob",
            "field_2": "2lAmnOperation_201",
            "field_3": "1723544154817766912",
            "field_4": "1723544154818599863",
        },
        {
            "field_1": "Backend_TestJob",
            "field_2": "81DznOperation_201",
            "field_3": "1723544154817793024",
            "field_4": "1723544154818380443",
        },
    ]
