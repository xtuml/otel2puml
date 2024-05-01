"""
This module provides a function to run the jAlergia algorithm and learn a
    probabilistic automaton from data or a file.

The main function `run` takes three optional arguments: `data`, `path_to_file`,
     and `path_to_output`.
- `data` is a string representing the input data.
- `path_to_file` is a string representing the path to the input data file.
- `path_to_output` is a string representing the path to the output file to save
     the learned model.

The function returns the learned probabilistic automaton model.

If both `data` and `path_to_file` are empty, a `ValueError` is raised.

Example usage:
    model = run(data="1,2,3,4,5", path_to_output="model.dot")
    model = run(path_to_file="data.txt", path_to_output="model.dot")
"""
from typing import Any

from aalpy.learning_algs import run_Alergia  # type: ignore[import-untyped]


def run(
        data: str = "",
        path_to_file: str = "",
        path_to_output: str = ""
) -> Any:
    """
    Run the jAlergia algorithm to learn a probabilistic automaton from data or
        a file.

    Args:
        data (str): The input data as a string. Default is an empty string.
        path_to_file (str): The path to the input data file. Default is an
            empty string.
        path_to_output (str): The path to the output file to save the learned
            model. Default is an empty string.

    Returns:
        model: The learned probabilistic automaton model.

    Raises:
        ValueError: If both `data` and `path_to_file` are empty.

    """
    if path_to_file != "" and data == "":
        with open(path_to_file, "r") as f:
            data = f.read()

    if path_to_file == "" and data == "":
        raise (ValueError)

    split_data = [event.split(",") for event in data.splitlines()]

    model = run_Alergia(data=split_data, automaton_type="mc", eps=0.05)

    if path_to_output != "":
        with open(path_to_output, "w") as f:
            f.write(str(model))

    return model
