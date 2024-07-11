"""Tests for the create_node_graph_from_event_graph module."""

import pytest
from networkx import DiGraph
from pm4py import ProcessTree

from tel2puml.node_map_to_puml.node import NodeTuple, Node, SubGraphNode
from tel2puml.node_map_to_puml.create_node_graph_from_event_graph import (
    update_graph_with_node_tuple,
    update_outgoing_logic_nodes,
    create_node_from_event,
)
from tel2puml.events import Event
from tel2puml.loop_detection.loop_types import LoopEvent


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


def test_update_outgoing_logic_nodes(
    process_tree_with_and_logic_gate: ProcessTree, nodes: list[Node]
) -> None:
    """Test the update_incoming_and_outgoing_logic_nodes function"""
    # setup
    event = Event("A")
    event.logic_gate_tree = process_tree_with_and_logic_gate
    node = Node(uid="A", event_type="A")
    node.update_node_list_with_nodes(nodes, "outgoing")

    update_outgoing_logic_nodes(event, node)

    assert len(node.outgoing_logic) == 1
    assert isinstance(node.outgoing_logic[0], Node)
    assert node.outgoing_logic[0].operator == "AND"
    assert node.outgoing_logic[0].outgoing == nodes
    assert node.outgoing_logic[0].outgoing_logic == nodes


def test_create_node_class_from_event_class() -> None:
    """Test the create_node_class_from_event_class function"""
    event = Event(event_type="A")
    node = create_node_from_event(event)
    assert isinstance(node, Node)
    assert node.event_type == "A"

    sub_graph: "DiGraph[Event]" = DiGraph()
    loop_event = LoopEvent(event_type="B", subgraph=sub_graph)
    sub_graph_node = create_node_from_event(loop_event)
    assert isinstance(sub_graph_node, SubGraphNode)
    assert sub_graph_node.event_type == "B"
    # SubGraphNode raises an error if sub_graph is not set when accessed
    with pytest.raises(ValueError):
        sub_graph_node.sub_graph
