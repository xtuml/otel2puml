"""Tests for the detect_loops function in the detect_loops module."""

from networkx import DiGraph

from tel2puml.tel2puml_types import DUMMY_START_EVENT, DUMMY_END_EVENT
from tel2puml.events import Event, EventSet
from tel2puml.loop_detection.loop_types import LOOP_EVENT_TYPE, LoopEvent
from tel2puml.loop_detection.detect_loops import detect_loops


class TestDetectLoops:
    """Tests for the detect_loops function in the detect_loops module."""
    def graph_simple_loops(self) -> "DiGraph[Event]":
        """Creates a graph with simple loops."""
        graph: "DiGraph[Event]" = DiGraph()
        start_event = Event(DUMMY_START_EVENT)
        A = Event("A")
        B = Event("B")
        C = Event("C")
        D = Event("D")
        graph.add_edge(start_event, A)
        graph.add_edge(A, B)
        graph.add_edge(B, A)
        graph.add_edge(B, C)
        graph.add_edge(C, D)
        graph.add_edge(D, C)
        for edge in graph.edges:
            edge[0].update_event_sets([edge[1].event_type])
            edge[1].update_in_event_sets([edge[0].event_type])
        return graph

    def check_seq_event_sub_graph(
        self, sub_graph: "DiGraph[Event]", event_types_to_check: list[str]
    ) -> None:
        """Check the sub graph of a sequence of events for the first test"""
        events_dict = {event.event_type: event for event in sub_graph.nodes}
        assert set(events_dict.keys()) == set(event_types_to_check) | {
            DUMMY_START_EVENT,
            DUMMY_END_EVENT,
        }
        event_types_updated: list[str | None] = (
            [None, DUMMY_START_EVENT]
            + event_types_to_check
            + [DUMMY_END_EVENT, None]
        )
        for event_type, next_event_type, prev_event_type in zip(
            event_types_updated,
            event_types_updated[1:] + [None],
            [None] + event_types_updated[:-1],
        ):
            if event_type is None:
                continue
            event = events_dict[event_type]
            if next_event_type is None:
                assert not event.event_sets
            else:
                assert {EventSet([next_event_type])} == event.event_sets
                assert (event, events_dict[next_event_type]) in sub_graph.edges
            if prev_event_type is None:
                assert not event.in_event_sets
            else:
                assert {EventSet([prev_event_type])} == event.in_event_sets

    def test_detect_loops_simple_loops(self) -> None:
        """Tests the detect_loops method with a graph with simple loops."""
        graph = self.graph_simple_loops()
        graph = detect_loops(graph)
        assert len(graph.nodes) == 3
        start_event_num = 0
        loop_event_num = 0
        loop_a_b = None
        loop_c_d = None
        for node in graph.nodes:
            if node.event_type == DUMMY_START_EVENT:
                start_event_num += 1
            if node.event_type in LOOP_EVENT_TYPE:
                assert isinstance(node, LoopEvent)
                loop_event_num += 1
                loop_graph = node.sub_graph
                for sub_node in loop_graph.nodes:
                    if sub_node.event_type == "A":
                        loop_a_b = loop_graph
                    if sub_node.event_type == "C":
                        loop_c_d = loop_graph
        assert start_event_num == 1
        assert loop_event_num == 2
        # check sub graphs
        assert loop_a_b is not None
        assert loop_c_d is not None
        # check a b sub graph
        self.check_seq_event_sub_graph(loop_a_b, ["A", "B"])
        # check c d sub graph
        self.check_seq_event_sub_graph(loop_c_d, ["C", "D"])

    def check_edges_and_event_sets(
        self, graph: "DiGraph[Event]", edges: list[tuple[Event, Event]],
        event_set_nums: list[tuple[int, int]] | None = None
    ) -> None:
        """Check the edges and event sets of the graph given edges and event
        set nums"""
        if event_set_nums is None:
            event_set_nums = [(1, 1) for _ in edges]
        assert set(graph.edges) == set(edges)
        event_sets_dict: dict[Event, dict[str, set[EventSet]]] = {}
        for edge, event_set_num in zip(edges, event_set_nums):
            if edge[0] not in event_sets_dict:
                event_sets_dict[edge[0]] = {
                    "event_sets": set(),
                    "in_event_sets": set(),
                }
            if edge[1] not in event_sets_dict:
                event_sets_dict[edge[1]] = {
                    "event_sets": set(),
                    "in_event_sets": set(),
                }
            for i in range(event_set_num[1]):
                event_sets_dict[edge[0]]["event_sets"].add(
                    EventSet([edge[1].event_type] * (i + 1))
                )
            for i in range(event_set_num[0]):
                event_sets_dict[edge[1]]["in_event_sets"].add(
                    EventSet([edge[0].event_type] * (i + 1))
                )
        for event, event_sets in event_sets_dict.items():
            assert event_sets["event_sets"] == event.event_sets
            assert event_sets["in_event_sets"] == event.in_event_sets

    def test_detect_loops_nested(self, graph: "DiGraph[Event]") -> None:
        """Tests the detect_loops method with a graph with nested loops."""
        graph = detect_loops(graph)
        assert len(graph.nodes) == 13
        events_dict = {event.event_type: event for event in graph.nodes}
        # check top level graph
        """After detecting loops the top level graph should be as show in the
        diagram in the following link:

        `tests/loop_detection/loop_test_graph_parent.svg`
        """
        assert set(events_dict.keys()) == {
            DUMMY_START_EVENT, DUMMY_END_EVENT, "A", "B", "C", "M", "J", "K",
            "L", "N", "O", "P", LOOP_EVENT_TYPE,
        }
        self.check_edges_and_event_sets(
            graph,
            [
                (events_dict[DUMMY_START_EVENT], events_dict["A"]),
                (events_dict["A"], events_dict["M"]),
                (events_dict["M"], events_dict["J"]),
                (events_dict["A"], events_dict["B"]),
                (events_dict["A"], events_dict["C"]),
                (events_dict["B"], events_dict[LOOP_EVENT_TYPE]),
                (events_dict["C"], events_dict[LOOP_EVENT_TYPE]),
                (events_dict[LOOP_EVENT_TYPE], events_dict["J"]),
                (events_dict[LOOP_EVENT_TYPE], events_dict["K"]),
                (events_dict[LOOP_EVENT_TYPE], events_dict["L"]),
                (events_dict["L"], events_dict["N"]),
                (events_dict["L"], events_dict["P"]),
                (events_dict["N"], events_dict["O"]),
                (events_dict["P"], events_dict[DUMMY_END_EVENT]),
                (events_dict["O"], events_dict[DUMMY_END_EVENT]),
                (events_dict["J"], events_dict[DUMMY_END_EVENT]),
                (events_dict["K"], events_dict[DUMMY_END_EVENT]),
            ],
            [
                (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 2), (1, 1), (1, 1),
                (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1),
                (1, 1),
            ],
        )
        # check loop event and subgraph
        """After detecting loops the sub graph of the loop should be as shown
        in the diagram in the following link:

        `tests/loop_detection/loop_test_graph_loop_sub_graph.svg`
        """
        loop_event = events_dict[LOOP_EVENT_TYPE]
        assert isinstance(loop_event, LoopEvent)
        loop_sub_graph = loop_event.sub_graph
        loop_sub_graph_events: dict[str, Event] = {}
        end_event_counter = 0
        for event in loop_sub_graph.nodes:
            if event.event_type == DUMMY_END_EVENT:
                loop_sub_graph_events[
                    f"{event.event_type}_{end_event_counter}"
                ] = event
                end_event_counter += 1
            else:
                loop_sub_graph_events[event.event_type] = event
        assert len(loop_sub_graph.nodes) == 11
        assert set(loop_sub_graph_events.keys()) == {
            DUMMY_START_EVENT, DUMMY_END_EVENT + "_0", DUMMY_END_EVENT + "_1",
            "D", "E", "F", "G", "N", "O", "M", LOOP_EVENT_TYPE,
        }
        # check dummy end events
        dummy_end_events = [
            loop_sub_graph_events[DUMMY_END_EVENT + f"_{i}"]
            for i in range(end_event_counter)
        ]
        dummy_end_loop = [
            event
            for event in dummy_end_events
            if event.in_event_sets == {EventSet([LOOP_EVENT_TYPE])}
        ][0]
        dummy_end_from_o = [
            event for event in dummy_end_events if event != dummy_end_loop
        ][0]
        self.check_edges_and_event_sets(
            loop_sub_graph,
            [
                (
                    loop_sub_graph_events[DUMMY_START_EVENT],
                    loop_sub_graph_events["D"],
                ),
                (
                    loop_sub_graph_events[DUMMY_START_EVENT],
                    loop_sub_graph_events["E"],
                ),
                (
                    loop_sub_graph_events[DUMMY_START_EVENT],
                    loop_sub_graph_events["F"],
                ),
                (loop_sub_graph_events["D"], loop_sub_graph_events["G"]),
                (loop_sub_graph_events["E"], loop_sub_graph_events["G"]),
                (loop_sub_graph_events["F"], loop_sub_graph_events["G"]),
                (
                    loop_sub_graph_events["G"],
                    loop_sub_graph_events[LOOP_EVENT_TYPE],
                ),
                (loop_sub_graph_events[LOOP_EVENT_TYPE], dummy_end_loop),
                (loop_sub_graph_events["G"], loop_sub_graph_events["M"]),
                (loop_sub_graph_events["F"], loop_sub_graph_events["N"]),
                (loop_sub_graph_events["N"], loop_sub_graph_events["O"]),
                (loop_sub_graph_events["O"], dummy_end_from_o),
            ],
            [(1, 2)] + [(1, 1)] * 11,
        )
        # check check loop event of sub graph and its sub graph
        """After detecting loops the sub graph of the loop in the sub graph
         i.e. nested loop, should be as shown in the diagram in the
         following link:

        `tests/loop_detection/loop_test_graph_loop_sub_graph_sub_graph.svg`
        """
        sub_graph_loop_event = loop_sub_graph_events[LOOP_EVENT_TYPE]
        assert isinstance(sub_graph_loop_event, LoopEvent)
        sub_graph_loop_sub_graph = sub_graph_loop_event.sub_graph
        sub_graph_loop_sub_graph_events = {
            event.event_type: event for event in sub_graph_loop_sub_graph.nodes
        }
        sub_graph_loop_sub_graph_events = {
            event.event_type: event for event in sub_graph_loop_sub_graph.nodes
        }
        assert len(sub_graph_loop_sub_graph.nodes) == 4
        assert set(sub_graph_loop_sub_graph_events.keys()) == {
            DUMMY_START_EVENT, "H", "I", DUMMY_END_EVENT,
        }
        self.check_edges_and_event_sets(
            sub_graph_loop_sub_graph,
            [
                (
                    sub_graph_loop_sub_graph_events[DUMMY_START_EVENT],
                    sub_graph_loop_sub_graph_events["H"],
                ),
                (
                    sub_graph_loop_sub_graph_events[DUMMY_START_EVENT],
                    sub_graph_loop_sub_graph_events["I"],
                ),
                (
                    sub_graph_loop_sub_graph_events["I"],
                    sub_graph_loop_sub_graph_events[DUMMY_END_EVENT],
                ),
                (
                    sub_graph_loop_sub_graph_events["H"],
                    sub_graph_loop_sub_graph_events[DUMMY_END_EVENT],
                ),
            ],
            [(1, 1)] * 4,
        )

    def test_detect_loops_self_loop(self) -> None:
        """Tests the detect_loops method with a graph with a self loop."""
        graph: "DiGraph[Event]" = DiGraph()
        start_event = Event(DUMMY_START_EVENT)
        A = Event("A")
        graph.add_edge(start_event, A)
        graph.add_edge(A, A)
        for edge in graph.edges:
            edge[0].update_event_sets([edge[1].event_type])
            edge[1].update_in_event_sets([edge[0].event_type])
        graph = detect_loops(graph)
        # check parent graph
        assert len(graph.nodes) == 2
        events_dict = {event.event_type: event for event in graph.nodes}
        assert set(events_dict.keys()) == {
            DUMMY_START_EVENT, LOOP_EVENT_TYPE,
        }
        self.check_edges_and_event_sets(
            graph,
            [
                (events_dict[DUMMY_START_EVENT], events_dict[LOOP_EVENT_TYPE]),
            ],
            [(1, 1)],
        )
        loop_event = events_dict[LOOP_EVENT_TYPE]
        # check loop event and subgraph
        assert isinstance(loop_event, LoopEvent)
        loop_sub_graph = loop_event.sub_graph
        loop_sub_graph_events = {
            event.event_type: event for event in loop_sub_graph.nodes
        }
        assert len(loop_sub_graph.nodes) == 3
        assert set(loop_sub_graph_events.keys()) == {
            DUMMY_START_EVENT, "A", DUMMY_END_EVENT,
        }
        self.check_edges_and_event_sets(
            loop_sub_graph,
            [
                (
                    loop_sub_graph_events[DUMMY_START_EVENT],
                    loop_sub_graph_events["A"],
                ),
                (
                    loop_sub_graph_events["A"],
                    loop_sub_graph_events[DUMMY_END_EVENT],
                ),
            ],
            [(1, 1)] * 2,
        )