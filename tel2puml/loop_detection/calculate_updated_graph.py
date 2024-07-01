"""Module to calculate the updated graph after a new loop event has been
created"""
from typing import Any, Generator

from networkx import DiGraph, has_path
import pandas as pd

from tel2puml.utils import (
    get_innodes_not_in_set, get_outnodes_not_in_set,
    remove_nodes_without_path_back_to_loop
)
from tel2puml.events import Event, EventSet
from tel2puml.loop_detection.sub_graph_of_loop import (
    remove_event_edges_and_event_sets
)
from tel2puml.loop_detection.loop_types import (
    LoopEvent, Loop, EventEdge
)


def calculate_updated_graph_with_loop_event(
    loop: Loop, loop_event: LoopEvent, graph: "DiGraph[Event]"
) -> "DiGraph[Event]":
    """Calculate the updated graph with the loop event.
    This method will remove the loop events from the graph and replace them
    with the loop event. It will also update the graph with the loop event
    and the edges that are associated with the loop event and update event sets
    of the Events that have edges in or out of the loop.

    :param loop: The loop to update the graph with.
    :type loop: `Loop`
    :param loop_event: The loop event to update the graph with.
    :type loop_event: :class:`LoopEvent`
    :param graph: The graph to update.
    :type graph: :class:`DiGraph`
    :return: The updated graph.
    :rtype: :class:`DiGraph`
    """
    # get root event of graph
    root_event = [
        event for event, degree in graph.in_degree() if degree == 0
    ][0]
    # handle start events
    update_graph_for_loop_start_events(
        loop.start_events, loop.loop_events, loop_event, graph
    )
    # handle end events
    update_graph_for_loop_end_events(
        loop.end_events, loop.loop_events, loop_event, graph
    )
    # remove edges and event sets for remaining edges out of loop events
    remove_event_edges_and_event_sets(
        {
            EventEdge(*edge)
            for edge in graph.out_edges(loop.loop_events)
        },
        graph
    )
    # remove all loop events
    graph.remove_nodes_from(loop.loop_events)
    # handle break events without path back to root event
    break_events_without_path_back_to_root = {
        event for event in loop.break_events if not has_path(
            graph, root_event, event
        )
    }
    update_graph_for_loop_end_events(
        break_events_without_path_back_to_root, loop.loop_events, loop_event,
        graph
    )
    # handle break events with path back to root event
    break_events_with_path_back_to_root = (
        loop.break_events - break_events_without_path_back_to_root
    )
    update_graph_for_break_events_with_path_to_root_event(
        break_events_with_path_back_to_root, loop.loop_events, loop_event,
        graph
    )
    remove_nodes_without_path_back_to_loop(
        set(graph.nodes),
        {root_event},
        graph
    )
    return graph


def get_event_list_from_event_sets_intersecting_with_event_types_set(
    event_sets: set[EventSet],
    event_types: set[str],
) -> Generator[list[str], Any, None]:
    """Get event lists from the event sets that intersect with event types in
    the event types set.

    :param event_sets: The event sets to get event lists from.
    :type event_sets: `set`[:class:`EventSet`]
    :param event_types: The event types to check for intersection with the
    event sets.
    :type event_types: `set`[`str`]
    :return: The event lists that intersect with the event types set.
    :rtype: `Generator`[`list`[`str`], `Any`, `None`]"""
    for event_set in event_sets:
        event_list = event_set.to_list()
        if event_types.intersection(event_list):
            yield event_list


def check_eventsets_indicate_branch_for_set_of_event_types(
    event_sets: set[EventSet], event_types: set[str]
) -> bool:
    """Check if the event sets indicate a branch for the set of event types.

    :param event_sets: The event sets to check for branch.
    :type event_sets: `set`[:class:`EventSet`]
    :param event_types: The event types to check for branch.
    :type event_types: `set`[`str`]
    :return: If the event sets indicate a branch for the set of event types.
    :rtype: `bool`"""
    df = pd.DataFrame.from_records(list(event_sets))
    if not event_types.issubset(df.columns):
        raise ValueError(
            "Event types not in event sets, cannot check for branch"
        )
    df = df[list(event_types)]
    for start_event_type in event_types:
        unique_nums = list(df[start_event_type].dropna().unique())
        if 0 in unique_nums:
            unique_nums.remove(0)
        if len(unique_nums) > 1:
            return True
    return False


