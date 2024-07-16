"""Tests for the create_node_graph_from_event_graph module."""

import pytest
from networkx import DiGraph
from pm4py import ProcessTree

from tel2puml.node_map_to_puml.node import NodeTuple, Node, SubGraphNode
from tel2puml.node_map_to_puml.create_node_graph_from_event_graph import (
    update_graph_with_node_tuple,
    update_outgoing_logic_nodes,
    create_node_from_event,
    create_node_graph_from_event_graph,
)
from tel2puml.events import Event
from tel2puml.loop_detection.loop_types import LoopEvent
from tel2puml.tel2puml_types import DUMMY_START_EVENT, DUMMY_END_EVENT


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


def test_create_node_graph_from_event_graph_basic() -> None:
    """This tests the functionality of create_node_graph_from_event_graph with
    a basic event graph with 2 nodes and 1 edge
    """
    # Create a simple event graph with a few nodes and edges
    event_graph: "DiGraph[Event]" = DiGraph()
    event1 = Event(event_type="A", uid="A")
    event2 = Event(event_type="B", uid="B")
    event_graph.add_node(event1)
    event_graph.add_node(event2)
    event_graph.add_edge(event1, event2)
    event1.update_event_sets([event2.event_type])
    event2.update_in_event_sets([event1.event_type])

    node_graph = create_node_graph_from_event_graph(event_graph)

    # Check the node graph
    assert len(node_graph.nodes) == 2
    assert len(node_graph.edges) == 1

    # Check the nodes
    assert list(node_graph.nodes)[0].event_type == "A"
    assert list(node_graph.nodes)[1].event_type == "B"

    # Check the edges
    edges = list(node_graph.edges)
    assert len(edges) == 1
    start_node, end_node = edges[0]
    assert start_node.event_type == "A"
    assert end_node.event_type == "B"
    # Check edge logic applied correctly
    assert start_node.outgoing[0].event_type == "B"
    assert len(start_node.incoming) == 0
    assert len(end_node.outgoing) == 0
    assert end_node.incoming[0].event_type == "A"


def check_graph_structure(
    graph: "DiGraph[Node]", expected_nodes: int, expected_edges: int
) -> None:
    """Check if the graph has the expected number of nodes and edges."""
    assert len(list(graph.nodes)) == expected_nodes
    assert len(graph.edges) == expected_edges


def check_edge(
    edge: tuple[Node, Node],
    expected_source_type: str,
    expected_target_type: str,
) -> None:
    """Check if the edge has the expected start and end node event types"""
    start_node, end_node = edge
    assert start_node.event_type == expected_source_type
    assert end_node.event_type == expected_target_type


def check_node_connections(
    node: Node,
    expected_outgoing_len: int | None,
    expected_outgoing_event_type: str | None,
    expected_incoming_len: int | None,
    expected_incoming_event_type: str | None,
) -> None:
    """Check if the node has the expected number and types of
    incoming and outgoing connections."""
    assert len(node.outgoing) == expected_outgoing_len
    if expected_outgoing_len > 0:
        assert node.outgoing[0].event_type == expected_outgoing_event_type
    assert len(node.outgoing_logic) == 0
    assert len(node.incoming) == expected_incoming_len
    if expected_incoming_len > 0:
        assert node.incoming[0].event_type == expected_incoming_event_type
    assert len(node.incoming_logic) == 0


def test_create_node_graph_from_event_graph_with_loop(
    event_graph_nested_loop_event_and_events: tuple[
        "DiGraph[Event]", list[Event]
    ],
) -> None:
    """Test the functionality of create_node_graph_from_event_graph
    with a self loop event."""
    event_graph, events = event_graph_nested_loop_event_and_events
    node_graph = create_node_graph_from_event_graph(event_graph)

    event1, event2, loop_event = events

    # Check main graph structure
    check_graph_structure(node_graph, expected_nodes=3, expected_edges=2)

    # Check main graph edges
    edges = list(node_graph.edges)
    check_edge(edges[0], event1.event_type, loop_event.event_type)
    check_edge(edges[1], loop_event.event_type, event2.event_type)

    # Check main graph node connections
    nodes = list(node_graph.nodes(data=True))
    check_node_connections(nodes[0][0], 1, loop_event.event_type, 0, None)
    check_node_connections(
        nodes[1][0], 1, event2.event_type, 1, event1.event_type
    )
    check_node_connections(nodes[2][0], 0, None, 1, loop_event.event_type)

    # Check subgraph node
    sub_graph_node = nodes[1][0]
    assert isinstance(sub_graph_node, SubGraphNode)

    # Check subgraph structure
    check_graph_structure(
        sub_graph_node.sub_graph, expected_nodes=3, expected_edges=2
    )

    # Check subgraph edges
    sub_edges = list(sub_graph_node.sub_graph.edges)
    check_edge(sub_edges[0], DUMMY_START_EVENT, "nested_self_loop_event")
    check_edge(sub_edges[1], "nested_self_loop_event", DUMMY_END_EVENT)

    # Check subgraph node connections
    sub_nodes = list(sub_graph_node.sub_graph.nodes(data=True))
    check_node_connections(
        sub_nodes[0][0], 1, "nested_self_loop_event", 0, None
    )
    check_node_connections(
        sub_nodes[1][0], 1, DUMMY_END_EVENT, 1, DUMMY_START_EVENT
    )
    check_node_connections(
        sub_nodes[2][0], 0, None, 1, "nested_self_loop_event"
    )
