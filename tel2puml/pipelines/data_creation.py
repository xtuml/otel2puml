"""Module to generate test data from a puml file."""

from typing import Generator, Any
import random

from test_harness.protocol_verifier.simulator_data import (
    Job,
    generate_single_events,
)
from test_event_generator.io.run import puml_file_to_test_events


def generate_test_data(
    input_puml_file: str,
    template_all_paths: bool = True,
    num_paths_to_template: int = 1,
) -> Generator[dict, Any, None]:
    """
    This function creates test data from a puml file. It uses the
    test_event_generator package to create the test data.
    :param input_puml_file: The puml file that contains the sequence diagram.
    :type input_puml_file: `str`
    :param template_all_paths: If True, the function will template all paths
    in the sequence diagram. If False, the function will template a random
    path in the sequence diagram.
    :type template_all_paths: `bool`
    :param num_paths_to_template: The number of paths to template. This
    parameter is only used if template_all_paths is False.
    :type num_paths_to_template: `int`
    :return: A generator that yields the test data.
    :rtype: `Generator[dict, Any, None]`
    """
    for event_sequence in generate_test_data_event_sequences_from_puml(
        input_puml_file, template_all_paths, num_paths_to_template
    ):
        yield from event_sequence


def generate_test_data_event_sequences_from_puml(
    input_puml_file: str,
    template_all_paths: bool = True,
    num_paths_to_template: int = 1,
) -> Generator[Generator[dict, Any, None], Any, None]:
    """This function creates test data from a puml file as distinct sequences.
    It uses the test_event_generator package to create the test data.

    :param input_puml_file: The puml file that contains the sequence diagram.
    :type input_puml_file: `str`
    :param template_all_paths: If True, the function will template all paths
    in the sequence diagram. If False, the function will template a random
    path in the sequence diagram.
    :type template_all_paths: `bool`
    :param num_paths_to_template: The number of paths to template. This
    parameter is only used if template_all_paths is False.
    :type num_paths_to_template: `int`
    :return: A generator that yields the test data.
    :rtype: `Generator[str, Any, None]`
    """
    test_job_templates = [
        job for job in generate_valid_jobs_from_puml_file(input_puml_file)
    ]
    counter = 0
    if template_all_paths:
        for job in test_job_templates:
            yield generate_event_jsons([job])
        counter = len(test_job_templates)
    while counter < num_paths_to_template:
        job_in_list = random.choices(test_job_templates, k=1)
        counter += 1
        yield generate_event_jsons(job_in_list)


def generate_event_jsons(jobs: list[Job]) -> Generator[dict, Any, None]:
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
) -> Generator[Job, Any, None]:
    """This function generates valid jobs from a puml file.

    :param input_puml_file: The puml file that contains the sequence diagram.
    :type input_puml_file: `str`
    :return: A generator that yields the valid jobs.
    :rtype: `Generator`[:class:`Job`, `Any`, `None`]
    """
    event_gen_options_to_use = {"invalid": False}
    test_jobs_with_info = puml_file_to_test_events(
        input_puml_file, **event_gen_options_to_use
    )
    for test_job_event_list, *_ in test_jobs_with_info[
        list(test_jobs_with_info.keys())[0]
    ]["ValidSols"][0]:
        job = Job()
        job.parse_input_jobfile(test_job_event_list)
        yield job
