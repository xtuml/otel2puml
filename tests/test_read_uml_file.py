"""
This module contains unit tests for the read_uml_file module.
The test class contains test methods for the format_events_list_as_nested_json,
    recursive_get_type, and get_event_list_from_puml functions.
"""
import unittest

from tel2puml.read_uml_file import (
    format_events_list_as_nested_json,
    recursive_get_type,
    get_event_list_from_puml,
    get_markov_sequence_lines_from_audit_event_stream
)
from tel2puml.pipelines.data_creation import (
    generate_test_data_event_sequences_from_puml
)
from tel2puml.tel2puml_types import DUMMY_START_EVENT


class Testread_uml_file(unittest.TestCase):
    """
    This module contains unit tests for the read_uml_file module.

    The read_uml_file module provides functions for formatting event lists as
        nested JSON, retrieving event types recursively,
        and getting event lists from a PlantUML file.
    """

    def test_format_events_list_as_nested_json(self) -> None:
        """
        Test case for the format_events_list_as_nested_json function.
        """
        audit_event_lists = [
            [
                [
                    {
                        "eventId": "1",
                        "eventType": "Event1",
                        "previousEventIds": ["2", "3"],
                    },
                    {"eventId": "2", "eventType": "Event2"},
                    {"eventId": "3", "eventType": "Event3"},
                ]
            ]
        ]
        DEBUG = False
        expected_output = {
            "1": {
                "eventType": "Event1",
                "previousEventIds": {
                    "2": {"eventType": "Event2"},
                    "3": {"eventType": "Event3"},
                },
            },
            "2": {"eventType": "Event2"},
            "3": {"eventType": "Event3"},
        }

        self.assertEqual(
            format_events_list_as_nested_json(audit_event_lists, DEBUG),
            expected_output,
        )

    def test_recursive_get_type(self) -> None:
        """
        Test case for the recursive_get_type function.

        This test case verifies the correctness of the recursive_get_type
            function by testing its output against an expected output.
        It creates a nested event tree and checks if the function correctly
            retrieves the types of all events in the tree.

        The expected output is a comma-separated string of event types:
            "type1,type2,type3,type4".
        """
        event_tree = {
            "eventType": "type1",
            "previousEventIds": {
                "item2": {
                    "eventType": "type2",
                    "previousEventIds": {
                        "item3": {
                            "eventType": "type3",
                            "previousEventIds": {
                                "item4": {"eventType": "type4"}
                            },
                        }
                    },
                }
            },
        }

        output_wip = ""
        max_depth = 10
        depth = 0
        expected_output = "type1,type2,type3,type4"
        self.assertEqual(
            recursive_get_type(event_tree, output_wip, max_depth, depth),
            expected_output,
        )

    def test_get_event_list_from_puml(self) -> None:
        """
        Test case for the get_event_list_from_puml function.

        This test case verifies the correctness of the get_event_list_from_puml
            function by comparing its output with the expected output.
        It uses a sample puml file, a puml key, and debug mode to retrieve
            the event list from the puml file.

        The expected output is a string representing the expected event list.

        """
        puml_file = "puml_files/simple_test.puml"
        puml_key = "ValidSols"
        output_file = ""
        DEBUG = True
        expected_output = "A,D\nA,B,C"
        self.assertEqual(
            get_event_list_from_puml(puml_file, puml_key, output_file, DEBUG),
            expected_output,
        )


def test_get_markov_sequence_lines_from_audit_event_stream() -> None:
    """Test the `get_markov_sequence_lines_from_audit_event_stream` function.
    """
    # check for a simple case
    event_sequences = generate_test_data_event_sequences_from_puml(
        "puml_files/simple_test.puml"
    )
    result = get_markov_sequence_lines_from_audit_event_stream(event_sequences)
    assert result == "A,D\nA,B,C"

    # check for a more complex case
    event_sequences = generate_test_data_event_sequences_from_puml(
            "puml_files/and_with repeated_pattern.puml"
        )
    result = get_markov_sequence_lines_from_audit_event_stream(event_sequences)
    expected_lines = ["A,G,H", "A,B,C,D", "A,B,C,D", "A,E,C,D"]
    for line in result.split("\n"):
        assert line in expected_lines
        expected_lines.remove(line)
    assert len(expected_lines) == 0
    # test case adding a dummy start event
    event_sequences = generate_test_data_event_sequences_from_puml(
        "puml_files/and_with repeated_pattern.puml"
    )
    result = get_markov_sequence_lines_from_audit_event_stream(
        event_sequences,
        add_dummy_start=True
    )
    expected_lines = [
        f"{DUMMY_START_EVENT},{expected_line}"
        for expected_line in ["A,G,H", "A,B,C,D", "A,B,C,D", "A,E,C,D"]
    ]
    for line in result.split("\n"):
        assert line in expected_lines
        expected_lines.remove(line)
    assert len(expected_lines) == 0


if __name__ == "__main__":
    unittest.main()
