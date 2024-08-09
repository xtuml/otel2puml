"""Tests for the sequence_otel module."""
from datetime import datetime

import numpy as np
import networkx as nx

from tel2puml.sequence_otel import (
    Span, Trace, get_slice_indexes, has_time_overlap
)
from tel2puml.utils import datetime_to_pv_string


def test_has_time_overlap() -> None:
    """Test the `has_time_overlap` function."""
    assert has_time_overlap([1, 3], [2, 3])
    assert has_time_overlap([1, 3], [1, 2])
    assert not has_time_overlap([1, 2], [2, 3])
    assert not has_time_overlap([1, 2], [3, 4])


def test_get_slice_indexes() -> None:
    """Test the `get_slice_indexes` function."""
    time_array = np.array([
        [2, 3], [4, 6], [5, 7], [6, 8]
    ])
    assert get_slice_indexes(time_array) == [0, 1, 4]


class TestSpan:
    """Tests for the `Span` class."""
    @staticmethod
    def test_time_array() -> None:
        """Test the `time_array` method."""
        span = Span("1", "a_span", 2, 3)
        assert list(span.time_array()) == [2, 3]

    @staticmethod
    def test_add_child_span() -> None:
        """Test the `add_child_span` method."""
        span = Span("1", "a_span", 2, 3)
        child_span = Span("2", "a_child_span", 2, 3)
        span.add_child_span(child_span)
        assert span.child_spans["2"] == child_span

    @staticmethod
    def spans_for_test() -> dict[str, Span]:
        """Return a dictionary of spans for testing."""
        span = Span("1", "a_span", 2, 8)
        child_span_1 = Span("2", "a_child_span_1", 2, 3)
        child_span_2 = Span("3", "a_child_span_2", 4, 6)
        child_span_3 = Span("4", "a_child_span_3", 5, 7)
        child_span_4 = Span("5", "a_child_span_4", 6, 8)
        span.add_child_span(child_span_1)
        span.add_child_span(child_span_2)
        span.add_child_span(child_span_3)
        span.add_child_span(child_span_4)
        return {
            "span": span,
            "child_span_1": child_span_1,
            "child_span_2": child_span_2,
            "child_span_3": child_span_3,
            "child_span_4": child_span_4
        }

    def updated_spans_for_test(self) -> dict[str, Span]:
        """Return a dictionary of spans for testing with updated spans."""
        grand_child_span_1 = Span("6", "a_grand_child_span_1", 2, 3)
        grand_child_span_2 = Span("7", "a_grand_child_span_2", 2, 2.5)
        spans_for_test = self.spans_for_test()
        spans_for_test["child_span_1"].add_child_span(grand_child_span_1)
        spans_for_test["child_span_1"].add_child_span(grand_child_span_2)
        spans_for_test["grand_child_span_1"] = grand_child_span_1
        spans_for_test["grand_child_span_2"] = grand_child_span_2
        return spans_for_test

    def test_start_time_order(self) -> None:
        """Test the `start_time_order` method."""
        spans = self.spans_for_test()
        assert spans["span"].start_time_order == [
            spans["child_span_1"], spans["child_span_2"],
            spans["child_span_3"], spans["child_span_4"]
        ]

    def test_child_spans_sequence_order(self) -> None:
        """Test the `child_spans_sequence_order` method."""
        spans = self.spans_for_test()
        assert spans["span"].child_spans_sequence_order() == [
            [spans["child_span_1"]],
            [
                spans[f"child_span_{i}"]
                for i in range(2, 5)
            ]
        ]
        assert spans["span"].child_spans_sequence_order(sync_spans=True) == [
            [spans[f"child_span_{i}"]]
            for i in range(1, 5)
        ]

    def test_update_graph_with_connections(self) -> None:
        """Test the `update_graph_with_connections` method."""
        # check case where child spans have no children
        spans = self.spans_for_test()
        graph: "nx.DiGraph[Span]" = nx.DiGraph()
        spans["span"].update_graph_with_connections(graph)
        assert set(graph.edges) == {
            (spans["child_span_1"], spans["child_span_2"]),
            (spans["child_span_1"], spans["child_span_3"]),
            (spans["child_span_1"], spans["child_span_4"]),
            (spans["child_span_2"], spans["span"]),
            (spans["child_span_3"], spans["span"]),
            (spans["child_span_4"], spans["span"])
        }
        # check purely synchronous case
        graph = nx.DiGraph()
        spans["span"].update_graph_with_connections(graph, sync_spans=True)
        assert set(graph.edges) == {
            (spans["child_span_1"], spans["child_span_2"]),
            (spans["child_span_2"], spans["child_span_3"]),
            (spans["child_span_3"], spans["child_span_4"]),
            (spans["child_span_4"], spans["span"])
        }
        # check case where some child spans have children
        spans = self.updated_spans_for_test()
        graph = nx.DiGraph()
        spans["span"].update_graph_with_connections(graph)
        assert set(graph.edges) == {
            (spans["child_span_1"], spans["child_span_2"]),
            (spans["child_span_1"], spans["child_span_3"]),
            (spans["child_span_1"], spans["child_span_4"]),
            (spans["child_span_2"], spans["span"]),
            (spans["child_span_3"], spans["span"]),
            (spans["child_span_4"], spans["span"]),
            (spans["grand_child_span_1"], spans["child_span_1"]),
            (spans["grand_child_span_2"], spans["child_span_1"])
        }
        # check purely synchronous case
        graph = nx.DiGraph()
        spans["span"].update_graph_with_connections(graph, sync_spans=True)
        assert set(graph.edges) == {
            (spans["child_span_1"], spans["child_span_2"]),
            (spans["child_span_2"], spans["child_span_3"]),
            (spans["child_span_3"], spans["child_span_4"]),
            (spans["child_span_4"], spans["span"]),
            (spans["grand_child_span_1"], spans["child_span_1"]),
            (spans["grand_child_span_2"], spans["child_span_1"])
        }

    def test_to_pv_event(self) -> None:
        """Test the `to_pv_event` method."""
        spans = self.spans_for_test()
        graph: "nx.DiGraph[Span]" = nx.DiGraph()
        spans["span"].update_graph_with_connections(graph)
        output_event = spans["span"].to_pv_event(
            "1", "a_job", graph
        )
        assert output_event == {
            "jobId": "1",
            "eventId": "1",
            "timestamp": datetime_to_pv_string(
                date_time=datetime.fromtimestamp(8*1e-9)
            ),
            "previousEventIds": ["3", "4", "5"],
            "applicationName": "default_app",
            "jobName": "a_job",
            "eventType": "a_span"
        }


