"""Tests for the `node_map_to_puml.node_update` module."""
from copy import deepcopy

from tel2puml.node_map_to_puml.node_update import (
    update_nodes_with_break_points,
    update_nodes_with_break_points_from_loops,
    update_logic_nodes_with_lonely_merges_from_node_to_node_kill_map,
    update_logic_node_with_lonely_merge,
    update_event_nodes_logic_nodes_with_lonely_merges
)
from tel2puml.node_map_to_puml.node import Node
from tel2puml.detect_loops import Loop
from tel2puml.tel2puml_types import PUMLEvent


class TestUpdateNodesWithBreakPoints:
    """Tests for the `update_nodes_with_break_points` function."""
    @staticmethod
    def loops_event_node_reference() -> tuple[Loop, dict[str, list[Node]]]:
        """Helper function to create loops and event node reference."""
        loop = Loop(["A"])
        sub_loop = Loop(["E"])
        sub_loop.add_break_point("E")
        loop.add_subloop(sub_loop)
        loop.add_break_point("A")
        event_node_reference = {
            x: [Node(uid=x, event_type=x)] for x in "AE"
        }
        return loop, event_node_reference

    def test_update_nodes_with_break_points(self) -> None:
        """Test updating nodes with break points."""
        _, event_node_reference = self.loops_event_node_reference()
        update_nodes_with_break_points(["A", "E"], event_node_reference)
        assert all(
            node.event_types == {PUMLEvent.BREAK}
            for x in "AE"
            for node in event_node_reference[x]
        )

    def test_update_nodes_with_break_points_from_loops(self) -> None:
        """Test updating nodes with break points from loops."""
        loop, event_node_reference = self.loops_event_node_reference()
        update_nodes_with_break_points_from_loops([loop], event_node_reference)
        assert all(
            node.event_types == {PUMLEvent.BREAK}
            for x in "AE"
            for node in event_node_reference[x]
        )


class TestUpdateLonelyMerges:
    """Tests for updating logic nodes with lonely merges."""
    @staticmethod
    def node_with_lonely_merges() -> Node:
        """Helper function to create a node with lonely merges."""
        A = Node(uid="A", event_type="A")
        logic_node_1 = Node(operator="XOR")
        A.outgoing_logic = [logic_node_1]
        nested_logic_node = Node(operator="AND")
        B = Node(uid="B", event_type="B")
        C = Node(uid="C", event_type="C")
        D = Node(uid="D", event_type="D")
        logic_node_1.outgoing_logic = [nested_logic_node, B]
        nested_logic_node.outgoing_logic = [C, D]
        return A

    def _check_lonely_merges(self, node: Node) -> None:
        """Helper function to check the lonely merges."""
        assert node.outgoing_logic[0].lonely_merge == (
            node.outgoing_logic[0].outgoing_logic[0]
        )
        assert node.outgoing_logic[0].outgoing_logic[0].lonely_merge == (
            node.outgoing_logic[0].outgoing_logic[0].outgoing_logic[0]
        )

    def test_update_logic_node_with_lonely_merge(self) -> None:
        """Test update_logic_node_with_lonely_merge. """
        A = self.node_with_lonely_merges()
        update_logic_node_with_lonely_merge(A.outgoing_logic[0], "BD")
        self._check_lonely_merges(A)

    def test_update_event_nodes_logic_nodes_with_lonely_merges(self) -> None:
        """Test update_event_nodes_logic_nodes_with_lonly_merges."""
        A = self.node_with_lonely_merges()
        update_event_nodes_logic_nodes_with_lonely_merges(A, "BD")
        self._check_lonely_merges(A)

    def test_update_logic_nodes_with_lonely_merges_from_node_to_node_kill_map(
        self
    ) -> None:
        """Test
        update_logic_nodes_with_lonely_merges_from_node_to_node_kill_map.
        """
        A = self.node_with_lonely_merges()
        A_copy = deepcopy(A)
        node_to_node_kill_map = {
            "A": ["B", "D"],
            "A_copy": ["B", "D"],
        }
        event_node_reference = {
            "A": [A],
            "A_copy": [A_copy],
        }
        update_logic_nodes_with_lonely_merges_from_node_to_node_kill_map(
            node_to_node_kill_map, event_node_reference
        )
        self._check_lonely_merges(A)
        self._check_lonely_merges(A_copy)
