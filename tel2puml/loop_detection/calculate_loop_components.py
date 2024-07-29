"""Module to calculate the loop components of a given graph."""

from typing import TypeVar

from networkx import DiGraph, has_path

from tel2puml.events import Event, get_event_to_over_lapping_events_map
from tel2puml.loop_detection.loop_types import Loop, EventEdge
from tel2puml.utils import (
    get_innodes_not_in_set,
    get_outnodes_not_in_set,
    get_nodes_with_outedges_not_in_set,
    get_nodes_with_outedges_in_set,
    get_nodes_with_inedge_not_in_set,
)

T = TypeVar("T")


def calc_components_of_loop(
    scc_events: set[Event], graph: "DiGraph[Event]"
) -> Loop:
    """Calculate the components of the loop.

    :param scc_events: The events in the SCC
    :type scc_events: `set`[:class:`Event`]
    :param graph: The graph to calculate the components from
    :type graph: :class:`DiGraph`[:class:`Event`]
    :return: The Loop components
    :rtype: :class:`Loop`
    """
    event_to_overlapping_events_map = get_event_to_over_lapping_events_map(
        graph
    )
    start_events, end_events, break_events, loop_edges = (
        calc_components_of_loop_generic(
            scc_events, graph, event_to_overlapping_events_map
        )
    )

    return Loop(
        scc_events,
        start_events,
        end_events,
        break_events,
        set(EventEdge(*edge) for edge in loop_edges),
    )


def calc_components_of_loop_generic(
    scc_nodes: set[T],
    graph: "DiGraph[T]",
    node_to_over_lapping_node_map: dict[T, list[set[T]]] | None = None,
) -> tuple[set[T], set[T], set[T], set[tuple[T, T]]]:
    """Calculate the components of the loop.

    :param scc_nodes: The nodes in the SCC
    :type scc_nodes: `set`[:class:`T`]
    :param graph: The graph to calculate the components from
    :type graph: :class:`DiGraph`[:class:`T`]
    :param node_to_over_lapping_node_map: The map of nodes to overlapping
    nodes, defaults to `None`
    :type node_to_over_lapping_node_map: `dict`[:class:`T`,
    `list`[`set`[:class:`T`]]] | None, optional
    :return: The start nodes, end nodes, break nodes and loop edges
    :rtype: `tuple`[`set`[:class:`T`], `set`[:class:`T`], `set`[:class:`T`],
    `set`[`tuple`[:class:`T`, :class:`T`]]]
    """
    if node_to_over_lapping_node_map is None:
        input_node_to_over_lapping_node_map: dict[T, list[set[T]]] = dict()
    else:
        input_node_to_over_lapping_node_map = node_to_over_lapping_node_map
    start_nodes = get_nodes_with_inedge_not_in_set(scc_nodes, scc_nodes, graph)
    end_nodes, break_nodes, loop_edges = calc_loop_end_break_and_loop_edges(
        start_nodes, scc_nodes, graph,
        input_node_to_over_lapping_node_map
    )
    return start_nodes, end_nodes, break_nodes, loop_edges


def calc_loop_end_break_and_loop_edges(
    start_nodes: set[T],
    scc_nodes: set[T],
    graph: "DiGraph[T]",
    node_to_over_lapping_node_map: dict[T, list[set[T]]] | None = None,
) -> tuple[set[T], set[T], set[tuple[T, T]]]:
    """Calculate the
    * end nodes of the loop
    * break nodes in the loop
    * node edges that create the loop

    :param start_nodes: The start nodes of the loop
    :type start_nodes: `set`[:class:`T`]
    :param scc_nodes: The nodes in the SCC
    :type scc_nodes: `set`[:class:`T`]
    :param graph: The graph to calculate the loop from
    :type graph: :class:`DiGraph`[:class:`T`]
    :param node_to_over_lapping_node_map: The map of nodes to overlapping
    nodes, defaults to `None`
    :type node_to_over_lapping_node_map: `dict`[:class:`T`,
    `list`[`set`[:class:`T`]]] | None, optional
    :return: The end nodes and the break nodes in the loop and the edges that
    create the loop
    :rtype: `tuple`[`set`[:class:`T`], `set`[:class:`T`],
    `set`[`tuple`[:class:`T`, :class:`T`]]]
    """
    if node_to_over_lapping_node_map is None:
        input_node_to_over_lapping_node_map: dict[T, list[set[T]]] = dict()
    else:
        input_node_to_over_lapping_node_map = node_to_over_lapping_node_map
    nodes_that_exit_loop = get_nodes_with_outedges_not_in_set(
        scc_nodes, scc_nodes, graph
    )
    end_nodes = get_end_nodes_using_start_nodes(scc_nodes, start_nodes, graph)
    if not nodes_that_exit_loop:
        break_nodes: set[T] = set()
        break_out_nodes: set[T] = set()
    else:
        end_nodes_with_exits = end_nodes.intersection(nodes_that_exit_loop)
        break_out_nodes = nodes_that_exit_loop.difference(end_nodes_with_exits)
        break_out_nodes = filter_break_out_nodes_based_on_overlaps(
            break_out_nodes, input_node_to_over_lapping_node_map, scc_nodes
        )
        if not end_nodes_with_exits:
            break_nodes = get_outnodes_not_in_set(
                break_out_nodes, scc_nodes, graph
            )
        else:
            break_nodes = get_break_nodes_if_end_to_start_exists(
                end_nodes,
                break_out_nodes,
                start_nodes,
                graph,
                scc_nodes,
            )
    break_nodes.difference_update(scc_nodes)
    loop_edges = get_loop_edges(start_nodes, end_nodes, graph)
    return end_nodes, break_nodes, loop_edges


