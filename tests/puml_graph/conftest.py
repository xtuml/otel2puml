"""Configuration for the tests in the puml_graph package.
"""
import pytest

from tel2puml.puml_graph.graph import PUMLGraph, PUMLEventNode
from tel2puml.tel2puml_types import PUMLOperator
from tel2puml.detect_loops import Loop


@pytest.fixture
def puml_graph() -> tuple[PUMLGraph, dict[tuple[str, int], PUMLEventNode]]:
    """Return a PUMLGraph instance.
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
    graph.add_edge(event_nodes[("A", 0)], and_start)
    graph.add_edge(and_start, xor_start_1)
    graph.add_edge(and_start, xor_start_2)
    graph.add_edge(and_start, event_nodes[("G", 0)])
    graph.add_edge(xor_start_1, event_nodes[("B", 0)])
    graph.add_edge(xor_start_1, event_nodes[("C", 0)])
    graph.add_edge(event_nodes[("B", 0)], event_nodes[("D", 0)])
    graph.add_edge(event_nodes[("C", 0)], event_nodes[("E", 0)])
    graph.add_edge(event_nodes[("D", 0)], xor_end_1)
    graph.add_edge(event_nodes[("E", 0)], xor_end_1)
    graph.add_edge(xor_start_2, event_nodes[("B", 1)])
    graph.add_edge(xor_start_2, event_nodes[("C", 1)])
    graph.add_edge(event_nodes[("B", 1)], event_nodes[("D", 1)])
    graph.add_edge(event_nodes[("C", 1)], event_nodes[("E", 1)])
    graph.add_edge(event_nodes[("D", 1)], xor_end_2)
    graph.add_edge(event_nodes[("E", 1)], xor_end_2)
    graph.add_edge(event_nodes[("G", 0)], event_nodes[("H", 0)])
    graph.add_edge(event_nodes[("H", 0)], event_nodes[("I", 0)])
    graph.add_edge(xor_end_1, and_end)
    graph.add_edge(xor_end_2, and_end)
    graph.add_edge(event_nodes[("I", 0)], and_end)
    graph.add_edge(and_end, event_nodes[("F", 0)])
    return graph, event_nodes


@pytest.fixture
def loop_1() -> Loop:
    """Return a Loop instance.
    """
    loop = Loop(nodes=["q1", "q2", "q3", "q4"])
    for end in ["q3", "q4"]:
        for start in ["q1", "q2"]:
            loop.add_edge_to_remove((end, start))
    return loop


@pytest.fixture
def subloop() -> Loop:
    loop = Loop(nodes=["q6"])
    loop.add_edge_to_remove(("q6", "q6"))
    return loop


@pytest.fixture
def loop_2(subloop: Loop) -> Loop:
    """Return a Loop instance.
    """
    loop = Loop(nodes=["q5", "q6", "q7"])
    loop.add_edge_to_remove(("q7", "q5"))
    loop.sub_loops.append(subloop)
    return loop
