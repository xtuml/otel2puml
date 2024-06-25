"""Module for creating sub graph of loop"""
from copy import deepcopy
from typing import Iterable, TypeVar

from networkx import DiGraph, weakly_connected_components

from tel2puml.events import Event
from tel2puml.loop_detection.loop_types import Loop, EventEdge
from tel2puml.tel2puml_types import DUMMY_START_EVENT, DUMMY_END_EVENT
from tel2puml.utils import (
    get_innodes_not_in_set, get_outnodes_not_in_set,
    remove_nodes_without_path_back_to_loop
)

T = TypeVar("T")


def remove_loop_edges(
    loop: Loop,
    graph: "DiGraph[Event]",
) -> None:
    """Remove the edges that describe the loop from the graph, this includes
    removing the :class:`EventSet`s that are associated with the removed edges.

    :param loop: The loop to remove the edges from.
    :type loop: :class:`Loop`
    :param graph: The graph to remove the edges from.
    :type graph: :class:`DiGraph`[:class:`Event`]
    """
    start_points_in_edges = {
        EventEdge(*in_edge)
        for in_edge in graph.in_edges(loop.start_events)
        if in_edge[0] not in loop.loop_events
    }
    remove_event_edges_and_event_sets(start_points_in_edges, graph)
    end_points_out_edges = set(
        EventEdge(*edge) for edge in graph.out_edges(loop.end_events)
        if edge[1] not in loop.loop_events
    )
    remove_event_edges_and_event_sets(end_points_out_edges, graph)
    break_points_out_edges = set(
        EventEdge(*edge) for edge in graph.out_edges(loop.break_events)
    )
    remove_event_edges_and_event_sets(break_points_out_edges, graph)
    remove_event_edges_and_event_sets(loop.edges_to_remove, graph)


def remove_event_sets_mirroring_removed_edges(
    event_edges: Iterable[EventEdge],
) -> None:
    """Remove the :class:`EventSet`s that are associated with the removed
    edges.

    :param event_edges: The edges to remove the :class:`EventSet`s from.
    :type event_edges: `Iterable`[:class:`EventEdge`]
    """
    for out_event, in_event in event_edges:
        out_event.remove_event_type_from_event_sets(in_event.event_type)
        in_event.remove_event_type_from_in_event_sets(out_event.event_type)


def remove_event_edges_and_event_sets(
    event_edges: Iterable[EventEdge],
    graph: "DiGraph[Event]",
) -> None:
    """Remove the edges from the graph and the :class:`EventSet`s that are
    associated with the removed edges.

    :param event_edges: The edges to remove.
    :type event_edges: `Iterable`[:class:`EventEdge`]
    :param graph: The graph to remove the edges from.
    :type graph: :class:`DiGraph`[:class:`Event`]
    """
    graph.remove_edges_from(event_edges)
    remove_event_sets_mirroring_removed_edges(event_edges)


def get_disconnected_loop_sub_graph(
    scc_nodes: set[T],
    graph: "DiGraph[T]",
) -> "DiGraph[T]":
    """Get the sub graph of the loop that is disconnected from the rest of the
    graph, given the nodes in the strong connected components. The graph needs
    to have had all connections to the nodes outside the loop removed
    previously.

    :param scc_nodes: The nodes in the SCC
    :type scc_nodes: `set`[:class:`T`]
    :param graph: The graph to get the sub graph from
    :type graph: :class:`DiGraph`[:class:`T`]
    :return: The sub graph of the loop
    :rtype: :class:`DiGraph`[:class:`T`]
    """
    for wcc_nodes in weakly_connected_components(graph):
        if scc_nodes.issubset(wcc_nodes):
            graph.remove_nodes_from(set(graph.nodes).difference(wcc_nodes))
            return graph
    raise ValueError("The SCC nodes are not a subgraph of the graph")


def add_start_and_end_events_to_sub_graph(
    loop: Loop,
    graph: "DiGraph[Event]",
) -> None:
    """Add the start and end events of the loop to the sub graph.

    :param loop: The loop to get the start and end events from.
    :type loop: :class:`Loop`
    :param graph: The graph to add the start and end events to.
    :type graph: :class:`DiGraph`[:class:`Event`]
    """
    # create dummy start and end events
    start_event = create_start_event(loop, graph)
    end_event = create_end_event(loop, graph)
    add_start_event_to_graph(start_event, loop, graph)
    add_end_event_to_graph(end_event, loop, graph)
    loop.loop_events.add(start_event)
    loop.loop_events.add(end_event)


