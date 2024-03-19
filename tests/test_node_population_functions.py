"""
This module tests the functions present in the 'node' class.
"""

import unittest
from unittest.mock import patch
from tel2puml.node_map_to_puml.node import Node
from tel2puml.node_map_to_puml.node_population_functions import (
    populate_incoming,
    populate_outgoing,
    print_outgoing,
    create_event_node_ref
)
import networkx as nx


class TestNode(unittest.TestCase):
    """
    Unit tests for the Node class.
    """

    def setUp(self):
        """
        Set up the test case by creating a directed graph and adding edges.
        """
        self.graph = nx.DiGraph()
        self.graph.add_edge("A", "B")
        self.graph.add_edge("A", "C")
        self.graph.add_edge("B", "D")
        self.graph.add_edge("C", "D")

    def test_populate_incoming(self):
        """
        Test case to verify the behavior of the populate_incoming method.

        It checks if the incoming nodes are correctly populated for a given
            node using a lookup table and a graph.

        The test ensures that the number of incoming nodes is correct and
            that the expected nodes are present in the incoming list.

        """
        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
            "D": Node("D"),
        }
        node = Node("D")
        populate_incoming(node, lookup_table, self.graph)
        self.assertEqual(len(node.incoming), 2)
        self.assertIn(lookup_table["B"], node.incoming)
        self.assertIn(lookup_table["C"], node.incoming)

    def test_populate_outgoing(self):
        """
        Test case to verify the functionality of the populate_outgoing method
            in the Node class.
        """
        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
            "D": Node("D"),
        }
        node = Node("A")
        lookup_table = populate_outgoing(node, self.graph, lookup_table, 2)
        self.assertEqual(len(node.outgoing), 2)
        self.assertIn(lookup_table["B"], node.outgoing)
        self.assertIn(lookup_table["C"], node.outgoing)

    def test_print_outgoing(self):
        """
        Test case for the print_outgoing method of the Node class.
        """
        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
            "D": Node("D"),
        }
        node = Node("A")
        lookup_table = populate_outgoing(node, self.graph, lookup_table, 2)
        expected_output_lines = [
            "-> A",
            "  -> B",
            "    -> D",
            "  -> C",
            "    -> D",
        ]

        with patch("builtins.print") as mock_print:
            print_outgoing(node)
            for loop in range(0, mock_print.call_count):
                self.assertEqual(
                    mock_print.call_args_list[loop].args[0],
                    expected_output_lines[loop],
                )


def test_create_event_node_ref():
    """Test case for the `create_event_node_ref` function.
    """
    lookup_table = {
        "q0": Node("q0"),
        "q1": Node("q1"),
        "q2": Node("q2"),
        "q3": Node("q3"),
    }
    node_reference = {
        "A": ["q0", "q1"],
        "B": ["q2"],
        "C": ["q3"],
    }
    node_ref = create_event_node_ref(lookup_table, node_reference)
    expected_output = {
        "A": [lookup_table["q0"], lookup_table["q1"]],
        "B": [lookup_table["q2"]],
        "C": [lookup_table["q3"]],
    }
    assert node_ref == expected_output


if __name__ == "__main__":
    unittest.main()
