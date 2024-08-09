"""Tests for the puml_graph.graph_loop_insert module."""

from tel2puml.legacy_loop_detection.detect_loops import Loop
from tel2puml.puml_graph.graph import PUMLEventNode, PUMLGraph
from tel2puml.legacy_loop_detection.puml_graph.graph_loop_insert import (
    insert_loops
)
from tel2puml.check_puml_equiv import check_networkx_graph_equivalence
from tel2puml.tel2puml_types import PUMLEvent


def test_insert_loops(
    puml_graph: tuple[PUMLGraph, dict[tuple[str, int], PUMLEventNode]],
    loop_1: Loop,
    loop_2: Loop,
    expected_puml_graph_post_loop_insertion: PUMLGraph,
    expected_loop_1_graph: PUMLGraph,
    expected_loop_2_graph: PUMLGraph,
) -> None:
    """"Test the insert_loops function acting on a PUMLGraph instance."""
    # setup
    graph, _ = puml_graph
    # test for test graph
    insert_loops(graph, [loop_1, loop_2])
    # should be 3 loop subgraphs 2 for loop 1 and 1 for loop 2
    assert len(graph.subgraph_nodes) == 3
    # check the subgraphs for loop 1
    loop_1_subgraph_nodes = [
        sub_graph_node
        for sub_graph_node in graph.subgraph_nodes
        if sub_graph_node.node_id in [("LOOP", 0), ("LOOP", 1)]
    ]
    expected_node_ids = [
        ("START", "XOR", 0),
        ("START", "XOR", 1),
        ("END", "XOR", 0),
        ("END", "XOR", 1),
        ("B", 0),
        ("C", 0),
        ("D", 0),
        ("E", 0),
        ("B", 1),
        ("C", 1),
        ("D", 1),
        ("E", 1),
    ]
    # check the first subgraph loop node
    assert PUMLEvent.LOOP in loop_1_subgraph_nodes[0].event_types
    loop_1_subgraph_nodes_node_1_subgraph = (
        loop_1_subgraph_nodes[0].sub_graph
    )
    assert isinstance(loop_1_subgraph_nodes_node_1_subgraph, PUMLGraph)
    for node in loop_1_subgraph_nodes_node_1_subgraph.nodes:
        assert node.node_id in expected_node_ids
        expected_node_ids.remove(node.node_id)
    assert len(expected_node_ids) == 6
    assert all(
        expected_node_ids[0][-1] == node_id[-1]
        for node_id in expected_node_ids
    )
    # check the next subgraph loop node
    assert PUMLEvent.LOOP in loop_1_subgraph_nodes[1].event_types
    loop_1_subgraph_nodes_node_2_subgraph = (
        loop_1_subgraph_nodes[1].sub_graph
    )
    assert isinstance(loop_1_subgraph_nodes_node_2_subgraph, PUMLGraph)
    for node in loop_1_subgraph_nodes_node_2_subgraph.nodes:
        assert node.node_id in expected_node_ids
        expected_node_ids.remove(node.node_id)
    assert len(expected_node_ids) == 0
    # check the subgraph for loop 2 that has a subgraph
    loop_2_subgraph_node = [
        sub_graph_node
        for sub_graph_node in graph.subgraph_nodes
        if sub_graph_node.node_id == ("LOOP", 2)
    ][0]
    expected_node_ids = [
        ("G", 0),
        ("LOOP", 3),
        ("I", 0),
    ]
    assert PUMLEvent.LOOP in loop_2_subgraph_node.event_types
    assert isinstance(loop_2_subgraph_node.sub_graph, PUMLGraph)
    for node in loop_2_subgraph_node.sub_graph.nodes:
        assert node.node_id in expected_node_ids
        expected_node_ids.remove(node.node_id)
    assert len(expected_node_ids) == 0
    # check the subgraph for loop 2 that is a subgraph
    nested_loop_subgraph_node = list(
        loop_2_subgraph_node.sub_graph.subgraph_nodes
    )[0]
    assert nested_loop_subgraph_node.node_id == ("LOOP", 3)
    assert PUMLEvent.LOOP in nested_loop_subgraph_node.event_types
    assert isinstance(nested_loop_subgraph_node.sub_graph, PUMLGraph)
    nested_loop_subgraph = nested_loop_subgraph_node.sub_graph
    assert len(nested_loop_subgraph.nodes) == 1
    for node in nested_loop_subgraph.nodes:
        assert node.node_id == ("H", 0)
    # check the top level graph has been updated correctly
    assert check_networkx_graph_equivalence(
        graph,
        expected_puml_graph_post_loop_insertion
    )
    # check the loop 1 graph is correct
    for sub_graph_node in loop_1_subgraph_nodes:
        assert isinstance(sub_graph_node.sub_graph, PUMLGraph)
        assert check_networkx_graph_equivalence(
            sub_graph_node.sub_graph,
            expected_loop_1_graph
        )
    # check the loop 2 graph is correct
    assert check_networkx_graph_equivalence(
        loop_2_subgraph_node.sub_graph,
        expected_loop_2_graph
    )
