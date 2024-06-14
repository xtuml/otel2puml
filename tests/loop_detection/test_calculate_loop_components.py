"""Tests for the calculate_loop_components module."""
from networkx import DiGraph

from tel2puml.loop_detection.calculate_loop_components import (
    get_break_nodes_from_potential_break_outnodes,
    get_break_nodes_if_end_to_start_exists,
    is_end_of_potential_ends,
    get_end_nodes_from_potential_end_nodes,
    get_end_nodes_using_start_nodes,
    get_loop_edges,
    calc_loop_end_break_and_loop_edges
)


class TestCalculateLoopComponents:
    """Tests for the calculate_loop_components module."""
    @staticmethod
    def create_graph_happy_path() -> "DiGraph[str]":
        """Creates a graph for the happy path of the algorithm."""
        graph: "DiGraph[str]" = DiGraph()
        graph.add_edge("A", "B")
        graph.add_edge("A", "C")
        graph.add_edge("B", "D")
        graph.add_edge("C", "E")
        graph.add_edge("D", "E")
        graph.add_edge("E", "F")
        graph.add_edge("B", "G")
        graph.add_edge("D", "H")
        graph.add_edge("G", "K")
        graph.add_edge("K", "F")
        graph.add_edge("H", "F")
        graph.add_edge("C", "I")
        return graph

    def create_graph_happy_path_with_loops(self) -> "DiGraph[str]":
        """Creates a graph for the happy path of the algorithm with loops."""
        graph = self.create_graph_happy_path()
        graph.add_edge("E", "A")
        return graph

    def test_get_break_nodes_from_potential_break_outnodes(self) -> None:
        """Tests the get_break_nodes_from_potential_break_outnodes method."""
        graph = self.create_graph_happy_path()
        assert get_break_nodes_from_potential_break_outnodes(
            {"B", "D", "C"}, {"F"}, {"E"}, graph
        ) == {"H", "K"}

    def test_get_break_nodes_if_end_to_start_exists(
        self,
    ) -> None:
        """Tests the get_end_nodes_and_break_nodes_if_end_to_start_exists
        method."""
        graph = self.create_graph_happy_path()
        assert get_break_nodes_if_end_to_start_exists(
            {"E"}, {"B", "D", "C"}, {"A"}, graph
        ) == {"H", "K"}

    @staticmethod
    def create_graph_unhappy_path() -> "DiGraph[str]":
        """Creates a graph for the unhappy path of the algorithms"""
        graph: "DiGraph[str]" = DiGraph()
        graph.add_edge("A", "B")
        graph.add_edge("B", "C")
        graph.add_edge("C", "D")
        graph.add_edge("D", "C")
        graph.add_edge("E", "F")
        graph.add_edge("F", "G")
        graph.add_edge("B", "G")
        graph.add_edge("G", "H")
        return graph

    def test_is_end_of_potential_ends(self) -> None:
        """Tests the is_end_of_potential_ends method."""
        graph = self.create_graph_unhappy_path()
        for node, truth in zip(
            ["C", "D", "H", "G"],
            [True, True, True, False]
        ):
            assert is_end_of_potential_ends(
                node,
                {"C", "D", "G", "H"}, graph
            ) is truth

    def test_get_end_nodes_from_potential_end_nodes(self) -> None:
        """Tests the get_end_nodes_from_potential_end_nodes method."""
        graph = self.create_graph_unhappy_path()
        assert get_end_nodes_from_potential_end_nodes(
            {"C", "D", "G", "H"}, graph
        ) == {"C", "D", "H"}

    def create_graph_unhappy_path_with_loops(self) -> "DiGraph[str]":
        """Creates a graph with a unhappy path and loops."""
        graph = self.create_graph_unhappy_path()
        graph.add_edge("C", "A")
        graph.add_edge("D", "A")
        graph.add_edge("G", "E")
        graph.add_edge("H", "E")
        return graph

    def test_get_end_nodes_using_start_nodes(self) -> None:
        """Tests the get_end_nodes_using_start_nodes method."""
        graph = self.create_graph_unhappy_path_with_loops()
        assert get_end_nodes_using_start_nodes(
            set(graph.nodes), {"A", "E"}, graph
        ) == {"C", "D", "H"}

    def test_get_loop_edges(self) -> None:
        """Tests the get_loop_edges method."""
        graph = self.create_graph_unhappy_path_with_loops()
        assert get_loop_edges(
            {"A", "E"}, {"C", "D", "H"}, graph
        ) == {
            ("C", "A"),
            ("D", "A"),
            ("H", "E"),
        }

    def test_calc_loop_end_break_and_loop_edges(self) -> None:
        """Tests the calc_loop_end_break_and_loop_edges method."""
        # unhappy path with no exits from the loop
        graph = self.create_graph_unhappy_path_with_loops()
        assert calc_loop_end_break_and_loop_edges(
            {"A", "E"},
            set(graph.nodes),
            graph
        ) == (
            {"C", "D", "H"},
            set(),
            {
                ("C", "A"),
                ("D", "A"),
                ("H", "E"),
            }
        )
        # unhappy path with exits from the loop
        nodes_before_add = set(graph.nodes)
        graph.add_edge("G", "I")
        graph.add_edge("B", "J")
        graph.add_edge("J", "K")
        graph.add_edge("I", "M")
        assert calc_loop_end_break_and_loop_edges(
            {"A", "E"},
            nodes_before_add,
            graph
        ) == (
            {"C", "D", "H"},
            {"I", "J"},
            {
                ("C", "A"),
                ("D", "A"),
                ("H", "E"),
            }
        )
        # happy path
        graph = self.create_graph_happy_path_with_loops()
        scc_nodes = set(graph.nodes).difference(
            {"I", "G", "K", "H", "F"}
        )
        graph.add_edge("F", "A")
        assert calc_loop_end_break_and_loop_edges(
            {"A"},
            scc_nodes,
            graph
        ) == (
            {"E"},
            {"K", "H"},
            {
                ("E", "A"),
            }
        )
