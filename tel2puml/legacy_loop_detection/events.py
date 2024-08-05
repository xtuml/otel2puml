"""Remove detected loop events from the events."""
from typing import Iterable

from tel2puml.events import Event
from tel2puml.legacy_loop_detection.detect_loops import Loop


def remove_detected_loop_events(
    mapping: dict[str, list[str]], events: dict[str, Event]
) -> None:
    """This function removes the detected loop events from the events.

    :param mapping: The mapping of event types to loop events.
    :type mapping: `dict`[`str`, `list`[`str`]]
    :param events: The events.
    :type events: `dict`[`str`, :class:`Event`]
    """
    for event_type, loop_events in mapping.items():
        for loop_event in loop_events:
            events[event_type].remove_event_type_from_event_sets(loop_event)


def get_loop_events_to_remove_mapping(
    loops: list[Loop],
    node_event_name_reference: dict[str, str],
) -> dict[str, list[str]]:
    """This function gets the mapping of event types to loop events to remove.

    :param loops: The loops.
    :type loops: `list`[:class:`Loop`]
    :param node_event_name_reference: The node event name reference.
    :type node_event_name_reference: `dict`[`str`, `str`]
    :return: The mapping of event types to loop events to remove.
    :rtype: `dict`[`str`, `list`[`str`]]
    """
    mapping: dict[str, list[str]] = {}
    for loop in loops:
        for node_from, node_to in loop.all_edges_to_remove:
            event_from = node_event_name_reference[node_from]
            event_to = node_event_name_reference[node_to]
            if event_from not in mapping:
                mapping[event_from] = []
            mapping[event_from].append(event_to)
    return mapping


def remove_detected_loop_data_from_events(
    loops: list[Loop],
    events: dict[str, Event],
    node_event_name_reference: dict[str, str],
) -> None:
    """This function removes the detected loop data from the events.

    :param loops: The loops.
    :type loops: `list`[:class:`Loop`]
    :param events: The events.
    :type events: `dict`[`str`, :class:`Event`]
    :param node_event_name_reference: The node event name reference.
    :type node_event_name_reference: `dict`[`str`, `str`]
    """
    loop_events_to_remove = get_loop_events_to_remove_mapping(
        loops, node_event_name_reference
    )
    remove_detected_loop_events(loop_events_to_remove, events)
    for loop in loops:
        if loop.sub_loops:
            remove_detected_loop_data_from_events(
                loop.sub_loops, events, node_event_name_reference
            )


def get_event_reference_from_events(
    events: Iterable[Event],
) -> dict[str, str]:
    """This function gets an event reference from a sequence of events.

    :param events: A sequence of events.
    :type events: `Iterable`[:class:`Event`]
    :return: The event reference.
    :rtype: `dict`[`str`, `str`]
    """
    return {event.event_type: event.event_type for event in events}
