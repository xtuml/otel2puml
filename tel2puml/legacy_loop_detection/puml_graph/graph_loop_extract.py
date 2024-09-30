"""This module contains the LoopExtraction class."""
from typing import TypedDict

from networkx import dfs_predecessors, has_path

from tel2puml.utils import (
    check_has_path_not_through_nodes, check_has_path_between_all_nodes
)
from tel2puml.legacy_loop_detection.detect_loops import Loop
from tel2puml.graph import PUMLNode, PUMLEventNode, PUMLGraph


class LoopNodes(TypedDict):
    """A set of PUMLEventNode loop nodes: start and end"""
    start_loop_nodes: set[PUMLEventNode]
    end_loop_nodes: set[PUMLEventNode]


def extract_loops_starts_and_ends_from_loop(
    puml_graph: PUMLGraph,
    loop: Loop
) -> list[tuple[PUMLNode, PUMLNode]]:
    """Extracts the unique loop start and end nodes from the graph calculated
    from the Markov loop nodes given in the provided loop.

    :param puml_graph: The PlantUML graph to extract the loop nodes from.
    :type puml_graph: :class:`PUMLGraph`
    :param loop: The markov loop nodes used to extract the start and end nodes
    from the graph.
    :type loop: :class:`Loop`
    :return: The unique loop start and end nodes as a list of tuples.
    :rtype: `list[tuple[:class:`PUMLNode`, :class:`PUMLNode`]]`
    """
    loop_nodes = get_event_nodes_from_loop(puml_graph, loop)
    loop_starts_and_ends = get_unique_loops_from_start_and_end_nodes(
        puml_graph, loop_nodes, loop
    )
    return loop_starts_and_ends


def get_event_nodes_from_loop(
    puml_graph: PUMLGraph,
    loop: Loop
) -> LoopNodes:
    """Returns the event nodes from the the PUMLGraph instance for the given
    loop nodes from the Markov graph. The returnes loop nodes may specify more
    than one loop that share the same underlying loop found in the Markov graph

    :param puml_graph: The PlantUML graph to get the nodes from.
    :type puml_graph: :class:`PUMLGraph`
    :param loop: The loop used to get the nodes.
    :type loop: :class:`Loop`
    :return: The event nodes from the loop.
    :rtype: `set`[:class:`PUMLEventNode`]
    """
    start_loop_nodes: set[PUMLEventNode] = set()
    end_loop_nodes: set[PUMLEventNode] = set()
    for start_point in loop.start_points:
        puml_graph.add_graph_node_to_set_from_reference(
            start_loop_nodes, start_point
        )
    for end_point in loop.end_points:
        puml_graph.add_graph_node_to_set_from_reference(
            end_loop_nodes, end_point
        )
    return LoopNodes(
        start_loop_nodes=start_loop_nodes,
        end_loop_nodes=end_loop_nodes,
    )


