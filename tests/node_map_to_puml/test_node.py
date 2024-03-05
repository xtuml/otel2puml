"""Tests for the node module."""
from copy import deepcopy, copy

from pm4py import ProcessTree

from tel2puml.node_map_to_puml.node import (
    Node,
    load_logic_tree_into_nodes,
    load_all_logic_trees_into_nodes,
)
from tel2puml.pipelines.logic_detection_pipeline import Event


class TestNode:
    """Tests for the node class."""

    @staticmethod
    def test_event_node_map_incoming():
        """Test the event_node_map property for incoming nodes."""
        node = Node(data="test_data", event_type="test_event_type")
        assert len(node.event_node_map_incoming) == 0
        incoming_nodes = [
            Node(data=f"test_data_{i}", event_type=f"test_event_type_{i}")
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
        node = Node(data="test_data", event_type="test_event_type")
        assert len(node.event_node_map_outgoing) == 0
        outgoing_nodes = [
            Node(data=f"test_data_{i}", event_type=f"test_event_type_{i}")
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
            node.load_logic_into_list(process_tree_no_logic, direction)
            assert len(direction_logic_list) == 3
            for direction_node in direction_node_list:
                assert direction_node in direction_logic_list

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
    def test_load_logic_into_list_stub_node(
        node_with_child_to_stub: Node,
        process_tree_with_and_logic_gate: ProcessTree,
    ) -> None:
        """Test the load_logic_into_list method with a stub node.

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


def test_load_logic_tree_into_nodes_incoming(
    node: Node,
    process_tree_no_logic: ProcessTree,
) -> None:
    """Test the load_logic_tree_into_nodes function for both incoming and
    outgoing nodes.

    :param node: The node to test.
    :type node: :class:`Node`
    :param process_tree_no_logic: The process tree with no logic.
    :type process_tree_no_logic: :class:`ProcessTree`
    """

    for direction in ["incoming", "outgoing"]:
        nodes_list = [deepcopy(node), deepcopy(node)]
        load_logic_tree_into_nodes(
            process_tree_no_logic, nodes_list, direction
        )
        for parent_node in nodes_list:
            direction_node_list = getattr(parent_node, direction)
            direction_logic_list = getattr(parent_node, f"{direction}_logic")
            assert len(direction_logic_list) == 3
            for direction_node in direction_node_list:
                assert direction_node in direction_logic_list


def test_load_all_logic_trees_into_nodes(
    events: dict[str, Event],
    node_map: dict[str, list[Node]],
) -> None:
    """Test the load_all_logic_trees_into_nodes function for both incoming and
    outgoing nodes.

    :param events: The events to test.
    :type events: `dict`[`str`, :class:`Event`]
    :param node_map: The node map to test.
    :type node_map: `dict`[`str`, `list`[:class:`Node`]]
    """
    for direction in ["incoming", "outgoing"]:
        load_all_logic_trees_into_nodes(events, node_map, direction)
        for nodes in node_map.values():
            node = nodes[0]
            direction_node_list = getattr(node, direction)
            direction_logic_list = getattr(node, f"{direction}_logic")
            assert len(direction_logic_list) == 3
            for direction_node in direction_node_list:
                assert direction_node in direction_logic_list
