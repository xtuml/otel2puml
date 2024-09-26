"""Test cases for pv_to_puml module"""

import os
import json
from typing import Generator, Any
from pathlib import Path

import pytest

from tel2puml.pv_to_puml import (
    pv_to_puml_string,
    pv_streams_to_puml_files,
    pv_files_to_pv_streams,
)
from tel2puml.data_pipelines.data_creation import (
    generate_test_data_event_sequences_from_puml,
)
from tel2puml.check_puml_equiv import check_puml_equivalence
from tel2puml.tel2puml_types import PVEvent


def test_pv_to_puml_string() -> None:
    """Test the `pv_to_puml_string` function returns a puml string of the
    expected length and structure
    """
    test_data = generate_test_data_event_sequences_from_puml(
        "puml_files/complicated_test.puml"
    )
    puml_string = pv_to_puml_string(test_data)
    with open(
        "puml_files/complicated_test.puml", "r", encoding="utf-8"
    ) as file:
        expected_puml_string = file.read()
    assert check_puml_equivalence(puml_string, expected_puml_string)
    # test with a loop
    test_data = generate_test_data_event_sequences_from_puml(
        "puml_files/loop_ANDFork_a.puml"
    )
    puml_string = pv_to_puml_string(test_data)
    with open("puml_files/loop_ANDFork_a.puml", "r", encoding="utf-8") as file:
        expected_puml_string = file.read()
    assert check_puml_equivalence(puml_string, expected_puml_string)
    # test with branch counts
    test_data = generate_test_data_event_sequences_from_puml(
        "puml_files/sequence_branch_counts.puml", is_branch_puml=True
    )
    puml_string = pv_to_puml_string(test_data)
    with open(
        "puml_files/sequence_branch_counts.puml", "r", encoding="utf-8"
    ) as file:
        expected_puml_string = file.read()
    assert check_puml_equivalence(puml_string, expected_puml_string)
    # test with a merge on the same event under the same parent logic block
    test_data = generate_test_data_event_sequences_from_puml(
        "puml_files/complicated_merge_with_same_event.puml"
    )
    puml_string = pv_to_puml_string(test_data)
    with open(
        "puml_files/complicated_merge_with_same_event.puml",
        "r",
        encoding="utf-8",
    ) as file:
        expected_puml_string = file.read()
    assert check_puml_equivalence(puml_string, expected_puml_string)


def test_pv_streams_to_puml_files(
    pv_streams: Generator[
        tuple[str, Generator[Generator[PVEvent, Any, None], Any, None]],
        Any,
        None,
    ],
    tmp_path: Path,
) -> None:
    """Tests the function pv_streams_to_puml_files"""
    # Create temp directory for puml files
    temp_dir = os.path.join(str(tmp_path), "temp_dir")
    os.makedirs(temp_dir)
    pv_streams_to_puml_files(pv_streams, output_file_directory=temp_dir)
    # Check that the expected files are created in temp_dir
    expected_files = ["Job_A.puml", "Job_B.puml"]
    for expected_file in expected_files:
        file_path = os.path.join(temp_dir, expected_file)
        assert os.path.exists(file_path)

        expected_content = (
            "@startuml\n"
            '    partition "default_name" {\n'
            '        group "default_name"\n'
            "            :A;\n"
            "            :B;\n"
            "            :C;\n"
            "            :D;\n"
            "        end group\n"
            "    }\n"
            "@enduml"
        )
        with open(file_path, "r") as f:
            content = f.read()
            content = content.strip()
            expected_content = expected_content.strip()
            assert content == expected_content


@pytest.mark.parametrize("group_by_job_id", [True, False])
def test_pv_files_to_pv_streams(
    mock_job_json_file: list[dict[str, Any]],
    tmp_path: Path,
    group_by_job_id: bool,
) -> None:
    """Tests the function pv_files_to_pv_streams"""

    def verify_pv_events(
        pv_stream: Generator[
            tuple[str, Generator[list[PVEvent], Any, None]], Any, None
        ],
    ) -> None:
        """Helper function to verify pv events"""
        pv_events = []
        for job_name, pv_event_gen in pv_stream:
            assert job_name == "default.puml"
            for pv_event_list in pv_event_gen:
                pv_events.extend(pv_event_list)

        assert len(pv_events) == 3
        assert pv_events[0]["eventId"] == "evt_001"
        assert pv_events[0]["eventType"] == "START"
        assert pv_events[0]["jobId"] == "job_id_001"
        assert pv_events[0]["applicationName"] == "BackupService"
        assert pv_events[0]["jobName"] == "TempFilesCleanup"

        assert pv_events[1]["eventId"] == "evt_002"
        assert pv_events[1]["eventType"] == "A"
        assert pv_events[1]["jobId"] == "job_id_001"
        assert pv_events[1]["applicationName"] == "BackupService"
        assert pv_events[1]["jobName"] == "TempFilesCleanup"

        assert pv_events[2]["eventId"] == "evt_003"
        assert pv_events[2]["eventType"] == "END"
        assert pv_events[2]["jobId"] == "job_id_001"
        assert pv_events[2]["applicationName"] == "BackupService"
        assert pv_events[2]["jobName"] == "TempFilesCleanup"

    def create_json_file(
        input_dir: Path, file_name: str, data: list[dict[str, Any]]
    ) -> Path:
        """Helper function to create json file"""
        input_dir.mkdir(parents=True, exist_ok=True)
        data_file = input_dir / file_name
        data_file.write_text(json.dumps(data))
        return data_file

    # Test 1: Test with directory path
    input_dir = tmp_path / "job_json"
    create_json_file(input_dir, "file1.json", mock_job_json_file)

    pv_stream = pv_files_to_pv_streams(
        file_directory=str(input_dir), group_by_job_id=group_by_job_id
    )
    verify_pv_events(pv_stream)

    # Test 2: Test with file list
    input_dir = tmp_path / "job_json"
    data_file = create_json_file(input_dir, "file1.json", mock_job_json_file)

    pv_stream = pv_files_to_pv_streams(
        file_list=[str(data_file)], group_by_job_id=group_by_job_id
    )
    verify_pv_events(pv_stream)
