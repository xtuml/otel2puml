"""Module to help sequence OTel traces to pv event sequences"""
from typing import Generator, Any, Iterable
from datetime import datetime

import numpy as np
import numba as nb
import networkx as nx

from tel2puml.tel2puml_types import PVEvent, OtelSpan
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
        self, span_id: str, name: str | None = None,
        start_time: int | None = None, end_time: int | None = None,
        parent_id: str | None = None,
        app_name: str = "default_app",
        status: str | None = None,
    ) -> None:
        self.span_id = span_id
        self.parent_id = parent_id
        self.name = name
        self._start_time = start_time
        self._end_time = end_time
        self.child_spans: dict[str, Span] = {}
        self.app_name = app_name
        self.status = status

    def __repr__(self) -> str:
        return (
            self.name + f"_{self.status}" if self.status is not None
            else self.name
        )

    def __hash__(self) -> int:
        return hash(self.span_id)

    def update_attrs(
        self, name: str, start_time: int, end_time: int,
        parent_id: str | None = None, app_name: str = "default_app",
        status: str | None = None
    ) -> None:
        """Update the attributes of the span"""
        self.name = name
        self._start_time = start_time
        self._end_time = end_time
        if parent_id is not None:
            self.parent_id = parent_id
        self.status = status
        self.app_name = app_name

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
            eventType=str(self)
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
    def __init__(
        self, trace_id: str | None = None, job_name: str = "default_job"
    ) -> None:
        """Constructor method"""
        self._trace_id = trace_id
        self.spans: dict[str, Span] = {}
        self._root_span: Span | None = None
        self.job_name = job_name
        self._graph = nx.DiGraph()

    @property
    def trace_id(self) -> str:
        """Return the trace id"""
        return self._trace_id

    @trace_id.setter
    def trace_id(self, trace_id: str) -> None:
        """Set the trace id"""
        if self._trace_id is not None:
            raise ValueError("Trace id has already been set")
        self._trace_id = trace_id

    def add_span(
        self,
        span_id: str, name: str, start_time: int, end_time: int,
        parent_id: str | None = None, app_name: str = "default_app",
        status: str | None = None
    ) -> None:
        """Add a span to the trace"""
        if span_id in self.spans:
            span = self.spans[span_id]
            span.update_attrs(
                name, start_time, end_time, parent_id,
                app_name, status)
        else:
            span = Span(
                span_id, name, start_time, end_time, parent_id, app_name,
                status
            )
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

    # def check_and_add_no_call_spans(self):
    #     """Check if there is a no call span and add it if there is not"""
    #     spans = [
    #           span for span in self.spans.values() if not span.child_spans]
    #     for span in spans:
    #         self.add_span(
    #             span.span_id + "NOCALL", span.name + "_NO_CALL",
    #             span._end_time, span._end_time, span.span_id
    #         )

    def yield_pv_event_sequence(self) -> Generator[PVEvent, Any, None]:
        """Return the pv event sequence"""
        graph = self._graph
        # self.check_and_add_no_call_spans()
        self.root_span.update_graph_with_connections(graph)
        for span in self.spans.values():
            yield span.to_pv_event(
                self.trace_id, self.job_name, graph
            )


def get_attribute_from_list(
    attributes: list[dict[str, Any]], attribute_keys_and_types: dict[str, str]
) -> dict[str, str]:
    """Get attributes from a list as would be given in OTel span data

    :param attributes: The attributes list to get the attribute from
    :type attributes: `list`[:class:`OtelAttribute`]
    :param attribute_keys_and_types: The attribute keys and types to get from
    the attributes list
    :type attribute_keys_and_types: `dict`[`str`, `str`]
    :return: Returns the attributes from the list as a dictionary with the
    attribute keys as the keys and the taken attribute values as the values
    :rtype: `dict`[`str`, `str`]
    """
    return {
        attribute["key"]: attribute["value"]["Value"][
            attribute_keys_and_types[attribute["key"]]
        ]
        for attribute in attributes
        if attribute["key"] in attribute_keys_and_types
    }


def get_name_and_operation(
    span: OtelSpan,
    attr_string: str = "attributes",
) -> tuple[str, str]:
    """Gets the name and operation from the span

    :param span: The span to get the name and operation from
    :type span: :class:`OtelExtendedSpan`
    :return: Returns the name and operation from the span
    :rtype: `tuple`[`str`, `str`]
    """
    if attr_string in span:
        services_operation = get_attribute_from_list(
            span[attr_string],
            {"coral.operation": "StringValue", "coral.service": "StringValue"},
        )
        if len(services_operation) == 2:
            name = services_operation["coral.service"]
            operation = services_operation["coral.operation"]
            if name == "":
                name = span["scope"]["name"]
            if operation == "":
                operation = span["name"]
        else:
            name = span["scope"]["name"]
            operation = span["name"]
    else:
        name = span["scope"]["name"]
        operation = span["name"]
    return name, operation


def get_http_status_code_from_span(
    span: OtelSpan,
) -> str | None:
    """Gets the http status code from the span

    :param span: The span to get the http status code from
    :type span: :class:`OtelExtendedSpan`
    :return: Returns the http status code from the span
    :rtype: `str`
    """
    if "attributes" not in span:
        return None
    http_code = get_attribute_from_list(
        span["attributes"], {"http.status_code": "IntValue"}
    )
    if "http.status_code" in http_code:
        return http_code["http.status_code"]
    return None


def get_trace_from_span_dicts(
    spans: Iterable[OtelSpan],
    job_name: str = "default_job"
) -> Trace:
    trace = Trace(job_name=job_name)
    for span in spans:
        if trace.trace_id is None:
            trace.trace_id = span["trace_id"]
        # span_name, span_operation = get_name_and_operation(span)
        span_status = get_http_status_code_from_span(span)
        trace.add_span(
            span["span_id"], span["operation"],
            span["start_time_unix_nano"], span["end_time_unix_nano"],
            (
                None if span["parent_span_id"] == "NONE"
                else span["parent_span_id"]
            ),
            status=span_status
        )
    return trace


if __name__ == "__main__":
    import json
    import glob
    from tel2puml.utils import get_graphviz_plot
    import matplotlib.pyplot as plt
    for i in range(0, 2000):
        path_prefix = (
            "/workspaces/TEL2PUML/outputs/may13-15/"
            f"ExportHigh/linked_spans_{i}_*"
        )
        files = glob.glob(path_prefix)
        if not files:
            continue
        spans = []
        for file in files:
            with open(file, "r") as f:
                spans.append(json.load(f))
        trace = get_trace_from_span_dicts(spans)
        json_list = list(trace.yield_pv_event_sequence())
        fig = get_graphviz_plot(trace._graph, (30, 30))
        fig.savefig(
            "outputs/may13-15/ExportHighPV/linked_spans_"
            f"{i}_pv_event_sequence.png"
        )
        plt.close(fig)
        with open(
            "outputs/may13-15/ExportHighPV/linked_spans_"
            f"{i}_pv_event_sequence.json", "w"
        ) as f:
            json.dump(json_list, f, indent=4)
        print(i)
