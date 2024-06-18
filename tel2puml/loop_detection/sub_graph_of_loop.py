"""Module for creating sub graph of loop"""

from typing import Iterable

from networkx import DiGraph

from tel2puml.events import Event
from tel2puml.loop_detection.loop_types import Loop, EventEdge


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
