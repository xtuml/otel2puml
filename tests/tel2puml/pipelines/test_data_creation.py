"""tests for module test_data_creation.py"""

from tel2puml.run_jAlergia import run
from tel2puml.read_uml_file import get_event_list_from_puml

from tel2puml.pipelines.data_creation import (
    generate_valid_jobs_from_puml_file,
    generate_event_jsons,
    generate_test_data,
)


def test_generate_valid_jobs_from_puml_file() -> None:
    """tests for function generate_valid_jobs_from_puml_file"""
    input_puml_file = "puml_files/ANDFork_ANDFork_a.puml"
    result = list(generate_valid_jobs_from_puml_file(input_puml_file))
    # assert
    assert len(result) == 1
    job = result[0]
    assert len(job.events) == 6
    assert set([event.event_type for event in job.events]) == set(
        ["A", "B", "C", "D", "E", "F"]
    )


def test_generate_event_jsons() -> None:
    """tests for function generate_event_jsons"""
    jobs = list(
        generate_valid_jobs_from_puml_file("puml_files/ANDFork_ANDFork_a.puml")
    )
    result = list(generate_event_jsons(jobs))
    # assert
    assert len(result) == 6
    assert all([isinstance(event, dict) for event in result])
    assert all(
        set(["eventId", "eventType", "timestamp", "jobId"]).issubset(
            set(event.keys())
        )
        for event in result
    )
    assert set([event["eventType"] for event in result]) == set(
        ["A", "B", "C", "D", "E", "F"]
    )


def test_generate_test_data_default_args():
    """tests for function generate_test_data"""
    input_puml_file = "puml_files/ANDFork_ANDFork_a.puml"
    result = list(generate_test_data(input_puml_file))
    # assert
    assert len(result) == 6
    assert all([isinstance(event, dict) for event in result])
    assert all(
        set(["eventId", "eventType", "timestamp", "jobId"]).issubset(
            set(event.keys())
        )
        for event in result
    )
    assert set([event["eventType"] for event in result]) == set(
        ["A", "B", "C", "D", "E", "F"]
    )


def test_generate_test_data_num_paths_to_template():
    """tests for function generate_test_data"""
    input_puml_file = "puml_files/ANDFork_ANDFork_a.puml"
    result = list(
        generate_test_data(input_puml_file, num_paths_to_template=10)
    )
    # assert
    assert len(result) == 60
    assert all([isinstance(event, dict) for event in result])
    assert all(
        set(["eventId", "eventType", "timestamp", "jobId"]).issubset(
            set(event.keys())
        )
        for event in result
    )
    assert set([event["eventType"] for event in result]) == set(
        ["A", "B", "C", "D", "E", "F"]
    )


def test_generate_test_data_template_all_paths_true_num_paths_zero():
    """tests for function generate_test_data"""
    input_puml_file = "puml_files/ANDFork_ANDFork_a.puml"
    result = list(generate_test_data(input_puml_file, num_paths_to_template=0))
    # assert
    assert len(result) == 6
    assert all([isinstance(event, dict) for event in result])
    assert all(
        set(["eventId", "eventType", "timestamp", "jobId"]).issubset(
            set(event.keys())
        )
        for event in result
    )
    assert set([event["eventType"] for event in result]) == set(
        ["A", "B", "C", "D", "E", "F"]
    )


def test_generate_test_data_template_all_paths_false_large_num_paths():
    """tests for function generate_test_data"""
    input_puml_file = "puml_files/sequence_xor_fork.puml"
    num_templates = 10000
    result = list(
        generate_test_data(
            input_puml_file,
            template_all_paths=False,
            num_paths_to_template=num_templates,
        )
    )
    # assert
    event_types_count = {
        "C": 0,
        "D": 0,
        "E": 0,
    }
    job_ids = set()
    for event in result:
        job_ids.add(event["jobId"])
        if event["eventType"] in event_types_count:
            event_types_count[event["eventType"]] += 1
    count_prob = {
        event_type: count / num_templates
        for event_type, count in event_types_count.items()
    }
    assert len(job_ids) == num_templates
    assert sum(event_types_count.values()) == num_templates
    for prob in count_prob.values():
        assert 0.32 < prob < 0.34


def test_puml_conversion_to_markov_chain():
    """
    Test the conversion of a PlantUML file to a Markov chain representation.

    This function tests a function that reads a PlantUML file, extracts the
        event list, and runs the conversion process to obtain the Markov chain
        representation. It then compares the obtained representation with the
        expected output.

    Raises:
        AssertionError: If the obtained Markov chain representation does not
        match the expected output.
    """
    puml_file_name = "simple_test"

    event_list = get_event_list_from_puml(
        puml_file="puml_files/" + puml_file_name + ".puml",
        puml_key="ValidSols",
        debug=False,
    )
    j_alergia_model = str(run(event_list))

    expected_output_lines = [
        "digraph learnedModel {\n"
        'q0 [label="A"];\n'
        'q1 [label="B"];\n'
        'q2 [label="C"];\n'
        'q3 [label="D"];\n'
        'q0 -> q2  [label="0.5"];\n'
        'q0 -> q1  [label="0.5"];\n'
        'q1 -> q3  [label="1.0"];\n'
        'q2 -> q3  [label="1.0"];\n'
        '__start0 [label="", shape=none];\n'
        '__start0 -> q0  [label=""];\n'
        "}\n"
    ]

    expected_output = "".join(expected_output_lines)

    assert j_alergia_model == expected_output
