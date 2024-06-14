"""Tests for the tel2puml.utils module."""
from networkx import DiGraph

from tel2puml.utils import (
    check_has_path_not_through_nodes,
    get_innodes_not_in_set, get_outnodes_not_in_set,
    get_nodes_with_outedges_not_in_set, get_nodes_with_outedges_in_set,
)


def test_check_has_path_not_through_nodes() -> None:
    """Tests the check_has_path_not_through_nodes method."""
    graph: "DiGraph[str]" = DiGraph()
    graph.add_node("A")
    graph.add_node("B")
    graph.add_node("C")
    graph.add_node("D")
    graph.add_node("E")
    graph.add_node("F")
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    graph.add_edge("C", "D")
    graph.add_edge("C", "E")
    graph.add_edge("D", "F")
    graph.add_edge("E", "F")
    # check case when there are no nodes to avoid and there is a path
    assert check_has_path_not_through_nodes(
        graph, "A", "F", []
    )
    # check case when there are no nodes to avoid and there is no path
    assert not check_has_path_not_through_nodes(
        graph, "F", "A", []
    )
    # check case when there are nodes to avoid, there is a path but it
    # goes through a node to avoid
    assert not check_has_path_not_through_nodes(
        graph, "A", "F", ["B"]
    )
    # check case when there are nodes to avoid, there is a path and it
    # does not go through any node to avoid that is not in the path
    assert check_has_path_not_through_nodes(
        graph, "A", "D", ["E"]
    )
    # check case when there are nodes to avoid, there is a path and the
    # node to avoid is a succesor of the target node
    assert check_has_path_not_through_nodes(
        graph, "A", "D", ["F"]
    )
    # check the case when source and target node are the same
    assert check_has_path_not_through_nodes(
        graph, "A", "A", []
    )
    # check the case when source and target node are the same and there
    # that node is in the nodes to avoid
    assert check_has_path_not_through_nodes(
        graph, "A", "A", ["A"]
    )


def test_get_innodes_not_in_set() -> None:
    """Tests the get_innodes_not_in_set method."""
    graph: "DiGraph[str]" = DiGraph()
    graph.add_node("A")
    graph.add_node("B")
    graph.add_node("C")
    graph.add_node("D")
    graph.add_edge("A", "B")
    graph.add_edge("A", "C")
    graph.add_edge("D", "C")
    graph.add_edge("D", "B")
    assert get_innodes_not_in_set(
        {"B", "C"}, {"B", "C"}, graph
    ) == {"A", "D"}
    assert get_innodes_not_in_set(
        {"B", "C"}, {"A", "D"}, graph
    ) == set()


def test_get_outnodes_not_in_set() -> None:
    """Tests the get_outnodes_not_in_set method."""
    graph: "DiGraph[str]" = DiGraph()
    graph.add_node("A")
    graph.add_node("B")
    graph.add_node("C")
    graph.add_node("D")
    graph.add_edge("A", "B")
    graph.add_edge("A", "C")
    graph.add_edge("D", "C")
    graph.add_edge("D", "B")
    assert get_outnodes_not_in_set(
        {"A", "D"}, {"A", "D"}, graph
    ) == {"B", "C"}
    assert get_outnodes_not_in_set(
        {"A", "D"}, {"B", "C"}, graph
    ) == set()


def test_get_nodes_with_outedges_not_in_set() -> None:
    """Tests the get_nodes_with_outedges_not_in_set method."""
    graph: "DiGraph[str]" = DiGraph()
    graph.add_node("A")
    graph.add_node("B")
    graph.add_node("C")
    graph.add_node("D")
    graph.add_edge("A", "B")
    graph.add_edge("A", "C")
    graph.add_edge("D", "C")
    graph.add_edge("D", "B")
    assert get_nodes_with_outedges_not_in_set(
        {"A", "D"}, {"A", "D"}, graph
    ) == {"A", "D"}
    assert get_nodes_with_outedges_not_in_set(
        {"A", "D"}, {"B", "C"}, graph
    ) == set()


def test_get_nodes_with_outedges_in_set() -> None:
    """Tests the get_nodes_with_outedges_in_set method."""
    graph: "DiGraph[str]" = DiGraph()
    graph.add_node("A")
    graph.add_node("B")
    graph.add_node("C")
    graph.add_node("D")
    graph.add_edge("A", "B")
    graph.add_edge("A", "C")
    graph.add_edge("D", "C")
    graph.add_edge("D", "B")
    assert get_nodes_with_outedges_in_set(
        {"A", "D"}, {"A", "D"}, graph
    ) == set()
    assert get_nodes_with_outedges_in_set(
        {"A", "D"}, {"B", "C"}, graph
    ) == {"A", "D"}
