"""
Unit tests for the JAlergiaPipeline class.
"""

import unittest
from tel2puml.jAlergiaPipeline import process_puml_into_graphs


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


if __name__ == "__main__":
    unittest.main()
