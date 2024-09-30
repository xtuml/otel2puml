"""Tests for the graph_loop_insert module."""
from typing import Hashable

import pytest

from tel2puml.puml_graph import PUMLGraph, PUMLEventNode, PUMLNode
from tel2puml.legacy_loop_detection.puml_graph.graph_loop_extract import (
    extract_loops_starts_and_ends_from_loop,
    get_event_nodes_from_loop,
    get_unique_loops_from_start_and_end_nodes,
    get_distinct_loops_starts_and_ends,
    walk_until_minimal_nodes_found,
    get_loop_start_and_end,
    calc_loop_start_node,
    calc_loop_end_node,
    LoopNodes,
    filter_end_nodes_with_successors
)
from tel2puml.legacy_loop_detection.detect_loops import Loop


def test_get_event_nodes_from_loop(
    puml_graph: tuple[PUMLGraph, dict[tuple[str, int], PUMLEventNode]],
    loop_1: Loop,
) -> None:
    """Tests the get_event_nodes_from_loop method."""
    graph, _ = puml_graph
    event_nodes = get_event_nodes_from_loop(graph, loop_1)
    assert len(event_nodes["start_loop_nodes"]) == 4
    assert len(event_nodes["end_loop_nodes"]) == 4
    for event_node_id in [
        (event_type, i) for event_type in ["B", "C"] for i in range(2)
    ]:
        assert puml_graph[1][event_node_id] in event_nodes["start_loop_nodes"]
    for event_node_id in [
        (event_type, i) for event_type in ["D", "E"] for i in range(2)
    ]:
        assert puml_graph[1][event_node_id] in event_nodes["end_loop_nodes"]


def test_walk_until_minimal_nodes_found(
    puml_graph: tuple[PUMLGraph, dict[tuple[str, int], PUMLEventNode]],
    loop_1: Loop,
    loop_2: Loop,
) -> None:
    """Tests the walk_until_minimal_nodes_found method."""
    # setup
    graph, event_nodes = puml_graph
    # test case where there are two loops in the graph that are from loop_1
    # and we should only find one of them from a given start node
    loop_nodes = get_event_nodes_from_loop(graph, loop_1)
    loop_found = walk_until_minimal_nodes_found(
        graph, list(loop_nodes["start_loop_nodes"])[0], loop_nodes, loop_1
    )
    expected_start_node_parent_graph_nodes: list[Hashable] = ["q1", "q2"]
    assert len(loop_found["start_loop_nodes"]) == 2
    for node in loop_found["start_loop_nodes"]:
        assert node.parent_graph_node in expected_start_node_parent_graph_nodes
        expected_start_node_parent_graph_nodes.remove(node.parent_graph_node)
    assert len(expected_start_node_parent_graph_nodes) == 0
    assert len(loop_found["end_loop_nodes"]) == 2
    expected_end_node_parent_graph_nodes: list[Hashable] = ["q3", "q4"]
    for node in loop_found["end_loop_nodes"]:
        assert node.parent_graph_node in expected_end_node_parent_graph_nodes
        expected_end_node_parent_graph_nodes.remove(node.parent_graph_node)
    assert len(expected_end_node_parent_graph_nodes) == 0
    # test case where there is only one loop in the graph from loop_2
    loop_nodes = get_event_nodes_from_loop(graph, loop_2)
    loop_found = walk_until_minimal_nodes_found(
        graph, list(loop_nodes["start_loop_nodes"])[0], loop_nodes, loop_2
    )
    expected_start_node_parent_graph_nodes = ["q5"]
    assert len(loop_found["start_loop_nodes"]) == 1
    for node in loop_found["start_loop_nodes"]:
        assert node.parent_graph_node in expected_start_node_parent_graph_nodes
        expected_start_node_parent_graph_nodes.remove(node.parent_graph_node)
    assert len(expected_start_node_parent_graph_nodes) == 0
    assert len(loop_found["end_loop_nodes"]) == 1
    expected_end_node_parent_graph_nodes = ["q7"]
    for node in loop_found["end_loop_nodes"]:
        assert node.parent_graph_node in expected_end_node_parent_graph_nodes
        expected_end_node_parent_graph_nodes.remove(node.parent_graph_node)
    assert len(expected_end_node_parent_graph_nodes) == 0
    # test case where there were no loop nodes found in the graph
    with pytest.raises(RuntimeError):
        walk_until_minimal_nodes_found(
            graph,
            list(loop_nodes["start_loop_nodes"])[0],
            LoopNodes(start_loop_nodes=set(), end_loop_nodes=set()),
            loop_1,
        )
    # test case where start node is above all the loops
    with pytest.raises(RuntimeError):
        walk_until_minimal_nodes_found(
            graph, event_nodes[("A", 0)], loop_nodes, loop_1
        )


