"""Tests for the node module."""

from copy import copy

from pm4py import ProcessTree

from tel2puml.walk_puml_graph.node import Node
from tel2puml.tel2puml_types import PUMLEvent, PUMLOperator


class TestNode:
    """Tests for the node class."""

    @staticmethod
    def test_event_node_map_incoming() -> None:
        """Test the event_node_map property for incoming nodes."""
        node = Node(uid="test_data", event_type="test_event_type")
        assert len(node.event_node_map_incoming) == 0
        incoming_nodes = [
            Node(uid=f"test_data_{i}", event_type=f"test_event_type_{i}")
            for i in range(3)
        ]
        node.update_node_list_with_nodes(incoming_nodes, "incoming")
        assert len(node.event_node_map_incoming) == 3
        for i in range(3):
            assert (
                node.event_node_map_incoming[f"test_event_type_{i}"]
                == incoming_nodes[i]
            )

    @staticmethod
    def test_event_node_map_outgoing() -> None:
        """Test the event_node_map property for outgoing nodes."""
        node = Node(uid="test_data", event_type="test_event_type")
        assert len(node.event_node_map_outgoing) == 0
        outgoing_nodes = [
            Node(uid=f"test_data_{i}", event_type=f"test_event_type_{i}")
            for i in range(3)
        ]
        node.update_node_list_with_nodes(outgoing_nodes, "outgoing")
        assert len(node.event_node_map_outgoing) == 3
        for i in range(3):
            assert (
                node.event_node_map_outgoing[f"test_event_type_{i}"]
                == outgoing_nodes[i]
            )

    @staticmethod
    def test_load_logic_into_list_no_logic(
        node: Node,
        process_tree_no_logic: ProcessTree,
    ) -> None:
        """Test the load_logic_into_list method with no logic.

        :param node: The node to test.
        :type node: :class:`Node`
        :param process_tree_no_logic: The process tree with no logic.
        :type process_tree_no_logic: :class:`ProcessTree`
        """
        for direction, direction_node_list, direction_logic_list in zip(
            ["incoming", "outgoing"],
            [node.incoming, node.outgoing],
            [node.incoming_logic, node.outgoing_logic],
        ):
            assert len(direction_logic_list) == 0
            assert len(direction_node_list) == 3
            node.load_logic_into_list(process_tree_no_logic, direction)
            assert len(direction_logic_list) == 0
            assert len(direction_node_list) == 3

    @staticmethod
    def test_load_logic_into_list_and_logic(
        node: Node,
        process_tree_with_and_logic_gate: ProcessTree,
    ) -> None:
        """Test the load_logic_into_list method and logic gate.

        :param node: The node to test.
        :type node: :class:`Node`
        :param process_tree_with_and_logic_gate: The process tree with an
        AND logic gate.
        :type process_tree_with_and_logic_gate: :class:`ProcessTree`
        """
        for direction, direction_node_list, direction_logic_list in zip(
            ["incoming", "outgoing"],
            [node.incoming, node.outgoing],
            [node.incoming_logic, node.outgoing_logic],
        ):
            assert len(direction_logic_list) == 0
            node.load_logic_into_list(
                process_tree_with_and_logic_gate, direction
            )
            assert len(direction_logic_list) == 1
            operator_node = direction_logic_list[0]
            assert operator_node.operator == "AND"
            operator_node_direction_logic_list = getattr(
                operator_node, f"{direction}_logic"
            )
            assert len(operator_node_direction_logic_list) == 3
            for incoming_node in direction_node_list:
                assert incoming_node in operator_node_direction_logic_list

    @staticmethod
    def test_load_logic_into_list_or_logic(
        node: Node,
        process_tree_with_or_logic_gate: ProcessTree,
    ) -> None:
        """Test the load_logic_into_list method or logic gate.

        :param node: The node to test.
        :type node: :class:`Node`
        :param process_tree_with_or_logic_gate: The process tree with an
        OR logic gate.
        :type process_tree_with_or_logic_gate: :class:`ProcessTree`
        """
        for direction, direction_node_list, direction_logic_list in zip(
            ["incoming", "outgoing"],
            [node.incoming, node.outgoing],
            [node.incoming_logic, node.outgoing_logic],
        ):
            assert len(direction_logic_list) == 0
            node.load_logic_into_list(
                process_tree_with_or_logic_gate, direction
            )
            assert len(direction_logic_list) == 1
            operator_node = direction_logic_list[0]
            assert operator_node.operator == "OR"
            operator_node_direction_logic_list = getattr(
                operator_node, f"{direction}_logic"
            )
            assert len(operator_node_direction_logic_list) == 3
            for incoming_node in direction_node_list:
                assert incoming_node in operator_node_direction_logic_list

    @staticmethod
    def test_load_logic_into_list_xor_logic(
        node: Node,
        process_tree_with_xor_logic_gate: ProcessTree,
    ) -> None:
        """Test the load_logic_into_list method xor logic gate.

        :param node: The node to test.
        :type node: :class:`Node`
        :param process_tree_with_xor_logic_gate: The process tree with an
            XOR logic gate.
        :type process_tree_with_xor_logic_gate: :class:`ProcessTree`
        """
        for direction, direction_node_list, direction_logic_list in zip(
            ["incoming", "outgoing"],
            [node.incoming, node.outgoing],
            [node.incoming_logic, node.outgoing_logic],
        ):
            assert len(direction_logic_list) == 0
            node.load_logic_into_list(
                process_tree_with_xor_logic_gate, direction
            )
            assert len(direction_logic_list) == 1
            operator_node = direction_logic_list[0]
            assert operator_node.operator == "XOR"
            operator_node_direction_logic_list = getattr(
                operator_node, f"{direction}_logic"
            )
            assert len(operator_node_direction_logic_list) == 3
            for incoming_node in direction_node_list:
                assert incoming_node in operator_node_direction_logic_list

    @staticmethod
    def test_load_logic_into_list_and_xor_logic(
        node: Node,
        process_tree_with_and_xor_logic_gate: ProcessTree,
    ) -> None:
        """Test the load_logic_into_list method and gate with xor gate nested
        underneath.

        :param node: The node to test.
        :type node: :class:`Node`
        :param process_tree_with_and_xor_logic_gate: The process tree with an
            AND logic gate and an XOR logic gate nested underneath.
        :type process_tree_with_and_xor_logic_gate: :class:`ProcessTree`
        """
        for direction, direction_node_list, direction_logic_list in zip(
            ["incoming", "outgoing"],
            [node.incoming, node.outgoing],
            [node.incoming_logic, node.outgoing_logic],
        ):
            assert len(direction_logic_list) == 0
            node.load_logic_into_list(
                process_tree_with_and_xor_logic_gate, direction
            )
            assert len(direction_logic_list) == 1
            and_node = direction_logic_list[0]
            assert and_node.operator == "AND"
            and_node_direction_logic_list = getattr(
                and_node, f"{direction}_logic"
            )
            assert len(and_node_direction_logic_list) == 2
            for child_node in and_node_direction_logic_list:
                if child_node.operator == "XOR":
                    xor_node = child_node
                else:
                    assert child_node == direction_node_list[0]
            xor_node_direction_logic_list = getattr(
                xor_node, f"{direction}_logic"
            )
            assert len(xor_node_direction_logic_list) == 2
            for incoming_node in direction_node_list[1:]:
                assert incoming_node in xor_node_direction_logic_list

    @staticmethod
    def test_load_logic_into_list_child_stub_node(
        node_with_child_to_stub: Node,
        process_tree_with_and_logic_gate: ProcessTree,
    ) -> None:
        """Test the load_logic_into_list method that should create a child stub
        node.

        :param node_with_child_to_stub: The node with a child missing.
        :type node_with_child_to_stub: :class:`Node`
        :param process_tree_no_logic: The process tree with no logic.
        :type process_tree_no_logic: :class:`ProcessTree`
        """
        for direction, direction_node_list, direction_logic_list in zip(
            ["incoming", "outgoing"],
            [
                node_with_child_to_stub.incoming,
                node_with_child_to_stub.outgoing,
            ],
            [
                node_with_child_to_stub.incoming_logic,
                node_with_child_to_stub.outgoing_logic,
            ],
        ):
            assert len(direction_node_list) == 2
            previous_direction_node_list = copy(direction_node_list)
            node_with_child_to_stub.load_logic_into_list(
                process_tree_with_and_logic_gate, direction
            )
            assert len(direction_node_list) == 3
            assert len(direction_logic_list) == 1
            operator_node = direction_logic_list[0]
            assert operator_node.operator == "AND"
            operator_node_direction_logic_list = getattr(
                operator_node, f"{direction}_logic"
            )
            assert len(operator_node_direction_logic_list) == 3
            copied_direction_node_list = copy(direction_node_list)
            for incoming_node in previous_direction_node_list:
                assert incoming_node in operator_node_direction_logic_list
                copied_direction_node_list.remove(incoming_node)
            assert len(copied_direction_node_list) == 1
            assert copied_direction_node_list[0].is_stub
            assert len(getattr(copied_direction_node_list[0], direction)) == 0
            assert (
                len(
                    getattr(
                        copied_direction_node_list[0], f"{direction}_logic"
                    )
                )
                == 0
            )

    @staticmethod
    def test_load_logic_into_list_parent_stub_node(
        process_tree_with_and_logic_gate: ProcessTree,
    ) -> None:
        """Test the load_logic_into_list method for a stub
        node. This should not update any of the lists on the stub node.
        """
        node = Node(uid="test_stub", event_type="test_stub", is_stub=True)
        for direction in ["incoming", "outgoing"]:
            assert len(getattr(node, direction)) == 0
            assert len(getattr(node, f"{direction}_logic")) == 0
            node.load_logic_into_list(
                process_tree_with_and_logic_gate, direction
            )
            assert len(getattr(node, direction)) == 0
            assert len(getattr(node, f"{direction}_logic")) == 0

    def test_load_logic_into_list_branch(
        self,
        process_tree_with_BRANCH: ProcessTree,
    ) -> None:
        """Test the load_logic_into_list method for a branch event."""

        node = Node(uid="A", event_type="A")
        getattr(node, "outgoing").append(Node(uid="B", event_type="B"))

        node.load_logic_into_list(process_tree_with_BRANCH, "outgoing")

        assert len(node.event_types) == 1
        assert PUMLEvent.BRANCH in node.event_types

        assert len(node.outgoing) == 1
        assert node.outgoing[0].uid == "B"

    def test_load_logic_into_list_branch_plus_xor(
        self,
        process_tree_with_BRANCH_plus_XOR: ProcessTree,
        node_for_BRANCH_plus_XOR: Node,
    ) -> None:
        """
        Test the load_logic_into_list method for a branch with a nested xor
            event.
        """

        node = node_for_BRANCH_plus_XOR

        direction = "outgoing"
        node.load_logic_into_list(process_tree_with_BRANCH_plus_XOR, direction)
        assert len(node.event_types) == 1
        assert PUMLEvent.BRANCH in node.event_types
        assert len(node.outgoing_logic) == 1
        assert node.outgoing_logic[0].operator == "XOR"
        assert len(node.outgoing_logic[0].outgoing_logic) == 2
        assert (
            len(
                [
                    outgoing
                    for outgoing in node.outgoing_logic[0].outgoing
                    if outgoing.uid == "uid2"
                ]
            )
            == 1
        )
        assert (
            len(
                [
                    outgoing
                    for outgoing in node.outgoing_logic[0].outgoing
                    if outgoing.uid == "uid3"
                ]
            )
            == 1
        )

        assert len(node.outgoing) == 2
        assert (
            len(
                [
                    outgoing
                    for outgoing in node.outgoing
                    if outgoing.uid == "uid2"
                ]
            )
            == 1
        )
        assert (
            len(
                [
                    outgoing
                    for outgoing in node.outgoing
                    if outgoing.uid == "uid3"
                ]
            )
            == 1
        )

    @staticmethod
    def test_traverse_logic() -> None:
        """Test the traverse_logic method."""
        # setup
        node = Node(uid="test_event", event_type="test_event")
        and_node = Node(uid="test_and", operator="AND")
        xor_node = Node(uid="test_xor", operator="XOR")
        or_node = Node(uid="test_or", operator="OR")
        extra_and_child = Node(
            uid="test_extra_and_child", event_type="test_extra_and_child"
        )
        and_node.outgoing_logic.extend([xor_node, or_node, extra_and_child])
        xor_nodes = [
            Node(uid=f"test_xor_{i}", event_type=f"XOR_{i}") for i in range(2)
        ]
        or_nodes = [
            Node(uid=f"test_or_{i}", event_type=f"OR_{i}") for i in range(2)
        ]
        xor_node.outgoing_logic.extend(xor_nodes)
        or_node.outgoing_logic.extend(or_nodes)
        node.update_node_list_with_nodes(
            [*xor_nodes, *or_nodes, extra_and_child], direction="outgoing"
        )
        node.outgoing_logic.append(and_node)
        # function call
        leaf_nodes = node.traverse_logic("outgoing")
        # test
        expected_leaf_nodes = [extra_and_child, *xor_nodes, *or_nodes]
        assert len(leaf_nodes) == 5
        for leaf_node in leaf_nodes:
            assert leaf_node in expected_leaf_nodes
            expected_leaf_nodes.remove(leaf_node)
        assert len(expected_leaf_nodes) == 0

    @staticmethod
    def test_get_operator_type() -> None:
        """Test the get_operator_type method."""
        for operator in PUMLOperator:
            node = Node(uid="test_operator", operator=operator.name)
            assert node.get_operator_type() == operator

    @staticmethod
    def test_lonely_merge() -> None:
        """Test the lonely_merge property."""
        node = Node(uid="test_event", event_type="test_event")
        # test with no outgoing logic
        assert node.lonely_merge is None
        # test with a single outgoing logic node but with is_loop_kill_path
        # false for that entry
        outgoing_logic_node_1 = Node(
            uid="test_outgoing_logic_node_1",
            event_type="test_outgoing_logic_node_1",
        )
        node.update_logic_list(outgoing_logic_node_1, "outgoing")
        assert node.lonely_merge is None
        # test with a single outgoing logic node with is_loop_kill_path entry
        # set to true
        node.is_loop_kill_path[0] = True
        assert node.lonely_merge is None
        # test with two outgoing logic nodes with is_loop_kill_path entry set
        # to [False, False]
        outgoing_logic_node_2 = Node(
            uid="test_outgoing_logic_node_2",
            event_type="test_outgoing_logic_node_2",
        )
        node.update_logic_list(outgoing_logic_node_2, "outgoing")
        node.is_loop_kill_path = [False, False]
        assert node.lonely_merge is None
        # test with two outgoing logic nodes with is_loop_kill_path entry set
        # to [True, False]
        node.is_loop_kill_path[0] = True
        assert node.lonely_merge == outgoing_logic_node_2