def get_unique_loops_from_start_and_end_nodes(
    puml_graph: PUMLGraph, loop_nodes: LoopNodes, loop: Loop
) -> list[tuple[PUMLNode, PUMLNode]]:
    """Returns the unique loops start and end nodes calculated from the loop
    taken from the underlying Markov graph.

    :param puml_graph: The PlantUML graph to get the nodes from.
    :type puml_graph: :class:`PUMLGraph`
    :param loop_nodes: The loop nodes to get the unique loops from.
    :type loop_nodes: :class:`LoopNodes`
    :param loop: The loop used to get the nodes.
    :type loop: :class:`Loop`
    :return: The unique loops from the start and end nodes of the loop as a
    list of tuples of start and end nodes.
    :rtype: `list[tuple[:class:`PUMLNode`, :class:`PUMLNode`]]`
    """
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
    """Returns the distinct loops start and end nodes calculated from the loop
    taken from the underlying Markov graph using the precalculated un-grouped
    start and end nodes.

    :param puml_graph: The PlantUML graph to get the nodes from.
    :type puml_graph: :class:`PUMLGraph`
    :param starts_and_ends: The un-grouped loop nodes to get the unique loops
    from.
    :type starts_and_ends: :class:`LoopNodes`
    :param loop: The loop used to get the nodes.
    :type loop: :class:`Loop`
    :return: The unique loops from the start and end nodes of the loop as a
    list of tuples of start and end nodes.
    :rtype: `list[:class:`LoopNodes`]`
    """
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
    """Method to walk through the predecessors of the given node in the graph
    until the minimal start and ends nodes from the underlying Markov graph
    are found.

    This method checks to make sure that the current node in the iteration:
    * Has a path to the start nodes that does not pass through the end nodes.
    * Has a path to end nodes that does not pass through the start nodes that
    have not been found yet.
    If the start and end nodes that are found that satisfy these conditions
    and the minimal start and end nodes from the Markov graph are the same,
    then the start and end nodes are returned as we have traversed far enough
    up the graph to be within the correct logic block.

    :param puml_graph: The PlantUML graph to get the nodes from.
    :type puml_graph: :class:`PUMLGraph`
    :param node: The node to start the walk from.
    :type node: :class:`PUMLEventNode`
    :param starts_and_ends: The start and end nodes of the loop.
    :type starts_and_ends: :class:`LoopNodes`
    :param loop: The loop used to get the nodes.
    :type loop: :class:`Loop`
    :return: The unique loop start and end nodes from the ungrouped start and
    end nodes of the loop.
    :rtype: :class:`LoopNodes`
    """
    predecessors = dfs_predecessors(puml_graph)
    minimal_start_nodes_required = loop.start_points
    minimal_end_nodes_required = loop.end_points
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
                end_loop_nodes=filter_end_nodes_with_successors(
                    found_end_nodes, puml_graph
                )
            )
        if node not in predecessors:
            raise RuntimeError("No possible loop start node found")
        node = predecessors[node]


def filter_end_nodes_with_successors(
    found_end_nodes: set[PUMLEventNode], puml_graph: PUMLGraph
) -> set[PUMLEventNode]:
    """Filters the given end nodes to only include nodes that have a successor
    node. This is done to ensure that the end nodes of the loop are not break
    nodes have merged further up the loop graph.

    :param found_end_nodes: The end nodes to filter.
    :type found_end_nodes: `set[:class:`PUMLEventNode`]`
    :param puml_graph: The PlantUML graph to get the nodes from.
    :type puml_graph: :class:`PUMLGraph`
    :return: The filtered end nodes.
    :rtype: `set[:class:`PUMLEventNode`]`
    """
    filtered_end_nodes = set()
    for potential_end_node in found_end_nodes:
        if all(
            not has_path(puml_graph, potential_end_node, potential_successor)
            for potential_successor in found_end_nodes
            if potential_successor != potential_end_node
        ):
            filtered_end_nodes.add(potential_end_node)
    return filtered_end_nodes


def get_loop_start_and_end(
    puml_graph: PUMLGraph, loop_starts_and_ends: LoopNodes
) -> tuple[PUMLNode, PUMLNode]:
    """Returns the single start and end nodes (may be operator nodes) for the
    given PUMLEventNode start and end nodes

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
    """Calculates the loop start node from the given loop start and end
    PUMLEventNode's. The start node is calculated by walking up the graph
    from the on of the given start nodes until a node is found that has a path
    to all of the given start and end nodes. This is performed so that the
    logical operators are not on the incorrect side of the loop as they should
    not cross the loop.

    :param puml_graph: The PlantUML graph to get the nodes from.
    :type puml_graph: :class:`PUMLGraph`
    :param loop_starts_and_ends: The start and end nodes of the loop.
    :type loop_starts_and_ends: :class:`LoopNodes`
    :return: The start node of the loop.
    :rtype: :class:`PUMLNode`"""
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
    """Calculates the loop end node from the given loop start and end
    PUMLEventNode's. The end node is calculated by walking down the graph
    from one of the given end nodes until a node is found that has a path back
    to all of the given start and end nodes. This is performed so that the
    logical operators are not on the incorrect side of the loop as they should
    not cross the loop.

    :param puml_graph: The PlantUML graph to get the nodes from.
    :type puml_graph: :class:`PUMLGraph`
    :param loop_starts_and_ends: The start and end nodes of the loop.
    :type loop_starts_and_ends: :class:`LoopNodes`
    :return: The end node of the loop.
    :rtype: :class:`PUMLNode`"""
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
