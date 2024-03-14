"""Unit and end-to-end tests for node_map_to_puml"""

import unittest
from tel2puml.node_map_to_puml.node import Node
from tel2puml.node_map_to_puml.node_map_to_puml import (
    is_in_loop,
    drill_down_tree,
    get_reverse_node_tree,
    append_logic_middle_or_end,
    append_logic_start,
    handle_loop_start,
    get_reverse_node_tree_dict,
    get_tree_similarity,
    get_smallest_reverse_tree,
    handle_immediate_children,
    handle_divergent_tree_children,
    create_content_logic,
    create_content,
    analyse_node,
    get_coords_in_nested_dict,
    format_output,
    find_nearest_extant_ancestor,
    insert_item_using_property_key,
    insert_missing_nodes,
    alter_node_tree_to_contain_logic_nodes,
    convert_nodes_to_puml,
)
from tel2puml.node_map_to_puml.node_population_functions import (
    convert_to_nodes,
    get_puml_data_and_analyse_with_jalergia,
)


class TestIsInLoop(unittest.TestCase):
    """Test case class for the `is_in_loop` function."""

    def test_is_in_loop_target_in_loop(self):
        """Test case where the target node is in a loop."""
        nodes = {"A": Node("A")}
        nodes["B"] = Node("B")
        nodes["C"] = Node("C")

        nodes["A"].outgoing = [nodes["B"]]
        nodes["B"].outgoing = [nodes["C"]]
        nodes["C"].outgoing = [nodes["A"]]
        nodes["C"].outgoing.append(Node("END_LOOP"))

        node_tree = nodes["A"]

        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        target = node_tree.outgoing[0]

        result = is_in_loop(target, logic_lines, node_tree)

        self.assertTrue(result)

    def test_is_in_loop_target_not_in_loop(self):
        """Test case where the target node is not in a loop."""
        nodes = {"A": Node("A")}
        nodes["B"] = Node("B")
        nodes["C"] = Node("C")
        nodes["D"] = Node("D")

        nodes["A"].outgoing = [nodes["B"]]
        nodes["B"].outgoing = [nodes["C"]]
        nodes["C"].outgoing = [nodes["A"]]
        nodes["C"].outgoing.append(Node("END_LOOP"))

        node_tree = nodes["A"]

        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        target = nodes["D"]

        result = is_in_loop(target, logic_lines, node_tree)

        self.assertFalse(result)

    def test_is_in_loop_max_depth_reached(self):
        """Test case where the maximum depth is reached."""
        nodes = {"A": Node("A")}
        nodes["B"] = Node("B")
        nodes["C"] = Node("C")
        nodes["D"] = Node("D")

        nodes["A"].outgoing = [nodes["B"]]
        nodes["B"].outgoing = [nodes["C"]]
        nodes["C"].outgoing = [nodes["A"]]
        nodes["C"].outgoing.append(Node("END_LOOP"))

        node_tree = nodes["A"]

        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        target = nodes["C"]

        result = is_in_loop(target, logic_lines, node_tree, max_depth=0)

        self.assertFalse(result)


class TestDrillDownTree(unittest.TestCase):
    """Test case class for the drill_down_tree function."""

    def test_drill_down_tree_single_node(self):
        """Test case with a single node."""
        node = Node("A")
        lookup_table = {}
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        max_depth = 10

        result = drill_down_tree(node, lookup_table, logic_lines, max_depth)

        self.assertEqual(result, node)

    def test_drill_down_tree_no_outgoing_nodes(self):
        """Test case with a node that has no outgoing nodes."""
        node = Node("A")
        lookup_table = {}
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        max_depth = 10

        result = drill_down_tree(node, lookup_table, logic_lines, max_depth)

        self.assertEqual(result, node)

    def test_drill_down_tree_single_outgoing_node(self):
        """Test case with a node that has a single outgoing node."""
        node = Node("A")
        node.outgoing = [Node("B")]
        lookup_table = {}
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        max_depth = 10

        result = drill_down_tree(node, lookup_table, logic_lines, max_depth)

        self.assertEqual(result, node.outgoing[0])

    def test_drill_down_tree_multiple_outgoing_nodes(self):
        """Test case with a node that has multiple outgoing nodes."""
        node = Node("A")
        node.outgoing = [Node("B"), Node("C")]
        lookup_table = {}
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        max_depth = 10

        result = drill_down_tree(node, lookup_table, logic_lines, max_depth)

        self.assertEqual(result, node)

    def test_drill_down_tree_allowed_nodes(self):
        """
        Test case with a node that has multiple outgoing nodes, but only one is
        allowed
        """
        node = Node("A")
        node.outgoing = [Node("B"), Node("C")]
        lookup_table = {"B": True}
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        max_depth = 10

        result = drill_down_tree(node, lookup_table, logic_lines, max_depth)

        self.assertEqual(result, node.outgoing[0])

    def test_drill_down_tree_in_loop(self):
        """Test case with a node that is in a loop."""
        nodes = {"A": Node("A")}
        nodes["B"] = Node("B")
        nodes["C"] = Node("C")
        nodes["D"] = Node("D")

        nodes["A"].outgoing = [nodes["B"]]
        nodes["B"].outgoing = [nodes["C"]]
        nodes["C"].outgoing = [nodes["A"]]
        nodes["C"].outgoing.append(Node("END_LOOP"))

        lookup_table = {}
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        max_depth = 10

        node = nodes["A"]
        target = nodes["C"]

        result = drill_down_tree(node, lookup_table, logic_lines, max_depth)

        self.assertEqual(result, target)

    def test_drill_down_tree_max_depth_reached(self):
        """Test case where the maximum depth is reached."""
        node = Node("A")
        node.outgoing = [Node("B")]
        lookup_table = {}
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        max_depth = 0

        result = drill_down_tree(node, lookup_table, logic_lines, max_depth)

        self.assertEqual(result, node)


class TestGetReverseNodeTree(unittest.TestCase):
    """Unit tests for the get_reverse_node_tree function."""

    def test_get_reverse_node_tree_single_node(self):
        """Test case with a single node"""
        node = Node("A")
        lookup_table = {}
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        max_depth = 10

        result = get_reverse_node_tree(
            node, lookup_table, logic_lines, max_depth
        )

        self.assertEqual(result, [])

    def test_get_reverse_node_tree_no_outgoing_nodes(self):
        """Test case with a node that has no outgoing nodes"""
        node = Node("A")
        lookup_table = {}
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        max_depth = 10

        result = get_reverse_node_tree(
            node, lookup_table, logic_lines, max_depth
        )

        self.assertEqual(result, [])

    def test_get_reverse_node_tree_single_outgoing_node(self):
        """Test case with a node that has a single outgoing node"""
        lookup_table = {"A": Node("A")}
        lookup_table["B"] = Node("B")
        lookup_table["C"] = Node("C")

        lookup_table["A"].outgoing = [lookup_table["B"]]
        lookup_table["B"].outgoing = [lookup_table["C"]]

        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        max_depth = 10

        result = get_reverse_node_tree(
            lookup_table["A"], lookup_table, logic_lines, max_depth
        )

        self.assertEqual(result, [lookup_table["C"], lookup_table["B"]])

    def test_get_reverse_node_tree_multiple_outgoing_nodes(self):
        """Test case with a node that has multiple outgoing nodes"""
        node = Node("A")
        node.outgoing = [Node("B"), Node("C")]
        lookup_table = {}
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        max_depth = 10

        result = get_reverse_node_tree(
            node, lookup_table, logic_lines, max_depth
        )

        self.assertEqual(result, [])

    def test_get_reverse_node_tree_allowed_nodes(self):
        """
        Test case with a node that has multiple outgoing nodes, but only
        one is in the lookup table
        """
        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
            "D": Node("D"),
        }
        node = lookup_table["A"]
        lookup_table["A"].outgoing = [lookup_table["B"], Node("1"), Node("2")]
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        max_depth = 10

        result = get_reverse_node_tree(
            node, lookup_table, logic_lines, max_depth
        )

        self.assertEqual(result, [lookup_table["B"]])

    def test_get_reverse_node_tree_in_loop(self):
        """Test case with a node that is in a loop"""

        nodes = {"A": Node("A")}
        nodes["B"] = Node("B")
        nodes["C"] = Node("C")
        nodes["D"] = Node("D")

        nodes["A"].outgoing = [nodes["B"]]
        nodes["B"].outgoing = [nodes["C"]]
        nodes["C"].outgoing = [nodes["A"]]
        nodes["C"].outgoing.append(Node("END_LOOP"))

        lookup_table = {}
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        max_depth = 10

        node = nodes["A"]

        result = get_reverse_node_tree(
            node, lookup_table, logic_lines, max_depth
        )

        self.assertEqual(result, [nodes["C"], nodes["B"]])

    def test_get_reverse_node_tree_max_depth_reached(self):
        """Test case where the maximum depth is reached"""
        node = Node("A")
        node.outgoing = [Node("B")]
        lookup_table = {}
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        max_depth = 0

        result = get_reverse_node_tree(
            node, lookup_table, logic_lines, max_depth
        )

        self.assertEqual(result, [])


