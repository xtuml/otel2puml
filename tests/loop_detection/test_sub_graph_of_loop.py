"""Tests for the sub_graph_of_loop module"""
from networkx import DiGraph

from tel2puml.events import Event, EventSet
from tel2puml.loop_detection.loop_types import Loop, EventEdge
from tel2puml.loop_detection.sub_graph_of_loop import (
    remove_event_sets_mirroring_removed_edges,
    remove_event_edges_and_event_sets,
    remove_loop_edges
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
