"""Module to generate test data from a puml file."""

from typing import Generator, Any
import random

from test_harness.protocol_verifier.simulator_data import (
    Job,
    generate_single_events,
)
from test_event_generator.io.run import puml_file_to_test_events
from tel2puml.tel2puml_types import DUMMY_START_EVENT


def generate_test_data(
    input_puml_file: str,
    template_all_paths: bool = True,
    num_paths_to_template: int = 1,
    is_branch_puml: bool = False,
) -> Generator[dict, Any, None]:
    """
    This function creates test data from a puml file. It uses the
    test_event_generator package to create the test data.
    :param input_puml_file: The puml file that contains the sequence diagram.
    :type input_puml_file: `str`
    :param template_all_paths: If True, the function will template all paths
    in the sequence diagram. If False, the function will template a random
    path in the sequence diagram, defaults to `True`.
    :type template_all_paths: `bool`, optional
    :param num_paths_to_template: The number of paths to template. This
    parameter is only used if template_all_paths is False, defaults to `1`.
    :type num_paths_to_template: `int`, optional
    :param is_branch_puml: If True, the function will generate test data for
    a puml file with branches, that is it will generate branch counts with two
    and three branches, defaults to `False`.
    :type is_branch_puml: `bool`, optional
    :return: A generator that yields the test data.
    :rtype: `Generator[dict, Any, None]`
    """
    for event_sequence in generate_test_data_event_sequences_from_puml(
        input_puml_file, template_all_paths, num_paths_to_template,
        is_branch_puml
    ):
        yield from event_sequence


def generate_test_data_event_sequences_from_puml(
    input_puml_file: str,
    template_all_paths: bool = True,
    num_paths_to_template: int = 1,
    is_branch_puml: bool = False,
    remove_dummy_start_event: bool = False,
) -> Generator[Generator[dict, Any, None], Any, None]:
    """This function creates test data from a puml file as distinct sequences.
    It uses the test_event_generator package to create the test data.

    :param input_puml_file: The puml file that contains the sequence diagram.
    :type input_puml_file: `str`
    :param template_all_paths: If True, the function will template all paths
    in the sequence diagram. If False, the function will template a random
    path in the sequence diagram, defaults to `True`.
    :type template_all_paths: `bool`, optional
    :param num_paths_to_template: The number of paths to template. This
    parameter is only used if template_all_paths is False, defaults to `1`.
    :type num_paths_to_template: `int`, optional
    :param is_branch_puml: If True, the function will generate test data for
    a puml file with branches, that is it will generate branch counts with two
    and three branches, defaults to `False`.
    :type is_branch_puml: `bool`, optional
    :return: A generator that yields the test data.
    :rtype: `Generator[str, Any, None]`
    """
    test_job_templates = [
        job for job in generate_valid_jobs_from_puml_file(
            input_puml_file,
        )
    ]
    if is_branch_puml:
        test_job_templates.extend(
            [job for job in generate_valid_jobs_from_puml_file(
                input_puml_file,
                num_branches=3
            )]
        )
    counter = 0
    if template_all_paths:
        for job in test_job_templates:
            event_jsons = generate_event_jsons([job])
            if remove_dummy_start_event:
                event_jsons = remove_dummy_start_event_from_event_sequence(
                    event_jsons
                )
            yield event_jsons
        counter = len(test_job_templates)
    while counter < num_paths_to_template:
        job_in_list = random.choices(test_job_templates, k=1)
        counter += 1
        event_jsons = generate_event_jsons(job_in_list)
        if remove_dummy_start_event:
            event_jsons = remove_dummy_start_event_from_event_sequence(
                event_jsons
            )
        yield event_jsons


def remove_dummy_start_event_from_event_sequence(
    event_sequence: Generator[dict, Any, None]
) -> Generator[dict, Any, None]:
    """This function removes the dummy start event from an event sequence that
    is given the appropriate event type.

    :param event_sequence: The event sequence.
    :type event_sequence: `Generator[dict, Any, None]`
    :return: A generator that yields the event sequence without the dummy
    start event.
    :rtype: `Generator[dict, Any, None]`
    """
    dummy_start_event_id = None
    prev_event_id_map: dict[str, list[str]] = {}
    events: dict[str, dict] = {}
    for event in event_sequence:
        events[event["eventId"]] = event
        if "previousEventIds" in event:
            previous_event_ids = event["previousEventIds"]
            if isinstance(previous_event_ids, str):
                previous_event_ids = [previous_event_ids]
            for previous_event_id in previous_event_ids:
                if previous_event_id not in prev_event_id_map:
                    prev_event_id_map[previous_event_id] = []
                prev_event_id_map[previous_event_id].append(event["eventId"])
        if event["eventType"] == DUMMY_START_EVENT:
            dummy_start_event_id = event["eventId"]
    if dummy_start_event_id is not None:
        for event_id in prev_event_id_map[dummy_start_event_id]:
            previous_event_ids = events[event_id]["previousEventIds"]
            if isinstance(previous_event_ids, str):
                previous_event_ids = [previous_event_ids]
            previous_event_ids.remove(dummy_start_event_id)
            if len(previous_event_ids) == 0:
                del events[event_id]["previousEventIds"]
            else:
                event["previousEventIds"] = previous_event_ids
        del events[dummy_start_event_id]
    yield from events.values()


def generate_event_jsons(
    jobs: list[Job],
) -> Generator[dict, Any, None]:
    """This function generates event jsons from a list of jobs.

    :param jobs: A list of jobs.
    :type jobs: `list`[:class:`Job`]
    :return: A generator that yields the event jsons.
    :rtype: `Generator`[`dict`, `Any`, `None`]
    """
    for generator_of_datums in generate_single_events(jobs):
        for datum in generator_of_datums:
            yield datum.kwargs["list_dict"][0]


def generate_valid_jobs_from_puml_file(
    input_puml_file: str,
    **extra_options,
) -> Generator[Job, Any, None]:
    """This function generates valid jobs from a puml file.

    :param input_puml_file: The puml file that contains the sequence diagram.
    :type input_puml_file: `str`
    :param extra_options: Extra options to pass to the test
    event generator.
    :type extra_options: `dict`
    :return: A generator that yields the valid jobs.
    :rtype: `Generator`[:class:`Job`, `Any`, `None`]
    """
    event_gen_options_to_use = {"invalid": False}
    event_gen_options_to_use.update(extra_options)
    test_jobs_with_info = puml_file_to_test_events(
        input_puml_file, **event_gen_options_to_use
    )
    for test_job_event_list, *_ in test_jobs_with_info[
        list(test_jobs_with_info.keys())[0]
    ]["ValidSols"][0]:
        job = Job()
        job.parse_input_jobfile(test_job_event_list)
        yield job
