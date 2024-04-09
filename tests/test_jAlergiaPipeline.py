"""
Unit tests for the JAlergiaPipeline class.
"""
import unittest

from networkx import MultiDiGraph

from tel2puml.jAlergiaPipeline import (
    process_puml_into_graphs,
    markov_lines_to_network_x,
    audit_event_sequences_to_network_x,
    remove_loop_data_from_graph,
    remove_loop_edges_from_graph,
)
from tel2puml.read_uml_file import (
    get_markov_sequence_lines_from_audit_event_stream
)
from tel2puml.pipelines.data_creation import (
    generate_test_data_event_sequences_from_puml,
)
from tel2puml.detect_loops import Loop


class TestJAlergiaPipeline(unittest.TestCase):
    """
    Unit tests for the JAlergiaPipeline class.
    """

    def test_process_puml_into_graphs_with_default_files(self):
        """
        Test the `process_puml_into_graphs` function with default files.
        """
        expected_graph_count = 13

        graphs = process_puml_into_graphs()

        self.assertEqual(len(graphs[0]), expected_graph_count)

    def test_process_puml_into_graphs_with_custom_file(self):
        """
        Test the `process_puml_into_graphs` function with a custom file.
        """
        custom_file = "custom_file"
        file_path = "puml_files/" + custom_file + ".puml"

        with open("puml_files/" + custom_file + ".puml", "w") as file:
            file.write(
                """@startuml
                            partition "Branch_Counts" {
                                group "Branch_Counts"
                                    :A;
                                    :B;
                                end group
                            }
                        @enduml"""
            )

        graphs = process_puml_into_graphs(
            puml_files=custom_file, print_output=False
        )

        import os

        if os.path.exists(file_path):
            os.remove(file_path)

        self.assertEqual(len(graphs), 2)
        self.assertEqual(
            "MultiDiGraph with 2 nodes and 1 edges", str(graphs[0][0])
        )


class TestMarkovPipelineTest:
    """Test the `markov_lines_to_network_x` and
    `audit_event_sequences_to_network_x` functions
    """
    @staticmethod
    def check_graph_and_refs(
        graph: MultiDiGraph, references: dict[str, dict]
    ) -> None:
        """Check the graph for correctness using the node references

        :param graph: The graph to check
        :type graph: :class:`MultiDiGraph`
        :param references: The references to use
        :type references: `dict`[`str`, `dict`]
        """
        assert graph.number_of_nodes() == 4
        assert graph.number_of_edges() == 3
        node_references = references["node_reference"]
        expected_edges = [
            (node_references["A"][0], node_references["D"][0]),
            (node_references["A"][0], node_references["B"][0]),
            (node_references["B"][0], node_references["C"][0]),
        ]
        for edge in graph.edges():
            assert edge in expected_edges
            expected_edges.remove(edge)
        assert len(expected_edges) == 0

    def test_markov_lines_to_network_x(self) -> None:
        """Test the `markov_lines_to_network_x` function.
        """
        event_sequences = generate_test_data_event_sequences_from_puml(
            "puml_files/simple_test.puml"
        )
        markov_lines = get_markov_sequence_lines_from_audit_event_stream(
            event_sequences
        )
        graph, references = markov_lines_to_network_x(markov_lines)
        self.check_graph_and_refs(graph, references)

    def test_audit_event_sequences_to_network_x(self) -> None:
        """Test the `audit_event_sequences_to_network_x` function.
        """
        event_sequences = generate_test_data_event_sequences_from_puml(
            "puml_files/simple_test.puml"
        )
        graph, references = audit_event_sequences_to_network_x(event_sequences)
        self.check_graph_and_refs(graph, references)


class TestLoopRemoval:
    def create_graph_with_loops(self) -> tuple[MultiDiGraph, Loop]:
        """Create a graph with loops for testing.

        :return: A tuple containing the graph and the loop
        :rtype: `tuple`[:class:`MultiDiGraph`, :class:`Loop`]
        """
        # setup the graph
        graph = MultiDiGraph()
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
        graph = MultiDiGraph()
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
