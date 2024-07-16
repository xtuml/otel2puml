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


def update_outgoing_logic_nodes(event: Event, node: Node) -> None:
    """Update the outgoing logic nodes

    :param event: The event to update the outgoing logic nodes
    :param node: The node to update the outgoing logic nodes
    """
    if event.logic_gate_tree:
        node.load_logic_into_list(event.logic_gate_tree, "outgoing")


def create_node_from_event(event: Event | LoopEvent) -> Node | SubGraphNode:
    """Create a node from an event

    :param event: The event to create the node from
    :type: :class: `Event` | `LoopEvent`
    :return: The node created from the event
    :rtype: :class: `Node` | `SubGraphNode`
    """
    # Check for LoopEvent first as it inherits from Event
    if isinstance(event, LoopEvent):
        return SubGraphNode(
            uid=event.uid,
            event_type=event.event_type,
            start_uid=event.start_uid,
            end_uid=event.end_uid,
            break_uids=event.break_uids,
        )
    else:
        return Node(event_type=event.event_type, uid=event.uid)


def create_node_graph_from_event_graph(
    event_graph: "DiGraph[Event]",
) -> "DiGraph[Node]":
    """Create a node graph from an event graph

    :param event_graph: The event graph to create the node graph from
    :type event_graph: `:class: DiGraph[Event]
    :return: The node graph created from the event graph
    :rtype node_graph: `:class: DiGraph[Node]
    """

    node_graph: "DiGraph[Node]" = DiGraph()

    event_node_dict: dict[Event, Node] = {}

    events = list(event_graph.nodes(data=True))

    for event, _ in events:
        node: Node | SubGraphNode = create_node_from_event(event)
        event_node_dict[event] = node

    event_edges = event_graph.edges

    for start_event, end_event in event_edges:
        node_edge = NodeTuple(
            out_node=event_node_dict[start_event],
            in_node=event_node_dict[end_event],
        )
        update_graph_with_node_tuple(node_edge, node_graph)

    for event, node in event_node_dict.items():
        update_outgoing_logic_nodes(event, node)

    for event, node in event_node_dict.items():
        if isinstance(event, LoopEvent):
            if isinstance(node, SubGraphNode):
                # Set node subgraphs by recursion
                node.sub_graph = create_node_graph_from_event_graph(
                    event.sub_graph
                )
            else:
                raise TypeError(f"{node} should be of type SubGraphNode")

    return node_graph