def get_event_list_with_loop_event_from_event_list(
    event_list: list[str], loop_event_type: str, event_types: set[str],
    is_branch: bool = False
) -> list[str]:
    """Get the event list with the loop event type added from the given
    event list if the event type is in the given event_types set. If it is
    indicated that the event sets have a branch, then the loop event type will
    be added for each event type in the event types list, if not all of those
    event types will be replaced with a single Loop event type.

    :param event_list: The event list to add the loop event type to.
    :type event_list: `list`[`str`]
    :param loop_event_type: The loop event type to add to the event list.
    :type loop_event_type: `str`
    :param event_types: The event types to check for intersection with the
    event list.
    :type event_types: `set`[`str`]
    :param is_branch: If the event sets indicate a branch for the set of
    event types.
    :type is_branch: `bool`
    :return: The event list with the loop event type added.
    :rtype: `list`[`str`]
    """
    if not event_types.intersection(event_list):
        raise ValueError("Event types not in event list")
    event_list_to_add = []
    for event_type in event_list:
        if event_type not in event_types:
            event_list_to_add.append(event_type)
        else:
            if is_branch:
                event_list_to_add.append(loop_event_type)
    if not is_branch:
        event_list_to_add.append(loop_event_type)
    return event_list_to_add


def get_event_lists_with_loop_events_from_event_lists(
    event_lists: list[list[str]], loop_event_type: str,
    event_types: set[str], is_branch: bool = False
) -> list[list[str]]:
    """Get the event lists with the loop event type added from the given
    event lists if the event type is in the given event_types set.

    :param event_lists: The event lists to add the loop event type to.
    :type event_lists: `list`[`list`[`str`]]
    :param loop_event_type: The loop event type to add to the event lists.
    :type loop_event_type: `str`
    :param event_types: The event types to check for intersection with the
    event lists.
    :type event_types: `set`[`str`]
    :param is_branch: If the event sets indicate a branch for the set of
    event types.
    :type is_branch: `bool`
    :return: The event lists with the loop event type added.
    :rtype: `list`[`list`[`str`]]
    """
    event_lists_to_add: list[list[str]] = []
    for event_list in event_lists:
        event_lists_to_add.append(
            get_event_list_with_loop_event_from_event_list(
                event_list, loop_event_type, event_types, is_branch
            )
        )
    return event_lists_to_add


def get_event_lists_with_loop_events(
    event_sets: set[EventSet], event_types: set[str], loop_event_type: str,
) -> list[list[str]]:
    """Get the event lists with the loop event type added from the event sets
    that intersect with the event types set.

    :param event_sets: The event sets to get event lists from.
    :type event_sets: `set`[:class:`EventSet`]
    :param event_types: The event types to check for intersection with the
    event sets.
    :type event_types: `set`[`str`]
    :param loop_event_type: The loop event type to add to the event lists.
    :type loop_event_type: `str`
    :return: The event lists with the loop event type added.
    :rtype: `list`[`list`[`str`]]
    """
    event_lists = list(
        get_event_list_from_event_sets_intersecting_with_event_types_set(
            event_sets, event_types
        )
    )
    is_branch = check_eventsets_indicate_branch_for_set_of_event_types(
        event_sets, event_types
    )
    return get_event_lists_with_loop_events_from_event_lists(
        event_lists, loop_event_type, event_types, is_branch
    )


def get_event_types_and_event_sets_overlap(
    event_sets: set[EventSet], event_types: set[str]
) -> set[str]:
    """Get the event types that overlap with the event sets and the event types
    set.

    :param event_sets: The event sets to check for overlap.
    :type event_sets: `set`[:class:`EventSet`]
    :param event_types: The event types to check for overlap with the event
    sets.
    :type event_types: `set`[`str`]
    :return: The event types that overlap with the event sets and the event
    types set.
    :rtype: `set`[`str`]
    """
    return event_types.intersection(
        event_type
        for event_set in event_sets
        for event_type in event_set.to_frozenset()
    )