class TestGetTreeSimilarity(unittest.TestCase):
    """Unit tests for the get_tree_similarity function"""

    def test_get_tree_similarity_all_trees_converge(self):
        """Test case where all trees in reverse_node_trees converge"""

        start_node = Node("A")
        end_node = Node("I")
        reverse_node_trees = {
            "Tree1": [end_node, Node("C"), Node("B"), start_node],
            "Tree2": [end_node, Node("E"), Node("D"), start_node],
            "Tree3": [end_node, Node("G"), start_node],
        }

        start_node.outgoing = [
            reverse_node_trees["Tree1"][2],
            reverse_node_trees["Tree2"][2],
            reverse_node_trees["Tree3"][2],
        ]
        end_node.incoming = [
            reverse_node_trees["Tree1"][1],
            reverse_node_trees["Tree2"][1],
            reverse_node_trees["Tree3"][1],
        ]

        reverse_node_trees["Tree1"][1].incoming = reverse_node_trees["Tree1"][
            2
        ]
        reverse_node_trees["Tree1"][1].outgoing = reverse_node_trees["Tree1"][
            0
        ]

        reverse_node_trees["Tree2"][1].incoming = reverse_node_trees["Tree2"][
            2
        ]
        reverse_node_trees["Tree2"][1].outgoing = reverse_node_trees["Tree2"][
            0
        ]

        reverse_node_trees["Tree3"][1].incoming = reverse_node_trees["Tree3"][
            2
        ]
        reverse_node_trees["Tree3"][1].outgoing = reverse_node_trees["Tree3"][
            0
        ]

        reverse_node_trees["Tree1"][2].incoming = reverse_node_trees["Tree1"][
            3
        ]
        reverse_node_trees["Tree1"][2].outgoing = reverse_node_trees["Tree1"][
            1
        ]

        reverse_node_trees["Tree2"][2].incoming = reverse_node_trees["Tree2"][
            3
        ]
        reverse_node_trees["Tree2"][2].outgoing = reverse_node_trees["Tree2"][
            1
        ]

        smallest_tree = reverse_node_trees["Tree3"]

        result = get_tree_similarity(reverse_node_trees, smallest_tree)

        self.assertEqual(result, 1)

    def test_get_tree_similarity_not_all_trees_converge(self):
        """Test case where not all trees in reverse_node_trees converge"""

        start_node = Node("A")
        end_node = Node("I")
        reverse_node_trees = {
            "Tree1": [end_node, Node("C"), Node("B"), start_node],
            "Tree2": [end_node, Node("E"), Node("D"), start_node],
            "Tree3": [Node("1"), Node("G"), Node("F"), start_node],
        }

        start_node.outgoing = [
            reverse_node_trees["Tree1"][2],
            reverse_node_trees["Tree2"][2],
            reverse_node_trees["Tree3"][2],
        ]
        end_node.incoming = [
            reverse_node_trees["Tree1"][1],
            reverse_node_trees["Tree2"][1],
        ]

        reverse_node_trees["Tree1"][1].incoming = reverse_node_trees["Tree1"][
            2
        ]
        reverse_node_trees["Tree1"][1].outgoing = reverse_node_trees["Tree1"][
            0
        ]

        reverse_node_trees["Tree2"][1].incoming = reverse_node_trees["Tree2"][
            2
        ]
        reverse_node_trees["Tree2"][1].outgoing = reverse_node_trees["Tree2"][
            0
        ]

        reverse_node_trees["Tree3"][1].incoming = reverse_node_trees["Tree3"][
            2
        ]
        reverse_node_trees["Tree3"][1].outgoing = reverse_node_trees["Tree3"][
            0
        ]

        reverse_node_trees["Tree1"][2].incoming = reverse_node_trees["Tree1"][
            3
        ]
        reverse_node_trees["Tree1"][2].outgoing = reverse_node_trees["Tree1"][
            1
        ]

        reverse_node_trees["Tree2"][2].incoming = reverse_node_trees["Tree2"][
            3
        ]
        reverse_node_trees["Tree2"][2].outgoing = reverse_node_trees["Tree2"][
            1
        ]

        reverse_node_trees["Tree3"][2].incoming = reverse_node_trees["Tree3"][
            3
        ]
        reverse_node_trees["Tree3"][2].outgoing = reverse_node_trees["Tree3"][
            1
        ]

        smallest_tree = reverse_node_trees["Tree1"]

        result = get_tree_similarity(reverse_node_trees, smallest_tree)

        self.assertEqual(result, 0)

    def test_get_tree_similarity_empty_tree(self):
        """Test case where reverse_node_trees contains an empty tree"""

        start_node = Node("A")
        end_node = Node("I")
        reverse_node_trees = {
            "Tree1": [end_node, Node("C"), Node("B"), start_node],
            "Tree2": [Node("K"), Node("E"), Node("D"), start_node],
            "Tree3": [],
        }

        start_node.outgoing = [
            reverse_node_trees["Tree1"][2],
            reverse_node_trees["Tree2"][2],
        ]
        end_node.incoming = [
            reverse_node_trees["Tree1"][1],
            reverse_node_trees["Tree2"][1],
        ]

        reverse_node_trees["Tree1"][1].incoming = reverse_node_trees["Tree1"][
            2
        ]
        reverse_node_trees["Tree1"][1].outgoing = reverse_node_trees["Tree1"][
            0
        ]

        reverse_node_trees["Tree2"][1].incoming = reverse_node_trees["Tree2"][
            2
        ]
        reverse_node_trees["Tree2"][1].outgoing = reverse_node_trees["Tree2"][
            0
        ]

        reverse_node_trees["Tree1"][2].incoming = reverse_node_trees["Tree1"][
            3
        ]
        reverse_node_trees["Tree1"][2].outgoing = reverse_node_trees["Tree1"][
            1
        ]

        reverse_node_trees["Tree2"][2].incoming = reverse_node_trees["Tree2"][
            3
        ]
        reverse_node_trees["Tree2"][2].outgoing = reverse_node_trees["Tree2"][
            1
        ]

        smallest_tree = reverse_node_trees["Tree1"]

        result = get_tree_similarity(reverse_node_trees, smallest_tree)

        self.assertEqual(result, 0)


class TestAppendLogicMiddleOrEnd(unittest.TestCase):
    """Unit tests for the append_logic_middle_or_end function"""

    def test_append_logic_middle_or_end_middle(self):
        """Test case for appending logic in the middle of a branch"""

        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
        }
        logic_table = {
            "XOR": Node(
                data="XOR",
                incoming=lookup_table["A"],
                outgoing=[lookup_table["B"], lookup_table["C"]],
            )
        }
        lookup_table["A"].outgoing_logic = [logic_table["XOR"]]
        lookup_table["B"].incoming_logic = [logic_table["XOR"]]
        lookup_table["C"].incoming_logic = [logic_table["XOR"]]

        output = [lookup_table["A"]]

        idx = 0
        node_tree = lookup_table["A"]
        node_tree.outgoing = [lookup_table["B"], lookup_table["C"]]
        logic_lines = {
            "XOR": {
                "start": "XOR_START",
                "middle": "XOR_MIDDLE",
                "end": "XOR_END",
            },
            "SWITCH": {
                "start": "SWITCH_START",
                "middle": ["SWITCH_MIDDLE_1", "SWITCH_MIDDLE_1"],
                "end": "SWITCH_END",
            },
        }

        result = append_logic_middle_or_end(
            output, idx, node_tree, logic_lines
        )

        expected_output = [
            lookup_table["A"],
            Node(
                "XOR_MIDDLE",
                incoming=lookup_table["A"],
                outgoing=[lookup_table["B"], lookup_table["C"]],
            ),
        ]
        self.assertEqual(result[0], expected_output[0])
        self.assertEqual(result[1].data, expected_output[1].data)
        self.assertEqual(result[1].incoming, expected_output[1].incoming)
        self.assertEqual(result[1].outgoing, expected_output[1].outgoing)

    def test_append_logic_middle_or_end_end(self):
        """Test case for appending logic at the end of a branch"""

        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
        }
        logic_table = {
            "XOR": Node(
                data="XOR",
                incoming=lookup_table["A"],
                outgoing=[lookup_table["B"], lookup_table["C"]],
            )
        }
        lookup_table["A"].outgoing_logic = [logic_table["XOR"]]
        lookup_table["B"].incoming_logic = [logic_table["XOR"]]
        lookup_table["C"].incoming_logic = [logic_table["XOR"]]

        output = [lookup_table["A"]]

        idx = 1
        node_tree = lookup_table["A"]
        node_tree.outgoing = [lookup_table["B"], lookup_table["C"]]
        logic_lines = {
            "XOR": {
                "start": "XOR_START",
                "middle": "XOR_MIDDLE",
                "end": "XOR_END",
            },
            "SWITCH": {
                "start": "SWITCH_START",
                "middle": ["SWITCH_MIDDLE_1", "SWITCH_MIDDLE_1"],
                "end": "SWITCH_END",
            },
        }

        result = append_logic_middle_or_end(
            output, idx, node_tree, logic_lines
        )

        expected_output = [
            lookup_table["A"],
            Node(
                "XOR_END",
                incoming=lookup_table["A"],
                outgoing=[lookup_table["B"], lookup_table["C"]],
            ),
        ]
        self.assertEqual(result[0], expected_output[0])
        self.assertEqual(result[1].data, expected_output[1].data)
        self.assertEqual(result[1].incoming, expected_output[1].incoming)
        self.assertEqual(result[1].outgoing, expected_output[1].outgoing)

    def test_append_logic_middle_or_end_switch_end(self):
        """
        Test case for appending logic at the end of a branch with a SWITCH node
        """
        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
            "D": Node("D"),
        }
        logic_table = {
            "XOR": Node(
                data="XOR",
                incoming=lookup_table["A"],
                outgoing=[
                    lookup_table["B"],
                    lookup_table["C"],
                    lookup_table["D"],
                ],
            )
        }
        lookup_table["A"].outgoing_logic = [logic_table["XOR"]]
        lookup_table["B"].incoming_logic = [logic_table["XOR"]]
        lookup_table["C"].incoming_logic = [logic_table["XOR"]]
        lookup_table["D"].incoming_logic = [logic_table["XOR"]]

        output = [lookup_table["A"]]

        idx = 2
        node_tree = lookup_table["A"]

        logic_lines = {
            "XOR": {
                "start": "XOR_START",
                "middle": "XOR_MIDDLE",
                "end": "XOR_END",
            },
            "SWITCH": {
                "start": "SWITCH_START",
                "middle": ["SWITCH_MIDDLE_1", "SWITCH_MIDDLE_1"],
                "end": "SWITCH_END",
            },
        }

        result = append_logic_middle_or_end(
            output, idx, node_tree, logic_lines
        )

        expected_output = [
            lookup_table["A"],
            Node(
                "SWITCH_END",
                incoming=lookup_table["A"],
                outgoing=[
                    lookup_table["B"],
                    lookup_table["C"],
                    lookup_table["D"],
                ],
            ),
        ]
        self.assertEqual(result[0], expected_output[0])
        self.assertEqual(result[1].data, expected_output[1].data)
        self.assertEqual(result[1].incoming, expected_output[1].incoming)
        self.assertEqual(result[1].outgoing, expected_output[1].outgoing)


