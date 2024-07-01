"""Configuration for loop detection tests."""
import pytest
from networkx import DiGraph

from tel2puml.events import Event
from tel2puml.tel2puml_types import DUMMY_START_EVENT, DUMMY_END_EVENT
from tel2puml.loop_detection.loop_types import Loop, EventEdge


@pytest.fixture
def graph() -> "DiGraph[Event]":
    """Returns a graph with Events."""
    graph: "DiGraph[Event]" = DiGraph()
    start_event = Event(DUMMY_START_EVENT)
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
    M = Event("M")
    N = Event("N")
    O_ = Event("O")
    P = Event("P")
    end_event = Event(DUMMY_END_EVENT)
    # add down stream edges
    graph.add_edge(start_event, A)
    graph.add_edge(A, B)
    graph.add_edge(A, C)
    graph.add_edge(B, D)
    graph.add_edge(B, E)
    graph.add_edge(C, F)
    graph.add_edge(D, G)
    graph.add_edge(E, G)
    graph.add_edge(F, G)
    graph.add_edge(G, H)
    graph.add_edge(G, I_)
    graph.add_edge(H, J)
    graph.add_edge(H, K)
    graph.add_edge(I_, L)
    graph.add_edge(A, M)
    graph.add_edge(M, J)
    graph.add_edge(F, N)
    graph.add_edge(L, N)
    graph.add_edge(N, O_)
    graph.add_edge(L, P)
    graph.add_edge(J, end_event)
    graph.add_edge(K, end_event)
    graph.add_edge(O_, end_event)
    graph.add_edge(P, end_event)
    # add loop back edges
    graph.add_edge(H, D)
    graph.add_edge(H, E)
    graph.add_edge(I_, F)
    # add loop between H and I
    graph.add_edge(H, I_)
    graph.add_edge(I_, H)
    # add event sets to events
    for edge in graph.edges:
        edge[0].update_event_sets([edge[1].event_type])
        edge[1].update_in_event_sets([edge[0].event_type])
    B.update_event_sets(["D", "D"])
    return graph


@pytest.fixture
def events(graph: "DiGraph[Event]") -> dict[str, Event]:
    """Returns a dictionary of events relating to the graph"""
    return {
        event.event_type: event
        for event in graph.nodes
    }


@pytest.fixture
def loop(events: dict[str, Event]) -> Loop:
    """Returns a Loop object for the graph."""
    return Loop(
        loop_events={
            events["D"], events["E"], events["F"], events["G"], events["H"],
            events["I"]
        },
        start_events={events["D"], events["E"], events["F"]},
        end_events={events["H"], events["I"]},
        break_events={events["M"]},
        edges_to_remove={
            EventEdge(events["H"], events["D"]),
            EventEdge(events["H"], events["E"]),
            EventEdge(events["I"], events["F"]),
        },
    )
