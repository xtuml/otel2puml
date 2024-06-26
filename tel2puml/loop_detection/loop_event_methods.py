"""Module that contains the methods for creating and connecting loop events"""

from typing import Any, Generator
from networkx import DiGraph

from tel2puml.loop_detection.loop_types import LoopEvent, Loop, LOOP_EVENT_TYPE
from tel2puml.events import Event, EventSet


def create_loop_event(
    loop: Loop,
    graph: "DiGraph[Event]",
    sub_graph: "DiGraph[Event]",
) -> LoopEvent:
    """Create the loop event.

    :param loop: The loop to create the event from.
    :type loop: :class:`Loop`
    :param graph: The graph to add the loop event to.
    :type graph: :class:`DiGraph`[:class:`Event`]
    :return: The loop event
    :rtype: :class:`LoopEvent`
    """
    loop_event_type = get_new_loop_event_type_from_graph(graph)
    loop_event = LoopEvent(loop_event_type, sub_graph)
    loop_event_types = {event.event_type for event in loop.loop_events}
    update_loop_event_in_event_sets(
        loop.start_events, loop_event, loop_event_types
    )
    update_loop_event_out_event_sets(
        loop.end_events | loop.break_events, loop_event, loop_event_types
    )
    return loop_event


def get_new_loop_event_type_from_graph(graph: "DiGraph[Event]") -> str:
    """Get a new loop event type from the graph.

    :param graph: The graph to get the new loop event type from.
    :type graph: :class:`DiGraph`[:class:`Event`]
    :return: The new loop event type.
    :rtype: `str`
    """
    max_loop_event = 0
    for event in graph.nodes:
        if LOOP_EVENT_TYPE in event.event_type:
            max_loop_event = max(
                int(event.event_type.split("_")[1]),
                max_loop_event,
            )
    return f"{LOOP_EVENT_TYPE}_{max_loop_event + 1}"


def update_loop_event_in_event_sets(
    start_events: set[Event],
    loop_event: LoopEvent,
    loop_event_types: set[str],
) -> None:
    """Update the in event sets of the loop event given the start events and
    the event types of the Events in the loop.

    :param start_events: The start events of the loop.
    :type start_events: `set`[:class:`Event`]
    :param loop_event: The loop event to update the in event sets of.
    :type loop_event: :class:`LoopEvent`
    :param loop_event_types: The loop event types.
    :type loop_event_types: `set`[`str`]
    """
    loop_in_events_list = get_loop_in_event_lists_not_within_loop(
        start_events, loop_event_types
    )
    for event_list in loop_in_events_list:
        loop_event.update_in_event_sets(event_list)


def update_loop_event_out_event_sets(
    end_break_events: set[Event],
    loop_event: LoopEvent,
    loop_event_types: set[str],
) -> None:
    """Update the out event sets of the loop event given the end and break
    events and the event types of the Events in the loop.

    :param end_break_events: The end and break events of the loop.
    :type end_break_events: `set`[:class:`Event`]
    :param loop_event: The loop event to update the out event sets of.
    :type loop_event: :class:`LoopEvent`
    :param loop_event_types: The loop event types.
    :type loop_event_types: `set`[`str`]
    """
    loop_out_events_list = get_loop_out_event_lists_not_within_loop(
        end_break_events, loop_event_types
    )
    for event_list in loop_out_events_list:
        loop_event.update_event_sets(event_list)


def get_loop_in_event_lists_not_within_loop(
    start_events: set[Event],
    loop_event_types: set[str],
) -> list[list[str]]:
    """Add the in event sets of the loop to the loop event.

    :param loop: The loop to add the in event sets from.
    :type loop: :class:`Loop`
    :param loop_event_types: The loop event types.
    :type loop_event_types: `set`[`str`]
    :return: The event lists to add.
    :rtype: `list`[`list`[`str`]]
    """
    event_lists_to_add: list[list[str]] = []
    for event in start_events:
        event_lists_to_add.extend(
            get_event_lists_to_add_from_event_not_within_loop(
                event.in_event_sets, loop_event_types
            )
        )
    return event_lists_to_add


def get_loop_out_event_lists_not_within_loop(
    end_break_events: set[Event],
    loop_event_types: set[str],
) -> list[list[str]]:
    """Add the out event sets of the loop to the loop event.

    :param loop: The loop to add the out event sets from.
    :type loop: :class:`Loop`
    :param loop_event_types: The loop event types.
    :type loop_event_types: `set`[`str`]
    :return: The event lists to add.
    :rtype: `list`[`list`[`str`]]
    """
    event_lists_to_add: list[list[str]] = []
    for event in end_break_events:
        event_lists_to_add.extend(
            get_event_lists_to_add_from_event_not_within_loop(
                event.event_sets, loop_event_types
            )
        )
    return event_lists_to_add


def get_event_lists_to_add_from_event_not_within_loop(
    event_sets: set[EventSet],
    loop_event_types: set[str],
) -> Generator[list[str], Any, None]:
    """Get the event lists to add from the event.

    :param event: The event to get the event lists from.
    :type event: :class:`Event`
    :param loop_event_types: The loop event types.
    :type loop_event_types: `set`[`str`]
    :return: Returns a generator of the event lists to add.
    :rtype: `Generator`[`list`[`str`], `Any`, `None`]
    """
    for event_set in event_sets:
        event_list = event_set.to_list()
        if not loop_event_types.intersection(event_list):
            yield event_list
