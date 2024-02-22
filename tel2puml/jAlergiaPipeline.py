"""
As this pipeline will be integrated elsewhere, it serves as a sample to
  demonstrate how the pipeline can be constructed using jAlergia2NetworkX
  and other related modules.
"""

from jAlergia2NetworkX import get_nodes, get_edges, convert_to_networkx
import run_jAlergia
from tel2puml.read_uml_file import get_event_list_from_puml

if __name__ == "__main__":
    puml_files = [
        "ANDFork_ANDFork_a",
        "ANDFork_ANDFork_repeated_events",
        "loop_ANDFork_a",
        "loop_loop_a",
        "loop_XORFork_a",
        "sequence_branch_counts",
        "sequence_break_points",
        "sequence_xor_fork",
        "sequence_xor_fork",
        "simple_test",
        "XOR_3_branches_similar_events",
    ]
    for puml_file_name in puml_files:

        print("current file: ", puml_file_name)

        event_list = None
        j_alergia_model = None
        node_reference = None
        events_reference = None
        edge_list = None
        node_list = None
        networkx_graph = None

        event_list = get_event_list_from_puml(
            puml_file="puml_files/" + puml_file_name + ".puml",
            puml_key="ValidSols",
            debug=False,
        )
        j_alergia_model = str(run_jAlergia.run(event_list))
        node_reference, events_reference, node_list = get_nodes(
            j_alergia_model
        )
        edge_list = get_edges(j_alergia_model)
        networkx_graph = convert_to_networkx(
            events_reference, edge_list, "outputs/" + puml_file_name + ".dot"
        )
