"""
This module contains the test class for the jAlergia2NetworkX module.
The test class contains test methods for the get_nodes, get_edges,
    and convert_to_networkx functions.
The setUp method is used to set up the test data.
"""

import unittest
from tel2puml.jAlergia2NetworkX import (
    get_nodes,
    get_edges,
    convert_to_networkx,
)


class TestJAlergia2NetworkX(unittest.TestCase):
    """
    Test class for jAlergia2NetworkX module.
    """

    def setUp(self):
        """
        Set up test data.
        """
        self.data = """
            q1 [shape="circle",label="A"]
            q2 [shape="circle",label="B"]
            q3 [shape="circle",label="C"]
            q1 -> q2 [label="1"]
            q2 -> q3 [label="2"]
        """

    def test_get_nodes(self):
        """
        Test get_nodes function.
        """
        node_reference, events_reference, node_list = get_nodes(self.data)
        self.assertEqual(
            node_reference, {"A": ["q1"], "B": ["q2"], "C": ["q3"]}
        )
        self.assertEqual(events_reference, {"q1": "A", "q2": "B", "q3": "C"})
        self.assertEqual(node_list, ["A", "B", "C"])

    def test_get_edges(self):
        """
        Test get_edges function.
        """
        edge_list = get_edges(self.data)
        self.assertEqual(
            edge_list,
            {("q1", "q2"): {"weight": "1"}, ("q2", "q3"): {"weight": "2"}},
        )

    def test_convert_to_networkx(self):
        """
        Test convert_to_networkx function.
        """
        events_reference = {"q1": "A", "q2": "B", "q3": "C"}
        edge_list = {
            ("q1", "q2"): {"weight": "1"},
            ("q2", "q3"): {"weight": "2"},
        }
        graph = convert_to_networkx(events_reference, edge_list)
        self.assertEqual(graph.number_of_nodes(), 3)
        self.assertEqual(graph.number_of_edges(), 2)
        self.assertEqual(graph.nodes["q1"]["label"], "A")
        self.assertEqual(
            str(graph.edges("q1", data=True, keys=True)),
            "[('q1', 'q2', 0, {'label': '1'})]",
        )
        self.assertEqual(
            str(graph.edges("q2", data=True, keys=True)),
            "[('q2', 'q3', 0, {'label': '2'})]",
        )


if __name__ == "__main__":
    unittest.main()
