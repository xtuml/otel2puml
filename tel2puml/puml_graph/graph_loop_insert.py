from tel2puml.detect_loops import Loop
from tel2puml.puml_graph.graph import (
    PUMLGraph, PUMLNode
)
from tel2puml.puml_graph.graph_loop_extract import (
    extract_loops_starts_and_ends_from_loop
)


def insert_loops(puml_graph: PUMLGraph, loops: list[Loop]) -> None:
    """Inserts the loops into the PlantUML graph.

    :param loops: The loops to be inserted.
    :type loops: `list[:class:`Loop`]`
    """
    for loop in loops:
        insert_loop(puml_graph, loop)


def insert_loop(puml_graph: PUMLGraph, loop: Loop):
    loop_starts_and_ends = extract_loops_starts_and_ends_from_loop(
        puml_graph,
        loop
    )
    for start_node, end_node in loop_starts_and_ends:
        replace_loop_nodes_with_sub_graph_and_insert_sub_loops(
            puml_graph, start_node, end_node, loop
        )


def replace_loop_nodes_with_sub_graph_and_insert_sub_loops(
    puml_graph: PUMLGraph, start_node: PUMLNode, end_node: PUMLNode, loop: Loop
) -> None:
    """Replaces the loop nodes with a sub graph and inserts the sub loops.

    :param start_node: The start node of the loop.
    :type start_node: :class:`PUMLNode`
    :param end_node: The end node of the loop.
    :type end_node: :class:`PUMLNode`
    :param loop: The loop to be inserted.
    :type loop: :class:`Loop`
    """
    sub_graph = puml_graph.replace_subgraph_node_from_start_and_end_nodes(
        start_node, end_node, "LOOP"
    )
    insert_loops(sub_graph, loop.sub_loops)
