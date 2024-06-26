"""Module for loop detection types."""
from typing import NamedTuple

from networkx import DiGraph

from tel2puml.events import Event


class LoopEvent(Event):
    """Event class for loop detection.

    :param event_type: The type of the event.
    :type event_type: `str`
    :param subgraph: The subgraph of the loop.
    :type subgraph: `DiGraph[Event]`"""

    def __init__(
        self, event_type: str, subgraph: "DiGraph[Event]"
    ) -> None:
        """Constructor method"""
        super().__init__(event_type)
        self.sub_graph = subgraph


class EventEdge(NamedTuple):
    """Named tuple for event edge.

    :param out_event: The out event.
    :type out_event: `Event`
    :param in_event: The in event.
    :type in_event: `Event`
    """

    out_event: Event
    in_event: Event


class Loop(NamedTuple):
    """Named tuple for loop detection.

    :param loop_events: The loop events.
    :type loop_events: `set`[:class:`Event`]
    :param start_events: The start events.
    :type start_events: `set`[:class:`Event`]
    :param end_events: The end events.
    :type end_events: `set`[:class:`Event`]
    :param break_events: The break events.
    :type break_events: `set`[:class:`Event`]
    :param edges_to_remove: The edges to remove.
    :type edges_to_remove: `set`[:class:`EventEdge`]
    """
    loop_events: set[Event]
    start_events: set[Event]
    end_events: set[Event]
    break_events: set[Event]
    edges_to_remove: set[EventEdge]


LOOP_EVENT_TYPE = "LOOP"
