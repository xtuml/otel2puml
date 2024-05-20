"""Module to help sequence OTel traces to pv event sequences"""
import numpy as np
import numba as nb


@nb.jit(nopython=True)
def get_slice_indexes(
    time_array: np.ndarray
) -> list[int]:
    """Get the indexes of the slices"""
    slice_indexes: list[int] = [0]
    i = 0
    while i < len(time_array):
        if has_time_overlap(time_array[i], time_array[i + 1]):
            pass
        else:
            slice_indexes.append(i + 1)
        i += 1
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
        self, span_id: str, name: str,
        start_time: int, end_time: int, parent_id: str | None = None
    ) -> None:
        self.span_id = span_id
        self.parent_id = parent_id
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.child_spans: dict[str, Span] = {}

    @property
    def start_time_order(self) -> list["Span"]:
        """Return the child spans in start time order"""
        return sorted(
            self.child_spans.values(),
            key=lambda span: span.start_time
        )

    def time_array(self) -> np.ndarray:
        """Return the start and end times as a numpy array"""
        return np.array([self.start_time, self.end_time])

    def add_child_span(self, span: "Span") -> None:
        """Add a child span to the span"""
        self.child_spans[span.span_id] = span

    def child_spans_sequence_order(self) -> list[list["Span"]]:
        """Return the child spans in sequence order"""
        ordered_spans = self.start_time_order
        time_array = np.array([span.time_array() for span in ordered_spans])
        slice_indexes = get_slice_indexes(time_array)
        return [
            ordered_spans[slice_indexes[i]:slice_indexes[i + 1]]
            for i in range(len(slice_indexes) - 1)
        ]

    def sequence_to_child_spans(self) -> list:
        """Recursive method to return the sequence of child spans"""
        return [
            [span.sequence_to_child_spans() for span in sequence]
            for sequence in self.child_spans_sequence_order()
        ] + [self]


class Trace:
    """A trace is a collection of spans"""
    def __init__(self, trace_id: str) -> None:
        self.trace_id = trace_id
        self.spans: dict[str, Span] = {}

    def add_span(self, span: Span) -> None:
        """Add a span to the trace"""
        self.spans[span.span_id] = span

    def update_span_children(self) -> None:
        """Update the children of each span"""
        for span in self.spans.values():
            if span.parent_id is not None:
                self.spans[span.parent_id].add_child_span(span)