class TestAppendLogicStart(unittest.TestCase):
    """Unit tests for the append_logic_start function"""

    def test_append_logic_start_regular_node(self):
        """Test case for appending logic start node for a regular node"""

        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
        }
        logic_table = {
            "XOR": Node(
                data="XOR",
                incoming=lookup_table["A"],
                outgoing=[
                    lookup_table["B"],
                    lookup_table["C"],
                ],
            )
        }
        lookup_table["A"].outgoing_logic = [logic_table["XOR"]]
        lookup_table["B"].incoming_logic = [logic_table["XOR"]]
        lookup_table["C"].incoming_logic = [logic_table["XOR"]]

        output = [lookup_table["A"]]

        node_tree = lookup_table["A"]

        logic_lines = {
            "XOR": {
                "start": "XOR_START",
                "middle": "XOR_MIDDLE",
                "end": "XOR_END",
            },
            "SWITCH": {
                "start": "SWITCH_START",
                "middle": ["SWITCH_MIDDLE_1", "SWITCH_MIDDLE_1"],
                "end": "SWITCH_END",
            },
        }
        result = append_logic_start(output, node_tree, logic_lines)

        expected_output = [
            lookup_table["A"],
            Node(
                "XOR_START",
                incoming=lookup_table["A"],
                outgoing=[
                    lookup_table["B"],
                    lookup_table["C"],
                ],
            ),
        ]
        self.assertEqual(result[0], expected_output[0])
        self.assertEqual(result[1].data, expected_output[1].data)
        self.assertEqual(result[1].incoming, expected_output[1].incoming)
        self.assertEqual(result[1].outgoing, expected_output[1].outgoing)

    def test_append_logic_start_switch_node(self):
        """Test case for appending logic start node for a switch node"""

        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
            "D": Node("D"),
        }
        logic_table = {
            "XOR": Node(
                data="XOR",
                incoming=lookup_table["A"],
                outgoing=[
                    lookup_table["B"],
                    lookup_table["C"],
                    lookup_table["D"],
                ],
            )
        }
        lookup_table["A"].outgoing_logic = [logic_table["XOR"]]
        lookup_table["B"].incoming_logic = [logic_table["XOR"]]
        lookup_table["C"].incoming_logic = [logic_table["XOR"]]
        lookup_table["D"].incoming_logic = [logic_table["XOR"]]

        output = [lookup_table["A"]]

        node_tree = lookup_table["A"]

        logic_lines = {
            "XOR": {
                "start": "XOR_START",
                "middle": "XOR_MIDDLE",
                "end": "XOR_END",
            },
            "SWITCH": {
                "start": "SWITCH_START",
                "middle": ["SWITCH_MIDDLE_1", "SWITCH_MIDDLE_1"],
                "end": "SWITCH_END",
            },
        }

        result = append_logic_start(output, node_tree, logic_lines)

        expected_output = [
            lookup_table["A"],
            Node(
                "SWITCH_START",
                incoming=lookup_table["A"],
                outgoing=[
                    lookup_table["B"],
                    lookup_table["C"],
                    lookup_table["D"],
                ],
            ),
        ]
        self.assertEqual(result[0], expected_output[0])
        self.assertEqual(result[1].data, expected_output[1].data)
        self.assertEqual(result[1].incoming, expected_output[1].incoming)
        self.assertEqual(result[1].outgoing, expected_output[1].outgoing)


class TestHandleLoopStart(unittest.TestCase):
    """Unit tests for the handle_loop_start function"""

    def test_handle_loop_start_no_loop_start(self):
        """Test case where there is no loop start detected"""
        output = []
        node_tree = Node("A")
        logic_lines = {"LOOP": {"start": "START_LOOP", "end": "END_LOOP"}}

        result = handle_loop_start(output, node_tree, logic_lines)

        self.assertEqual(result, [])

    def test_handle_loop_start_with_loop_start(self):
        """Test case where there is a loop start detected"""
        output = []

        nodes = {"A": Node("A")}
        nodes["B"] = Node("B")
        nodes["C"] = Node("C")
        nodes["D"] = Node("D")

        nodes["A"].outgoing = [nodes["B"]]
        nodes["B"].outgoing = [nodes["C"]]
        nodes["C"].outgoing = [nodes["D"]]
        nodes["D"].outgoing = [nodes["A"]]

        nodes["A"].incoming = [nodes["D"]]
        nodes["B"].incoming = [nodes["A"]]
        nodes["C"].incoming = [nodes["B"]]
        nodes["D"].incoming = [nodes["C"]]

        nodes["D"].outgoing.append(Node("END_LOOP"))
        node_tree = nodes["A"]
        logic_lines = {"LOOP": {"start": "START_LOOP", "end": "END_LOOP"}}

        result = handle_loop_start(output, node_tree, logic_lines)

        self.assertEqual(result[0].uid, "START_LOOP")
        self.assertEqual(result[0].incoming, [nodes["D"]])
        self.assertEqual(result[0].outgoing, [nodes["B"]])

    def test_handle_loop_start_multiple_possible_descendants(self):
        """
        Test case where there are multiple possible descendant incoming nodes
        """
        output = []
        nodes = {"A": Node("A")}
        nodes["B"] = Node("B")
        nodes["C"] = Node("C")
        nodes["D"] = Node("D")

        nodes["A"].outgoing = [nodes["B"], nodes["C"]]
        nodes["B"].outgoing = [nodes["A"], nodes["D"]]
        nodes["C"].outgoing = [nodes["A"], nodes["D"]]
        nodes["D"].outgoing = []

        nodes["A"].incoming = [nodes["B"], nodes["C"]]
        nodes["B"].incoming = [nodes["A"]]
        nodes["C"].incoming = [nodes["A"]]
        nodes["D"].incoming = [nodes["B"], nodes["C"]]

        nodes["B"].outgoing.append(Node("END_LOOP"))
        nodes["C"].outgoing.append(Node("END_LOOP"))
        node_tree = nodes["A"]
        logic_lines = {"LOOP": {"start": "START_LOOP", "end": "END_LOOP"}}

        result = handle_loop_start(output, node_tree, logic_lines)

        self.assertEqual(result[0].uid, "START_LOOP")
        self.assertEqual(result[0].incoming, [nodes["B"], nodes["C"]])
        self.assertEqual(result[0].outgoing, [nodes["B"], nodes["C"]])

    def test_handle_loop_start_no_possible_descendants(self):
        """Test case where there are no possible descendant incoming nodes"""
        output = []
        node_tree = Node("A")
        node_tree.incoming = [Node("B")]
        logic_lines = {"LOOP": {"start": "START_LOOP", "end": "END_LOOP"}}

        result = handle_loop_start(output, node_tree, logic_lines)

        self.assertEqual(result, [])


class TestGetReverseNodeTreeDict(unittest.TestCase):
    """Unit tests for the get_reverse_node_tree_dict function"""

    def test_get_reverse_node_tree_dict_with_reverse_node_trees(self):
        """Test case with reverse node trees"""
        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
            "D": Node("D"),
            "E": Node("E"),
            "F": Node("F"),
            "G": Node("G"),
        }
        logic_table = {
            "XOR": Node(
                data="XOR",
                incoming=lookup_table["B"],
                outgoing=[lookup_table["C"], lookup_table["D"]],
            )
        }
        lookup_table["B"].outgoing_logic = [logic_table["XOR"]]
        lookup_table["C"].incoming_logic = [logic_table["XOR"]]
        lookup_table["D"].incoming_logic = [logic_table["XOR"]]

        lookup_table["A"].outgoing = [lookup_table["B"]]
        lookup_table["B"].outgoing = [lookup_table["C"], lookup_table["D"]]
        lookup_table["C"].outgoing = [lookup_table["E"]]
        lookup_table["D"].outgoing = [lookup_table["F"]]
        lookup_table["E"].outgoing = [lookup_table["G"]]
        lookup_table["F"].outgoing = [lookup_table["G"]]

        node_tree = lookup_table["B"]

        logic_lines = {
            "XOR": {
                "start": "XOR_START",
                "middle": "XOR_MIDDLE",
                "end": "XOR_END",
            },
            "SWITCH": {
                "start": "SWITCH_START",
                "middle": ["SWITCH_MIDDLE_1", "SWITCH_MIDDLE_1"],
                "end": "SWITCH_END",
            },
            "LOOP": {"end": "END_LOOP"},
        }

        reverse_node_trees = get_reverse_node_tree_dict(
            node_tree, lookup_table, logic_lines
        )

        self.assertEqual(
            reverse_node_trees,
            {
                "C": [lookup_table["G"], lookup_table["E"]],
                "D": [lookup_table["G"], lookup_table["F"]],
            },
        )


class TestGetSmallestReverseTree(unittest.TestCase):
    """Unit tests for the get_smallest_reverse_tree function"""

    def test_get_smallest_reverse_tree_empty_dict(self):
        """Test case with an empty dictionary"""
        reverse_node_trees = {}

        result = get_smallest_reverse_tree(reverse_node_trees)

        self.assertEqual(result, [])

    def test_get_smallest_reverse_tree_single_tree(self):
        """Test case with a single reverse tree"""
        reverse_node_trees = {"tree1": [1, 2, 3, 4, 5]}

        result = get_smallest_reverse_tree(reverse_node_trees)

        self.assertEqual(result, [1, 2, 3, 4, 5])

    def test_get_smallest_reverse_tree_multiple_trees(self):
        """Test case with multiple reverse trees"""
        reverse_node_trees = {
            "tree1": [1, 2, 3],
            "tree2": [1, 2, 3, 4],
            "tree3": [1, 2],
            "tree4": [1, 2, 3, 4, 5],
        }

        result = get_smallest_reverse_tree(reverse_node_trees)

        self.assertEqual(result, [1, 2])

    def test_get_smallest_reverse_tree_equal_length_trees(self):
        """Test case with multiple reverse trees of equal length"""
        reverse_node_trees = {
            "tree1": [1, 2, 3],
            "tree2": [4, 5, 6],
            "tree3": [7, 8, 9],
        }

        result = get_smallest_reverse_tree(reverse_node_trees)

        self.assertEqual(result, [1, 2, 3])


