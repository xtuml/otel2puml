"""Module to calculate the loop components of a given graph."""

from typing import Any

from networkx import DiGraph, has_path

from tel2puml.utils import (
    get_innodes_not_in_set,
    get_outnodes_not_in_set,
    get_nodes_with_outedges_not_in_set,
    get_nodes_with_outedges_in_set,
)


def calc_loop_end_break_and_loop_edges(
    start_nodes: set[Any],
    scc_nodes: set[Any],
    graph: "DiGraph[Any]",
) -> tuple[set[Any], set[Any], set[tuple[Any, Any]]]:
    """Calculate the
    * end nodes of the loop
    * break nodes in the loop
    * node edges that create the loop

    :param start_nodes: The start nodes of the loop
    :type start_nodes: `set`[:class:`Any`]
    :param scc_nodes: The nodes in the SCC
    :type scc_nodes: `set`[:class:`Any`]
    :param graph: The graph to calculate the loop from
    :type graph: :class:`DiGraph`[:class:`Any`]
    :return: The end nodes and the break nodes in the loop and the edges that
    create the loop
    :rtype: `tuple`[`set`[:class:`Any`], `set`[:class:`Any`],
    `set`[`tuple`[:class:`Any`, :class:`Any`]]]
    """
    nodes_that_exit_loop = get_nodes_with_outedges_not_in_set(
        scc_nodes, scc_nodes, graph
    )
    end_nodes = get_end_nodes_using_start_nodes(scc_nodes, start_nodes, graph)
    if not nodes_that_exit_loop:
        break_nodes = set()
    else:
        end_nodes_with_exits = end_nodes.intersection(nodes_that_exit_loop)
        if not end_nodes_with_exits:
            break_nodes = get_outnodes_not_in_set(scc_nodes, scc_nodes, graph)
        else:
            break_nodes = get_break_nodes_if_end_to_start_exists(
                end_nodes,
                nodes_that_exit_loop.difference(end_nodes_with_exits),
                start_nodes,
                graph,
            )
    loop_edges = get_loop_edges(start_nodes, end_nodes, graph)
    return end_nodes, break_nodes, loop_edges


def get_break_nodes_if_end_to_start_exists(
    end_nodes: set[Any],
    nodes_without_edge_to_start_nodes: set[Any],
    start_nodes: set[Any],
    graph: "DiGraph[Any]",
) -> set[Any]:
    """Get the end nodes and break nodes if the subset of nodes with edges
    to the start nodes is empty.

    :param end_nodes: The subset of nodes with edges to
    the start nodes
    :type end_nodes: `set`[:class:`Any`]
    :param nodes_without_edge_to_start_nodes: The subset of nodes without
    edges to the start nodes
    :type nodes_without_edge_to_start_nodes: `set`[:class:`Any`]
    :param start_nodes: The start nodes of the loop
    :type start_nodes: `set`[:class:`Any`]
    :param graph: The graph to find the end nodes and break nodes from
    :type graph: :class:`DiGraph`[:class:`Any`]
    :return: The end nodes and break nodes
    :rtype: set`[:class:`Any`]
    """
    exit_points = get_outnodes_not_in_set(end_nodes, start_nodes, graph)
    break_nodes = get_break_nodes_from_potential_break_outnodes(
        nodes_without_edge_to_start_nodes, exit_points, end_nodes, graph
    )
    return break_nodes


def get_break_nodes_from_potential_break_outnodes(
    potential_break_outnodes: set[Any],
    exit_points: set[Any],
    end_nodes: set[Any],
    graph: "DiGraph[Any]",
) -> set[Any]:
    """Get the break nodes from the potential break out nodes and exit
    points.

    :param potential_break_outnodes: The potential break out nodes
    :type potential_break_outnodes: `set`[:class:`Any`]
    :param exit_points: The exit points of the loop
    :type exit_points: `set`[:class:`Any`]
    :param graph: The graph to find the break nodes from
    :type graph: :class:`DiGraph`[:class:`Any`]
    :return: The break nodes
    :rtype: `set`[:class:`Any`]
    """
    in_nodes_to_exit_points_not_end_nodes = get_innodes_not_in_set(
        exit_points, end_nodes, graph
    )
    return set(
        in_node
        for in_node in in_nodes_to_exit_points_not_end_nodes
        for node in potential_break_outnodes
        if has_path(graph, node, in_node)
    )


