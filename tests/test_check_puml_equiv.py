"""Tests for the check_puml_equiv module."""

from test_event_generator.solutions.graph_solution import GraphSolution
from tel2puml.check_puml_equiv import (
    parse_raw_job_def,
    create_networkx_graph_from_parsed_puml,
)


def test_create_networkx_graph_from_parsed_puml():
    with open(
        "puml_files/bunched_XOR_switch.puml", "r", encoding="utf-8"
    ) as file:
        puml_string = file.read()
    result = list(parse_raw_job_def(puml_string))[0]
    graph = create_networkx_graph_from_parsed_puml(result)
    GraphSolution.get_graphviz_plot(graph).savefig(
        "sequence_branch_counts.png"
    )
    print("here")
