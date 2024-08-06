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

    def check_loop_event_for_uids(
        self,
        loop_event: LoopEvent,
        start_event: Event,
        end_event: Event,
        break_events: set[Event],
    ) -> None:
        """Check the sub graph and loop event for the uids of the events."""
        assert loop_event.start_uid == start_event.uid
        assert loop_event.end_uid == end_event.uid
        assert loop_event.break_uids == {event.uid for event in break_events}

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
            if LOOP_EVENT_TYPE in node.event_type:
                assert isinstance(node, LoopEvent)
                loop_event_num += 1
                loop_graph = node.sub_graph
                start_event = None
                end_event = None
                for sub_node in loop_graph.nodes:
                    if sub_node.event_type == "A":
                        loop_a_b = loop_graph
                    if sub_node.event_type == "C":
                        loop_c_d = loop_graph
                    if sub_node.event_type == DUMMY_START_EVENT:
                        start_event = sub_node
                    if sub_node.event_type == DUMMY_END_EVENT:
                        end_event = sub_node
                assert start_event is not None
                assert end_event is not None
                self.check_loop_event_for_uids(
                    node, start_event, end_event, set()
                )
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
        loop_event_name = LOOP_EVENT_TYPE + "_1"
        assert set(events_dict.keys()) == {
            DUMMY_START_EVENT, DUMMY_END_EVENT, "A", "B", "C", "M", "J", "K",
            "L", "N", "O", "P", loop_event_name,
        }
        self.check_edges_and_event_sets(
            graph,
            [
                (events_dict[DUMMY_START_EVENT], events_dict["A"]),
                (events_dict["A"], events_dict["M"]),
                (events_dict["M"], events_dict["J"]),
                (events_dict["A"], events_dict["B"]),
                (events_dict["A"], events_dict["C"]),
                (events_dict["B"], events_dict[loop_event_name]),
                (events_dict["C"], events_dict[loop_event_name]),
                (events_dict[loop_event_name], events_dict["J"]),
                (events_dict[loop_event_name], events_dict["K"]),
                (events_dict[loop_event_name], events_dict["L"]),
                (events_dict[loop_event_name], events_dict["O"]),
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
                (1, 1), (1, 1)
            ],
        )
        # check loop event and subgraph
        """After detecting loops the sub graph of the loop should be as shown
        in the diagram in the following link:

        `tests/loop_detection/loop_test_graph_loop_sub_graph.svg`
        """
        loop_event = events_dict[loop_event_name]
        assert isinstance(loop_event, LoopEvent)
        loop_sub_graph = loop_event.sub_graph
        loop_sub_graph_events: dict[str, Event] = {
            event.event_type: event for event in loop_sub_graph.nodes
        }
        assert len(loop_sub_graph.nodes) == 9
        assert set(loop_sub_graph_events.keys()) == {
            DUMMY_START_EVENT, DUMMY_END_EVENT,
            "D", "E", "F", "G", "N", "M", loop_event_name,
        }
        dummy_end_loop = loop_sub_graph_events[DUMMY_END_EVENT]
        # check uids of loop event
        self.check_loop_event_for_uids(
            loop_event, loop_sub_graph_events[DUMMY_START_EVENT],
            dummy_end_loop, {
                loop_sub_graph_events["M"], loop_sub_graph_events["N"],
            }
        )
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
                    loop_sub_graph_events[loop_event_name],
                ),
                (loop_sub_graph_events[loop_event_name], dummy_end_loop),
                (loop_sub_graph_events["G"], loop_sub_graph_events["M"]),
                (loop_sub_graph_events["F"], loop_sub_graph_events["N"]),
            ],
            [(1, 2)] + [(1, 1)] * 9,
        )
        # check check loop event of sub graph and its sub graph
        """After detecting loops the sub graph of the loop in the sub graph
         i.e. nested loop, should be as shown in the diagram in the
         following link:

        `tests/loop_detection/loop_test_graph_loop_sub_graph_sub_graph.svg`
        """
        sub_graph_loop_event = loop_sub_graph_events[loop_event_name]
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
        # check uids of loop event
        self.check_loop_event_for_uids(
            sub_graph_loop_event,
            sub_graph_loop_sub_graph_events[DUMMY_START_EVENT],
            sub_graph_loop_sub_graph_events[DUMMY_END_EVENT],
            set()
        )
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
        loop_event_name = LOOP_EVENT_TYPE + "_1"
        events_dict = {event.event_type: event for event in graph.nodes}
        assert set(events_dict.keys()) == {
            DUMMY_START_EVENT, loop_event_name,
        }
        self.check_edges_and_event_sets(
            graph,
            [
                (events_dict[DUMMY_START_EVENT], events_dict[loop_event_name]),
            ],
            [(1, 1)],
        )
        loop_event = events_dict[loop_event_name]
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
        # check uid of loop event
        self.check_loop_event_for_uids(
            loop_event, loop_sub_graph_events[DUMMY_START_EVENT],
            loop_sub_graph_events[DUMMY_END_EVENT], set()
        )
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
