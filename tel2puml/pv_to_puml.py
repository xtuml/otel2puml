"""Module to convert a stream of PV event sequences to a PlantUML sequence
diagram, inferring the logic from the PV event sequences.
"""
from typing import Generator, Iterable, Any
from itertools import tee
import json
import os

from tel2puml.utils import convert_nested_generator_to_generator_of_list
from tel2puml.tel2puml_types import PVEvent
from tel2puml.pipelines.logic_detection_pipeline import (
    update_all_connections_from_clustered_events,
    remove_detected_loop_data_from_events
)
from tel2puml.jAlergiaPipeline import (
    audit_event_sequences_to_network_x,
    remove_loop_data_from_graph
)
from tel2puml.node_map_to_puml.node import (
    merge_markov_without_loops_and_logic_detection_analysis,
    create_puml_graph_from_node_class_graph
)
from tel2puml.detect_loops import detect_loops
from tel2puml.puml_graph.graph_loop_insert import insert_loops


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
    pv_stream_logic, pv_stream_markov = tee(
        convert_nested_generator_to_generator_of_list(
            pv_stream
        ),
        2
    )
    # run the logic detection pipeline
    forward_logic, backward_logic = (
        update_all_connections_from_clustered_events(pv_stream_logic)
    )
    # run the markov chain analysis
    markov_graph, event_node_references = audit_event_sequences_to_network_x(
        pv_stream_markov
    )
    # run the loop detection pipeline
    loops = detect_loops(markov_graph)
    # remove the loop edges from the Markov graph
    remove_loop_data_from_graph(markov_graph, loops)
    # remove loop edges from the logic trees
    remove_detected_loop_data_from_events(
        loops, forward_logic, event_node_references["event_reference"]
    )
    # merge the Markov graph and the logic trees
    merged_markov_and_logic = (
        merge_markov_without_loops_and_logic_detection_analysis(
            (markov_graph, event_node_references["event_reference"]),
            backward_logic,
            forward_logic
        )
    )
    # create the PlantUML graph
    puml_graph = create_puml_graph_from_node_class_graph(
        merged_markov_and_logic
    )
    # insert the detected loops into the PlantUML graph
    insert_loops(puml_graph, loops)
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
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def pv_job_files_to_event_sequence_streams(
    file_paths: list[str],
) -> Generator[list[PVEvent], Any, None]:
    for file_path in file_paths:
        yield pv_job_file_to_event_sequence(file_path)


def pv_jobs_from_folder_to_event_sequence_streams(
    folder_path: str,
) -> Generator[list[PVEvent], Any, None]:
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
    pv_stream = pv_jobs_from_folder_to_event_sequence_streams(folder_path)
    pv_to_puml_file(pv_stream, puml_file_path, puml_name)


def pv_jobs_from_files_to_puml_file(
    file_paths: list[str],
    puml_file_path: str = "default.puml",
    puml_name: str = "default_name",
) -> None:
    pv_stream = pv_job_files_to_event_sequence_streams(file_paths)
    pv_to_puml_file(pv_stream, puml_file_path, puml_name)
