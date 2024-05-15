"""
This module reads data from a list of puml file paths, analyses it with
jAlergia, then returns the results of the analsyis in networkx format
"""
from networkx import DiGraph

from tel2puml.detect_loops import Loop


def remove_loop_data_from_graph(
    graph: DiGraph,
    loops: list[Loop],
) -> None:
    """Removes the loop data from the given graph. Removes the indicated edges
    and recursively removes the loop data from the sub loops.

    :param graph: The graph to remove the loop data from
    :type graph: :class:`DiGraph`
    :param loops: The loops used to remove the loop data from the graph
    :type loops: `list`[:class:`Loop`]
    """
    for loop in loops:
        remove_loop_edges_from_graph(graph, loop)
        remove_loop_data_from_graph(graph, loop.sub_loops)


def remove_loop_edges_from_graph(
    graph: DiGraph,
    loop: Loop,
) -> None:
    """Removes the given loop's edges to remove from the given graph.

    :param graph: The graph to remove the edges from
    :type graph: :class:`DiGraph`
    :param loop: The loop containing the edges to remove
    :type loop: :class:`Loop`
    """
    for edge in loop.all_edges_to_remove:
        graph.remove_edge(*edge)
