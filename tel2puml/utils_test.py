"""Utils for tests
"""
from tel2puml.pipelines.data_creation import (
    generate_test_data_event_sequences_from_puml
)
from tel2puml.pv_to_puml import pv_to_puml_string
from tel2puml.check_puml_equiv import check_puml_equivalence


def end_to_end_test(
    puml_file: str,
    is_branch_puml: bool = False,
    dummy_start_event: bool = False,
) -> None:
    """End to end test for a given puml file.

    :param puml_file: The puml file to test.
    :type puml_file: `str`
    :param is_branch_puml: Whether the puml file is a branch puml, defaults to
    False.
    :type is_branch_puml: `bool`, optional
    :param dummy_start_event: Whether to remove the dummy start event, defaults
    to False.
    :type dummy_start_event: `bool`, optional
    """
    test_data = generate_test_data_event_sequences_from_puml(
        puml_file, is_branch_puml=is_branch_puml,
        remove_dummy_start_event=dummy_start_event
    )
    puml_string = pv_to_puml_string(test_data)
    with open(
        puml_file, "r", encoding="utf-8"
    ) as file:
        expected_puml_string = file.read()
    assert check_puml_equivalence(puml_string, expected_puml_string)
