"""Module to hold the logic for creating node graph from event graph"""

from networkx import DiGraph

from tel2puml.node_map_to_puml.node import NodeTuple, Node, SubGraphNode
from tel2puml.events import Event
from tel2puml.loop_detection.loop_types import LoopEvent


def update_graph_with_node_tuple(
    node_edge: NodeTuple, node_graph: "DiGraph[Node]"
) -> "DiGraph[Node]":
    """Update the graph with the node tuple.

    :param node_edge: The node tuple to update the graph with
    :type: :class:`NodeTuple`
    :param node_graph: The node graph to update
    :type: :class:`DiGraph[Node]`
    :return: The node graph updated with the node tuple
    :rtype: :class:`DiGraph[Node]`
    """
    node_graph.add_edges_from([(node_edge.out_node, node_edge.in_node)])
    out_node, in_node = node_edge
    out_node.update_node_list_with_node(in_node, "outgoing")
    in_node.update_node_list_with_node(out_node, "incoming")

    return node_graph


def create_node_from_event(event: Event | LoopEvent) -> Node | SubGraphNode:
    """Create a node from an event

    :param event: The event to create the node from
    :type: :class: `Event` | `LoopEvent`
    :return: The node created from the event
    :rtype: :class: `Node` | `SubGraphNode`
    """
    # Check for LoopEvent first as it inherits from Event
    if isinstance(event, LoopEvent):
        return SubGraphNode(uid=event.uid, event_type=event.event_type)
    else:
        return Node(event_type=event.event_type, uid=event.uid)
