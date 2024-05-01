"""Test cases for pv_to_puml module"""
from tel2puml.pv_to_puml import pv_to_puml_string
from tel2puml.pipelines.data_creation import (
    generate_test_data_event_sequences_from_puml
)
from tel2puml.check_puml_equiv import check_puml_equivalence


def test_pv_to_puml_string() -> None:
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
        expected_puml_string = file.read()
    assert check_puml_equivalence(puml_string, expected_puml_string)
    # test with a loop
    test_data = generate_test_data_event_sequences_from_puml(
        "puml_files/loop_ANDFork_a.puml"
    )
    puml_string = pv_to_puml_string(test_data)
    with open(
        "puml_files/loop_ANDFork_a.puml", "r", encoding="utf-8"
    ) as file:
        expected_puml_string = file.read()
    assert check_puml_equivalence(puml_string, expected_puml_string)
    # test with branch counts
    test_data = generate_test_data_event_sequences_from_puml(
        "puml_files/sequence_branch_counts.puml",
        is_branch_puml=True
    )
    puml_string = pv_to_puml_string(test_data)
    with open(
        "puml_files/sequence_branch_counts.puml", "r", encoding="utf-8"
    ) as file:
        expected_puml_string = file.read()
    assert check_puml_equivalence(puml_string, expected_puml_string)
    # test with a merge on the same event under the same parent logic block
    test_data = generate_test_data_event_sequences_from_puml(
        "puml_files/complicated_merge_with_same_event.puml"
    )
    puml_string = pv_to_puml_string(test_data)
    with open(
        "puml_files/complicated_merge_with_same_event.puml", "r",
        encoding="utf-8"
    ) as file:
        expected_puml_string = file.read()
    assert check_puml_equivalence(puml_string, expected_puml_string)