class TestHandleImmediateChildren(unittest.TestCase):
    """Unit tests for the handle_immediate_children function"""

    def test_handle_immediate_children_tree_similarity_greater_than_zero(self):
        """Test case where tree_similarity is greater than zero"""
        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
        }
        logic_table = {
            "XOR": Node(
                data="XOR",
                incoming=lookup_table["A"],
                outgoing=[
                    lookup_table["B"],
                    lookup_table["C"],
                ],
            )
        }
        lookup_table["A"].outgoing_logic = [logic_table["XOR"]]
        lookup_table["B"].incoming_logic = [logic_table["XOR"]]
        lookup_table["C"].incoming_logic = [logic_table["XOR"]]

        output = [lookup_table["A"]]

        node_tree = lookup_table["A"]

        logic_lines = {
            "XOR": {
                "start": "XOR_START",
                "middle": "XOR_MIDDLE",
                "end": "XOR_END",
            },
            "SWITCH": {
                "start": "SWITCH_START",
                "middle": ["SWITCH_MIDDLE_1", "SWITCH_MIDDLE_1"],
                "end": "SWITCH_END",
            },
        }
        output = [lookup_table["A"], Node(logic_lines["XOR"]["start"])]
        reverse_node_trees = {
            "B": [lookup_table["B"]],
            "C": [lookup_table["C"]],
        }
        depth = 1
        max_depth = 10

        expected_output = ["A", "XOR_START", "B", "XOR_MIDDLE", "C", "XOR_END"]

        result = handle_immediate_children(
            node_tree,
            1,
            reverse_node_trees,
            output,
            logic_lines,
            lookup_table,
            depth,
            max_depth,
        )

        for idx, item in enumerate(expected_output):
            self.assertEqual(result[idx].uid, item)

    def test_handle_immediate_children_tree_similarity_zero(self):
        """Test case where tree_similarity is zero"""
        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
            "D": Node("D"),
        }
        logic_table = {
            "XOR": Node(
                data="XOR",
                incoming=lookup_table["A"],
                outgoing=[
                    lookup_table["B"],
                    lookup_table["C"],
                ],
            )
        }
        lookup_table["A"].outgoing_logic = [logic_table["XOR"]]
        lookup_table["B"].incoming_logic = [logic_table["XOR"]]
        lookup_table["C"].incoming_logic = [logic_table["XOR"]]
        lookup_table["C"].outgoing = [lookup_table["D"]]

        output = [lookup_table["A"]]

        node_tree = lookup_table["A"]

        logic_lines = {
            "XOR": {
                "start": "XOR_START",
                "middle": "XOR_MIDDLE",
                "end": "XOR_END",
            },
            "SWITCH": {
                "start": "SWITCH_START",
                "middle": ["SWITCH_MIDDLE_1", "SWITCH_MIDDLE_1"],
                "end": "SWITCH_END",
            },
            "LOOP": {"end": "LOOP_END"},
        }
        output = [lookup_table["A"], Node(logic_lines["XOR"]["start"])]
        reverse_node_trees = {
            "B": [lookup_table["B"]],
            "C": [lookup_table["C"]],
        }
        depth = 1
        max_depth = 10

        expected_output = [
            "A",
            "XOR_START",
            "B",
            "XOR_MIDDLE",
            "C",
            "D",
            "XOR_END",
        ]

        result = handle_immediate_children(
            node_tree,
            0,
            reverse_node_trees,
            output,
            logic_lines,
            lookup_table,
            depth,
            max_depth,
        )

        for idx, item in enumerate(expected_output):
            self.assertEqual(result[idx].uid, item)

    def test_handle_immediate_children_max_depth_reached(self):
        """Test case where the maximum depth is reached"""
        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
            "D": Node("D"),
        }
        logic_table = {
            "XOR": Node(
                data="XOR",
                incoming=lookup_table["A"],
                outgoing=[
                    lookup_table["B"],
                    lookup_table["C"],
                ],
            )
        }
        lookup_table["A"].outgoing_logic = [logic_table["XOR"]]
        lookup_table["B"].incoming_logic = [logic_table["XOR"]]
        lookup_table["C"].incoming_logic = [logic_table["XOR"]]
        lookup_table["C"].outgoing = [lookup_table["D"]]

        output = [lookup_table["A"]]

        node_tree = lookup_table["A"]

        logic_lines = {
            "XOR": {
                "start": "XOR_START",
                "middle": "XOR_MIDDLE",
                "end": "XOR_END",
            },
            "SWITCH": {
                "start": "SWITCH_START",
                "middle": ["SWITCH_MIDDLE_1", "SWITCH_MIDDLE_1"],
                "end": "SWITCH_END",
            },
            "LOOP": {"end": "LOOP_END"},
        }
        output = [lookup_table["A"], Node(logic_lines["XOR"]["start"])]
        reverse_node_trees = {
            "B": [lookup_table["B"]],
            "C": [lookup_table["C"]],
        }
        depth = 1
        max_depth = 0

        expected_output = ["A", "XOR_START", "XOR_MIDDLE", "XOR_END"]

        result = handle_immediate_children(
            node_tree,
            0,
            reverse_node_trees,
            output,
            logic_lines,
            lookup_table,
            depth,
            max_depth,
        )

        for idx, item in enumerate(expected_output):
            self.assertEqual(result[idx].uid, item)


class TestHandleDivergentTreeChildren(unittest.TestCase):
    """Unit tests for the handle_divergent_tree_children function"""

    def test_handle_divergent_tree_children_no_similarity(self):
        """Test case where tree similarity is 0"""
        smallest_tree = [Node("A"), Node("B"), Node("C")]
        output = "output"
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        lookup_table = {"A": Node("A"), "B": Node("B"), "C": Node("C")}

        result = handle_divergent_tree_children(
            0, smallest_tree, output, logic_lines, lookup_table
        )

        self.assertEqual(result, output)

    def test_handle_divergent_tree_children_with_similarity(self):
        """Test case where tree similarity is greater than 0"""

        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
            "D": Node("D"),
            "E": Node("E"),
        }
        logic_table = {
            "XOR": Node(
                data="XOR",
                incoming=lookup_table["A"],
                outgoing=[
                    lookup_table["B"],
                    lookup_table["C"],
                ],
            )
        }
        lookup_table["A"].outgoing_logic = [logic_table["XOR"]]
        lookup_table["B"].incoming_logic = [logic_table["XOR"]]
        lookup_table["C"].incoming_logic = [logic_table["XOR"]]
        lookup_table["B"].outgoing = [lookup_table["E"]]
        lookup_table["C"].outgoing = [lookup_table["D"]]
        lookup_table["D"].outgoing = [lookup_table["E"]]

        output = [lookup_table["A"]]

        logic_lines = {
            "XOR": {
                "start": "XOR_START",
                "middle": "XOR_MIDDLE",
                "end": "XOR_END",
            },
            "SWITCH": {
                "start": "SWITCH_START",
                "middle": ["SWITCH_MIDDLE_1", "SWITCH_MIDDLE_1"],
                "end": "SWITCH_END",
            },
            "LOOP": {"end": "LOOP_END"},
        }
        output = []
        tree = [lookup_table["D"], lookup_table["C"], lookup_table["A"]]

        result = handle_divergent_tree_children(
            2, tree, output, logic_lines, lookup_table
        )

        expected_output = [lookup_table["C"], lookup_table["D"]]

        self.assertEqual(result, expected_output)


class TestCreateContentLogic(unittest.TestCase):
    """Unit tests for the create_content_logic function"""

    def test_create_content_logic_multiple_outgoing_nodes(self):
        """Test case with a node that has multiple outgoing nodes"""
        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
        }

        logic_table = {
            "XOR_1": Node(
                "XOR",
                incoming=[lookup_table["A"]],
                outgoing=[lookup_table["B"], lookup_table["C"]],
            )
        }

        lookup_table["A"].outgoing = [lookup_table["B"], lookup_table["C"]]
        lookup_table["B"].incoming = [lookup_table["A"]]
        lookup_table["C"].incoming = [lookup_table["A"]]

        lookup_table["A"].outgoing_logic = [logic_table["XOR_1"]]
        lookup_table["B"].incoming_logic = [logic_table["XOR_1"]]
        lookup_table["C"].incoming_logic = [logic_table["XOR_1"]]

        output = []
        logic_lines = {
            "LOOP": {"end": "END_LOOP"},
            "XOR": {
                "start": "XOR_START",
                "middle": "XOR_MIDDLE",
                "end": "XOR_END",
            },
        }
        max_depth = 10

        expected_output = ["A", "XOR_START", "B", "XOR_MIDDLE", "C", "XOR_END"]

        result = create_content_logic(
            lookup_table["A"],
            output,
            logic_lines,
            lookup_table,
            max_depth=max_depth,
        )

        for idx, item in enumerate(expected_output):
            self.assertEqual(result[idx].uid, item)

    def test_create_content_logic_in_loop(self):
        """Test case with a node that is in a loop"""
        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
            "D": Node("D"),
        }

        logic_table = {
            "XOR_1": Node(
                "XOR",
                incoming=[lookup_table["A"]],
                outgoing=[lookup_table["B"], lookup_table["C"]],
            )
        }

        lookup_table["A"].outgoing = [lookup_table["B"], lookup_table["C"]]
        lookup_table["A"].outgoing = [lookup_table["D"]]
        lookup_table["B"].incoming = [lookup_table["A"]]
        lookup_table["B"].outgoing = [lookup_table["D"]]
        lookup_table["C"].incoming = [lookup_table["A"]]
        lookup_table["C"].outgoing = [lookup_table["D"]]
        lookup_table["D"].incoming = [lookup_table["B"], lookup_table["C"]]
        lookup_table["D"].outgoing = [lookup_table["A"], Node("END_LOOP")]

        lookup_table["A"].outgoing_logic = [logic_table["XOR_1"]]
        lookup_table["B"].incoming_logic = [logic_table["XOR_1"]]
        lookup_table["C"].incoming_logic = [logic_table["XOR_1"]]

        output = []
        logic_lines = {
            "LOOP": {"start": "START_LOOP", "end": "END_LOOP"},
            "XOR": {
                "start": "XOR_START",
                "middle": "XOR_MIDDLE",
                "end": "XOR_END",
            },
        }
        max_depth = 10

        expected_output = [
            "A",
            "XOR_START",
            "B",
            "XOR_MIDDLE",
            "C",
            "XOR_END",
            "D",
            "END_LOOP",
        ]
        max_depth = 10

        result = create_content_logic(
            lookup_table["A"],
            output,
            logic_lines,
            lookup_table,
            max_depth=max_depth,
        )

        for idx, item in enumerate(expected_output):
            self.assertEqual(result[idx].uid, item)

    def test_create_content_logic_max_depth_reached(self):
        """Test case where the maximum depth is reached"""
        node = Node("A")
        node.outgoing = [Node("B")]
        output = []
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        lookup_table = {}
        max_depth = 0

        result = create_content_logic(
            node, output, logic_lines, lookup_table, max_depth=max_depth
        )

        self.assertEqual(result, [])