def get_break_nodes_if_end_to_start_exists(
    end_nodes: set[T],
    nodes_without_edge_to_start_nodes: set[T],
    start_nodes: set[T],
    graph: "DiGraph[T]",
    scc_nodes: set[T],
) -> set[T]:
    """Get the end nodes and break nodes if the subset of nodes with edges
    to the start nodes is empty.

    :param end_nodes: The subset of nodes with edges to
    the start nodes
    :type end_nodes: `set`[:class:`T`]
    :param nodes_without_edge_to_start_nodes: The subset of nodes without
    edges to the start nodes
    :type nodes_without_edge_to_start_nodes: `set`[:class:`T`]
    :param start_nodes: The start nodes of the loop
    :type start_nodes: `set`[:class:`T`]
    :param graph: The graph to find the end nodes and break nodes from
    :type graph: :class:`DiGraph`[:class:`T`]
    :param scc_nodes: The nodes in the SCC
    :type scc_nodes: `set`[:class:`T`]
    :return: The end nodes and break nodes
    :rtype: set`[:class:`T`]
    """
    exit_points = get_outnodes_not_in_set(end_nodes, start_nodes, graph)
    exit_points.difference_update(end_nodes)
    break_nodes = get_break_nodes_from_potential_break_outnodes(
        nodes_without_edge_to_start_nodes, exit_points, graph,
        scc_nodes
    )
    return break_nodes


def get_break_nodes_from_potential_break_outnodes(
    potential_break_outnodes: set[T],
    exit_points: set[T],
    graph: "DiGraph[T]",
    scc_nodes: set[T],
) -> set[T]:
    """Get the break nodes from the potential break out nodes and exit
    points.

    :param potential_break_outnodes: The potential break out nodes
    :type potential_break_outnodes: `set`[:class:`T`]
    :param exit_points: The exit points of the loop
    :type exit_points: `set`[:class:`T`]
    :param graph: The graph to find the break nodes from
    :type graph: :class:`DiGraph`[:class:`T`]
    :param scc_nodes: The nodes in the SCC
    :type scc_nodes: `set`[:class:`T`]
    :return: The break nodes
    :rtype: `set`[:class:`T`]
    """
    in_nodes_to_exit_points_not_end_nodes = get_innodes_not_in_set(
        exit_points, scc_nodes, graph
    )
    break_nodes: set[T] = set()
    for node in potential_break_outnodes:
        # get all break nodes that have a path to the exit points
        # from the break out node
        in_nodes_with_path_from_node = [
            in_node
            for in_node in in_nodes_to_exit_points_not_end_nodes
            if has_path(graph, node, in_node)
        ]
        break_nodes.update(in_nodes_with_path_from_node)
        # get all break nodes that have no path to the exit points
        # from the break out node
        break_nodes.update([
            out_node
            for out_node in get_outnodes_not_in_set(
                {node}, scc_nodes, graph
            )
            if all(
                not has_path(graph, out_node, in_node)
                for in_node in in_nodes_to_exit_points_not_end_nodes
            )
        ])
    return break_nodes


def get_end_nodes_using_start_nodes(
    nodes: set[T],
    start_nodes: set[T],
    graph: "DiGraph[T]",
) -> set[T]:
    """Get the end nodes given the loop start nodes and the graph

    :param start_nodes: The start nodes of the loop
    :type start_nodes: `set`[:class:`T`]
    :param nodes: The nodes to find the furthest from the start nodes
    :type nodes: `set`[:class:`T`]
    :param graph: The graph to find the nodes furthest from the start nodes
    :type graph: :class:`DiGraph`[:class:`T`]`
    :return: The nodes furthest from the start nodes
    :rtype: `set`[:class:`T`]
    """
    nodes_with_edge_to_start_nodes = get_nodes_with_outedges_in_set(
        nodes, start_nodes, graph
    )
    copy_graph: DiGraph["T"] = graph.subgraph(nodes).copy()
    copy_graph.remove_edges_from(graph.in_edges(start_nodes))
    end_nodes = get_end_nodes_from_potential_end_nodes(
        nodes_with_edge_to_start_nodes, copy_graph
    )
    return end_nodes


