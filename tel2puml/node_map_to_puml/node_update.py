""""""
from typing import Iterable

from networkx import DiGraph

from tel2puml.detect_loops import Loop, get_all_break_points_from_loops
from tel2puml.node_map_to_puml.node import Node, SubGraphNode
from tel2puml.tel2puml_types import PUMLEvent


def update_nodes_with_break_points_from_loops(
    loops: list[Loop],
    event_node_reference: dict[str, list[Node]],
) -> None:
    """Updates the given merged graph with the break points from the given
    loops.

    :param merged_graph: The merged graph to update with the break points
    :type merged_graph: :class:`DiGraph`
    :param loops: The loops to extract the break points from
    :type loops: `list`[:class:`Loop`]
    """
    break_points = get_all_break_points_from_loops(loops)
    update_nodes_with_break_points(break_points, event_node_reference)


def update_nodes_with_break_points(
    break_points: Iterable[str],
    event_node_reference: dict[str, list[Node]],
) -> None:
    """Updates the given nodes with the given break points.

    :param break_points: The break points to update the nodes with
    :type break_points: `Iterable`[`str`]
    :param event_node_reference: The event node reference to update
    :type event_node_reference: `dict`[`str`, `list`[:class:`Node`]]
    """
    for break_point in break_points:
        for node in event_node_reference[break_point]:
            node.update_event_types(PUMLEvent.BREAK)


def get_node_to_node_map_from_edges(
    edges: Iterable[tuple[str, str]],
) -> dict[str, set[str]]:
    """Gets the node to node map from the given edges.

    :param edges: The edges to get the node to node map from
    :type edges: `Iterable`[`tuple`[`str`, `str`]]
    :return: The node to node map
    :rtype: `dict`[`str`, `set`[`str`]]
    """
    node_to_node_map: dict[str, set[str]] = {}
    for start_event, end_event in edges:
        if start_event not in node_to_node_map:
            node_to_node_map[start_event] = set()
        node_to_node_map[start_event].add(end_event)
    return node_to_node_map


def add_loop_kill_paths_for_nodes(
    node_to_node_kill_map: dict[str, set[str]],
    node_class_graph: "DiGraph[Node]"
) -> None:
    """Adds the loop kill paths for the given nodes.

    :param node_to_node_kill_map: The node to node kill map to use to add the
    loop kill paths
    :type node_to_node_kill_map: `dict`[`str`, `set`[`str`]]
    :param node_class_graph: The node class graph to update
    :type node_class_graph: :class:`DiGraph`[:class:`Node`]
    """
    for node in node_class_graph.nodes:
        if node.uid in node_to_node_kill_map:
            if len(node.outgoing_logic) != 1:
                raise ValueError(
                    f"Node {node.uid} does not have a single logic node"
                    "when it should do"
                )
            logic_node = node.outgoing_logic[0]
            logic_node.update_loop_kill_paths_from_given_leaf_nodes(
                node_to_node_kill_map[node.uid]
            )


def update_nested_node_graph_with_break_points(
    nested_node_graph: "DiGraph[Node]",
) -> None:
    """Updates the nested node graph with the break points.

    :param nested_node_graph: The nested node graph to update
    :type nested_node_graph: :class:`DiGraph`[:class:`Node`]
    """
    for node in nested_node_graph.nodes:
        if isinstance(node, SubGraphNode):
            update_sub_graph_node_break_points(node)
            update_nested_node_graph_with_break_points(node.sub_graph)


def update_sub_graph_node_break_points(
    sub_graph_node: SubGraphNode,
) -> None:
    """Updates the sub graph node with the break points.

    :param sub_graph_node: The sub graph node to update
    :type sub_graph_node: :class:`SubGraphNode`
    """
    for node in sub_graph_node.sub_graph.nodes:
        if node.uid in sub_graph_node.break_uids:
            node.update_event_types(PUMLEvent.BREAK)