class TestCreateContent(unittest.TestCase):
    """Unit tests for the create_content function"""

    def test_create_content_append_first_node(self):
        """Test case where append_first_node is True"""
        node_tree = Node("A")
        node_tree.outgoing = [Node("B")]
        output = []
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        lookup_table = {"B": Node("B")}
        max_depth = 10

        result = create_content(
            node_tree,
            output,
            logic_lines,
            lookup_table,
            append_first_node=True,
            depth=0,
            max_depth=max_depth,
        )

        expected_result = ["A", "B"]

        for idx, item in enumerate(expected_result):
            self.assertEqual(result[idx].uid, item)

    def test_create_content_append_first_node_false(self):
        """Test case where append_first_node is False"""
        node_tree = Node("A")
        node_tree.outgoing = [Node("B")]
        output = []
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        lookup_table = {"B": Node("B")}
        max_depth = 10

        result = create_content(
            node_tree,
            output,
            logic_lines,
            lookup_table,
            append_first_node=False,
            depth=0,
            max_depth=max_depth,
        )

        self.assertEqual(result, [])

    def test_create_content_node_is_loop(self):
        """Test case where the node is a loop"""
        node_tree = Node("A")
        node_tree.outgoing = [
            Node("B", outgoing=[node_tree, Node("END_LOOP")])
        ]
        output = []
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        lookup_table = {"A": node_tree, "B": Node("B")}
        max_depth = 10

        result = create_content(
            node_tree,
            output,
            logic_lines,
            lookup_table,
            append_first_node=True,
            depth=0,
            max_depth=max_depth,
        )

        expected_result = ["A", "B", "END_LOOP"]

        for idx, item in enumerate(expected_result):
            self.assertEqual(result[idx].uid, item)

    def test_create_content_max_depth_reached(self):
        """Test case where the maximum depth is reached"""
        node_tree = Node("A")
        node_tree.outgoing = [Node("B"), Node("C")]
        output = []
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        lookup_table = {"B": Node("B")}
        max_depth = 0

        result = create_content(
            node_tree,
            output,
            logic_lines,
            lookup_table,
            append_first_node=True,
            depth=0,
            max_depth=max_depth,
        )

        self.assertEqual(result, [])


class TestAnalyseNode(unittest.TestCase):
    """Unit tests for the analyse_node function"""

    def test_analyse_node_with_logic(self):
        """Test case where the head node has outgoing logic"""

        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
        }
        logic_table = {
            "XOR": Node(
                data="XOR",
                incoming=lookup_table["A"],
                outgoing=[
                    lookup_table["B"],
                    lookup_table["C"],
                ],
            )
        }
        lookup_table["A"].outgoing_logic = [logic_table["XOR"]]
        lookup_table["B"].incoming_logic = [logic_table["XOR"]]
        lookup_table["C"].incoming_logic = [logic_table["XOR"]]

        logic_lines = {
            "XOR": {
                "start": "XOR_START",
                "middle": "XOR_MIDDLE",
                "end": "XOR_END",
            },
            "SWITCH": {
                "start": "SWITCH_START",
                "middle": ["SWITCH_MIDDLE_1", "SWITCH_MIDDLE_1"],
                "end": "SWITCH_END",
            },
        }
        output = []

        depth = 1
        max_depth = 10

        expected_output = ["A", "XOR_START", "B", "XOR_MIDDLE", "C", "XOR_END"]

        result = analyse_node(
            node_tree=lookup_table["A"],
            output=output,
            logic_lines=logic_lines,
            lookup_table=lookup_table,
            append_first_node=True,
            depth=depth,
            max_depth=max_depth,
        )

        for idx, item in enumerate(expected_output):
            self.assertEqual(result[idx].uid, item)

    def test_analyse_node_with_uid(self):
        """Test case where the head node is a data node"""
        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
            "D": Node("D"),
        }
        logic_table = {
            "XOR": Node(
                data="XOR",
                incoming=lookup_table["B"],
                outgoing=[
                    lookup_table["C"],
                    lookup_table["D"],
                ],
            )
        }
        lookup_table["B"].outgoing_logic = [logic_table["XOR"]]
        lookup_table["C"].incoming_logic = [logic_table["XOR"]]
        lookup_table["D"].incoming_logic = [logic_table["XOR"]]

        lookup_table["A"].outgoing = [lookup_table["B"]]
        lookup_table["B"].outgoing = [lookup_table["C"], lookup_table["D"]]

        lookup_table["B"].incoming = [lookup_table["A"]]
        lookup_table["C"].incoming = [lookup_table["B"]]
        lookup_table["D"].incoming = [lookup_table["B"]]

        logic_lines = {
            "XOR": {
                "start": "XOR_START",
                "middle": "XOR_MIDDLE",
                "end": "XOR_END",
            },
            "SWITCH": {
                "start": "SWITCH_START",
                "middle": ["SWITCH_MIDDLE_1", "SWITCH_MIDDLE_1"],
                "end": "SWITCH_END",
            },
            "LOOP": {"end": "END_LOOP"},
        }
        output = []

        depth = 1
        max_depth = 10

        expected_output = [
            "A",
            "B",
            "XOR_START",
            "C",
            "XOR_MIDDLE",
            "D",
            "XOR_END",
        ]

        result = analyse_node(
            node_tree=lookup_table["A"],
            output=output,
            logic_lines=logic_lines,
            lookup_table=lookup_table,
            append_first_node=True,
            depth=depth,
            max_depth=max_depth,
        )

        for idx, item in enumerate(expected_output):
            self.assertEqual(result[idx].uid, item)

    def test_analyse_node_with_leaf_uid(self):
        """Test case where the node is a leaf uid node"""
        node = Node("A")
        output = []
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        lookup_table = {}
        append_first_node = True
        depth = 0
        max_depth = 10

        result = analyse_node(
            node_tree=node,
            output=output,
            logic_lines=logic_lines,
            lookup_table=lookup_table,
            append_first_node=append_first_node,
            depth=depth,
            max_depth=max_depth,
        )

        self.assertEqual(result, output)

    def test_analyse_node_max_depth_reached(self):
        """Test case where the maximum depth is reached"""
        node = Node("A")
        output = []
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        lookup_table = {}
        append_first_node = True
        depth = 10
        max_depth = 10

        result = analyse_node(
            node_tree=node,
            output=output,
            logic_lines=logic_lines,
            lookup_table=lookup_table,
            append_first_node=append_first_node,
            depth=depth,
            max_depth=max_depth,
        )

        self.assertEqual(result, output)


class TestGetCoordsInNestedDict(unittest.TestCase):
    """Unit tests for the get_coords_in_nested_dict function"""

    def test_item_present(self):
        """Test case where the item is present in the nested dictionary"""
        dictionary = {
            "parent1": {"child1": "item1", "child2": "item2"},
            "parent2": {"child3": "item3", "child4": "item4"},
        }
        item = "item3"

        result = get_coords_in_nested_dict(item, dictionary)

        self.assertEqual(result, "child3")

    def test_item_not_present(self):
        """
        Test case where the item is not present in the nested dictionary
        """
        dictionary = {
            "parent1": {"child1": "item1", "child2": "item2"},
            "parent2": {"child3": "item3", "child4": "item4"},
        }
        item = "item5"

        result = get_coords_in_nested_dict(item, dictionary)

        self.assertIsNone(result)

    def test_empty_dictionary(self):
        """Test case where the nested dictionary is empty"""
        dictionary = {}
        item = "item1"

        result = get_coords_in_nested_dict(item, dictionary)

        self.assertIsNone(result)

    def test_empty_nested_dictionary(self):
        """Test case where the nested dictionary is empty"""
        dictionary = {"parent1": {}, "parent2": {}}
        item = "item1"

        result = get_coords_in_nested_dict(item, dictionary)

        self.assertIsNone(result)


