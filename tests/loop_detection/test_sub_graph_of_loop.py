"""Tests for the sub_graph_of_loop module"""
from networkx import DiGraph

import pytest

from tel2puml.events import Event, EventSet
from tel2puml.tel2puml_types import DUMMY_START_EVENT, DUMMY_END_EVENT
from tel2puml.loop_detection.loop_types import Loop, EventEdge
from tel2puml.loop_detection.sub_graph_of_loop import (
    remove_event_sets_mirroring_removed_edges,
    remove_event_edges_and_event_sets,
    remove_loop_edges,
    get_disconnected_loop_sub_graph,
    create_start_event,
    create_end_event,
    add_start_and_end_events_to_sub_graph
)


class TestsRemoveEdgesAndEventSets:
    """Group of tests for removal of edges and event sets:

    * remove_event_sets_mirroring_removed_edges
    * remove_event_edges_and_event_sets
    """
    @staticmethod
    def graph_and_events() -> tuple["DiGraph[Event]", dict[str, Event]]:
        """Create a graph for testing"""
        graph: "DiGraph[Event]" = DiGraph()
        A = Event("A")
        B = Event("B")
        C = Event("C")
        D = Event("D")
        E = Event("E")
        F = Event("F")
        G = Event("G")
        graph.add_edge(A, B)
        graph.add_edge(A, C)
        graph.add_edge(B, D)
        graph.add_edge(C, D)
        graph.add_edge(D, E)
        graph.add_edge(B, F)
        graph.add_edge(F, G)
        graph.add_edge(G, E)
        graph.add_edge(D, A)
        for edge in graph.edges:
            if not edge[0].event_type == "A":
                edge[0].update_event_sets([edge[1].event_type])
            edge[1].update_in_event_sets([edge[0].event_type])
        A.update_event_sets(["B", "C"])
        return graph, {
            "A": A,
            "B": B,
            "C": C,
            "D": D,
            "E": E,
            "F": F,
            "G": G,
        }

    def test_remove_event_sets_mirroring_removed_edges(self) -> None:
        """Test the removal of event sets that mirror the removal of edges."""
        _, events = self.graph_and_events()
        # Test removing a single event edge from the graph
        assert events["A"].in_event_sets == {EventSet(["D"])}
        assert events["D"].event_sets == {EventSet(["E"]), EventSet(["A"])}
        remove_event_sets_mirroring_removed_edges(
            [EventEdge(events["D"], events["A"])]
        )
        assert events["A"].in_event_sets == set()
        assert events["D"].event_sets == {EventSet(["E"])}
        # test removing an event sets that are asynchronous events
        assert events["A"].event_sets == {EventSet(["B", "C"])}
        assert events["B"].in_event_sets == {EventSet(["A"])}
        assert events["C"].in_event_sets == {EventSet(["A"])}
        remove_event_sets_mirroring_removed_edges(
            [EventEdge(events["A"], events["B"])]
        )
        assert events["A"].event_sets == set()
        assert events["B"].in_event_sets == set()
        assert events["C"].in_event_sets == {EventSet(["A"])}

    def test_remove_event_edges_and_event_sets(self) -> None:
        """Test the removal of event edges and event sets."""
        graph, events = self.graph_and_events()
        # Test removing a single event edge from the graph
        assert events["A"].in_event_sets == {EventSet(["D"])}
        assert events["D"].event_sets == {EventSet(["E"]), EventSet(["A"])}
        remove_event_edges_and_event_sets(
            [EventEdge(events["D"], events["A"])],
            graph,
        )
        assert events["A"].in_event_sets == set()
        assert events["D"].event_sets == {EventSet(["E"])}
        assert EventEdge(events["D"], events["A"]) not in graph.edges()
        # test removing an event sets that are asynchronous events
        assert events["A"].event_sets == {EventSet(["B", "C"])}
        assert events["B"].in_event_sets == {EventSet(["A"])}
        assert events["C"].in_event_sets == {EventSet(["A"])}
        remove_event_edges_and_event_sets(
            [EventEdge(events["A"], events["B"])],
            graph,
        )
        assert events["A"].event_sets == set()
        assert events["B"].in_event_sets == set()
        assert events["C"].in_event_sets == {EventSet(["A"])}
        assert EventEdge(events["A"], events["B"]) not in graph.edges()

    def test_remove_loop_edges(self) -> None:
        """Test the removal of loop edges and event sets."""
        graph, events = self.graph_and_events()
        loop = Loop(
            loop_events={events["A"], events["B"], events["C"], events["D"]},
            start_events={events["A"]},
            end_events={events["D"]},
            break_events={events["G"]},
            edges_to_remove={EventEdge(events["D"], events["A"])},
        )
        # add edge from outside loop to start of loop
        X = Event("X")
        graph.add_edge(X, events["A"])
        X.update_event_sets(["A"])
        events["A"].update_in_event_sets(["X"])
        # pre-removal checks
        assert events["A"].in_event_sets == {EventSet(["D"]), EventSet(["X"])}
        assert events["D"].event_sets == {EventSet(["E"]), EventSet(["A"])}
        assert events["G"].event_sets == {EventSet(["E"])}
        assert events["E"].in_event_sets == {EventSet(["D"]), EventSet(["G"])}
        assert EventEdge(events["D"], events["A"]) in graph.edges()
        assert EventEdge(events["G"], events["E"]) in graph.edges()
        assert EventEdge(events["D"], events["E"]) in graph.edges()
        assert EventEdge(X, events["A"]) in graph.edges()
        remove_loop_edges(loop, graph)
        # check all correct event sets removed
        assert events["A"].in_event_sets == set()
        assert events["G"].event_sets == set()
        assert events["E"].event_sets == set()
        assert events["D"].event_sets == set()
        # check all edges removed
        assert EventEdge(events["D"], events["A"]) not in graph.edges()
        assert EventEdge(events["G"], events["E"]) not in graph.edges()
        assert EventEdge(events["D"], events["E"]) not in graph.edges()
        assert EventEdge(X, events["A"]) not in graph.edges()

    @staticmethod
    def disconnected_graph() -> "DiGraph[str]":
        """Create a graph with diconnected components."""
        graph: "DiGraph[str]" = DiGraph()
        graph.add_edge("A", "B")
        graph.add_edge("B", "C")
        graph.add_edge("X", "Y")
        graph.add_edge("B", "E")
        graph.add_edge("A", "G")
        graph.add_edge("G", "H")
        graph.add_edge("D", "F")
        return graph

    def test_get_disconnected_loop_sub_graph(self) -> None:
        """Test the creation of a sub graph from a loop."""
        # check normal case
        graph = self.disconnected_graph()
        graph = get_disconnected_loop_sub_graph({"A", "B", "C"}, graph)
        assert set(graph.nodes) == {"A", "B", "C", "E", "G", "H"}
        assert set(graph.edges) == {
            ("A", "B"), ("B", "C"), ("B", "E"), ("G", "H"), ("A", "G")
        }
        # check case where input scc_nodes is not a subset of the graph
        graph = self.disconnected_graph()
        with pytest.raises(ValueError):
            get_disconnected_loop_sub_graph({"M", "N"}, graph)


