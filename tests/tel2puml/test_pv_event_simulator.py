"""tests for module test_data_creation.py"""

from typing import Any

import pytest
from pytest import MonkeyPatch

from tel2puml.pv_event_simulator import (
    generate_valid_jobs_from_puml_file,
    generate_event_jsons,
    generate_test_data,
    generate_test_data_event_sequences_from_puml,
    Job,
    transform_dict_into_pv_event,
)
from tel2puml.tel2puml_types import PVEvent, PVEventMappingConfig


class TestJob:
    """Test class for Job"""

    def input_job(self) -> list[PVEvent]:
        """Returns a list of PVEvent objects"""
        return [
            PVEvent(
                eventType="A",
                jobId="B",
                timestamp="2021-01-01T00:00:00",
                eventId=f"{i}",
                jobName="C",
                applicationName="D",
                previousEventIds=[] if i == 0 else [f"{i-1}"],
            )
            for i in range(2)
        ]

    def input_job_with_dict(self) -> list[dict[str, Any]]:
        """Returns a list of dictionaries representing PVEvent objects"""
        return [{**event} for event in self.input_job()]

    def test_init(self) -> None:
        """tests for Job.__init__"""
        job = Job()
        assert job.events == []

    def test_parse_input_job(self) -> None:
        """tests for Job.parse_input_job_file"""
        job = Job()
        job.parse_input_job(self.input_job_with_dict())
        assert len(job.events) == 2
        assert job.events == self.input_job()

    def test_sim_event(self) -> None:
        """tests for Job.sim_event"""
        events = self.input_job()
        event = events[1]
        sim_event = Job.sim_event(event, "X", {"0": "map0", "1": "map1"})
        expected_event = PVEvent(
            eventType="A",
            jobId="X",
            timestamp="2021-01-01T00:00:00",
            eventId="map1",
            jobName="C",
            applicationName="D",
            previousEventIds=["map0"],
        )
        assert sim_event == expected_event
        # test case where event id map does not contain the event id
        with pytest.raises(ValueError):
            Job.sim_event(event, "X", {"0": "map0"})
        # test case where event id map does not contain the previous event id
        with pytest.raises(ValueError):
            Job.sim_event(event, "X", {"1": "map1"})
        # test positive case where the previous event is a string
        event["previousEventIds"] = "0"
        sim_event = Job.sim_event(event, "X", {"0": "map0", "1": "map1"})
        assert sim_event == expected_event

    @staticmethod
    @pytest.fixture
    def patch_uuid4(monkeypatch: MonkeyPatch) -> None:
        """fixture to patch uuid4"""
        import tel2puml.pv_event_simulator

        to_pop_from = ["map0", "map1", "X"]
        monkeypatch.setattr(
            tel2puml.pv_event_simulator, "uuid4", lambda: to_pop_from.pop(0)
        )

    @pytest.mark.usefixtures("patch_uuid4")
    def test_create_new_event_id_map(self) -> None:
        """tests for Job.create_new_event_id_map"""
        job = Job()
        job.parse_input_job(self.input_job_with_dict())
        event_id_map = job.create_new_event_id_map()
        assert event_id_map == {"0": "map0", "1": "map1"}
        # test case where the job has no events
        job.events = []
        event_id_map = job.create_new_event_id_map()
        assert event_id_map == {}

    @pytest.mark.usefixtures("patch_uuid4")
    def test_simulate_job(self) -> None:
        """tests for Job.simulate_job"""
        job = Job()
        job.parse_input_job(self.input_job_with_dict())
        events = list(job.simulate_job())
        assert len(events) == 2
        for i, out_event, expected_event in zip(
            range(2), events, self.input_job()
        ):
            assert (
                out_event["applicationName"]
                == expected_event["applicationName"]
            )
            assert out_event["eventType"] == expected_event["eventType"]
            assert out_event["jobId"] == "X"
            assert out_event["timestamp"] == expected_event["timestamp"]
            assert out_event["jobName"] == expected_event["jobName"]
            if i == 0:
                assert out_event["previousEventIds"] == []
                assert out_event["eventId"] == "map0"
            else:
                assert out_event["previousEventIds"] == ["map0"]
                assert out_event["eventId"] == "map1"


