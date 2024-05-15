"""
Unit tests for the JAlergiaPipeline class.
"""
import unittest

from networkx import DiGraph

from tel2puml.jAlergiaPipeline import (
    remove_loop_data_from_graph,
    remove_loop_edges_from_graph,
)
from tel2puml.detect_loops import Loop


class TestLoopRemoval:
    """Test the loop removal functions."""
    def create_graph_with_loops(self) -> tuple[DiGraph, Loop]:
        """Create a graph with loops for testing.

        :return: A tuple containing the graph and the loop
        :rtype: `tuple`[:class:`MultiDiGraph`, :class:`Loop`]
        """
        # setup the graph
        graph = DiGraph()
        graph.add_edge("A", "B")
        graph.add_edge("B", "B")
        graph.add_edge("B", "C")
        graph.add_edge("C", "C")
        graph.add_edge("C", "D")
        graph.add_edge("D", "B")
        graph.add_edge("D", "E")
        graph.add_edge("D", "F")
        graph.add_edge("E", "A")
        graph.add_edge("F", "A")
        # setup loops
        loop = Loop(["A", "B", "C", "D", "E", "F"])
        loop.add_edge_to_remove(("E", "A"))
        loop.add_edge_to_remove(("F", "A"))
        sub_loop = Loop(["B", "C", "D"])
        sub_loop.add_edge_to_remove(("D", "B"))
        nested_sub_loop = Loop(["C"])
        nested_sub_loop.add_edge_to_remove(("C", "C"))
        sub_loop.add_subloop(nested_sub_loop)
        loop.add_subloop(sub_loop)
        return graph, loop

    def test_remove_loop_edges_from_graph(self) -> None:
        """Test the `remove_loop_edges_from_graph` function.
        """
        # setup the graph
        graph, loop = self.create_graph_with_loops()
        # test remove two edges given by the loop
        remove_loop_edges_from_graph(graph, loop)
        assert graph.number_of_edges() == 8
        for removed_edge in [("D", "A"), ("E", "A")]:
            assert not graph.has_edge(*removed_edge)

    def test_remove_loop_data_from_graph(self) -> None:
        """Test the `remove_loop_data_from_graph` function.
        """
        # test simple loop removal with no sub loops
        # setup the graph and loops
        graph = DiGraph()
        graph.add_edge("A", "B")
        graph.add_edge("B", "C")
        graph.add_edge("C", "A")
        graph.add_edge("C", "D")
        graph.add_edge("D", "E")
        graph.add_edge("E", "D")
        loop_1 = Loop(["A", "B", "C"])
        loop_1.add_edge_to_remove(("C", "A"))
        loop_2 = Loop(["D", "E"])
        loop_2.add_edge_to_remove(("E", "D"))
        # test remove all edges given by the loops
        remove_loop_data_from_graph(graph, [loop_1, loop_2])
        assert graph.number_of_edges() == 4
        for removed_edge in [("C", "A"), ("E", "D")]:
            assert not graph.has_edge(*removed_edge)
        # setup the graph and loop
        graph, loop = self.create_graph_with_loops()
        # test remove all edges given by the loop and nested sub loops
        remove_loop_data_from_graph(graph, [loop])
        assert graph.number_of_edges() == 6
        for removed_edge in [("D", "B"), ("E", "A"), ("F", "A"), ("C", "C")]:
            assert not graph.has_edge(*removed_edge)


if __name__ == "__main__":
    unittest.main()