class TestTrace:
    """Tests for the `Trace` class."""
    @staticmethod
    def trace_for_test() -> Trace:
        """Return a trace for testing."""
        trace = Trace("1")
        spans_to_add: list[
            tuple[str, str, float, float] |
            tuple[str, str, float, float, str]
        ] = [
            ("1", "a_span", 2, 8),
            ("2", "a_child_span_1", 2, 3, "1"),
            ("3", "a_child_span_2", 4, 6, "1"),
            ("4", "a_child_span_3", 5, 7, "1"),
            ("5", "a_child_span_4", 6, 8, "1")
        ]

        for span_details in spans_to_add:
            trace.add_span(*span_details)
        return trace

    def test_add_span(self) -> None:
        """Test the `add_span` method."""
        # check for simple case
        trace = Trace("1")
        trace.add_span("1", "a_span", 2, 3)
        assert "1" in trace.spans
        span = trace.spans["1"]
        assert isinstance(span, Span)
        assert span.name == "a_span"
        assert span._start_time == 2
        assert span._end_time == 3
        assert span.parent_id is None
        assert span.span_id == "1"
        assert trace.spans["1"] == span
        # check children for trace with multiple spans
        trace = self.trace_for_test()
        assert set(trace.spans["1"].child_spans.values()) == {
            trace.spans["2"], trace.spans["3"],
            trace.spans["4"], trace.spans["5"]
        }
        for span_id in ["2", "3", "4", "5"]:
            assert trace.spans[span_id].child_spans == {}

    def test_root_span(self) -> None:
        """Test the `root_span` property."""
        trace = self.trace_for_test()
        assert trace.root_span == trace.spans["1"]

    def test_yield_pv_event_sequence(self) -> None:
        """Test the `yield_pv_event_sequence` method."""
        trace = self.trace_for_test()
        events = list(trace.yield_pv_event_sequence())
        assert len(events) == 5
        assert events[0] == {
            "jobId": "1",
            "eventId": "1",
            "timestamp": datetime_to_pv_string(
                date_time=datetime.fromtimestamp(8*1e-9)
            ),
            "previousEventIds": ["3", "4", "5"],
            "applicationName": "default_app",
            "jobName": "default_job",
            "eventType": "a_span"
        }
        assert events[1] == {
            "jobId": "1",
            "eventId": "2",
            "timestamp": datetime_to_pv_string(
                date_time=datetime.fromtimestamp(3*1e-9)
            ),
            "previousEventIds": [],
            "applicationName": "default_app",
            "jobName": "default_job",
            "eventType": "a_child_span_1"
        }
        assert events[2] == {
            "jobId": "1",
            "eventId": "3",
            "timestamp": datetime_to_pv_string(
                date_time=datetime.fromtimestamp(6*1e-9)
            ),
            "previousEventIds": ["2"],
            "applicationName": "default_app",
            "jobName": "default_job",
            "eventType": "a_child_span_2"
        }
        assert events[3] == {
            "jobId": "1",
            "eventId": "4",
            "timestamp": datetime_to_pv_string(
                date_time=datetime.fromtimestamp(7*1e-9)
            ),
            "previousEventIds": ["2"],
            "applicationName": "default_app",
            "jobName": "default_job",
            "eventType": "a_child_span_3"
        }
        assert events[4] == {
            "jobId": "1",
            "eventId": "5",
            "timestamp": datetime_to_pv_string(
                date_time=datetime.fromtimestamp(8*1e-9)
            ),
            "previousEventIds": ["2"],
            "applicationName": "default_app",
            "jobName": "default_job",
            "eventType": "a_child_span_4"
        }
        # check case where spans are synchronous
        trace = self.trace_for_test()
        events = list(trace.yield_pv_event_sequence(sync_spans=True))
        assert len(events) == 5
        assert events[0] == {
            "jobId": "1",
            "eventId": "1",
            "timestamp": datetime_to_pv_string(
                date_time=datetime.fromtimestamp(8*1e-9)
            ),
            "previousEventIds": ["5"],
            "applicationName": "default_app",
            "jobName": "default_job",
            "eventType": "a_span"
        }
        assert events[1] == {
            "jobId": "1",
            "eventId": "2",
            "timestamp": datetime_to_pv_string(
                date_time=datetime.fromtimestamp(3*1e-9)
            ),
            "previousEventIds": [],
            "applicationName": "default_app",
            "jobName": "default_job",
            "eventType": "a_child_span_1"
        }
        assert events[2] == {
            "jobId": "1",
            "eventId": "3",
            "timestamp": datetime_to_pv_string(
                date_time=datetime.fromtimestamp(6*1e-9)
            ),
            "previousEventIds": ["2"],
            "applicationName": "default_app",
            "jobName": "default_job",
            "eventType": "a_child_span_2"
        }
        assert events[3] == {
            "jobId": "1",
            "eventId": "4",
            "timestamp": datetime_to_pv_string(
                date_time=datetime.fromtimestamp(7*1e-9)
            ),
            "previousEventIds": ["3"],
            "applicationName": "default_app",
            "jobName": "default_job",
            "eventType": "a_child_span_3"
        }
        assert events[4] == {
            "jobId": "1",
            "eventId": "5",
            "timestamp": datetime_to_pv_string(
                date_time=datetime.fromtimestamp(8*1e-9)
            ),
            "previousEventIds": ["4"],
            "applicationName": "default_app",
            "jobName": "default_job",
            "eventType": "a_child_span_4"
        }
