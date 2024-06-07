"""Module to convert a stream of PV event sequences to a PlantUML sequence
diagram, inferring the logic from the PV event sequences.
"""
from typing import Generator, Iterable, Any
import json
import os

import networkx as nx

from tel2puml.tel2puml_types import PVEvent
from tel2puml.pipelines.data_ingestion import (
    update_all_connections_from_clustered_events
)
from tel2puml.events import (
    remove_detected_loop_data_from_events,
    events_to_markov_graph,
    get_event_reference_from_events
)
from tel2puml.jAlergiaPipeline import (
    remove_loop_data_from_graph
)
from tel2puml.node_map_to_puml.node import (
    merge_markov_without_loops_and_logic_detection_analysis,
    create_puml_graph_from_node_class_graph,
)
from tel2puml.detect_loops import (
    detect_loops, get_all_break_edges_from_loops,
    get_all_lonely_merge_killed_edges_from_loops,
    get_all_kill_edges_from_loops
)
from tel2puml.puml_graph.graph_loop_insert import insert_loops
from tel2puml.node_map_to_puml.node_update import (
    update_nodes_with_break_points_from_loops,
    get_node_to_node_map_from_edges,
    update_logic_nodes_with_lonely_merges_from_node_to_node_kill_map,
    add_loop_kill_paths_for_nodes
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
            pv_stream,
            add_dummy_start=True
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
            (markov_graph, event_reference),
            backward_logic,
            forward_logic
        )
    )
    # update the nodes with break points
    update_nodes_with_break_points_from_loops(loops, event_node_reference)
    # get all break edges
    break_edges = get_all_break_edges_from_loops(loops)
    # get all lonely merge kill edges from loops
    loop_kill_egdes = get_all_lonely_merge_killed_edges_from_loops(
        markov_graph,
        loops
    )
    kill_edges = break_edges.union(loop_kill_egdes)
    # get the node to node kill map and update the logic nodes with lonely
    # merges
    node_to_node_kill_map = get_node_to_node_map_from_edges(kill_edges)
    update_logic_nodes_with_lonely_merges_from_node_to_node_kill_map(
        node_to_node_kill_map, event_node_reference
    )
    # get all kill edges from loops and update the logic nodes with them
    loop_must_kill_edges = get_all_kill_edges_from_loops(markov_graph, loops)
    must_kill_node_to_node_map = get_node_to_node_map_from_edges(
        loop_must_kill_edges
    )
    add_loop_kill_paths_for_nodes(
        must_kill_node_to_node_map,
        merged_markov_and_logic
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


def pv_to_puml_file(
    pv_stream: Iterable[Iterable[PVEvent]],
    puml_file_path: str = "default.puml",
    puml_name: str = "default_name",
) -> None:
    """Converts a stream of PV event sequences to a PlantUML sequence diagram,
    inferring the logic from the PV event sequences and the structure from the
    Markov chain analysis.

    :param pv_stream: A Iterable of PV event sequences
    :type pv_stream: `Iterable`[`Iterable`[:class:`PVEvent`]]
    :param puml_file_path: The path to save the PlantUML file to
    :type puml_file_path: `str`
    :param puml_name: The name of the PlantUML group to create
    :type puml_name: `str`
    """
    puml_string = pv_to_puml_string(pv_stream, puml_name)
    with open(puml_file_path, "w") as puml_file:
        puml_file.write(puml_string)


def pv_job_file_to_event_sequence(
    file_path: str,
) -> list[PVEvent]:
    """Reads a PV job json array file and returns the event sequence

    :param file_path: The path to the PV job json file
    :type file_path: `str`
    :return: The event sequence
    :rtype: `list`[:class:`PVEvent`]
    """
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def pv_job_files_to_event_sequence_streams(
    file_paths: list[str],
) -> Generator[list[PVEvent], Any, None]:
    """Reads a list of PV job json array files and yields the event sequences
    when iterated over

    :param file_paths: The paths to the PV job json files
    :type file_paths: `list`[`str`]
    :return: A generator of event sequences
    :rtype: `Generator`[`list`[:class:`PVEvent`], Any, None]
    """
    for file_path in file_paths:
        yield pv_job_file_to_event_sequence(file_path)


def pv_jobs_from_folder_to_event_sequence_streams(
    folder_path: str,
) -> Generator[list[PVEvent], Any, None]:
    """Reads a folder of PV job json array files and yields the event sequences
    when iterated over

    :param folder_path: The path to the folder containing the PV job json files
    :type folder_path: `str`
    :return: A generator of event sequences
    :rtype: `Generator`[`list`[:class:`PVEvent`], Any, None]
    """
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".json"):
            yield pv_job_file_to_event_sequence(
                os.path.join(folder_path, file_name)
            )


def pv_jobs_from_folder_to_puml_file(
    folder_path: str,
    puml_file_path: str = "default.puml",
    puml_name: str = "default_name",
) -> None:
    """Reads a folder of PV job json array files and writes the PlantUML
    sequence diagram to a file

    :param folder_path: The path to the folder containing the PV job json files
    :type folder_path: `str`
    :param puml_file_path: The path to save the PlantUML file to
    :type puml_file_path: `str`
    :param puml_name: The name of the PlantUML group to create
    :type puml_name: `str`
    """
    pv_stream = pv_jobs_from_folder_to_event_sequence_streams(folder_path)
    pv_to_puml_file(pv_stream, puml_file_path, puml_name)


def pv_jobs_from_files_to_puml_file(
    file_paths: list[str],
    puml_file_path: str = "default.puml",
    puml_name: str = "default_name",
) -> None:
    """Reads a list of PV job json array files and writes the PlantUML
    sequence diagram to a file

    :param file_paths: The paths to the PV job json files
    :type file_paths: `list`[`str`]
    :param puml_file_path: The path to save the PlantUML file to
    :type puml_file_path: `str`
    :param puml_name: The name of the PlantUML group to create
    :type puml_name: `str`
    """
    pv_stream = pv_job_files_to_event_sequence_streams(file_paths)
    pv_to_puml_file(pv_stream, puml_file_path, puml_name)
