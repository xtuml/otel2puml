"""Configuration for the tests in the puml_graph package.
"""
import pytest

from tel2puml.puml_graph import (
    PUMLGraph,
    PUMLEventNode,
    PUMLOperatorNode,
)
from tel2puml.tel2puml_types import PUMLOperator, PUMLEvent
from tel2puml.loop_detection.loop_types import DUMMY_BREAK_EVENT_TYPE


@pytest.fixture
def puml_graph() -> tuple[PUMLGraph, dict[tuple[str, int], PUMLEventNode]]:
    """Return a PUMLGraph instance.

    The graph paths are as follows:
    ```
    A -> AND -> XOR1 -> B0 -> D0 -> XOR1 -> AND -> F
    A -> AND -> XOR1 -> C0 -> E0 -> XOR1 -> AND -> F
    A -> AND -> XOR2 -> B1 -> D1 -> XOR2 -> AND -> F
    A -> AND -> XOR2 -> C1 -> E1 -> XOR2 -> AND -> F
    A -> AND -> G -> H -> I -> AND -> F
    ```
    :return: PUMLGraph instance
    :rtype: :class:`PUMLGraph`
    """
    graph = PUMLGraph()
    event_nodes: dict[tuple[str, int], PUMLEventNode] = {}
    event_nodes[("A", 0)] = graph.create_event_node(
        "A", parent_graph_node="q0"
    )
    and_start, and_end = graph.create_operator_node_pair(PUMLOperator.AND)
    xor_start_1, xor_end_1 = graph.create_operator_node_pair(PUMLOperator.XOR)
    event_nodes[("B", 0)] = graph.create_event_node(
        "B", parent_graph_node="q1"
    )
    event_nodes[("C", 0)] = graph.create_event_node(
        "C", parent_graph_node="q2"
    )
    event_nodes[("D", 0)] = graph.create_event_node(
        "D", parent_graph_node="q3"
    )
    event_nodes[("E", 0)] = graph.create_event_node(
        "E", parent_graph_node="q4"
    )
    xor_start_2, xor_end_2 = graph.create_operator_node_pair(PUMLOperator.XOR)
    event_nodes[("B", 1)] = graph.create_event_node(
        "B", parent_graph_node="q1"
    )
    event_nodes[("C", 1)] = graph.create_event_node(
        "C", parent_graph_node="q2"
    )
    event_nodes[("D", 1)] = graph.create_event_node(
        "D", parent_graph_node="q3"
    )
    event_nodes[("E", 1)] = graph.create_event_node(
        "E", parent_graph_node="q4"
    )
    event_nodes[("G", 0)] = graph.create_event_node(
        "G", parent_graph_node="q5"
    )
    event_nodes[("H", 0)] = graph.create_event_node(
        "H", parent_graph_node="q6"
    )
    event_nodes[("I", 0)] = graph.create_event_node(
        "I", parent_graph_node="q7"
    )
    event_nodes[("F", 0)] = graph.create_event_node(
        "F", parent_graph_node="q8"
    )
    graph.add_puml_edge(event_nodes[("A", 0)], and_start)
    graph.add_puml_edge(and_start, xor_start_1)
    graph.add_puml_edge(and_start, xor_start_2)
    graph.add_puml_edge(and_start, event_nodes[("G", 0)])
    graph.add_puml_edge(xor_start_1, event_nodes[("B", 0)])
    graph.add_puml_edge(xor_start_1, event_nodes[("C", 0)])
    graph.add_puml_edge(event_nodes[("B", 0)], event_nodes[("D", 0)])
    graph.add_puml_edge(event_nodes[("C", 0)], event_nodes[("E", 0)])
    graph.add_puml_edge(event_nodes[("D", 0)], xor_end_1)
    graph.add_puml_edge(event_nodes[("E", 0)], xor_end_1)
    graph.add_puml_edge(xor_start_2, event_nodes[("B", 1)])
    graph.add_puml_edge(xor_start_2, event_nodes[("C", 1)])
    graph.add_puml_edge(event_nodes[("B", 1)], event_nodes[("D", 1)])
    graph.add_puml_edge(event_nodes[("C", 1)], event_nodes[("E", 1)])
    graph.add_puml_edge(event_nodes[("D", 1)], xor_end_2)
    graph.add_puml_edge(event_nodes[("E", 1)], xor_end_2)
    graph.add_puml_edge(event_nodes[("G", 0)], event_nodes[("H", 0)])
    graph.add_puml_edge(event_nodes[("H", 0)], event_nodes[("I", 0)])
    graph.add_puml_edge(xor_end_1, and_end)
    graph.add_puml_edge(xor_end_2, and_end)
    graph.add_puml_edge(event_nodes[("I", 0)], and_end)
    graph.add_puml_edge(and_end, event_nodes[("F", 0)])
    return graph, event_nodes


@pytest.fixture
def graph_with_dummy_break_event(
) -> tuple[PUMLGraph, dict[str, PUMLEventNode | PUMLOperatorNode]]:
    """Return a PUMLGraph instance with a dummy break event.

    The graph is as follows:
    ```
    START -> A -> XOR_START_1 -> B -> XOR_END_1
    START -> A -> XOR_START_1 -> XOR_START_2 -> C -> XOR_END_2 -> XOR_END_1
    START -> A -> XOR_START_1 -> XOR_START_2 -> DUMMY_BREAK_EVENT -> XOR_END_2\
    -> XOR_END_1
    ```
    :return: PUMLGraph instance
    :rtype: :class:`PUMLGraph`
    """
    graph = PUMLGraph()
    START = graph.create_event_node(
        "START", parent_graph_node="START"
    )
    A = graph.create_event_node(
        "A", parent_graph_node="A"
    )
    XOR_START_1, XOR_END_1 = graph.create_operator_node_pair(PUMLOperator.XOR)
    B = graph.create_event_node("B", parent_graph_node="B")
    XOR_START_2, XOR_END_2 = graph.create_operator_node_pair(PUMLOperator.XOR)
    C = graph.create_event_node("C", parent_graph_node="C")
    DUMMY_BREAK_EVENT = graph.create_event_node(
        DUMMY_BREAK_EVENT_TYPE, event_types=PUMLEvent.BREAK
    )
    graph.add_puml_edge(START, A)
    graph.add_puml_edge(A, XOR_START_1)
    graph.add_puml_edge(XOR_START_1, B)
    graph.add_puml_edge(XOR_START_1, XOR_START_2)
    graph.add_puml_edge(B, XOR_END_1)
    graph.add_puml_edge(XOR_START_2, C)
    graph.add_puml_edge(XOR_START_2, DUMMY_BREAK_EVENT)
    graph.add_puml_edge(C, XOR_END_2)
    graph.add_puml_edge(XOR_END_1, XOR_END_2)
    graph.add_puml_edge(DUMMY_BREAK_EVENT, XOR_END_2)
    nodes: dict[str, PUMLEventNode | PUMLOperatorNode] = {
        "START": START,
        "A": A,
        "B": B,
        "C": C,
        DUMMY_BREAK_EVENT_TYPE: DUMMY_BREAK_EVENT,
        "XOR_START_1": XOR_START_1,
        "XOR_END_1": XOR_END_1,
        "XOR_START_2": XOR_START_2,
        "XOR_END_2": XOR_END_2
    }
    return graph, nodes
