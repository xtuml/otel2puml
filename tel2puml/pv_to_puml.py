"""Module to convert a stream of PV event sequences to a PlantUML sequence
diagram, inferring the logic from the PV event sequences.
"""

from typing import Generator, Iterable, Any
import json
import os

import networkx as nx

from tel2puml.tel2puml_types import PVEvent
from tel2puml.data_pipelines.data_ingestion import (
    update_all_connections_from_clustered_events,
    cluster_events_by_job_id,
    update_and_create_events_from_clustered_pvevents
)
from tel2puml.events import (
    remove_detected_loop_data_from_events,
    events_to_markov_graph,
    get_event_reference_from_events,
    create_graph_from_events
)
from tel2puml.walk_puml_graph.node import (
    merge_markov_without_loops_and_logic_detection_analysis,
)
from tel2puml.walk_puml_graph.walk_puml_logic_graph import (
    create_puml_graph_from_node_class_graph,
    walk_nested_graph
)
from tel2puml.detect_loops import (
    detect_loops,
    get_all_kill_edges_from_loops,
    remove_loop_data_from_graph
)
from tel2puml.puml_graph.graph_loop_insert import insert_loops
from tel2puml.walk_puml_graph.node_update import (
    update_nodes_with_break_points_from_loops,
    get_node_to_node_map_from_edges,
    add_loop_kill_paths_for_nodes,
    update_nested_node_graph_with_break_points
)
from tel2puml.loop_detection.detect_loops import (
    detect_loops as detect_loops_v2
)
from tel2puml.walk_puml_graph.create_node_graph_from_event_graph import (
    create_node_graph_from_event_graph
)
from tel2puml.walk_puml_graph.find_and_add_loop_kill_paths import (
    find_and_add_loop_kill_paths_to_nested_graphs,
)
from tel2puml.puml_graph.graph import (
    remove_dummy_start_and_end_events_from_nested_graphs,
    update_nested_sub_graphs_for_dummy_break_event_nodes
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


def pv_to_puml_string_v2(
    pv_stream: Iterable[Iterable[PVEvent]],
    puml_name: str = "default_name",
) -> str:
    """Converts a stream of PV event sequences to a PlantUML sequence diagram,
    inferring the logic from the PV event sequences and the structure from the
    from connections between events.

    :param pv_stream: A Iterable of PV event sequences
    :type pv_stream: `Iterable`[`Iterable`[:class:`PVEvent`]]
    :param puml_name: The name of the PlantUML group to create
    :type puml_name: `str`
    :return: The PlantUML string
    :rtype: `str`
    """
    # ingest events and create graph
    events = update_and_create_events_from_clustered_pvevents(pv_stream)
    initial_events_graph = create_graph_from_events(events.values())
    # detect loops
    nested_loop_event_graph = detect_loops_v2(initial_events_graph)
    # convert graph to Node graph
    node_graph = create_node_graph_from_event_graph(nested_loop_event_graph)
    # update nested graph with break points
    update_nested_node_graph_with_break_points(node_graph)
    # add loop kill paths to nested graphs
    find_and_add_loop_kill_paths_to_nested_graphs(node_graph)
    # walk the nested graph and create the PlantUML graph
    puml_graph = walk_nested_graph(node_graph)
    # remove dummy start and end events
    update_nested_sub_graphs_for_dummy_break_event_nodes(puml_graph)
    remove_dummy_start_and_end_events_from_nested_graphs(puml_graph)
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
    puml_string = pv_to_puml_string_v2(pv_stream, puml_name)
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


def pv_events_from_folder_to_puml_file(
    folder_path: str,
    puml_file_path: str = "default.puml",
    puml_name: str = "default_name",
    group_by_job: bool = True,
) -> None:
    """Reads a folder of PV json job array files, groups events by jobId and
    writes the PlantUML sequence diagram

    :param folder_path: The path to the folder containing the PV job json files
    :type folder_path: `str`
    :param puml_file_path: The filepath of the puml file output
    :type puml_file_path: `str`
    :param group_by_job: Boolean to group events by job id
    :type group_by_job: `bool`
    """
    if not group_by_job:
        return
    # parse events from folder into pv stream
    pv_stream = pv_jobs_from_folder_to_event_sequence_streams(folder_path)
    # map job id to pv events
    events_by_job_id = cluster_events_by_job_id(pv_stream)

    # pv_stream expects Iterable[Iterable[PVEvent]]
    pv_to_puml_file(
        pv_stream=[pv_stream for pv_stream in events_by_job_id.values()],
        puml_file_path=puml_file_path,
        puml_name=puml_name,
    )