def test_generate_valid_jobs_from_puml_file() -> None:
    """tests for function generate_valid_jobs_from_puml_file"""
    input_puml_file = "puml_files/ANDFork_ANDFork_a.puml"
    result = list(generate_valid_jobs_from_puml_file(input_puml_file))
    # assert
    assert len(result) == 1
    job = result[0]
    assert len(job.events) == 6
    assert set([event["eventType"] for event in job.events]) == set(
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


def test_generate_test_data_default_args() -> None:
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


def test_generate_test_data_num_paths_to_template() -> None:
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


def test_generate_test_data_template_all_paths_true_num_paths_zero() -> None:
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


def test_generate_test_data_template_all_paths_false_large_num_paths() -> None:
    """tests for function generate_test_data"""
    input_puml_file = "puml_files/sequence_xor_fork.puml"
    num_templates = 100000
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
        assert 0.32 <= prob < 0.3466


def test_generate_test_data_event_sequences_from_puml_branch_counts() -> None:
    """tests for function generate_test_data_event_sequences_from_puml with
    branch counts"""
    input_puml_file = "puml_files/simple_branch_count.puml"
    result = list(
        generate_test_data_event_sequences_from_puml(
            input_puml_file, is_branch_puml=True
        )
    )
    # two sequences should be generated
    assert len(result) == 2
    # the sequences generated should have 2 or 3 events of type C, exclusively
    expected_numbers_of_event_c = [2, 3]
    for event_sequence in result:
        num_c = 0
        for event in event_sequence:
            if event["eventType"] == "C":
                num_c += 1
        assert num_c in expected_numbers_of_event_c
        expected_numbers_of_event_c.remove(num_c)
    assert len(expected_numbers_of_event_c) == 0


def test_transform_dict_into_pv_event_no_mapping_config() -> None:
    """Tests the function transform_dict_into_pv_event with no mapping config
    """

    def validate_pv_event(pv_event: PVEvent, prev_id: bool) -> None:
        """Helper function to validate pv_event"""
        assert isinstance(pv_event, dict)
        assert pv_event["eventId"] == "event_test"
        assert pv_event["eventType"] == "eventType_test"
        assert pv_event["jobId"] == "jobId_test"
        assert pv_event["timestamp"] == "timestamp_test"
        assert pv_event["applicationName"] == "applicationName_test"
        assert pv_event["jobName"] == "jobName_test"
        if prev_id:
            assert pv_event["previousEventIds"] == ["1"]

    # Test 1: Successful transformation no previous_event_id
    pv_event_dict: dict[str, Any] = {
        "eventId": "event_test",
        "eventType": "eventType_test",
        "jobId": "jobId_test",
        "timestamp": "timestamp_test",
        "applicationName": "applicationName_test",
        "jobName": "jobName_test",
    }

    pv_event = transform_dict_into_pv_event(pv_event_dict)
    validate_pv_event(pv_event, False)

    # Test 2: Successful transformation previous_event_id as string
    pv_event_dict = {
        "eventId": "event_test",
        "eventType": "eventType_test",
        "jobId": "jobId_test",
        "timestamp": "timestamp_test",
        "applicationName": "applicationName_test",
        "jobName": "jobName_test",
        "previousEventIds": "1",
    }

    pv_event = transform_dict_into_pv_event(pv_event_dict)
    validate_pv_event(pv_event, True)

    # Test 3: Successful transformation previous_event_id as list
    pv_event_dict = {
        "eventId": "event_test",
        "eventType": "eventType_test",
        "jobId": "jobId_test",
        "timestamp": "timestamp_test",
        "applicationName": "applicationName_test",
        "jobName": "jobName_test",
        "previousEventIds": ["1"],
    }

    pv_event = transform_dict_into_pv_event(pv_event_dict)
    validate_pv_event(pv_event, True)

    # Test 4: Incorrect mandatory field
    pv_event_dict = {
        "eventId": "event_test",
        "IncorrectField": "eventType_test",
        "jobId": "jobId_test",
        "timestamp": "timestamp_test",
        "applicationName": "applicationName_test",
        "jobName": "jobName_test",
    }
    with pytest.raises(ValueError):
        pv_event = transform_dict_into_pv_event(pv_event_dict)


def test_transform_dict_into_pv_event_with_mapping_config() -> None:
    """Tests the function transform_dict_into_pv_event with mapping config"""

    def validate_pv_event(pv_event: PVEvent, prev_id: bool) -> None:
        """Helper function to validate pv_event"""
        assert isinstance(pv_event, dict)
        assert pv_event["eventId"] == "event_test"
        assert pv_event["eventType"] == "eventType_test"
        assert pv_event["jobId"] == "jobId_test"
        assert pv_event["timestamp"] == "timestamp_test"
        assert pv_event["applicationName"] == "applicationName_test"
        assert pv_event["jobName"] == "jobName_test"
        if prev_id:
            assert pv_event["previousEventIds"] == ["1"]

    # mapping config used for all tests
    mapping_config = PVEventMappingConfig(
        jobId="jobIdNew",
        eventId="eventIdNew",
        timestamp="timestampNew",
        previousEventIds="previousEventIdsNew",
        applicationName="applicationNameNew",
        jobName="jobNameNew",
        eventType="eventTypeNew",
    )
    # Test 1: Successful transformation no previous_event_id
    pv_event_dict: dict[str, Any] = {
        "eventIdNew": "event_test",
        "eventTypeNew": "eventType_test",
        "jobIdNew": "jobId_test",
        "timestampNew": "timestamp_test",
        "applicationNameNew": "applicationName_test",
        "jobNameNew": "jobName_test",
    }

    pv_event = transform_dict_into_pv_event(
        pv_event_dict, mapping_config=mapping_config
    )
    validate_pv_event(pv_event, False)

    # Test 2: Successful transformation previous_event_id as string
    pv_event_dict = {
        "eventIdNew": "event_test",
        "eventTypeNew": "eventType_test",
        "jobIdNew": "jobId_test",
        "timestampNew": "timestamp_test",
        "applicationNameNew": "applicationName_test",
        "jobNameNew": "jobName_test",
        "previousEventIdsNew": "1",
    }

    pv_event = transform_dict_into_pv_event(
        pv_event_dict, mapping_config=mapping_config
    )
    validate_pv_event(pv_event, True)

    # Test 3: Successful transformation previous_event_id as list
    pv_event_dict = {
        "eventIdNew": "event_test",
        "eventTypeNew": "eventType_test",
        "jobIdNew": "jobId_test",
        "timestampNew": "timestamp_test",
        "applicationNameNew": "applicationName_test",
        "jobNameNew": "jobName_test",
        "previousEventIdsNew": ["1"],
    }

    pv_event = transform_dict_into_pv_event(
        pv_event_dict, mapping_config=mapping_config
    )
    validate_pv_event(pv_event, True)

    # Test 4: Incorrect mandatory field
    pv_event_dict = {
        "eventIdNew": "event_test",
        "IncorrectField": "eventType_test",
        "jobIdNew": "jobId_test",
        "timestampNew": "timestamp_test",
        "applicationNameNew": "applicationName_test",
        "jobNameNew": "jobName_test",
    }
    with pytest.raises(ValueError):
        pv_event = transform_dict_into_pv_event(
            pv_event_dict, mapping_config=mapping_config
        )