class TestFormatOutput(unittest.TestCase):
    """Unit tests for the format_output function"""

    def test_format_output_no_event_reference(self):
        """Test case where there is no event reference"""
        input = [Node("A"), Node("B"), Node("C")]
        logic_lines = {
            "SWITCH": {"start": "START", "middle": ["MIDDLE"], "end": "END"}
        }
        tab_chars = "\t"
        tab_num = 2
        event_reference = {}

        expected_output = ["\t\tA", "\t\tB", "\t\tC"]

        result = format_output(
            input, logic_lines, tab_chars, tab_num, event_reference
        )

        self.assertEqual(result, expected_output)

    def test_format_output_with_event_reference(self):
        """Test case where there is an event reference"""
        input = [Node("A"), Node("B"), Node("C")]
        logic_lines = {
            "SWITCH": {"start": "START", "middle": ["MIDDLE"], "end": "END"}
        }
        tab_chars = "\t"
        tab_num = 2
        event_reference = {"B": "EVENT1"}

        expected_output = ["\t\tA", "\t\t:EVENT1;", "\t\tC"]

        result = format_output(
            input, logic_lines, tab_chars, tab_num, event_reference
        )

        self.assertEqual(result, expected_output)

    def test_format_output_with_switch_start(self):
        """Test case where there is a switch start line"""
        input = [Node("START"), Node("A"), Node("B"), Node("C")]
        logic_lines = {
            "SWITCH": {"start": "START", "middle": ["MIDDLE"], "end": "END"}
        }
        tab_chars = "\t"
        tab_num = 2
        event_reference = {}

        expected_output = ["\t\tSTART", "\t\t\t\tA", "\t\t\t\tB", "\t\t\t\tC"]

        result = format_output(
            input, logic_lines, tab_chars, tab_num, event_reference
        )

        self.assertEqual(result, expected_output)

    def test_format_output_with_switch_middle(self):
        """Test case where there is a switch middle line"""
        input = [Node("A"), Node("MIDDLE"), Node("B"), Node("C")]
        logic_lines = {
            "SWITCH": {"start": "START", "middle": ["MIDDLE"], "end": "END"}
        }
        tab_chars = "\t"
        tab_num = 2
        event_reference = {}

        expected_output = ["\t\tA", "\tMIDDLE", "\t\tB", "\t\tC"]

        result = format_output(
            input, logic_lines, tab_chars, tab_num, event_reference
        )

        self.assertEqual(result, expected_output)

    def test_format_output_with_switch_end(self):
        """Test case where there is a switch end line"""
        input = [Node("A"), Node("B"), Node("END")]
        logic_lines = {
            "SWITCH": {"start": "START", "middle": ["MIDDLE"], "end": "END"}
        }
        tab_chars = "\t"
        tab_num = 2
        event_reference = {}

        expected_output = ["\t\tA", "\t\tB", "END"]

        result = format_output(
            input, logic_lines, tab_chars, tab_num, event_reference
        )

        self.assertEqual(result, expected_output)

    def test_format_output_with_switch_middle_in_end(self):
        """Test case where there is a switch middle line in the end line"""
        input = [Node("A"), Node("B"), Node("MIDDLE"), Node("END")]
        logic_lines = {
            "SWITCH": {"start": "START", "middle": ["MIDDLE"], "end": "END"}
        }
        tab_chars = "\t"
        tab_num = 2
        event_reference = {}

        expected_output = ["\t\tA", "\t\tB", "\tMIDDLE", "END"]

        result = format_output(
            input, logic_lines, tab_chars, tab_num, event_reference
        )

        self.assertEqual(result, expected_output)

    def test_format_output_with_switch_middle_in_middle(self):
        """
        Test case where there is a switch middle line in the middle line
        """
        input = [
            Node("A"),
            Node("MIDDLE"),
            Node("B"),
            Node("MIDDLE"),
            Node("C"),
        ]
        logic_lines = {
            "SWITCH": {"start": "START", "middle": ["MIDDLE"], "end": "END"}
        }
        tab_chars = "\t"
        tab_num = 2
        event_reference = {}

        expected_output = ["\t\tA", "\tMIDDLE", "\t\tB", "\tMIDDLE", "\t\tC"]

        result = format_output(
            input, logic_lines, tab_chars, tab_num, event_reference
        )

        self.assertEqual(result, expected_output)


class TestFindNearestExtantAncestor(unittest.TestCase):
    """Unit tests for the find_nearest_extant_ancestor function"""

    def test_find_nearest_extant_ancestor_node_in_uid_list(self):
        """Test case where the node is in the uid_list"""
        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
            "D": Node("D"),
        }
        lookup_table["A"].outgoing = [lookup_table["B"]]
        lookup_table["B"].outgoing = [lookup_table["C"]]
        lookup_table["C"].outgoing = [lookup_table["D"]]

        lookup_table["B"].incoming = [lookup_table["A"]]
        lookup_table["C"].incoming = [lookup_table["B"]]
        lookup_table["D"].incoming = [lookup_table["C"]]

        uid_list = [
            lookup_table["A"],
            lookup_table["B"],
            lookup_table["C"],
            lookup_table["D"],
        ]
        node = lookup_table["D"]

        result = find_nearest_extant_ancestor(uid_list, node)

        self.assertEqual(result, node)

    def test_find_nearest_extant_ancestor_node_not_in_uid_list(self):
        """Test case where the node is not in the uid_list"""
        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
            "D": Node("D"),
        }
        lookup_table["A"].outgoing = [lookup_table["B"]]
        lookup_table["B"].outgoing = [lookup_table["C"]]
        lookup_table["C"].outgoing = [lookup_table["D"]]

        lookup_table["B"].incoming = [lookup_table["A"]]
        lookup_table["C"].incoming = [lookup_table["B"]]
        lookup_table["D"].incoming = [lookup_table["C"]]

        uid_list = [lookup_table["A"], lookup_table["B"], lookup_table["C"]]
        node = lookup_table["D"]
        result = find_nearest_extant_ancestor(uid_list, node)

        self.assertEqual(result, node.incoming[0])

    def test_find_nearest_extant_ancestor_max_depth_reached(self):
        """Test case where the maximum depth is reached"""
        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
            "D": Node("D"),
        }
        lookup_table["A"].outgoing = [lookup_table["B"]]
        lookup_table["B"].outgoing = [lookup_table["C"]]
        lookup_table["C"].outgoing = [lookup_table["D"]]

        lookup_table["B"].incoming = [lookup_table["A"]]
        lookup_table["C"].incoming = [lookup_table["B"]]
        lookup_table["D"].incoming = [lookup_table["C"]]

        uid_list = [lookup_table["A"], lookup_table["B"], lookup_table["C"]]
        node = lookup_table["D"]

        result = find_nearest_extant_ancestor(uid_list, node, max_depth=0)

        self.assertEqual(result, node)


class TestInsertItemUsingPropertyKey(unittest.TestCase):
    """Unit tests for the insert_item_using_property_key function"""

    def test_insert_item_using_property_key_incoming(self):
        """Test case for inserting a node based on the incoming property"""
        uid_list = [Node("A"), Node("B"), Node("C")]
        node = Node("D", incoming=[uid_list[2]])
        logic_lines = {}
        property_key = "incoming"
        insert_before_item = False

        result = insert_item_using_property_key(
            uid_list, node, logic_lines, property_key, insert_before_item
        )

        expected = [uid_list[0], uid_list[1], uid_list[2], node]
        self.assertEqual(result, expected)

    def test_insert_item_using_property_key_outgoing(self):
        """Test case for inserting a node based on the outgoing property"""
        uid_list = [Node("A"), Node("B"), Node("D")]
        node = Node("C", outgoing=[uid_list[2]], incoming=[uid_list[1]])
        property_key = "outgoing"
        insert_before_item = True
        logic_lines = {}

        result = insert_item_using_property_key(
            uid_list, node, logic_lines, property_key, insert_before_item
        )

        expected = [uid_list[0], uid_list[1], node, uid_list[-1]]
        self.assertEqual(result, expected)

    def test_insert_item_using_property_key_incoming_logic(self):
        """
        Test case for inserting a node based on the incoming_logic property
        """
        uid_list = [Node("A"), Node("B"), Node("C")]
        uid_list.append(Node("XOR", incoming=uid_list[2]))
        node = Node("D", incoming_logic=[uid_list[-1]], incoming=[uid_list[3]])
        uid_list[-1].outgoing = node
        logic_lines = {"XOR": {"start": "XOR"}}
        property_key = "incoming_logic"
        insert_before_item = False

        result = insert_item_using_property_key(
            uid_list, node, logic_lines, property_key, insert_before_item
        )

        expected = [uid_list[0], uid_list[1], uid_list[2], uid_list[3], node]
        self.assertEqual(result, expected)

    def test_insert_item_using_property_key_outgoing_logic(self):
        """
        Test case for inserting a node based on the outgoing_logic property
        """
        uid_list = [Node("A"), Node("B"), Node("XOR"), Node("D")]
        node = Node("C", outgoing_logic=[uid_list[2]])
        node.incoming = [uid_list[-1]]
        uid_list[2].incoming = [node]
        uid_list[2].outgoing = [uid_list[3]]
        uid_list[3].incoming = [uid_list[1]]
        property_key = "outgoing_logic"
        insert_before_item = False
        logic_lines = {"XOR": {"start": "XOR"}}

        result = insert_item_using_property_key(
            uid_list, node, logic_lines, property_key, insert_before_item
        )

        expected = [uid_list[0], uid_list[1], uid_list[2], node, uid_list[-1]]
        self.assertEqual(result, expected)

    def test_insert_item_using_property_key_invalid_property_key(self):
        """Test case for inserting a node with an invalid property key"""
        uid_list = [Node("A"), Node("B"), Node("C")]
        node = Node("D")
        property_key = "invalid_key"
        insert_before_item = False

        with self.assertRaises(Exception):
            insert_item_using_property_key(
                uid_list, node, property_key, insert_before_item
            )

    def test_insert_item_using_property_key_insert_before_item(self):
        """Test case for inserting a node before the nearest relative"""
        uid_list = [Node("A"), Node("B"), Node("D")]
        node = Node("C", incoming=[uid_list[-1]])
        property_key = "incoming"
        insert_before_item = True
        logic_lines = {}

        result = insert_item_using_property_key(
            uid_list, node, logic_lines, property_key, insert_before_item
        )

        expected = [uid_list[0], uid_list[1], node, uid_list[3]]
        self.assertEqual(result, expected)