def add_start_event_to_graph(
    start_event: Event,
    loop: Loop,
    graph: "DiGraph[Event]",
) -> None:
    """Add the edges from the start event to the loop start events.

    :param start_event: The start event to add the edges from.
    :type start_event: :class:`Event`
    :param loop: The loop to get the start events from.
    :type loop: :class:`Loop`
    :param graph: The graph to add the edges to.
    :type graph: :class:`DiGraph`[:class:`Event`]
    """
    for node in graph.nodes:
        if node.event_type == DUMMY_START_EVENT:
            raise ValueError("A start event already exists in the graph")
    for loop_start_event in loop.start_events:
        graph.add_edge(start_event, loop_start_event)
        loop_start_event.update_in_event_sets([DUMMY_START_EVENT])


def add_end_event_to_graph(
    end_event: Event,
    loop: Loop,
    graph: "DiGraph[Event]",
) -> None:
    """Add the edges from the loop end events to the end event.

    :param end_event: The end event to add the edges to.
    :type end_event: :class:`Event`
    :param loop: The loop to get the end events from.
    :type loop: :class:`Loop`
    :param graph: The graph to add the edges to.
    :type graph: :class:`DiGraph`[:class:`Event`]
    """
    for node in graph.nodes:
        if node.event_type == DUMMY_END_EVENT:
            raise ValueError("An end event already exists in the graph")
    for loop_end_event in loop.end_events:
        graph.add_edge(loop_end_event, end_event)
        loop_end_event.update_event_sets([DUMMY_END_EVENT])


def create_start_event(
    loop: Loop,
    graph: "DiGraph[Event]",
) -> Event:
    """Create the start event of the loop.

    :param loop: The loop to create the start event for.
    :type loop: :class:`Loop`
    :param graph: The graph to create the start event from.
    :type graph: :class:`DiGraph`[:class:`Event`]
    :return: The start event of the loop.
    :rtype: :class:`Event`
    """
    start_event = Event(DUMMY_START_EVENT)
    in_nodes = get_innodes_not_in_set(
        loop.start_events, loop.loop_events, graph
    )
    # update start events out event sets
    for in_node in in_nodes:
        for event_set in in_node.event_sets:
            start_event.update_event_sets(event_set.to_list())
    return start_event


def create_end_event(
    loop: Loop,
    graph: "DiGraph[Event]",
) -> Event:
    """Create the end event of the loop.

    :param loop: The loop to create the end event for.
    :type loop: :class:`Loop`
    :param graph: The graph to create the end event from.
    :type graph: :class:`DiGraph`[:class:`Event`]
    :return: The end event of the loop.
    :rtype: :class:`Event`
    """
    end_event = Event(DUMMY_END_EVENT)
    loop_event_types = {event.event_type for event in loop.loop_events}
    for end_event_node in loop.end_events:
        exit_event_nodes = get_outnodes_not_in_set(
            {end_event_node}, loop.loop_events, graph
        )
        # check if there are any exit event nodes
        if exit_event_nodes:
            # update end events in event sets to mirror exit event nodes
            for out_node in exit_event_nodes:
                for event_set in out_node.in_event_sets:
                    if event_set.to_frozenset().issubset(loop_event_types):
                        end_event.update_in_event_sets(event_set.to_list())
        else:
            # if no exit event nodes update end events in event sets to
            # to be a single occurence of the end event
            end_event.update_in_event_sets([end_event_node.event_type])
    return end_event


def create_sub_graph_of_loop(
    loop: Loop,
    graph: "DiGraph[Event]",
) -> "DiGraph[Event]":
    """Create a sub graph of the loop.

    :param loop: The loop to create the sub graph from.
    :type loop: :class:`Loop`
    :param graph: The graph to create the sub graph from.
    :type graph: :class:`DiGraph`[:class:`Event`]
    :return: The sub graph of the loop.
    :rtype: :class:`DiGraph`[:class:`Event`]
    """
    sub_loop, sub_graph = deepcopy((loop, graph))
    # add start and end events to subgraph
    add_start_and_end_events_to_sub_graph(sub_loop, sub_graph)
    # remove loop edges from sub graph
    remove_loop_edges(sub_loop, sub_graph)
    # remove nodes from the graph without a path back to the loop events
    remove_nodes_without_path_back_to_loop(
        set(sub_graph.nodes), sub_loop.loop_events, sub_graph
    )
    return sub_graph