def update_graph_for_loop_start_events(
    start_events: set[Event], loop_events: set[Event],
    loop_event: LoopEvent, graph: "DiGraph[Event]"
) -> None:
    """Update the graph for the loop start events.

    :param start_events: The start events to update the graph with.
    :type start_events: `set`[:class:`Event`]
    :param loop_events: The loop events to update the graph with.
    :type loop_events: `set`[:class:`Event`]
    :param loop_event: The loop event to update the graph with.
    :type loop_event: :class:`LoopEvent`
    :param graph: The graph to update.
    :type graph: :class:`DiGraph`
    """
    events_into_start_events = get_innodes_not_in_set(
        start_events, loop_events, graph
    )
    start_events_types = {event.event_type for event in start_events}
    for event in events_into_start_events:
        event_types_overlap = get_event_types_and_event_sets_overlap(
            event.event_sets, start_events_types
        )
        event_lists_to_add = get_event_lists_with_loop_events(
            event.event_sets, event_types_overlap, loop_event.event_type
        )
        for event_list_to_add in event_lists_to_add:
            event.update_event_sets(event_list_to_add)
    event_edges = {
        EventEdge(event, start_event)
        for start_event in start_events
        for event in events_into_start_events
        if (event, start_event) in graph.edges
    }
    remove_event_edges_and_event_sets(event_edges, graph)
    for event in events_into_start_events:
        graph.add_edge(event, loop_event)


def update_graph_for_loop_end_events(
    end_events: set[Event], loop_events: set[Event],
    loop_event: LoopEvent, graph: "DiGraph[Event]"
) -> None:
    """Update the graph for the loop end events.

    :param end_events: The end events to update the graph with.
    :type end_events: `set`[:class:`Event`]
    :param loop_events: The loop events to update the graph with.
    :type loop_events: `set`[:class:`Event`]
    :param loop_event: The loop event to update the graph with.
    :type loop_event: :class:`LoopEvent`
    :param graph: The graph to update.
    :type graph: :class:`DiGraph`
    """
    events_out_of_end_events = get_outnodes_not_in_set(
        end_events, loop_events, graph
    )
    end_event_types = {event.event_type for event in end_events}
    for event in events_out_of_end_events:
        event_types_overlap = get_event_types_and_event_sets_overlap(
            event.in_event_sets, end_event_types
        )
        event_lists_to_add = get_event_lists_with_loop_events(
            event.in_event_sets, event_types_overlap, loop_event.event_type
        )
        for event_list_to_add in event_lists_to_add:
            event.update_in_event_sets(event_list_to_add)
    event_edges = {
        EventEdge(end_event, event)
        for end_event in end_events
        for event in events_out_of_end_events
        if (end_event, event) in graph.edges
    }
    remove_event_edges_and_event_sets(event_edges, graph)
    for event in events_out_of_end_events:
        graph.add_edge(loop_event, event)


def update_graph_for_break_events_with_path_to_root_event(
    break_events: set[Event], loop_events: set[Event],
    loop_event: LoopEvent, graph: "DiGraph[Event]"
) -> None:
    """Update the graph for the break events with a path back to the root
    event.

    :param end_events: The end events to update the graph with.
    :type end_events: `set`[:class:`Event`]
    :param loop_events: The loop events to update the graph with.
    :type loop_events: `set`[:class:`Event`]
    :param loop_event: The loop event to update the graph with.
    :type loop_event: :class:`LoopEvent`
    :param graph: The graph to update.
    :type graph: :class:`DiGraph`
    """
    events_out_of_break_events = get_outnodes_not_in_set(
        break_events, loop_events, graph
    )
    end_event_types = {event.event_type for event in break_events}
    for event in events_out_of_break_events:
        event_types_overlap = get_event_types_and_event_sets_overlap(
            event.in_event_sets, end_event_types
        )
        event_lists_to_add = get_event_lists_with_loop_events(
            event.in_event_sets, event_types_overlap, loop_event.event_type
        )
        for event_list_to_add in event_lists_to_add:
            event.update_in_event_sets(event_list_to_add)
    for event in events_out_of_break_events:
        graph.add_edge(loop_event, event)