def get_end_nodes_using_start_nodes(
    nodes: set[Any],
    start_nodes: set[Any],
    graph: "DiGraph[Any]",
) -> set[Any]:
    """Get the end nodes given the loop start nodes and the graph

    :param start_nodes: The start nodes of the loop
    :type start_nodes: `set`[:class:`Any`]
    :param nodes: The nodes to find the furthest from the start nodes
    :type nodes: `set`[:class:`Any`]
    :param graph: The graph to find the nodes furthest from the start nodes
    :type graph: :class:`DiGraph`[:class:`Any`]`
    :return: The nodes furthest from the start nodes
    :rtype: `set`[:class:`Any`]
    """
    nodes_with_edge_to_start_nodes = get_nodes_with_outedges_in_set(
        nodes, start_nodes, graph
    )
    copy_graph: DiGraph["Any"] = graph.subgraph(nodes).copy()
    copy_graph.remove_edges_from(graph.in_edges(start_nodes))
    end_nodes = get_end_nodes_from_potential_end_nodes(
        nodes_with_edge_to_start_nodes, copy_graph
    )
    return end_nodes


def get_end_nodes_from_potential_end_nodes(
    potential_end_nodes: set[Any], graph: "DiGraph[Any]"
) -> set[Any]:
    """Get the end nodes from the potential end nodes.

    :param potential_end_nodes: The potential end nodes
    :type potential_end_nodes: `set`[:class:`Any`]
    :param graph: The graph to find the end nodes from
    :type graph: :class:`DiGraph`[:
    class:`Any`]
    :return: The end nodes
    :rtype: `set`[:class:`Any`]
    """
    return set(
        node
        for node in potential_end_nodes
        if is_end_of_potential_ends(node, potential_end_nodes, graph)
    )


def is_end_of_potential_ends(
    node: Any,
    potential_end_nodes: set[Any],
    graph: "DiGraph[Any]",
) -> bool:
    """Check if the node is the end of the potential end nodes.

    :param node: The node to check if it is the end of the potential end
    nodes
    :type node: :class:`Any`
    :param potential_end_nodes: The potential end nodes
    :type potential_end_nodes: `set`[:class:`Any`]
    :param graph: The graph to check if the node is the end of the potential
    end nodes
    :type graph: :class:`DiGraph`[:
    class:`Any`]
    :return: If the node is the end of the potential end nodes
    :rtype: `bool`
    """
    return (
        all(
            int(has_path(graph, other_node, node))
            - int(has_path(graph, node, other_node)) >= 0
            for other_node in potential_end_nodes
        )
    )


def get_loop_edges(
    start_nodes: set[Any],
    end_nodes: set[Any],
    graph: "DiGraph[Any]",
) -> set[tuple[Any, Any]]:
    """Get the edges that create the loop.

    :param start_nodes: The start nodes of the loop
    :type start_nodes: `set`[:class:`Any`]
    :param end_nodes: The end nodes of the loop
    :type end_nodes: `set`[:class:`Any`]
    :param graph: The graph to find the loop edges from
    :type graph: :class:`DiGraph`[:class:`Any`]
    :return: The edges that create the loop
    :rtype: `set`[`tuple`[:class:`Any`, :class:`Any`]]
    """
    return set(
        edge
        for edge in graph.out_edges(end_nodes)
        if edge[1] in start_nodes and edge[0] in end_nodes
    )