def get_end_nodes_from_potential_end_nodes(
    potential_end_nodes: set[T], graph: "DiGraph[T]"
) -> set[T]:
    """Get the end nodes from the potential end nodes.

    :param potential_end_nodes: The potential end nodes
    :type potential_end_nodes: `set`[:class:`T`]
    :param graph: The graph to find the end nodes from
    :type graph: :class:`DiGraph`[:
    class:`T`]
    :return: The end nodes
    :rtype: `set`[:class:`T`]
    """
    return set(
        node
        for node in potential_end_nodes
        if is_end_of_potential_ends(node, potential_end_nodes, graph)
    )


def is_end_of_potential_ends(
    node: T,
    potential_end_nodes: set[T],
    graph: "DiGraph[T]",
) -> bool:
    """Check if the node is the end of the potential end nodes.

    :param node: The node to check if it is the end of the potential end
    nodes
    :type node: :class:`T`
    :param potential_end_nodes: The potential end nodes
    :type potential_end_nodes: `set`[:class:`T`]
    :param graph: The graph to check if the node is the end of the potential
    end nodes
    :type graph: :class:`DiGraph`[:
    class:`T`]
    :return: If the node is the end of the potential end nodes
    :rtype: `bool`
    """
    return all(
        int(has_path(graph, other_node, node))
        - int(has_path(graph, node, other_node))
        >= 0
        for other_node in potential_end_nodes
    )


def get_loop_edges(
    start_nodes: set[T],
    end_nodes: set[T],
    graph: "DiGraph[T]",
) -> set[tuple[T, T]]:
    """Get the edges that create the loop.

    :param start_nodes: The start nodes of the loop
    :type start_nodes: `set`[:class:`T`]
    :param end_nodes: The end nodes of the loop
    :type end_nodes: `set`[:class:`T`]
    :param graph: The graph to find the loop edges from
    :type graph: :class:`DiGraph`[:class:`T`]
    :return: The edges that create the loop
    :rtype: `set`[`tuple`[:class:`T`, :class:`T`]]
    """
    return set(
        edge
        for edge in graph.out_edges(end_nodes)
        if edge[1] in start_nodes and edge[0] in end_nodes
    )


def does_node_set_have_intersection_with_nodes_to_check(
    node_set: set[T], nodes_to_check: set[T]
) -> bool:
    """Check if the node set has intersection with the nodes to check.

    :param node_set: The node set to check if it overlaps with the nodes to
    check
    :type node_set: `set`[:class:`T`]
    :param nodes_to_check: The nodes to check if they overlap with the node
    set
    :type nodes_to_check: `set`[:class:`T`]
    :return: If the node set overlaps with the nodes to check
    :rtype: `bool`
    """
    difference_length = len(node_set.difference(nodes_to_check))
    if 0 < difference_length < len(node_set):
        return True
    return False


def do_any_node_sets_have_intersection_with_nodes_to_check(
    node_sets: list[set[T]], nodes_to_check: set[T]
) -> bool:
    """Check if any of the node sets have and intersection with the nodes to
    check.

    :param node_sets: The node sets to check if they overlap with the nodes to
    check
    :type node_sets: `list`[`set`[:class:`T`]]
    :param nodes_to_check: The nodes to check if they overlap with the node
    sets
    :type nodes_to_check: `set`[:class:`T`]
    :return: If any of the node sets overlap with the nodes to check
    :rtype: `bool`
    """
    for node_set in node_sets:
        if does_node_set_have_intersection_with_nodes_to_check(
            node_set, nodes_to_check
        ):
            return True
    return False


def filter_break_out_nodes_based_on_overlaps(
    break_out_nodes: set[T],
    node_to_over_lapping_node_map: dict[T, list[set[T]]],
    nodes_to_check: set[T],
) -> set[T]:
    """Filter the break out nodes based on the overlapping nodes out of the
    break out and if they have an intersection with the nodes to check.

    :param break_out_nodes: The break out nodes to filter
    :type break_out_nodes: `set`[:class:`T`]
    :param node_to_over_lapping_node_map: The map of nodes to overlapping
    nodes
    :type node_to_over_lapping_node_map: `dict`[:class:`T`,
    `list`[`set`[:class:`T`]]] | None
    :param nodes_to_check: The nodes to check if they overlap with the break
    out nodes
    :type nodes_to_check: `set`[:class:`T`]
    :return: The filtered break out nodes
    :rtype: `set`[:class:`T`]
    """
    update_break_out_nodes: set[T] = set()
    for break_out_node in break_out_nodes:
        if break_out_node not in node_to_over_lapping_node_map:
            update_break_out_nodes.add(break_out_node)
        else:
            if not do_any_node_sets_have_intersection_with_nodes_to_check(
                node_to_over_lapping_node_map[break_out_node],
                nodes_to_check
            ):
                update_break_out_nodes.add(break_out_node)
    return update_break_out_nodes
