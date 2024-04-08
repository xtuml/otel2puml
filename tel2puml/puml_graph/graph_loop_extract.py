"""This module contains the LoopExtraction class."""
from typing import TypedDict

from networkx import dfs_predecessors

from tel2puml.utils import (
    check_has_path_not_through_nodes, check_has_path_between_all_nodes
)
from tel2puml.detect_loops import Loop
from tel2puml.puml_graph.graph import PUMLNode, PUMLEventNode, PUMLGraph


class LoopNodes(TypedDict):
    """A loop node"""
    start_loop_nodes: set[PUMLEventNode]
    end_loop_nodes: set[PUMLEventNode]


def extract_loops_starts_and_ends_from_loop(
    puml_graph: PUMLGraph,
    loop: Loop
) -> list[tuple[PUMLNode, PUMLNode]]:
    loop_nodes = get_event_nodes_from_loop(puml_graph, loop)
    loop_starts_and_ends = get_unique_loops_from_start_and_end_nodes(
        puml_graph, loop_nodes, loop
    )
    return loop_starts_and_ends


def get_event_nodes_from_loop(
    puml_graph: PUMLGraph,
    loop: Loop
) -> LoopNodes:
    """Returns the event nodes from the loop.

    :param loop: The loop to get the nodes from.
    :type loop: :class:`Loop`
    :return: The event nodes from the loop.
    :rtype: `set`[:class:`PUMLEventNode`]
    """
    start_loop_nodes = set()
    end_loop_nodes = set()
    for edge_to_remove in loop.edges_to_remove:
        puml_graph.add_graph_node_to_set_from_reference(
            end_loop_nodes, edge_to_remove[0]
        )
        puml_graph.add_graph_node_to_set_from_reference(
            start_loop_nodes, edge_to_remove[1]
        )
    return LoopNodes(
        start_loop_nodes=start_loop_nodes,
        end_loop_nodes=end_loop_nodes,
    )


def get_unique_loops_from_start_and_end_nodes(
    puml_graph: PUMLGraph, loop_nodes: LoopNodes, loop: Loop
) -> list[tuple[PUMLNode, PUMLNode]]:
    loops_starts_and_ends = get_distinct_loops_starts_and_ends(
        puml_graph, loop_nodes, loop
    )
    loops_start_and_end_singular_nodes = [
        get_loop_start_and_end(puml_graph, loop)
        for loop in loops_starts_and_ends
    ]
    return loops_start_and_end_singular_nodes


def get_distinct_loops_starts_and_ends(
    puml_graph: PUMLGraph,
    starts_and_ends: LoopNodes,
    loop: Loop
) -> list[LoopNodes]:
    start_node = list(starts_and_ends["start_loop_nodes"])[0]
    loops = []
    while True:
        loop_nodes = walk_until_minimal_nodes_found(
            puml_graph, start_node, starts_and_ends, loop
        )
        loops.append(loop_nodes)
        starts_and_ends["start_loop_nodes"].difference_update(
            loop_nodes["start_loop_nodes"]
        )
        starts_and_ends["end_loop_nodes"].difference_update(
            loop_nodes["end_loop_nodes"]
        )
        if len(starts_and_ends["start_loop_nodes"]) == 0:
            break
        start_node = list(starts_and_ends["start_loop_nodes"])[0]
    return loops


def walk_until_minimal_nodes_found(
    puml_graph: PUMLGraph,
    node: PUMLEventNode,
    starts_and_ends: LoopNodes,
    loop: Loop
) -> LoopNodes:
    predecessors = dfs_predecessors(puml_graph)
    minimal_start_nodes_required = set(
        edge_to_remove[1] for edge_to_remove in loop.edges_to_remove
    )
    minimal_end_nodes_required = set(
        edge_to_remove[0] for edge_to_remove in loop.edges_to_remove
    )
    while True:
        found_start_nodes = set(
            start_node
            for start_node in starts_and_ends["start_loop_nodes"]
            if check_has_path_not_through_nodes(
                puml_graph, node, start_node, starts_and_ends["end_loop_nodes"]
            )
        )
        found_end_nodes = set(
            end_node
            for end_node in starts_and_ends["end_loop_nodes"]
            if check_has_path_not_through_nodes(
                puml_graph, node, end_node,
                starts_and_ends["start_loop_nodes"].difference(
                    found_start_nodes
                )
            )
        )
        if (
            set(
                start_node.parent_graph_node
                for start_node in found_start_nodes
            ) == minimal_start_nodes_required
        ) and (
            set(
                end_node.parent_graph_node
                for end_node in found_end_nodes
            ) == minimal_end_nodes_required
        ):
            return LoopNodes(
                start_loop_nodes=found_start_nodes,
                end_loop_nodes=found_end_nodes
            )
        if node not in predecessors:
            raise RuntimeError("No possible loop start node found")
        node = predecessors[node]


def get_loop_start_and_end(
    puml_graph: PUMLGraph, loop_starts_and_ends: LoopNodes
) -> tuple[PUMLNode, PUMLNode]:
    """Returns the start and end nodes of the loop.

    :param loop_starts_and_ends: The start and end nodes of the loop.
    :type loop_starts_and_ends: :class:`LoopNodes`
    :return: The start and end nodes of the loop.
    :rtype: `tuple[:class:`PUMLNode`, :class:`PUMLNode`]`
    """
    start_node = calc_loop_start_node(
        puml_graph, loop_starts_and_ends)
    end_node = calc_loop_end_node(puml_graph, loop_starts_and_ends)
    return start_node, end_node


def calc_loop_start_node(
    puml_graph: PUMLGraph, loop_starts_and_ends: LoopNodes
) -> PUMLNode:
    predecessors = dfs_predecessors(puml_graph)
    if len(loop_starts_and_ends["start_loop_nodes"]) == 0:
        raise RuntimeError("No loop start nodes have been given")
    node = list(loop_starts_and_ends["start_loop_nodes"])[0]
    all_nodes = [
        *loop_starts_and_ends["start_loop_nodes"],
        *loop_starts_and_ends["end_loop_nodes"]
    ]
    while True:
        if node not in predecessors:
            break
        if check_has_path_between_all_nodes(puml_graph, [node], all_nodes):
            break
        node = predecessors[node]
        if isinstance(node, PUMLEventNode):
            raise RuntimeError("No possible loop start node found")
    return node


def calc_loop_end_node(
    puml_graph: PUMLGraph, loop_starts_and_ends: LoopNodes
) -> PUMLNode:
    if len(loop_starts_and_ends["end_loop_nodes"]) == 0:
        raise RuntimeError("No loop end nodes have been given")
    node = list(loop_starts_and_ends["end_loop_nodes"])[0]
    all_nodes = [
        *loop_starts_and_ends["start_loop_nodes"],
        *loop_starts_and_ends["end_loop_nodes"]
    ]
    while True:
        out_edges = list(puml_graph.out_edges(node))
        if len(out_edges) == 0:
            break
        if check_has_path_between_all_nodes(puml_graph, all_nodes, [node]):
            break
        node = out_edges[0][1]
        if isinstance(node, PUMLEventNode):
            raise RuntimeError("No possible loop start node found")
    return node
