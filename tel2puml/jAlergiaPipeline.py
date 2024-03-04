"""
    This module reads data from a list of puml file paths, analyses it with
    jAlergia, then returns the results of the analsyis in networkx format
"""

from tel2puml.jAlergia2NetworkX import (
    get_nodes,
    get_edges,
    convert_to_networkx,
)
import tel2puml.run_jAlergia as run_jAlergia
from tel2puml.read_uml_file import get_event_list_from_puml


def main(puml_files: str = "", print_output: bool = False):
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

            if (print_output):

                networkx_graphs.append(
                    convert_to_networkx(
                        event_reference,
                        edge_list,
                        "outputs/" + puml_file_name + ".dot",
                    )
                )
            else:
                networkx_graphs.append(
                    convert_to_networkx(
                        event_reference,
                        edge_list
                    )
                )

    return networkx_graphs, event_references


if __name__ == "__main__":
    main(print_output=True)
