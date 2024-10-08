"""Module to convert OpenTelemetry data to PVEvents."""

import os
import json
import logging
from typing import Generator, Any

from tel2puml.otel_to_pv.config import IngestDataConfig, SequenceModelConfig
from tel2puml.otel_to_pv.ingest_otel_data import (
    ingest_data_into_dataholder,
    fetch_data_holder,
)
from tel2puml.otel_to_pv.sequence_otel import sequence_otel_job_id_streams
from tel2puml.tel2puml_types import PVEvent

LOGGER = logging.getLogger(__name__)


def otel_to_pv(
    config: IngestDataConfig,
    ingest_data: bool = False,
    find_unique_graphs: bool = False,
    save_events: bool = False,
    output_file_directory: str = ".",
) -> Generator[
    tuple[str, Generator[Generator[PVEvent, Any, None], Any, None]], Any, None
]:
    """
    Stream data from data holder and convert to PVEvents. Optional parameters
    to ingest data, find unique graphs within the data set, and save PVEvents
    as json job files.

    :param config: The configuration for data ingestion and processing.
    :type config: :class:`IngestDataConfig`
    :param ingest_data: Flag to indicate whether to load data into the data
    holder. Defaults to False.
    :type ingest_data: `bool`, optional
    :param find_unique_graphs: Flag to indicate whether to find unique graphs
    within the data holder object. Defaults to False.
    :type find_unique_graphs: `bool`, optional
    :return: Generator of tuples of job_name to generator of generators of
    PVEvents grouped by job_name, then job_id.
    :param save_events: Flag to indicate whether to save events as json to
    file. Defaults to False.
    :type save_events: bool
    :param output_file_directory: Output file directory.
    :type output_file_directory: `str`
    :rtype: `Generator`[`tuple`[`str`, `Generator`[`Generator`[:class:
    `PVEvent`, `Any`, `None`], `Any`, `None`]], `Any`, `None`]

    """
    if ingest_data:
        data_holder = ingest_data_into_dataholder(config)
    else:
        data_holder = fetch_data_holder(config)
    # validate spans
    data_holder.remove_inconsistent_jobs()
    # remove jobs totally within time buffer zones
    data_holder.remove_jobs_outside_of_time_window()
    # make sure job names are consistent in traces
    data_holder.update_job_names_by_root_span()
    # find unique graphs if required
    if find_unique_graphs:
        job_name_to_job_ids_map: dict[str, set[str]] | None = (
            data_holder.find_unique_graphs()
        )
    else:
        job_name_to_job_ids_map = None

    job_name_group_streams = data_holder.stream_data(job_name_to_job_ids_map)
    # get the async event groups from the config
    sequencer_config = config.get("sequencer", SequenceModelConfig())
    async_event_groups = sequencer_config.async_event_groups
    event_name_map_information = sequencer_config.event_name_map_information
    pv_event_gen = (
        (
            job_name,
            sequence_otel_job_id_streams(
                job_id_streams,
                async_flag=sequencer_config.async_flag,
                event_to_async_group_map=(
                    async_event_groups.get(job_name, None)
                ),
                event_types_map_information=(
                    event_name_map_information.get(job_name, None)
                ),
            ),
        )
        for job_name, job_id_streams in job_name_group_streams
    )
    if save_events:
        for job_name, pv_event_streams in pv_event_gen:
            handle_save_events(
                job_name, pv_event_streams, output_file_directory
            )

    return pv_event_gen


def handle_save_events(
    job_name: str,
    pv_event_streams: Generator[
        Generator[PVEvent, Any, None],
        Any,
        None,
    ],
    output_file_directory: str,
) -> None:
    """Function to handle the save events flag. Saves PVEvents as job json
    files within a job folder within the output file directory.

    :param job_name: The job name
    :type job_name: `str`
    :param pv_event_streams: Generator of generator of PVEvents
    :type pv_event_streams: `Generator`[ `Generator`[:class`PVEvent`, `Any`,
    `None`], `Any`, `None`, ]
    :param output_file_directory: Output file directory
    :type output_file_directory: `str`
    """
    try:
        os.makedirs(f"{output_file_directory}/{job_name}", exist_ok=True)
    except OSError as e:
        LOGGER.error(
            f"Error creating directory {output_file_directory}/"
            f"{job_name}: {e}"
        )
    file_no = 1
    for pv_event_stream in pv_event_streams:
        for pv_event in pv_event_stream:
            save_pv_event_to_file(
                job_name, pv_event, output_file_directory, file_no
            )
            file_no += 1


def save_pv_event_to_file(
    job_name: str, pv_event: PVEvent, output_file_directory: str, count: int
) -> None:
    """Saves a PVEvent as a json file to a folder within the output directory.

    :param pv_event: The PVEvent to save
    :type pv_event: :class:`PVEvent`
    :param output_file_directory: Output file directory
    :type output_file_directory: `str`
    """
    try:
        with open(
            f"{output_file_directory}/{job_name}/"
            f"pv_event_sequence_{count}.json",
            "w",
        ) as f:
            json.dump(pv_event, f, indent=4)
    except IOError as e:
        LOGGER.error(
            f"Error writing file {output_file_directory}/"
            f"{job_name}/pv_event_sequence_{count}.json: {e}"
        )