def test_get_distinct_loop_starts_and_ends(
    puml_graph: tuple[PUMLGraph, dict[tuple[str, int], PUMLEventNode]],
    loop_1: Loop,
    loop_2: Loop,
) -> None:
    """Tests the get_distinct_loop_start_and_ends method."""

    # setup
    def check_loops_are_correct(
        loops: list[LoopNodes],
        expected_start_node_sets: list[set[PUMLEventNode]],
        expected_end_node_sets: list[set[PUMLEventNode]],
    ) -> None:
        for loop in loops:
            assert loop["start_loop_nodes"] in expected_start_node_sets
            expected_start_node_sets.remove(loop["start_loop_nodes"])
            assert loop["end_loop_nodes"] in expected_end_node_sets
            expected_end_node_sets.remove(loop["end_loop_nodes"])
        assert len(expected_start_node_sets) == 0
        assert len(expected_end_node_sets) == 0

    graph, event_nodes = puml_graph
    # test case where there are two loops in the graph that are from loop_1
    # and we should find both of them
    loop_starts_and_ends = get_event_nodes_from_loop(graph, loop_1)
    distinct_loops = get_distinct_loops_starts_and_ends(
        graph, loop_starts_and_ends, loop_1
    )
    expected_start_node_sets = [
        {event_nodes[("B", 0)], event_nodes[("C", 0)]},
        {event_nodes[("B", 1)], event_nodes[("C", 1)]},
    ]
    expected_end_node_sets = [
        {event_nodes[("D", 0)], event_nodes[("E", 0)]},
        {event_nodes[("D", 1)], event_nodes[("E", 1)]},
    ]
    assert len(distinct_loops) == 2
    check_loops_are_correct(
        distinct_loops, expected_start_node_sets, expected_end_node_sets
    )
    # test case where there is only one loop in the graph from loop_2
    loop_starts_and_ends = get_event_nodes_from_loop(graph, loop_2)
    distinct_loops = get_distinct_loops_starts_and_ends(
        graph, loop_starts_and_ends, loop_2
    )
    expected_start_node_sets = [{event_nodes[("G", 0)]}]
    expected_end_node_sets = [{event_nodes[("I", 0)]}]
    assert len(distinct_loops) == 1
    check_loops_are_correct(
        distinct_loops, expected_start_node_sets, expected_end_node_sets
    )


