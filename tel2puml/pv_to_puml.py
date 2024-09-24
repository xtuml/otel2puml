"""Module to convert a stream of PV event sequences to a PlantUML sequence
diagram, inferring the logic from the PV event sequences.
"""

from typing import Generator, Iterable, Any
import json
import os

from tel2puml.tel2puml_types import PVEvent
from tel2puml.data_pipelines.data_ingestion import (
    cluster_events_by_job_id,
    update_and_create_events_from_clustered_pvevents,
)
from tel2puml.data_pipelines.data_creation import transform_dict_into_pv_event
from tel2puml.events import create_graph_from_events
from tel2puml.walk_puml_graph.walk_puml_logic_graph import walk_nested_graph
from tel2puml.walk_puml_graph.node_update import (
    update_nested_node_graph_with_break_points,
)
from tel2puml.loop_detection.detect_loops import detect_loops
from tel2puml.walk_puml_graph.create_node_graph_from_event_graph import (
    create_node_graph_from_event_graph,
)
from tel2puml.walk_puml_graph.find_and_add_loop_kill_paths import (
    find_and_add_loop_kill_paths_to_nested_graphs,
)
from tel2puml.puml_graph.graph import (
    remove_dummy_start_and_end_events_from_nested_graphs,
    update_nested_sub_graphs_for_dummy_break_event_nodes,
)


def pv_to_puml_string(
    pv_stream: Iterable[Iterable[PVEvent]],
    puml_name: str = "default_name",
    keep_dummy_events: bool = False,
) -> str:
    """Converts a stream of PV event sequences to a PlantUML sequence diagram,
    inferring the logic from the PV event sequences and the structure from the
    from connections between events.

    :param pv_stream: A Iterable of PV event sequences
    :type pv_stream: `Iterable`[`Iterable`[:class:`PVEvent`]]
    :param puml_name: The name of the PlantUML group to create
    :type puml_name: `str`
    :param keep_dummy_events: Boolean to keep dummy events in the PlantUML
    :type keep_dummy_events: `bool`
    :return: The PlantUML string
    :rtype: `str`
    """
    # ingest events and create graph
    events = update_and_create_events_from_clustered_pvevents(
        pv_stream, add_dummy_start=True
    )
    initial_events_graph = create_graph_from_events(events.values())
    # detect loops
    nested_loop_event_graph = detect_loops(initial_events_graph)
    # convert graph to Node graph
    node_graph = create_node_graph_from_event_graph(nested_loop_event_graph)
    # update nested graph with break points
    update_nested_node_graph_with_break_points(node_graph)
    # add loop kill paths to nested graphs
    find_and_add_loop_kill_paths_to_nested_graphs(node_graph)
    # walk the nested graph and create the PlantUML graph
    puml_graph = walk_nested_graph(node_graph)
    # remove dummy start and end events
    if not keep_dummy_events:
        update_nested_sub_graphs_for_dummy_break_event_nodes(puml_graph)
    remove_dummy_start_and_end_events_from_nested_graphs(puml_graph)
    return puml_graph.write_puml_string(puml_name)


def pv_to_puml_file(
    pv_stream: Iterable[Iterable[PVEvent]],
    puml_file_path: str = "default.puml",
    puml_name: str = "default_name",
    keep_dummy_events: bool = False,
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
    :param keep_dummy_events: Boolean to keep dummy events in the PlantUML
    :type keep_dummy_events: `bool`
    """
    puml_string = pv_to_puml_string(pv_stream, puml_name, keep_dummy_events)
    with open(puml_file_path, "w") as puml_file:
        puml_file.write(puml_string)


def pv_event_file_to_event(file_path: str) -> PVEvent:
    """Reads a PV event json file and returns the event

    :param file_path: The path to the PV event json file
    :type file_path: `str`
    :return: The event
    :rtype: :class:`PVEvent`
    """
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
        if not isinstance(data, dict):
            raise ValueError("The file does not contain a single event")
    return transform_dict_into_pv_event(data)


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
        if not isinstance(data, list):
            raise ValueError("The file does not contain a list of events")
    out_data: list[PVEvent] = []
    for event in data:
        if not isinstance(event, dict):
            raise ValueError("The file does not contain a list of events")
        out_data.append(transform_dict_into_pv_event(event))
    return out_data


def pv_events_from_folder_to_event_stream(
    folder_path: str,
) -> Generator[PVEvent, Any, None]:
    """Reads a folder of PV event json files and yields the events when
    iterated over

    :param folder_path: The path to the folder containing the PV event json
    files
    :type folder_path: `str`
    :return: A generator of events
    :rtype: `Generator`[:class:`PVEvent`, Any, None]
    """
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".json"):
            yield pv_event_file_to_event(os.path.join(folder_path, file_name))


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
    keep_dummy_events: bool = False,
) -> None:
    """Reads a folder of PV job json array files and writes the PlantUML
    sequence diagram to a file

    :param folder_path: The path to the folder containing the PV job json files
    :type folder_path: `str`
    :param puml_file_path: The path to save the PlantUML file to
    :type puml_file_path: `str`
    :param puml_name: The name of the PlantUML group to create
    :type puml_name: `str`
    :param keep_dummy_events: Boolean to keep dummy events in the PlantUML
    :type keep_dummy_events: `bool`
    """
    pv_stream = pv_jobs_from_folder_to_event_sequence_streams(folder_path)
    pv_to_puml_file(pv_stream, puml_file_path, puml_name, keep_dummy_events)


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
    pv_stream = pv_events_from_folder_to_event_stream(folder_path)
    # map job id to pv events
    events_by_job_id = cluster_events_by_job_id(pv_stream)

    # pv_stream expects Iterable[Iterable[PVEvent]]
    pv_to_puml_file(
        pv_stream=[pv_stream for pv_stream in events_by_job_id.values()],
        puml_file_path=puml_file_path,
        puml_name=puml_name,
    )


def pv_streams_to_puml_files(
    pv_streams: Generator[
        tuple[str, Generator[Generator[PVEvent, Any, None], Any, None]],
        Any,
        None,
    ],
    file_directory: str = ".",
) -> None:
    """
    Function to convert and save a stream of PVEvents to puml files.

    :param pv_streams: Generator of tuples of job_name to generator of
    generators of PVEvents grouped by job_name, then job_id.
    :type pv_streams: `Generator`[`tuple`[`str`, `Generator`[`Generator`
    [:class:`PVEvent`, `Any`, `None`], `Any`, `None`]], `Any`, `None`]
    :param file_directory: The file directory to store puml files. Defaults to
    "."
    :type file_directory: `str`
    """
    for job_name, job_event_gen in pv_streams:
        puml_file_path = os.path.join(file_directory, f"{job_name}.puml")
        pv_to_puml_file(
            job_event_gen,
            puml_file_path=puml_file_path,
        )
