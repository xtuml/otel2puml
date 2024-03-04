"""
This module contains unit tests for the `run_jAlergia` module.
The test class contains test methods for the `run` function.
"""

import unittest
from tel2puml.run_jAlergia import run
import os


class TestRunJAlergia(unittest.TestCase):
    """
    Test class for the `run_jAlergia` module.
    """

    def teardown(self):
        """
        Clean up the test environment.
        """
        # Delete the model.dot file
        if os.path.exists("model.dot"):
            os.remove("model.dot")

    def test_run_with_data(self):
        """
        Test the `run` function with data input.
        """
        data = "1,2,3,4,5"
        path_to_output = "model.dot"
        expected_model_lines = [
            "digraph learnedModel {\n"
            'q0 [label="1"];\n'
            'q1 [label="2"];\n'
            'q2 [label="3"];\n'
            'q3 [label="4"];\n'
            'q4 [label="5"];\n'
            'q0 -> q1  [label="1.0"];\n'
            'q1 -> q2  [label="1.0"];\n'
            'q2 -> q3  [label="1.0"];\n'
            'q3 -> q4  [label="1.0"];\n'
            '__start0 [label="", shape=none];\n'
            '__start0 -> q0  [label=""];\n'
            "}\n"
        ]

        expected_model = "".join(expected_model_lines)

        model = run(data=data, path_to_output=path_to_output)

        self.assertEqual(str(model), expected_model)

        with open(path_to_output, "r") as f:
            self.assertEqual(f.read(), str(expected_model))

        self.teardown()

    def test_run_with_empty_data_and_file(self):
        """
        Test the `run` function with empty data and file inputs.
        """
        with self.assertRaises(ValueError):
            run()


if __name__ == "__main__":
    unittest.main()
