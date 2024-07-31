"""Tests for the `walk_puml_graph.node_update` module."""
from tel2puml.walk_puml_graph.node_update import (
    update_nodes_with_break_points,
    update_nodes_with_break_points_from_loops,
)
from tel2puml.walk_puml_graph.node import Node
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