class TestInsertMissingNodes(unittest.TestCase):
    """Unit tests for the insert_missing_nodes function"""

    def test_insert_missing_nodes_no_missing_nodes(self):
        """Test case with no missing nodes"""
        uid_list = ["A", "B", "C"]
        missing_nodes = []
        logic_lines = {}

        result = insert_missing_nodes(uid_list, missing_nodes, logic_lines)

        self.assertEqual(result, uid_list)

    def test_insert_missing_nodes_missing_nodes_at_beginning(self):
        """Test case with missing nodes at the beginning of the uid list"""
        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
            "D": Node("D"),
            "E": Node("E"),
            "F": Node("F"),
        }
        lookup_table["A"].outgoing = [lookup_table["B"]]
        lookup_table["B"].outgoing = [lookup_table["C"]]
        lookup_table["C"].outgoing = [lookup_table["D"]]
        lookup_table["D"].outgoing = [lookup_table["E"]]
        lookup_table["E"].outgoing = [lookup_table["F"]]

        lookup_table["B"].incoming = [lookup_table["A"]]
        lookup_table["C"].incoming = [lookup_table["B"]]
        lookup_table["D"].incoming = [lookup_table["C"]]
        lookup_table["E"].incoming = [lookup_table["D"]]
        lookup_table["F"].incoming = [lookup_table["E"]]

        uid_list = [lookup_table["D"], lookup_table["E"], lookup_table["F"]]
        missing_nodes = [
            lookup_table["A"],
            lookup_table["B"],
            lookup_table["C"],
        ]

        logic_lines = {}

        result = insert_missing_nodes(uid_list, missing_nodes, logic_lines)

        expected_result = [
            lookup_table["A"],
            lookup_table["B"],
            lookup_table["C"],
            lookup_table["D"],
            lookup_table["E"],
            lookup_table["F"],
        ]
        self.assertEqual(result, expected_result)

    def test_insert_missing_nodes_missing_nodes_at_end(self):
        """Test case with missing nodes at the end of the uid list"""
        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
            "D": Node("D"),
            "E": Node("E"),
            "F": Node("F"),
        }
        lookup_table["A"].outgoing = [lookup_table["B"]]
        lookup_table["B"].outgoing = [lookup_table["C"]]
        lookup_table["C"].outgoing = [lookup_table["D"]]
        lookup_table["D"].outgoing = [lookup_table["E"]]
        lookup_table["E"].outgoing = [lookup_table["F"]]

        lookup_table["B"].incoming = [lookup_table["A"]]
        lookup_table["C"].incoming = [lookup_table["B"]]
        lookup_table["D"].incoming = [lookup_table["C"]]
        lookup_table["E"].incoming = [lookup_table["D"]]
        lookup_table["F"].incoming = [lookup_table["E"]]

        uid_list = [lookup_table["A"], lookup_table["B"], lookup_table["C"]]
        missing_nodes = [
            lookup_table["D"],
            lookup_table["E"],
            lookup_table["F"],
        ]
        logic_lines = {}

        result = insert_missing_nodes(uid_list, missing_nodes, logic_lines)

        expected_result = [
            lookup_table["A"],
            lookup_table["B"],
            lookup_table["C"],
            lookup_table["D"],
            lookup_table["E"],
            lookup_table["F"],
        ]
        self.assertEqual(result, expected_result)

    def test_insert_missing_nodes_missing_nodes_in_middle(self):
        """Test case with missing nodes in the middle of the uid list"""
        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
            "D": Node("D"),
            "E": Node("E"),
            "F": Node("F"),
        }
        lookup_table["A"].outgoing = [lookup_table["B"]]
        lookup_table["B"].outgoing = [lookup_table["C"]]
        lookup_table["C"].outgoing = [lookup_table["D"]]
        lookup_table["D"].outgoing = [lookup_table["E"]]
        lookup_table["E"].outgoing = [lookup_table["F"]]

        lookup_table["B"].incoming = [lookup_table["A"]]
        lookup_table["C"].incoming = [lookup_table["B"]]
        lookup_table["D"].incoming = [lookup_table["C"]]
        lookup_table["E"].incoming = [lookup_table["D"]]
        lookup_table["F"].incoming = [lookup_table["E"]]

        uid_list = [lookup_table["A"], lookup_table["B"], lookup_table["F"]]
        missing_nodes = [
            lookup_table["C"],
            lookup_table["D"],
            lookup_table["E"],
        ]
        logic_lines = {}

        result = insert_missing_nodes(uid_list, missing_nodes, logic_lines)

        expected_result = [
            lookup_table["A"],
            lookup_table["B"],
            lookup_table["C"],
            lookup_table["D"],
            lookup_table["E"],
            lookup_table["F"],
        ]
        self.assertEqual(result, expected_result)


class TestAlterNodeTreeToContainLogicNodes(unittest.TestCase):
    """
    Test case class for the alter_node_tree_to_contain_logic_nodes function.
    """

    def test_alter_node_tree_to_contain_logic_nodes_no_logic(self):
        """
        Test case to verify the behavior of
            alter_node_tree_to_contain_logic_nodes when there is no logic to be
            added.

        """
        logic_table = {}
        lookup_table = {"A": Node("A")}
        result = alter_node_tree_to_contain_logic_nodes(
            lookup_table, logic_table
        )

        self.assertEqual(lookup_table, result)

    def test_alter_node_tree_to_contain_logic_nodes_no_nodes(self):
        """
        Test case to verify the behavior of the
            alter_node_tree_to_contain_logic_nodes method when no logic nodes
            are provided
        """
        logic_table = {
            "XOR_1": Node(
                "XOR", incoming=[Node("A")], outgoing=[Node("B"), Node("C")]
            )
        }
        lookup_table = {}
        result = alter_node_tree_to_contain_logic_nodes(
            lookup_table, logic_table
        )

        self.assertEqual(lookup_table, result)

    def test_alter_node_tree_to_contain_logic_nodes_one_logic_node(self):
        """
        Test case for the alter_node_tree_to_contain_logic_nodes method when
            only one logic node is provided
        """
        lookup_table = {"A": Node("A"), "B": Node("B"), "C": Node("C")}
        lookup_table["A"].outgoing = [lookup_table["B"], lookup_table["C"]]
        lookup_table["B"].incoming = [lookup_table["A"]]
        lookup_table["C"].incoming = [lookup_table["A"]]

        logic_table = {
            "XOR_1": Node(
                "XOR",
                incoming=[lookup_table["A"]],
                outgoing=[lookup_table["B"], lookup_table["C"]],
            )
        }
        result = alter_node_tree_to_contain_logic_nodes(
            lookup_table, logic_table
        )

        expected_results = {
            "A": {"incoming_logic": [], "outgoing_logic": ["B", "C"]},
            "B": {"incoming_logic": ["A"], "outgoing_logic": []},
            "C": {"incoming_logic": ["A"], "outgoing_logic": []},
        }

        for expected_result in expected_results:
            if len(expected_results[expected_result]["incoming_logic"]) > 0:
                for idx, item in enumerate(
                    expected_results[expected_result]["incoming_logic"]
                ):
                    self.assertEqual(
                        item, result[expected_result].incoming[idx].uid
                    )

            if len(expected_results[expected_result]["outgoing_logic"]) > 0:
                for idx, item in enumerate(
                    expected_results[expected_result]["outgoing_logic"]
                ):
                    self.assertEqual(
                        item, result[expected_result].outgoing[idx].uid
                    )


class TestConvertNodesToPuml(unittest.TestCase):
    """End-to-end testing for the puml pipeline"""

    def test_convert_nodes_to_puml_no_branching(self):
        """
        Test case for generating a PlantUML diagram using the
        a simple node tree with no branches
        """

        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
        }

        lookup_table["A"].outgoing = [lookup_table["B"]]
        lookup_table["B"].outgoing = [lookup_table["C"]]

        lookup_table["B"].incoming = [lookup_table["A"]]
        lookup_table["C"].incoming = [lookup_table["B"]]

        event_reference = {
            "A": "A",
            "B": "B",
            "C": "C",
        }

        head_node = lookup_table[list(lookup_table.keys())[0]]

        puml_name = "No branches"

        puml_full = convert_nodes_to_puml(
            lookup_table, head_node, event_reference, puml_name
        )

        self.assertEqual(
            [
                "@startuml",
                'partition "No branches" {',
                '    group "No branches"',
                "        :A;",
                "        :B;",
                "        :C;",
                "    end group",
                "}",
                "@enduml",
            ],
            puml_full,
        )

    def test_convert_nodes_to_puml_one_XOR(self):
        """
        Test case for generating a PlantUML diagram using the
        a simple node tree with no branches
        """

        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
        }

        lookup_table["A"].outgoing = [lookup_table["B"]]

        lookup_table["B"].incoming = [lookup_table["A"]]
        lookup_table["C"].incoming = [lookup_table["B"]]

        event_reference = {
            "A": "A",
            "B": "B",
            "C": "C",
        }

        xor_node = Node(
            "XOR",
            incoming=lookup_table["A"],
            outgoing=[lookup_table["B"], lookup_table["C"]],
        )

        lookup_table["A"].outgoing_logic = [xor_node]
        lookup_table["B"].incoming_logic = [xor_node]
        lookup_table["C"].incoming_logic = [xor_node]

        head_node = lookup_table[list(lookup_table.keys())[0]]

        puml_name = "One XOR"

        puml_full = convert_nodes_to_puml(
            lookup_table, head_node, event_reference, puml_name
        )

        self.assertEqual(
            [
                "@startuml",
                'partition "One XOR" {',
                '    group "One XOR"',
                "        :A;",
                "        if (XOR) then (true)",
                "            :B;",
                "        else (false)",
                "            :C;",
                "        endif",
                "    end group",
                "}",
                "@enduml",
            ],
            puml_full,
        )

    def test_convert_nodes_to_puml_one_LOOP(self):
        """
        Test case for generating a PlantUML diagram using the
        a simple node tree with no branches
        """

        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
            "D": Node("D"),
        }

        lookup_table["A"].outgoing = [lookup_table["B"]]
        lookup_table["B"].outgoing = [lookup_table["C"]]
        lookup_table["C"].outgoing = [
            Node("repeat while (unconstrained)", incoming=lookup_table["C"]),
            lookup_table["B"],
            lookup_table["D"],
        ]

        lookup_table["B"].incoming = [lookup_table["A"], lookup_table["C"]]
        lookup_table["C"].incoming = [lookup_table["B"]]
        lookup_table["D"].incoming = [lookup_table["C"]]

        event_reference = {
            "A": "A",
            "B": "B",
            "C": "C",
            "D": "D",
        }

        head_node = lookup_table[list(lookup_table.keys())[0]]

        puml_name = "One XOR"

        puml_full = convert_nodes_to_puml(
            lookup_table, head_node, event_reference, puml_name
        )

        self.assertEqual(
            [
                "@startuml",
                'partition "One XOR" {',
                '    group "One XOR"',
                "        :A;",
                "        repeat",
                "            :B;",
                "            :C;",
                "        repeat while (unconstrained)",
                "        :D;",
                "    end group",
                "}",
                "@enduml",
            ],
            puml_full,
        )

    def test_convert_nodes_to_puml_one_AND(self):
        """
        Test case for generating a PlantUML diagram using the
        a simple node tree with no branches
        """

        lookup_table = {
            "A": Node("A"),
            "B": Node("B"),
            "C": Node("C"),
        }

        lookup_table["A"].outgoing = [lookup_table["B"]]

        lookup_table["B"].incoming = [lookup_table["A"]]
        lookup_table["C"].incoming = [lookup_table["B"]]

        event_reference = {
            "A": "A",
            "B": "B",
            "C": "C",
        }

        xor_node = Node(
            "AND",
            incoming=lookup_table["A"],
            outgoing=[lookup_table["B"], lookup_table["C"]],
        )

        lookup_table["A"].outgoing_logic = [xor_node]
        lookup_table["B"].incoming_logic = [xor_node]
        lookup_table["C"].incoming_logic = [xor_node]

        head_node = lookup_table[list(lookup_table.keys())[0]]

        puml_name = "One XOR"

        puml_full = convert_nodes_to_puml(
            lookup_table, head_node, event_reference, puml_name
        )

        self.assertEqual(
            [
                "@startuml",
                'partition "One XOR" {',
                '    group "One XOR"',
                "        :A;",
                "        fork",
                "            :B;",
                "        fork again",
                "            :C;",
                "        end fork",
                "    end group",
                "}",
                "@enduml",
            ],
            puml_full,
        )


