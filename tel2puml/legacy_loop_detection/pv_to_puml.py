"""Module to convert a stream of PV event sequences to a PlantUML sequence
diagram, inferring the logic from the PV event sequences.
"""

from typing import Iterable

import networkx as nx

from tel2puml.tel2puml_types import PVEvent
from tel2puml.pv_to_puml.data_ingestion import (
    update_all_connections_from_clustered_events,
)
from tel2puml.events import events_to_markov_graph
from tel2puml.legacy_loop_detection.events import (
    remove_detected_loop_data_from_events,
    get_event_reference_from_events
)
from tel2puml.legacy_loop_detection.walk_puml_graph.node import (
    merge_markov_without_loops_and_logic_detection_analysis,
)
from tel2puml.pv_to_puml.walk_puml_graph.walk_puml_logic_graph import (
    create_puml_graph_from_node_class_graph,
)
from tel2puml.legacy_loop_detection.detect_loops import (
    detect_loops,
    get_all_kill_edges_from_loops,
    remove_loop_data_from_graph
)
from tel2puml.legacy_loop_detection.puml_graph.graph_loop_insert import (
    insert_loops
)
from tel2puml.pv_to_puml.walk_puml_graph.node_update import (
    get_node_to_node_map_from_edges,
    add_loop_kill_paths_for_nodes,
)
from tel2puml.legacy_loop_detection.walk_puml_graph.node_update import (
    update_nodes_with_break_points_from_loops,
)


def pv_to_puml_string(
    pv_stream: Iterable[Iterable[PVEvent]],
    puml_name: str = "default_name",
) -> str:
    """Converts a stream of PV event sequences to a PlantUML sequence diagram,
    inferring the logic from the PV event sequences and the structure from the
    Markov chain analysis.

    :param pv_stream: A Iterable of PV event sequences
    :type pv_stream: `Iterable`[`Iterable`[:class:`PVEvent`]]
    :param puml_name: The name of the PlantUML group to create
    :type puml_name: `str`
    """
    # run the logic detection pipeline
    forward_logic, backward_logic = (
        update_all_connections_from_clustered_events(
            pv_stream, add_dummy_start=True
        )
    )
    # create the markov chain graph and event reference
    markov_graph = events_to_markov_graph(forward_logic.values())
    event_reference = get_event_reference_from_events(forward_logic.values())
    # run the loop detection pipeline
    loops = detect_loops(markov_graph)
    # remove the loop edges from the Markov graph
    remove_loop_data_from_graph(markov_graph, loops)
    # remove loop edges from the logic trees
    remove_detected_loop_data_from_events(
        loops, forward_logic, event_reference
    )
    try:
        nx.find_cycle(markov_graph)
        raise RuntimeError("Markov graph has a cycle after lop removals")
    except nx.NetworkXNoCycle:
        pass
    # merge the Markov graph and the logic trees
    merged_markov_and_logic, event_node_reference = (
        merge_markov_without_loops_and_logic_detection_analysis(
            (markov_graph, event_reference), backward_logic, forward_logic
        )
    )
    # update the nodes with break points
    update_nodes_with_break_points_from_loops(loops, event_node_reference)
    # get all kill edges from loops and update the logic nodes with them
    loop_must_kill_edges = get_all_kill_edges_from_loops(markov_graph, loops)
    must_kill_node_to_node_map = get_node_to_node_map_from_edges(
        loop_must_kill_edges
    )
    add_loop_kill_paths_for_nodes(
        must_kill_node_to_node_map, merged_markov_and_logic
    )
    # create the PlantUML graph
    puml_graph = create_puml_graph_from_node_class_graph(
        merged_markov_and_logic
    )
    # insert the detected loops into the PlantUML graph
    insert_loops(puml_graph, loops)
    # remove the dummy start event
    puml_graph.remove_dummy_start_event_nodes()
    # convert the PlantUML graph to a PlantUML string
    return puml_graph.write_puml_string(puml_name)
