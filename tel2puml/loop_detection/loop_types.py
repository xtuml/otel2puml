"""Module for loop detection types."""
from typing import NamedTuple

from networkx import DiGraph

from tel2puml.events import Event


class LoopEvent(Event):
    """Event class for loop detection.

    :param event_type: The type of the event.
    :type event_type: `str`
    :param subgraph: The subgraph of the loop.
    :type subgraph: `DiGraph[Event]`
    :param start_uid: The start uid of the loop, defaults to `None`.
    :type start_uid: `str` | `None`, optional
    :param end_uid: The end uid of the loop, defaults to `None`.
    :type end_uid: `str` | `None`, optional
    :param break_uids: The break uids of the loop, defaults to `None`.
    :type break_uids: `set`[`str`] | `None`, optional
    """

    def __init__(
        self, event_type: str, subgraph: "DiGraph[Event]",
        start_uid: str | None = None, end_uid: str | None = None,
        break_uids: set[str] | None = None
    ) -> None:
        """Constructor method"""
        super().__init__(event_type)
        self.sub_graph = subgraph
        self._start_uid: str | None = start_uid
        self._end_uid: str | None = end_uid
        self._break_uids: set[str] | None = break_uids

    @property
    def start_uid(self) -> str:
        """Getter for start_uid."""
        if self._start_uid is None:
            raise AttributeError("start_uid is not set.")
        return self._start_uid

    @start_uid.setter
    def start_uid(self, start_uid: str) -> None:
        """Setter for start_uid."""
        if self._start_uid is None:
            self._start_uid = start_uid
        else:
            raise AttributeError("start_uid is already set.")

    @property
    def end_uid(self) -> str:
        """Getter for end_uid."""
        if self._end_uid is None:
            raise AttributeError("end_uid is not set.")
        return self._end_uid

    @end_uid.setter
    def end_uid(self, end_uid: str) -> None:
        """Setter for end_uid."""
        if self._end_uid is None:
            self._end_uid = end_uid
        else:
            raise AttributeError("end_uid is already set.")

    @property
    def break_uids(self) -> set[str]:
        """Getter for break_uids."""
        if self._break_uids is None:
            raise AttributeError("break_uids is not set.")
        return self._break_uids

    @break_uids.setter
    def break_uids(self, break_uids: set[str]) -> None:
        """Setter for break_uids."""
        if self._break_uids is None:
            self._break_uids = break_uids
        else:
            raise AttributeError("break_uids is already set.")


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

DUMMY_BREAK_EVENT_TYPE = "DUMMY_BREAK"