class TestEndToEnd(unittest.TestCase):
    """End-to-end testing for the puml pipeline"""

    def test_simple_test(self):
        """
        Test case for generating a PlantUML diagram using the
        simple_test.puml file as a base for event generation
        """

        puml_name = "simple_test"
        print_output = True

        graph_list, event_references = get_puml_data_and_analyse_with_jalergia(
            puml_name, print_output
        )
        lookup_tables, node_trees, event_references = convert_to_nodes(
            graph_list, event_references, print_output
        )

        lookup_table = lookup_tables[0]
        event_reference = event_references[0]
        head_node = node_trees[0]

        logic_table = {
            "NODE_XOR_1": Node(
                uid="XOR",
                incoming=[lookup_table["q0"]],
                outgoing=[lookup_table["q1"], lookup_table["q2"]],
            )
        }

        lookup_table = alter_node_tree_to_contain_logic_nodes(
            lookup_table, logic_table
        )

        puml_full = convert_nodes_to_puml(
            lookup_table, head_node, event_reference, puml_name
        )

        self.assertEqual(
            [
                "@startuml",
                'partition "simple_test" {',
                '    group "simple_test"',
                "        :A;",
                "        if (XOR) then (true)",
                "            :B;",
                "            :C;",
                "        else (false)",
                "            :D;",
                "        endif",
                "    end group",
                "}",
                "@enduml",
            ],
            puml_full,
        )

    def test_sequence_xor_fork(self):
        """
        Test case for generating a PlantUML diagram using the
        sequence_xor_fork.puml file as a base for event generation
        """
        puml_name = "sequence_xor_fork"
        print_output = True

        graph_list, event_references = get_puml_data_and_analyse_with_jalergia(
            puml_name, print_output
        )
        lookup_tables, node_trees, event_references = convert_to_nodes(
            graph_list, event_references, print_output
        )

        lookup_table = lookup_tables[0]
        event_reference = event_references[0]
        head_node = node_trees[0]

        logic_table = {
            "NODE_XOR_1": Node(
                uid="XOR",
                incoming=[lookup_table["q1"]],
                outgoing=[
                    lookup_table["q2"],
                    lookup_table["q3"],
                    lookup_table["q4"],
                ],
            )
        }

        lookup_table = alter_node_tree_to_contain_logic_nodes(
            lookup_table, logic_table
        )

        puml_full = convert_nodes_to_puml(
            lookup_table, head_node, event_reference, puml_name
        )

        self.assertEqual(
            [
                "@startuml",
                'partition "sequence_xor_fork" {',
                '    group "sequence_xor_fork"',
                "        :A;",
                "        :B;",
                "        switch (XOR)",
                '            case ("1")',
                "                :C;",
                '            case ("2")',
                "                :D;",
                '            case ("3")',
                "                :E;",
                "        endswitch",
                "        :F;",
                "    end group",
                "}",
                "@enduml",
            ],
            puml_full,
        )

    def test_loop_XORFork_a(self):
        """
        Test case for generating a PlantUML diagram using the
        loop_XORFork_a.puml file as a base for event generation
        """
        puml_name = "loop_XORFork_a"
        print_output = True

        graph_list, event_references = get_puml_data_and_analyse_with_jalergia(
            puml_name, print_output
        )
        lookup_tables, node_trees, event_references = convert_to_nodes(
            graph_list, event_references, print_output
        )

        lookup_table = lookup_tables[0]
        event_reference = event_references[0]
        head_node = node_trees[0]

        logic_table = {
            "NODE_XOR_1": Node(
                uid="XOR",
                incoming=[lookup_table["q1"]],
                outgoing=[lookup_table["q2"], lookup_table["q3"]],
            )
        }

        lookup_table = alter_node_tree_to_contain_logic_nodes(
            lookup_table, logic_table
        )

        puml_full = convert_nodes_to_puml(
            lookup_table, head_node, event_reference, puml_name
        )

        self.assertEqual(
            [
                "@startuml",
                'partition "loop_XORFork_a" {',
                '    group "loop_XORFork_a"',
                "        :A;",
                "        repeat",
                "            :B;",
                "            if (XOR) then (true)",
                "                :C;",
                "            else (false)",
                "                :D;",
                "                :E;",
                "            endif",
                "            :F;",
                "        repeat while (unconstrained)",
                "        :G;",
                "    end group",
                "}",
                "@enduml",
            ],
            puml_full,
        )

    def test_complicated_test(self):
        """
        Test case for generating a PlantUML diagram using the
        complicated_test.puml file as a base for event generation
        """
        puml_name = "complicated_test"
        print_output = True

        graph_list, event_references = get_puml_data_and_analyse_with_jalergia(
            puml_name, print_output
        )
        lookup_tables, node_trees, event_references = convert_to_nodes(
            graph_list, event_references, print_output
        )

        lookup_table = lookup_tables[0]
        event_reference = event_references[0]
        head_node = node_trees[0]

        logic_table = {
            "NODE_XOR_1": Node(
                uid="XOR",
                incoming=[lookup_table["q0"]],
                outgoing=[lookup_table["q1"], lookup_table["q2"]],
            ),
            "NODE_XOR_2": Node(
                uid="XOR",
                incoming=[lookup_table["q3"]],
                outgoing=[lookup_table["q6"], lookup_table["q7"]],
            ),
            "NODE_XOR_3": Node(
                uid="XOR",
                incoming=[lookup_table["q2"]],
                outgoing=[lookup_table["q4"], lookup_table["q5"]],
            ),
            "NODE_XOR_4": Node(
                uid="XOR",
                incoming=[lookup_table["q4"]],
                outgoing=[lookup_table["q8"], lookup_table["q9"]],
            ),
        }

        lookup_table = alter_node_tree_to_contain_logic_nodes(
            lookup_table, logic_table
        )

        puml_full = convert_nodes_to_puml(
            lookup_table, head_node, event_reference, puml_name
        )

        self.assertEqual(
            [
                "@startuml",
                'partition "complicated_test" {',
                '    group "complicated_test"',
                "        :A;",
                "        if (XOR) then (true)",
                "            :B;",
                "            :C;",
                "            if (XOR) then (true)",
                "                :D;",
                "            else (false)",
                "                :E;",
                "            endif",
                "        else (false)",
                "            :F;",
                "            if (XOR) then (true)",
                "                :G;",
                "                if (XOR) then (true)",
                "                    :H;",
                "                else (false)",
                "                    :I;",
                "                endif",
                "            else (false)",
                "                :J;",
                "            endif",
                "        endif",
                "        :K;",
                "    end group",
                "}",
                "@enduml",
            ],
            puml_full,
        )

    def test_branching_loop_end_test(self):
        """
        Test case for generating a PlantUML diagram using the
        branching_loop_end_test.puml file as a base for event generation
        """
        puml_name = "branching_loop_end_test"
        print_output = True

        graph_list, event_references = get_puml_data_and_analyse_with_jalergia(
            puml_name, print_output
        )
        lookup_tables, node_trees, event_references = convert_to_nodes(
            graph_list, event_references, print_output
        )

        lookup_table = lookup_tables[0]
        event_reference = event_references[0]
        head_node = node_trees[0]

        logic_table = {
            "NODE_XOR_1": Node(
                uid="XOR",
                incoming=[lookup_table["q1"]],
                outgoing=[lookup_table["q2"], lookup_table["q3"]],
            )
        }

        lookup_table = alter_node_tree_to_contain_logic_nodes(
            lookup_table, logic_table
        )

        puml_full = convert_nodes_to_puml(
            lookup_table, head_node, event_reference, puml_name
        )

        self.assertEqual(
            [
                "@startuml",
                'partition "branching_loop_end_test" {',
                '    group "branching_loop_end_test"',
                "        :A;",
                "        repeat",
                "            :B;",
                "            if (XOR) then (true)",
                "                :C;",
                "            else (false)",
                "                :D;",
                "            repeat while (unconstrained)",
                "            :E;",
                "        endif",
                "        :F;",
                "    end group",
                "}",
                "@enduml",
            ],
            puml_full,
        )


if __name__ == "__main__":
    unittest.main()
