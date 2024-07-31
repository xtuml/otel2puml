"""Tests for the `walk_puml_graph.find_and_add_loop_kill_paths` module."""

from networkx import DiGraph

from tel2puml.walk_puml_graph.node import Node, SubGraphNode
from tel2puml.walk_puml_graph.find_and_add_loop_kill_paths import (
    find_and_add_loop_kill_paths_to_nested_graphs,
    find_and_add_loop_kill_paths_to_sub_graph_node,
)


def check_kill_paths_set_correctly(
    graph: "DiGraph[Node]",
    start_uid: str,
) -> None:
    """Check if the kill paths are set correctly.

    :param graph: The graph to check.
    :type graph: `DiGraph[Node]`
    :param start_uid: The start uid of the graph.
    :type start_uid: `str`
    """
    for node in graph.nodes:
        if node.uid == start_uid:
            logic_node = node.outgoing_logic[0]
            assert logic_node.is_loop_kill_path == [False, True]


def test_find_and_add_loop_kill_paths_to_sub_graph_node(
    nested_sub_graph_node_with_kill_paths: SubGraphNode,
) -> None:
    """Test finding and adding loop kill paths to a sub graph node."""
    find_and_add_loop_kill_paths_to_sub_graph_node(
        nested_sub_graph_node_with_kill_paths
    )
    check_kill_paths_set_correctly(
        nested_sub_graph_node_with_kill_paths.sub_graph,
        nested_sub_graph_node_with_kill_paths.start_uid,
    )


def test_find_and_add_loop_kill_paths_to_nested_graphs(
    graph_with_nested_kill_paths: "DiGraph[Node]",
    nested_sub_graph_node_with_kill_paths: SubGraphNode,
    sub_graph_node_with_kill_paths: SubGraphNode,
) -> None:
    """Test finding and adding loop kill paths to nested graphs."""
    find_and_add_loop_kill_paths_to_nested_graphs(graph_with_nested_kill_paths)
    check_kill_paths_set_correctly(
        nested_sub_graph_node_with_kill_paths.sub_graph,
        nested_sub_graph_node_with_kill_paths.start_uid,
    )
    check_kill_paths_set_correctly(
        sub_graph_node_with_kill_paths.sub_graph,
        sub_graph_node_with_kill_paths.start_uid,
    )
