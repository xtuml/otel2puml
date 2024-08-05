"""Contains the functions to insert the detected loops into the PlantUML graph.
"""
from tel2puml.legacy_loop_detection.detect_loops import Loop
from tel2puml.puml_graph.graph import (
    PUMLGraph
)
from tel2puml.legacy_loop_detection.puml_graph.graph_loop_extract import (
    extract_loops_starts_and_ends_from_loop
)
from tel2puml.tel2puml_types import PUMLEvent


def insert_loops(puml_graph: PUMLGraph, loops: list[Loop]) -> None:
    """Inserts the detected loops into the PlantUML graph.

    :param loops: The loops to be inserted.
    :type loops: `list[:class:`Loop`]`
    """
    for loop in loops:
        insert_loop(puml_graph, loop)


def insert_loop(puml_graph: PUMLGraph, loop: Loop) -> None:
    """Inserts the detected loop into the PlantUML graph, extracting the
    unique loop start and end nodes of the graph first before inserting them
    into the graph.

    :param puml_graph: The PlantUML graph to insert the loop into.
    :type puml_graph: :class:`PUMLGraph`
    """
    loop_starts_and_ends = extract_loops_starts_and_ends_from_loop(
        puml_graph,
        loop
    )
    for start_node, end_node in loop_starts_and_ends:
        sub_graph_node = (
            puml_graph.replace_subgraph_node_from_start_and_end_nodes(
                start_node, end_node, "LOOP",
                PUMLEvent.LOOP
            )
        )
        insert_loops(sub_graph_node.sub_graph, loop.sub_loops)