class TestAddStartAndEndEventsToSubGraph:
    """Group of tests for adding start and end events to a sub graph"""
    @staticmethod
    def graph_events_loop() -> tuple["DiGraph[Event]", dict[str, Event], Loop]:
        """Create a graph for testing"""
        graph: "DiGraph[Event]" = DiGraph()
        A = Event("A")
        B = Event("B")
        C = Event("C")
        D = Event("D")
        E = Event("E")
        F = Event("F")
        G = Event("G")
        H = Event("H")
        I_ = Event("I")
        J = Event("J")
        K = Event("K")
        L = Event("L")
        graph.add_edge(A, C)
        graph.add_edge(C, D)
        graph.add_edge(D, E)
        graph.add_edge(B, F)
        graph.add_edge(B, G)
        graph.add_edge(F, H)
        graph.add_edge(G, H)
        graph.add_edge(H, D)
        graph.add_edge(H, I_)
        graph.add_edge(I_, J)
        graph.add_edge(D, J)
        graph.add_edge(J, K)
        graph.add_edge(E, K)
        # a loop backs
        graph.add_edge(E, C)
        graph.add_edge(I_, F)
        graph.add_edge(I_, G)
        graph.add_edge(J, F)
        graph.add_edge(J, G)
        # add break path
        graph.add_edge(D, L)
        graph.add_edge(L, K)
        for node in graph.nodes:
            if node.event_type == "B":
                node.update_event_sets(["F", "G"])
                continue
            if node.event_type == "H":
                node.update_in_event_sets(["F", "G"])
                node.update_event_sets(["D"])
                node.update_in_event_sets(["I"])
                continue
            if node.event_type == "I":
                node.update_in_event_sets(["H"])
                node.update_event_sets(["J"])
                node.update_event_sets(["F", "G"])
                continue
            if node.event_type == "J":
                node.update_in_event_sets(["I"])
                node.update_in_event_sets(["D"])
                node.update_event_sets(["K"])
                node.update_event_sets(["F", "G"])
                continue
            for in_edge in graph.in_edges(node):
                node.update_in_event_sets([in_edge[0].event_type])
            for out_edge in graph.out_edges(node):
                node.update_event_sets([out_edge[1].event_type])
        loop = Loop(
            loop_events={C, D, E, F, G, H, I_, J},
            start_events={C, F, G},
            end_events={E, I_, J},
            break_events=set(),
            edges_to_remove={
                EventEdge(E, C),
                EventEdge(I_, F),
                EventEdge(I_, G),
                EventEdge(J, F),
                EventEdge(J, G)
            }
        )
        return graph, {
            "A": A,
            "B": B,
            "C": C,
            "D": D,
            "E": E,
            "F": F,
            "G": G,
            "H": H,
            "I": I_,
            "J": J,
            "K": K,
            "L": L,
        }, loop

    def test_create_start_event(self) -> None:
        """Test the creation of a start event."""
        graph, _, loop = self.graph_events_loop()
        start_event = create_start_event(loop, graph)
        assert start_event.event_type == DUMMY_START_EVENT
        assert start_event.in_event_sets == set()
        assert start_event.event_sets == {
            EventSet(["F", "G"]),
            EventSet(["C"]),
        }

    def test_create_end_event(self) -> None:
        """Test the creation of an end event."""
        graph, _, loop = self.graph_events_loop()
        end_event = create_end_event(loop, graph)
        assert end_event.event_type == DUMMY_END_EVENT
        assert end_event.in_event_sets == {
            EventSet(["E"]),
            EventSet(["I"]),
            EventSet(["J"]),
        }
        assert end_event.event_sets == set()

    def test_add_start_and_end_events_to_sub_graph(self) -> None:
        """Test the addition of start and end events to a sub graph."""
        graph, events, loop = self.graph_events_loop()
        add_start_and_end_events_to_sub_graph(loop, graph)
        start_event = next(
            node
            for node in graph.nodes
            if node.event_type == DUMMY_START_EVENT
        )
        end_event = next(
            node for node in graph.nodes if node.event_type == DUMMY_END_EVENT
        )
        assert set(graph.nodes) == {node for node in events.values()} | {
            start_event,
            end_event,
        }
        assert set(graph.out_edges(start_event)) == {
            (start_event, events["C"]),
            (start_event, events["F"]),
            (start_event, events["G"]),
        }
        assert set(graph.in_edges(start_event)) == set()
        assert set(graph.in_edges(end_event)) == {
            (events["E"], end_event),
            (events["I"], end_event),
            (events["J"], end_event),
        }
        assert set(graph.out_edges(end_event)) == set()
        assert start_event.event_sets == {
            EventSet(["F", "G"]),
            EventSet(["C"]),
        }
        assert end_event.in_event_sets == {
            EventSet(["E"]),
            EventSet(["I"]),
            EventSet(["J"]),
        }
        assert end_event.event_sets == set()
