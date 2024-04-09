"""
This module reads data from a list of puml file paths, analyses it with
jAlergia, then returns the results of the analsyis in networkx format
"""
from typing import Iterable

from networkx import MultiDiGraph

from tel2puml.jAlergia2NetworkX import (
    get_nodes,
    get_edges,
    convert_to_networkx,
)
import tel2puml.run_jAlergia as run_jAlergia
from tel2puml.read_uml_file import (
    get_event_list_from_puml, get_markov_sequence_lines_from_audit_event_stream
)
from tel2puml.tel2puml_types import PVEvent
from tel2puml.detect_loops import Loop


def process_puml_into_graphs(
    puml_files: str = "", puml_content: str = "", print_output: bool = False
):
    """
    Process a list of PlantUML files and convert them into NetworkX graphs.

    Args:
        puml_files (str): Optional. The name of the PlantUML file(s) to
            process. If not provided, a default list of files will be used.
        print_output (bool): Optional. If True, print the current file
            being processed.

    Returns:
        list: A list of NetworkX graphs representing the converted
            PlantUML files.
    """
    if puml_files == "":
        puml_files = [
            "ANDFork_ANDFork_a",
            "ANDFork_ANDFork_repeated_events",
            "loop_ANDFork_a",
            "loop_loop_a",
            "loop_XORFork_a",
            "sequence_xor_fork",
            "sequence_xor_fork",
            "XOR_3_branches_similar_events",
            "simple_test",
            "complicated_test",
            "triple_xor_test",
            "branching_loop_end_test",
            "and_plus_xor_test",
        ]
    else:
        puml_files = [puml_files, ""]

    networkx_graphs = []
    event_references = []

    for puml_file_name in puml_files:
        if puml_file_name != "":

            if print_output:
                print("current file: ", puml_file_name)

            event_list = get_event_list_from_puml(
                puml_file="puml_files/" + puml_file_name + ".puml",
                puml_key="ValidSols",
                debug=False,
            )
            j_alergia_model = str(run_jAlergia.run(event_list))
            node_reference, event_reference, node_list = get_nodes(
                j_alergia_model
            )
            edge_list = get_edges(j_alergia_model)

            event_references.append(event_reference)

            if print_output:

                networkx_graphs.append(
                    convert_to_networkx(
                        event_reference,
                        edge_list,
                        "outputs/" + puml_file_name + ".dot",
                    )
                )
            else:
                networkx_graphs.append(
                    convert_to_networkx(event_reference, edge_list)
                )

    return networkx_graphs, event_references


def markov_lines_to_network_x(
    markov_lines: str
) -> tuple[MultiDiGraph, dict[str, dict]]:
    """Converts the given markov lines as a string into a NetworkX graph.

    :param markov_lines: The markov lines to convert to the graph
    :type markov_lines: `str`
    :return: A tuple containing the NetworkX graph and the event reference
    :rtype: `tuple`[:class:`MultiDiGraph`, `dict`[`str`, `dict`]]
    """
    j_alergia_model = str(
        run_jAlergia.run(data=markov_lines)
    )
    node_reference, event_reference, _ = get_nodes(j_alergia_model)
    edge_list = get_edges(j_alergia_model)
    return convert_to_networkx(event_reference, edge_list), {
        "node_reference": node_reference,
        "event_reference": event_reference,
    }


def audit_event_sequences_to_network_x(
    audit_event_sequences: Iterable[Iterable[PVEvent]],
) -> tuple[MultiDiGraph, dict[str, dict]]:
    """Converts the given audit event sequences into a NetworkX graph.

    :param audit_event_sequences: The audit event sequences to convert to the
    graph
    :type audit_event_sequences: `Iterable`[`Iterable`[:class:`PVEvent`]]
    :return: A tuple containing the NetworkX graph and the event reference
    :rtype: `tuple`[:class:`MultiDiGraph`, `dict`[`str`, `dict`]]
    """
    markov_lines = (
        get_markov_sequence_lines_from_audit_event_stream(
            audit_event_sequences
        )
    )
    return markov_lines_to_network_x(markov_lines)


def remove_loop_data_from_graph(
    graph: MultiDiGraph,
    loops: list[Loop],
) -> None:
    """Removes the loop data from the given graph. Removes the indicated edges
    and recursively removes the loop data from the sub loops.

    :param graph: The graph to remove the loop data from
    :type graph: :class:`MultiDiGraph`
    :param loops: The loops used to remove the loop data from the graph
    :type loops: `list`[:class:`Loop`]
    """
    for loop in loops:
        remove_loop_edges_from_graph(graph, loop)
        remove_loop_data_from_graph(graph, loop.sub_loops)


def remove_loop_edges_from_graph(
    graph: MultiDiGraph,
    loop: Loop,
) -> None:
    """Removes the given loop's edges to remove from the given graph.

    :param graph: The graph to remove the edges from
    :type graph: :class:`MultiDiGraph`
    :param loop: The loop containing the edges to remove
    :type loop: :class:`Loop`
    """
    for edge in loop.edges_to_remove:
        graph.remove_edge(*edge)


if __name__ == "__main__":
    process_puml_into_graphs(print_output=True)
