"""end to end test function
"""
from typing import Callable

import pytest

from tel2puml.pv_event_simulator import (
    generate_test_data_event_sequences_from_puml
)
from tel2puml.pv_to_puml.pv_to_puml import pv_to_puml_string
from tel2puml.check_puml_equiv import (
    check_puml_string_equivalence_to_puml_files
)


def end_to_end_helper(
    puml_file: str,
    is_branch_puml: bool = False,
    dummy_start_event: bool = False,
    should_pass: bool = True,
    equivalent_pumls: list[str] | None = None,
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
    :param should_pass: Whether the test should pass, defaults to True.
    :type should_pass: `bool`, optional
    :param equivalent_pumls: The equivalent pumls to compare against, defaults
    to None.
    :type equivalent_pumls: `list`[`str`], optional
    """
    test_data = generate_test_data_event_sequences_from_puml(
        puml_file, is_branch_puml=is_branch_puml,
        remove_dummy_start_event=dummy_start_event
    )
    puml_string = pv_to_puml_string(test_data)
    assert check_puml_string_equivalence_to_puml_files(
        puml_string,
        [puml_file] + (equivalent_pumls or []),
    ) == should_pass


@pytest.fixture
def end_to_end_test() -> Callable[..., None]:
    """End to end test fixture."""
    return end_to_end_helper