def test_calc_loop_start_node(
    puml_graph: tuple[PUMLGraph, dict[tuple[str, int], PUMLEventNode]],
    loop_1: Loop,
    loop_2: Loop,
) -> None:
    """Tests the calc_loop_start_node method."""
    graph, event_nodes = puml_graph
    # test case where there are two loops in the graph that are from loop_1
    loop_starts_and_ends = get_event_nodes_from_loop(graph, loop_1)
    distinct_loops = get_distinct_loops_starts_and_ends(
        graph, loop_starts_and_ends, loop_1
    )
    expected_start_node_ids = {
        event_nodes[("B", 0)]: ("START", "XOR", 0),
        event_nodes[("B", 1)]: ("START", "XOR", 1),
        event_nodes[("C", 0)]: ("START", "XOR", 0),
        event_nodes[("C", 1)]: ("START", "XOR", 1),
    }
    for loop in distinct_loops:
        a_start_node = list(loop["start_loop_nodes"])[0]
        start_node = calc_loop_start_node(graph, loop)
        assert start_node.node_id == expected_start_node_ids[a_start_node]
    # test case where there is only one loop in the graph from loop_2
    loop_starts_and_ends = get_event_nodes_from_loop(graph, loop_2)
    distinct_loops = get_distinct_loops_starts_and_ends(
        graph, loop_starts_and_ends, loop_2
    )
    start_node = calc_loop_start_node(graph, distinct_loops[0])
    assert start_node == event_nodes[("G", 0)]
    # test case where there are no start nodes
    with pytest.raises(RuntimeError) as exc_info:
        calc_loop_start_node(
            graph, LoopNodes(start_loop_nodes=set(), end_loop_nodes=set())
        )
    assert "No loop start nodes have been given" in str(exc_info.value)
    # test case where loop start node has no path to end node is above all the
    # loops
    with pytest.raises(RuntimeError) as exc_info:
        calc_loop_start_node(
            graph,
            LoopNodes(
                start_loop_nodes={event_nodes[("B", 0)]},
                end_loop_nodes={event_nodes[("A", 0)]},
            ),
        )
    assert "No possible loop start node found" in str(exc_info.value)


def test_calc_loop_end_node(
    puml_graph: tuple[PUMLGraph, dict[tuple[str, int], PUMLEventNode]],
    loop_1: Loop,
    loop_2: Loop,
) -> None:
    """Tests the calc_loop_end_node method for the given graph and loops."""
    graph, event_nodes = puml_graph
    # test case where there are two loops in the graph that are from loop_1
    loop_starts_and_ends = get_event_nodes_from_loop(graph, loop_1)
    distinct_loops = get_distinct_loops_starts_and_ends(
        graph, loop_starts_and_ends, loop_1
    )
    expected_end_node_ids = {
        event_nodes[("D", 0)]: ("END", "XOR", 0),
        event_nodes[("D", 1)]: ("END", "XOR", 1),
        event_nodes[("E", 0)]: ("END", "XOR", 0),
        event_nodes[("E", 1)]: ("END", "XOR", 1),
    }
    for loop in distinct_loops:
        a_end_node = list(loop["end_loop_nodes"])[0]
        end_node = calc_loop_end_node(graph, loop)
        assert end_node.node_id == expected_end_node_ids[a_end_node]
    # test case where there is only one loop in the graph from loop_2
    loop_starts_and_ends = get_event_nodes_from_loop(graph, loop_2)
    distinct_loops = get_distinct_loops_starts_and_ends(
        graph, loop_starts_and_ends, loop_2
    )
    end_node = calc_loop_end_node(graph, distinct_loops[0])
    assert end_node == event_nodes[("I", 0)]
    # test case where there are no end nodes
    with pytest.raises(RuntimeError) as exc_info:
        calc_loop_end_node(
            graph, LoopNodes(start_loop_nodes=set(), end_loop_nodes=set())
        )
    assert "No loop end nodes have been given" in str(exc_info.value)
    # test case where loop start node has no path to end node is above all the
    # loops
    with pytest.raises(RuntimeError) as exc_info:
        calc_loop_end_node(
            graph,
            LoopNodes(
                start_loop_nodes={event_nodes[("B", 0)]},
                end_loop_nodes={event_nodes[("A", 0)]},
            ),
        )
    assert "No possible loop start node found" in str(exc_info.value)


