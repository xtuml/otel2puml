import unittest
from tel2puml.node_map_to_puml.node import Node
from tel2puml.node_map_to_puml.node_map_to_puml import (
    create_content,
    is_in_loop,
    drill_down_tree,
    get_reverse_node_tree,
    append_logic_middle_or_end,
    append_logic_start,
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


if __name__ == "__main__":
    unittest.main()