"""This module holds the 'node' class"""
from typing import Literal

from networkx import DiGraph

from pm4py import ProcessTree

from tel2puml.events import Event
from tel2puml.logic_detection import Operator as Logic_operator
from tel2puml.tel2puml_types import PUMLEvent
from tel2puml.walk_puml_graph.node import Node


def load_all_logic_trees_into_nodes(
    events: dict[str, Event],
    nodes: dict[str, list[Node]],
    direction: Literal["incoming", "outgoing"],
) -> None:
    """Loads all logic trees into the nodes.

    :param events: The events to load.
    :type events: `dict`[`str`, :class:`Event`]
    :param nodes: The nodes to load the logic into.
    :type nodes: `dict`[`str`, `list`[:class:`Node`]]
    :param direction: The direction to load the logic.
    :type direction: `Literal`[`"incoming"`, `"outgoing"`]
    """
    if direction not in ["incoming", "outgoing"]:
        raise ValueError(f"Invalid direction {direction}")
    for event_type, event in events.items():
        # catch the case when the event has no logic gate tree
        if event.logic_gate_tree is not None:
            load_logic_tree_into_nodes(
                event.logic_gate_tree, nodes[event_type], direction
            )


def load_logic_tree_into_nodes(
    logic_gate_tree: ProcessTree,
    nodes: list[Node],
    direction: Literal["incoming", "outgoing"],
) -> None:
    """Loads a logic tree into the nodes of a list

    :param logic_gate_tree: The logic gate tree to load into the nodes.
    :type logic_gate_tree: :class:`ProcessTree`
    :param nodes: The nodes to load the logic into.
    :type nodes: `list`[:class:`Node`]
    :param direction: The direction to load the logic.
    :type direction: `Literal`[`"incoming"`, `"outgoing"`]
    """
    for node in nodes:
        node.load_logic_into_list(logic_gate_tree, direction)


def create_networkx_graph_of_nodes_from_markov_graph(
    markov_graph: "DiGraph[str]",
    node_event_references: dict[str, str],
) -> tuple["DiGraph[Node]", dict[str, list[Node]]]:
    """Creates a NetworkX graph of nodes from a Markov graph.

    :param markov_graph: The Markov graph to create the NetworkX graph from.
    :type markov_graph: :class:`DiGraph`[`str`]
    :param node_event_references: The node event references.
    :type node_event_references: `dict`[`str`, `str`]
    :return: A tuple containing the NetworkX graph and the event node
    reference.
    :rtype: `tuple`[:class:`DiGraph`[:class:`Node`], `dict`[`str`,
    `list`[:class:`Node`]]]
    """
    networkx_graph: "DiGraph[Node]" = DiGraph()
    uid_to_node = {}
    for node in markov_graph.nodes:
        node_class = Node(
            uid=node,
            event_type=node_event_references[node],
        )
        networkx_graph.add_node(node_class)
        uid_to_node[node] = node_class
    for node_class in networkx_graph.nodes:
        edges_to_node = markov_graph.in_edges(node_class.uid)
        for edge in edges_to_node:
            networkx_graph.add_edge(
                uid_to_node[edge[0]],
                uid_to_node[edge[1]],
            )
            node_class.incoming.append(uid_to_node[edge[0]])
        edges_from_node = markov_graph.out_edges(node_class.uid)
        for edge in edges_from_node:
            node_class.outgoing.append(uid_to_node[edge[1]])
    event_node_ref = create_event_node_ref(networkx_graph)
    return networkx_graph, event_node_ref


def create_event_node_ref(
    node_class_network_x_graph: "DiGraph[Node]",
) -> dict[str, list[Node]]:
    """Creates an event node reference.

    :param node_class_network_x_graph: The node class NetworkX graph.
    :type node_class_network_x_graph: :class:`DiGraph`[:class:`Node`]
    :return: The event node reference.
    :rtype: `dict`[`str`, `list`[:class:`Node`]]
    """
    event_node_ref: dict[str, list[Node]] = {}
    for node in node_class_network_x_graph.nodes:
        if node.event_type is None:
            raise ValueError(
                f"Node event type is not set for node with uid {node.uid}"
            )
        if node.event_type not in event_node_ref:
            event_node_ref[node.event_type] = []
        event_node_ref[node.event_type].append(node)
    return event_node_ref


def load_all_incoming_events_into_nodes(
    events: dict[str, Event],
    nodes: dict[str, list[Node]],
) -> None:
    """Loads all incoming events into nodes.

    :param events: The events to load.
    :type events: `dict`[`str`, :class:`Event`]
    :param nodes: The nodes to load the events into.
    :type nodes: `dict`[`str`, `list`[:class:`Node`]]
    """
    for event_type, event in events.items():
        for node in nodes[event_type]:
            node.eventsets_incoming = event.event_sets
            if event.logic_gate_tree is not None:
                if event.logic_gate_tree.operator == Logic_operator.BRANCH:
                    node.update_event_types(PUMLEvent.MERGE)


def merge_markov_without_loops_and_logic_detection_analysis(
    markov_graph_ref_pair: tuple["DiGraph[str]", dict[str, str]],
    incoming_logic_events: dict[str, Event],
    outgoing_logic_events: dict[str, Event],
) -> tuple["DiGraph[Node]", dict[str, list[Node]]]:
    """Merges a Markov graph without loops and logic detection analysis.

    :param markov_graph_ref_pair: The Markov graph reference pair.
    :type markov_graph_ref_pair: `tuple`[:class:`DiGraph`[`str`],
    `dict`[`str`, `str`]]
    :param incoming_logic_events: The incoming logic events.
    :type incoming_logic_events: `dict`[`str`, :class:`Event`]
    :param outgoing_logic_events: The outgoing logic events.
    :type outgoing_logic_events: `dict`[`str`, :class:`Event`]
    :return: A tuple containing the NetworkX graph and the event node
    reference.
    :rtype: `tuple`[:class:`DiGraph`[:class:`Node`], `dict`[`str`,
    `list`[:class:`Node`]]]
    """
    markov_graph, node_event_references = markov_graph_ref_pair
    node_class_graph, event_node_map = (
        create_networkx_graph_of_nodes_from_markov_graph(
            markov_graph, node_event_references
        )
    )
    load_all_logic_trees_into_nodes(
        outgoing_logic_events, event_node_map, "outgoing"
    )
    load_all_incoming_events_into_nodes(incoming_logic_events, event_node_map)
    return node_class_graph, event_node_map
