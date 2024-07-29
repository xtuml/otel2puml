"""Module to bring together all the loop detection functions and detect loops
in a graph."""

from networkx import DiGraph, strongly_connected_components

from tel2puml.events import Event
from .calculate_loop_components import (
    calc_components_of_loop
)
from .sub_graph_of_loop import create_sub_graph_of_loop
from .loop_event_methods import (
    create_loop_event,
    update_loop_event_with_start_end_and_breaks,
)
from .calculate_updated_graph import (
    calculate_updated_graph_with_loop_event,
    filter_and_replace_breaks_connected_to_end_events
)


def detect_loops(graph: "DiGraph[Event]") -> "DiGraph[Event]":
    """Detects loops in a graph and returns a new graph with the loops
    inserted as LoopEvents and the original edges and event sets updated

    :param graph: The graph to detect loops in
    :type graph: :class:`DiGraph`[:class:`Event`]
    :return: The graph with the loops inserted
    :rtype: :class:`DiGraph`[:class:`Event`]
    """
    scc_events = list(strongly_connected_components(graph))
    for scc_nodes in scc_events:
        if len(scc_nodes) == 1:
            node = list(scc_nodes)[0]
            if not graph.has_edge(node, node):
                continue
        loop = calc_components_of_loop(scc_nodes, graph)
        filter_and_replace_breaks_connected_to_end_events(graph, loop)
        sub_graph, start_event, end_event = create_sub_graph_of_loop(
            loop, graph
        )
        sub_graph = detect_loops(sub_graph)
        loop_event = create_loop_event(loop, graph, sub_graph)
        update_loop_event_with_start_end_and_breaks(
            start_event, end_event, loop.break_events, loop_event
        )
        graph = calculate_updated_graph_with_loop_event(
            loop, loop_event, graph
        )
    return graph
