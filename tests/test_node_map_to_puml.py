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
    handle_immediate_children,
    handle_divergent_tree_children,
    create_content_logic,
    create_content,
    analyse_node,
)


class TestIsInLoop(unittest.TestCase):
    def test_is_in_loop_target_in_loop(self):
        # Test case where the target node is in a loop
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
        # Test case where the target node is not in a loop

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
        # Test case where the maximum depth is reached
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
    def test_drill_down_tree_single_node(self):
        # Test case with a single node
        node = Node("A")
        lookup_table = {}
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        max_depth = 10

        result = drill_down_tree(node, lookup_table, logic_lines, max_depth)

        self.assertEqual(result, node)

    def test_drill_down_tree_no_outgoing_nodes(self):
        # Test case with a node that has no outgoing nodes
        node = Node("A")
        lookup_table = {}
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        max_depth = 10

        result = drill_down_tree(node, lookup_table, logic_lines, max_depth)

        self.assertEqual(result, node)

    def test_drill_down_tree_single_outgoing_node(self):
        # Test case with a node that has a single outgoing node
        node = Node("A")
        node.outgoing = [Node("B")]
        lookup_table = {}
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        max_depth = 10

        result = drill_down_tree(node, lookup_table, logic_lines, max_depth)

        self.assertEqual(result, node.outgoing[0])

    def test_drill_down_tree_multiple_outgoing_nodes(self):
        # Test case with a node that has multiple outgoing nodes
        node = Node("A")
        node.outgoing = [Node("B"), Node("C")]
        lookup_table = {}
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        max_depth = 10

        result = drill_down_tree(node, lookup_table, logic_lines, max_depth)

        self.assertEqual(result, node)

    def test_drill_down_tree_allowed_nodes(self):
        # Test case with a node that has multiple outgoing nodes, but only one is allowed
        node = Node("A")
        node.outgoing = [Node("B"), Node("C")]
        lookup_table = {"B": True}
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        max_depth = 10

        result = drill_down_tree(node, lookup_table, logic_lines, max_depth)

        self.assertEqual(result, node.outgoing[0])

    def test_drill_down_tree_in_loop(self):
        # Test case with a node that is in a loop

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
        # Test case where the maximum depth is reached
        node = Node("A")
        node.outgoing = [Node("B")]
        lookup_table = {}
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        max_depth = 0

        result = drill_down_tree(node, lookup_table, logic_lines, max_depth)

        self.assertEqual(result, node)


class TestGetReverseNodeTree(unittest.TestCase):
    def test_get_reverse_node_tree_single_node(self):
        # Test case with a single node
        node = Node("A")
        lookup_table = {}
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        max_depth = 10

        result = get_reverse_node_tree(
            node, lookup_table, logic_lines, max_depth
        )

        self.assertEqual(result, [])

    def test_get_reverse_node_tree_no_outgoing_nodes(self):
        # Test case with a node that has no outgoing nodes
        node = Node("A")
        lookup_table = {}
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        max_depth = 10

        result = get_reverse_node_tree(
            node, lookup_table, logic_lines, max_depth
        )

        self.assertEqual(result, [])

    def test_get_reverse_node_tree_single_outgoing_node(self):
        # Test case with a node that has a single outgoing node
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
        # Test case with a node that has multiple outgoing nodes
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
        # Test case with a node that has multiple outgoing nodes, but only one
        #   is in the lookup table
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
        # Test case with a node that is in a loop

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
        # Test case where the maximum depth is reached
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
    def test_get_tree_similarity_all_trees_converge(self):
        # Test case where all trees in reverse_node_trees converge

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
        # Test case where not all trees in reverse_node_trees converge

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
        # Test case where reverse_node_trees contains an empty tree

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
    def test_append_logic_middle_or_end_middle(self):
        # Test case for appending logic in the middle of a branch

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
        # Test case for appending logic at the end of a branch

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
        # Test case for appending logic at the end of a branch with a SWITCH
        #   node
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
    def test_append_logic_start_regular_node(self):
        # Test case for appending logic start node for a regular node

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
        # Test case for appending logic start node for a switch node

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
    def test_handle_loop_start_no_loop_start(self):
        # Test case where there is no loop start detected
        output = []
        node_tree = Node("A")
        logic_lines = {"LOOP": {"start": "START_LOOP", "end": "END_LOOP"}}

        result = handle_loop_start(output, node_tree, logic_lines)

        self.assertEqual(result, [])

    def test_handle_loop_start_with_loop_start(self):
        # Test case where there is a loop start detected
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
        # Test case where there are multiple possible descendant incoming nodes
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
        # Test case where there are no possible descendant incoming nodes
        output = []
        node_tree = Node("A")
        node_tree.incoming = [Node("B")]
        logic_lines = {"LOOP": {"start": "START_LOOP", "end": "END_LOOP"}}

        result = handle_loop_start(output, node_tree, logic_lines)

        self.assertEqual(result, [])


class TestGetReverseNodeTreeDict(unittest.TestCase):
    def test_get_reverse_node_tree_dict_with_reverse_node_trees(self):
        # Test case with reverse node trees
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


class TestHandleImmediateChildren(unittest.TestCase):
    def test_handle_immediate_children_tree_similarity_greater_than_zero(self):
        # Test case where tree_similarity is greater than zero
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
        # Test case where tree_similarity is zero
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
        # Test case where the maximum depth is reached
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
    def test_handle_divergent_tree_children_no_similarity(self):
        # Test case where tree similarity is 0
        smallest_tree = [Node("A"), Node("B"), Node("C")]
        output = "output"
        logic_lines = {"LOOP": {"end": "END_LOOP"}}
        lookup_table = {"A": Node("A"), "B": Node("B"), "C": Node("C")}

        result = handle_divergent_tree_children(
            0, smallest_tree, output, logic_lines, lookup_table
        )

        self.assertEqual(result, output)

    def test_handle_divergent_tree_children_with_similarity(self):
        # Test case where tree similarity is greater than 0

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
    def test_create_content_logic_multiple_outgoing_nodes(self):
        # Test case with a node that has multiple outgoing nodes
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
        # Test case with a node that is in a loop
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
        # Test case where the maximum depth is reached
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
    def test_create_content_append_first_node(self):
        # Test case where append_first_node is True
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
        # Test case where append_first_node is False
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
        # Test case where the node is a loop
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
        # Test case where the maximum depth is reached
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
    def test_analyse_node_with_logic(self):
        # Test case where the head node has outgoing logic

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

        for idx,item in enumerate(expected_output):
            self.assertEqual(result[idx].uid, item)

    def test_analyse_node_with_uid(self):
        # Test case where the head node is a data node
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
            "LOOP":{"end":"END_LOOP"},
        }
        output = []

        depth = 1
        max_depth = 10

        expected_output = ["A", "B", "XOR_START", "C", "XOR_MIDDLE", "D", "XOR_END"]

        result = analyse_node(
            node_tree=lookup_table["A"],
            output=output,
            logic_lines=logic_lines,
            lookup_table=lookup_table,
            append_first_node=True,
            depth=depth,
            max_depth=max_depth,
        )

        for idx,item in enumerate(expected_output):
            self.assertEqual(result[idx].uid, item)

    def test_analyse_node_with_leaf_uid(self):
        # Test case where the node is a leaf uid node
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

        self.assertEqual(result, output)  # Assert that output is not modified

    def test_analyse_node_max_depth_reached(self):
        # Test case where the maximum depth is reached
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

        self.assertEqual(result, output)  # Assert that output is not modified


if __name__ == "__main__":
    unittest.main()