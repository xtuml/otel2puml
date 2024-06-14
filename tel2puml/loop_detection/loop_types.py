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

    :param start_event: The start event of the loop.
    :type start_event: `Event`
    :param end_event: The end event of the loop.
    :type end_event: `Event`
    :param break_event: The break event of the loop.
    :type break_event: `Event`
    :param edges_to_remove: The edges to remove.
    :type edges_to_remove: `set`[:class:`EventEdge`]
    """

    start_events: set[Event]
    end_events: set[Event]
    break_events: set[Event]
    edges_to_remove: set[EventEdge]
