"""Module to help sequence OTel traces to pv event sequences"""
from typing import Generator, Any
from datetime import datetime

import numpy as np
import numba as nb
import networkx as nx

from tel2puml.tel2puml_types import PVEvent
from tel2puml.utils import datetime_to_pv_string


@nb.jit(nopython=True)
def get_slice_indexes(
    time_array: np.ndarray
) -> list[int]:
    """Get the indexes of the slices"""
    slice_indexes = [0]
    i = 0
    time_array_length = len(time_array)
    for i in range(time_array_length - 1):
        if has_time_overlap(time_array[i], time_array[i + 1]):
            pass
        else:
            slice_indexes.append(i + 1)
    slice_indexes.append(time_array_length)
    return slice_indexes


@nb.jit(nopython=True)
def has_time_overlap(time_vec_1: np.ndarray, time_vec_2: np.ndarray) -> bool:
    """Calculate the overlap between two time vectors"""
    start_time = max(time_vec_1[0], time_vec_2[0])
    end_time = min(time_vec_1[1], time_vec_2[1])
    return start_time < end_time


class Span:
    """A span is a single operation in a trace"""
    def __init__(
        self, span_id: str, name: str | None,
        start_time: int | None, end_time: int | None,
        parent_id: str | None = None,
        app_name: str = "default_app"
    ) -> None:
        self.span_id = span_id
        self.parent_id = parent_id
        self.name = name
        self._start_time = start_time
        self._end_time = end_time
        self.child_spans: dict[str, Span] = {}
        self.app_name = app_name

    def __repr__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.span_id)

    def update_attrs(
        self, name: str, start_time: int, end_time: int,
        parent_id: str | None = None
    ) -> None:
        """Update the attributes of the span"""
        self.name = name
        self._start_time = start_time
        self._end_time = end_time
        if parent_id is not None:
            self.parent_id = parent_id

    @property
    def start_time_order(self) -> list["Span"]:
        """Return the child spans in start time order"""
        return sorted(
            self.child_spans.values(),
            key=lambda span: span._start_time
        )

    @property
    def end_time(self) -> datetime:
        """Return the end time as a datetime"""
        return datetime.fromtimestamp(self._end_time * 1e-9)

    def time_array(self) -> np.ndarray:
        """Return the start and end times as a numpy array"""
        return np.array([self._start_time, self._end_time])

    def add_child_span(self, span: "Span") -> None:
        """Add a child span to the span"""
        self.child_spans[span.span_id] = span

    def child_spans_sequence_order(self) -> list[list["Span"]]:
        """Return the child spans in sequence order"""
        if not self.child_spans:
            return []
        ordered_spans = self.start_time_order
        time_array = np.array([span.time_array() for span in ordered_spans])
        slice_indexes = get_slice_indexes(time_array)
        return [
            ordered_spans[slice_indexes[i]:slice_indexes[i + 1]]
            for i in range(len(slice_indexes) - 1)
        ]

    def update_graph_with_connections(
        self, graph: nx.DiGraph
    ) -> list["Span"]:
        """Update the graph with connections"""
        previous_spans = [self]
        for async_span_group in reversed(self.child_spans_sequence_order()):
            next_previous_spans = []
            for span in async_span_group:
                for previous_span in previous_spans:
                    graph.add_edge(span, previous_span)
                next_previous_spans.extend(
                    span.update_graph_with_connections(graph)
                )
            previous_spans = next_previous_spans
        return previous_spans

    def to_pv_event(
        self,
        job_id: str,
        job_name: str,
        graph: nx.DiGraph
    ) -> PVEvent:
        """Return the span as a pv event"""
        return PVEvent(
            jobId=job_id, eventId=self.span_id,
            timestamp=datetime_to_pv_string(self.end_time),
            previousEventIds=self.get_previous_event_ids(graph),
            applicationName=self.app_name, jobName=job_name,
            eventType=self.name
        )

    def get_previous_event_ids(
        self, graph: nx.DiGraph
    ) -> list[str]:
        """Return the previous event ids"""
        return [
            node.span_id
            for node in graph.predecessors(self)
        ]


class Trace:
    """A trace is a collection of spans"""
    def __init__(self, trace_id: str, job_name: str = "default_job") -> None:
        self.trace_id = trace_id
        self.spans: dict[str, Span] = {}
        self._root_span: Span | None = None
        self.job_name = job_name

    def add_span(
        self,
        span_id: str, name: str, start_time: int, end_time: int,
        parent_id: str | None = None
    ) -> None:
        """Add a span to the trace"""
        if span_id in self.spans:
            span = self.spans[span_id]
            span.update_attrs(name, start_time, end_time, parent_id)
        else:
            span = Span(span_id, name, start_time, end_time, parent_id)
            self.spans[span_id] = span
        if parent_id is not None:
            if parent_id not in self.spans:
                self.spans[parent_id] = Span(parent_id)
            self.spans[parent_id].add_child_span(span)
        else:
            self._root_span = span

    @property
    def root_span(self) -> Span:
        """Return the root span of the trace"""
        if self._root_span is None:
            raise ValueError("Root span has not been set")
        return self._root_span

    def yield_pv_event_sequence(self) -> Generator[PVEvent, Any, None]:
        """Return the pv event sequence"""
        graph = nx.DiGraph()
        self.root_span.update_graph_with_connections(graph)
        for span in self.spans.values():
            yield span.to_pv_event(
                self.trace_id, self.job_name, graph
            )
