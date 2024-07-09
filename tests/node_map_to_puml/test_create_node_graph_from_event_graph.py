"""Tests for the create_node_graph_from_event_graph module."""
from networkx import DiGraph

from tel2puml.node_map_to_puml.node import NodeTuple, Node
from tel2puml.node_map_to_puml.create_node_graph_from_event_graph import (
    update_graph_with_node_tuple,
)


def test_update_graph_with_node_tuple() -> None:
    """Test the update_graph_with_node_tuple function"""
    A = Node(uid="A", event_type="A")
    B = Node(uid="B", event_type="B")

    node_tuple = NodeTuple(out_node=A, in_node=B)
    graph: "DiGraph[Node]" = DiGraph()

    updated_graph = update_graph_with_node_tuple(node_tuple, graph)

    assert updated_graph.has_edge(A, B)
    assert A.outgoing == [B]
    assert B.incoming == [A]
