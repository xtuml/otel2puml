"""Tests the loop event methods module."""

from networkx import DiGraph

from tel2puml.events import EventSet, Event
from tel2puml.loop_detection.loop_types import Loop, LoopEvent, LOOP_EVENT_TYPE
from tel2puml.loop_detection.loop_event_methods import (
    get_event_lists_to_add_from_event_not_within_loop,
    get_loop_in_event_lists_not_within_loop,
    get_loop_out_event_lists_not_within_loop,
    update_loop_event_in_event_sets,
    update_loop_event_out_event_sets,
    get_new_loop_event_type_from_graph,
    create_loop_event
)


class TestCreateLoopEvent:
    """Tests the create loop event method."""
    @staticmethod
    def loop_event_types() -> set[str]:
        """The loop event types."""
        return {
            "B",
            "C",
        }

    def loop_and_graph(
        self,
    ) -> tuple[Loop, "DiGraph[Event]"]:
        """The loop events and graph."""
        A = Event("A")
        B = Event("B")
        C = Event("C")
        D = Event("D")
        E = Event("E")
        graph: "DiGraph[Event]" = DiGraph()
        graph.add_edge(A, B)
        graph.add_edge(B, C)
        graph.add_edge(B, D)
        graph.add_edge(D, E)
        graph.add_edge(C, E)
        graph.add_edge(C, B)
        for node in graph.nodes:
            for edge in graph.in_edges(node):
                node.update_in_event_sets([edge[0].event_type])
            for edge in graph.out_edges(node):
                node.update_event_sets([edge[1].event_type])
        return (
            Loop(
                loop_events={B, C},
                start_events={B},
                end_events={C},
                break_events={D},
                edges_to_remove=set(),
            ),
            graph,
        )

    def test_get_new_loop_event_type_from_graph(self) -> None:
        """Tests the get new loop event type from graph method."""
        _, graph = self.loop_and_graph()
        assert (
            get_new_loop_event_type_from_graph(graph) == f"{LOOP_EVENT_TYPE}_1"
        )
        loop_1 = LoopEvent(f"{LOOP_EVENT_TYPE}_1", graph)
        graph.add_node(loop_1)
        assert (
            get_new_loop_event_type_from_graph(graph) == f"{LOOP_EVENT_TYPE}_2"
        )

    def test_get_event_lists_to_add_from_event_not_within_loop(self) -> None:
        """Tests the get event lists to add from event not within loop method.
        """
        event_sets = {
            EventSet(["A", "B"]),
            EventSet(["C"]),
            EventSet(["D", "E"]),
            EventSet(["F"]),
        }
        assert {
            EventSet(event_list)
            for event_list in
            get_event_lists_to_add_from_event_not_within_loop(
                event_sets, self.loop_event_types()
            )
        } == {
            EventSet(["D", "E"]),
            EventSet(["F"]),
        }

    def test_get_loop_in_event_lists_not_within_loop(self) -> None:
        """Tests the get loop in event lists not within loop method."""
        loop, _ = self.loop_and_graph()
        assert {
            EventSet(event_list)
            for event_list in get_loop_in_event_lists_not_within_loop(
                loop.start_events, self.loop_event_types()
            )
        } == {
            EventSet(["A"]),
        }

    def test_get_loop_out_event_lists_not_within_loop(self) -> None:
        """Tests the get loop out event lists not within loop method."""
        loop, _ = self.loop_and_graph()
        assert {
            EventSet(event_list)
            for event_list in get_loop_out_event_lists_not_within_loop(
                loop.end_events, self.loop_event_types()
            )
        } == {
            EventSet(["E"]),
        }

    def test_update_loop_event_in_event_sets(self) -> None:
        """Tests the update loop event in event sets method."""
        loop, _ = self.loop_and_graph()
        sub_graph: "DiGraph[Event]" = DiGraph()
        loop_event = LoopEvent("LOOP", sub_graph)
        update_loop_event_in_event_sets(
            loop.start_events, loop_event, self.loop_event_types()
        )
        assert loop_event.in_event_sets == {EventSet(["A"])}

    def test_update_loop_event_out_event_sets(self) -> None:
        """Tests the update loop event out event sets method."""
        loop, _ = self.loop_and_graph()
        sub_graph: "DiGraph[Event]" = DiGraph()
        loop_event = LoopEvent("LOOP", sub_graph)
        update_loop_event_out_event_sets(
            loop.end_events | loop.break_events,
            loop_event,
            self.loop_event_types(),
        )
        assert loop_event.event_sets == {EventSet(["E"])}

    def test_create_loop_event(self) -> None:
        """Tests the create loop event method."""
        loop, graph = self.loop_and_graph()
        loop_event = create_loop_event(loop, graph, graph)
        assert loop_event.in_event_sets == {EventSet(["A"])}
        assert loop_event.event_sets == {EventSet(["E"])}
        assert loop_event.event_type == LOOP_EVENT_TYPE
