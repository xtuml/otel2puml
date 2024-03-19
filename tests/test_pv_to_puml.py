"""Test cases for pv_to_puml module"""
from tel2puml.pv_to_puml import pv_to_puml_string
from tel2puml.pipelines.data_creation import (
    generate_test_data_event_sequences_from_puml
)


def test_pv_to_puml_string():
    """Test the `pv_to_puml_string` function returns a puml string of the
    expected length and structure
    """
    test_data = generate_test_data_event_sequences_from_puml(
        "puml_files/complicated_test.puml"
    )
    puml_string = pv_to_puml_string(test_data)
    with open(
        "puml_files/complicated_test.puml", "r", encoding="utf-8"
    ) as file:
        expected_puml_lines = file.readlines()
    puml_string_lines = puml_string.splitlines(keepends=True)
    assert len(puml_string_lines) == len(expected_puml_lines)
    assert puml_string_lines[0] == expected_puml_lines[0]
    assert puml_string_lines[-1] == expected_puml_lines[-1]