def test_get_loop_starts_and_ends(
    puml_graph: tuple[PUMLGraph, dict[tuple[str, int], PUMLEventNode]],
    loop_1: Loop,
) -> None:
    """Tests the get_loop_starts_and_ends method returns the correct list of
    unique loops with the correct start and end nodes."""
    graph, event_nodes = puml_graph
    # test case where there are two loops in the graph that are from loop_1
    loop_starts_and_ends = get_event_nodes_from_loop(graph, loop_1)
    distinct_loops = get_distinct_loops_starts_and_ends(
        graph, loop_starts_and_ends, loop_1
    )
    expected_start_node_ids = {
        event_nodes[("B", 0)]: ("START", "XOR", 0),
        event_nodes[("B", 1)]: ("START", "XOR", 1),
        event_nodes[("C", 0)]: ("START", "XOR", 0),
        event_nodes[("C", 1)]: ("START", "XOR", 1),
    }
    expected_end_node_ids = {
        event_nodes[("D", 0)]: ("END", "XOR", 0),
        event_nodes[("D", 1)]: ("END", "XOR", 1),
        event_nodes[("E", 0)]: ("END", "XOR", 0),
        event_nodes[("E", 1)]: ("END", "XOR", 1),
    }
    for loop in distinct_loops:
        a_start_node = list(loop["start_loop_nodes"])[0]
        a_end_node = list(loop["end_loop_nodes"])[0]
        start_node, end_node = get_loop_start_and_end(
            graph, loop
        )
        end_node = calc_loop_end_node(graph, loop)
        assert end_node.node_id == expected_end_node_ids[a_end_node]
        assert start_node.node_id == expected_start_node_ids[a_start_node]


class TestGetLoopStartAndEnd:
    """Tests for methods that get the unique loops with a helper method to
    check that the correct unique loops were found."""
    @staticmethod
    def check_correct_start_and_end_nodes(
        unique_loops: list[tuple[PUMLNode, PUMLNode]],
    ) -> None:
        """Helper method for checking the correct unique loops were
        found"""
        expected_loop_start_end_ids: list[tuple[Hashable, Hashable]] = [
            (("START", "XOR", 0), ("END", "XOR", 0)),
            (("START", "XOR", 1), ("END", "XOR", 1)),
        ]
        assert len(unique_loops) == 2
        for loop in unique_loops:
            start_node, end_node = loop
            assert (
                start_node.node_id,
                end_node.node_id,
            ) in expected_loop_start_end_ids
            expected_loop_start_end_ids.remove(
                (start_node.node_id, end_node.node_id)
            )
        assert len(expected_loop_start_end_ids) == 0

    def test_get_unique_loops_from_start_and_end_nodes(
        self,
        puml_graph: tuple[PUMLGraph, dict[tuple[str, int], PUMLEventNode]],
        loop_1: Loop,
    ) -> None:
        """Tests the get_unique_loops_from_start_and_end_nodes method gets the
        correct start and end nodes for the given mixed loop starts and ends.
        The loop appears twice in the given graph"""
        graph, _ = puml_graph
        # test case where there are two loops in the graph that are from loop_1
        loop_starts_and_ends = get_event_nodes_from_loop(graph, loop_1)
        unique_loops = get_unique_loops_from_start_and_end_nodes(
            graph, loop_starts_and_ends, loop_1
        )
        self.check_correct_start_and_end_nodes(unique_loops)

    def test_extract_loops_starts_and_ends(
        self,
        puml_graph: tuple[PUMLGraph, dict[tuple[str, int], PUMLEventNode]],
        loop_1: Loop,
    ) -> None:
        """Tests the extract_loops_starts_and_ends_from_loop method gets the
        correct start and end nodes for the given loop of Markov nodes. The
        loop appears twice in the given graph"""
        graph, _ = puml_graph
        # test case where there are two loops in the graph that are from loop_1
        unique_loops = extract_loops_starts_and_ends_from_loop(
            graph, loop_1
        )
        self.check_correct_start_and_end_nodes(unique_loops)

    @staticmethod
    def test_filter_end_nodes_with_successors() -> None:
        """Tests the filter_end_nodes_with_successors method."""
        puml_graph = PUMLGraph()
        A = puml_graph.create_event_node("A")
        B = puml_graph.create_event_node("B")
        puml_graph.add_puml_edge(A, B)
        filtered_end_nodes = filter_end_nodes_with_successors(
            {A, B}, puml_graph
        )
        assert filtered_end_nodes == {B}
