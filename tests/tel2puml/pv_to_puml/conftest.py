"""Fixtures for testing pv_to_puml module"""

from typing import Generator, Any
from datetime import datetime, timedelta

import pytest

from tel2puml.tel2puml_types import PVEvent


def event_generator(
    job_name: str,
    job_id: str,
    base_timestamp: datetime,
    event_types: list[str],
) -> Generator[PVEvent, Any, None]:
    """Function to stream PVEvents."""
    current_timestamp = base_timestamp
    prev_event_id = None
    for i in range(4):
        event_id = f"event_{i}_{job_id}"
        previousEventId: str | None = prev_event_id
        yield PVEvent(
            jobName=job_name,
            jobId=job_id,
            eventId=event_id,
            eventType=event_types[i % len(event_types)],
            applicationName="app-name",
            timestamp=current_timestamp.isoformat(),
            previousEventIds=previousEventId if previousEventId else [],
        )
        prev_event_id = event_id
        current_timestamp += timedelta(minutes=5)


def job_id_generator(
    job_name: str, event_types: list[str]
) -> Generator[Generator[PVEvent, Any, None], Any, None]:
    """Function to stream groups of PVEvents, grouped by job_id."""
    job_ids = [
        f"job_1_{job_name}",
        f"job_2_{job_name}",
    ]
    base_timestamp = datetime.now()
    for job_id in job_ids:
        yield event_generator(job_name, job_id, base_timestamp, event_types)
        base_timestamp += timedelta(minutes=10)


@pytest.fixture
def pv_streams() -> Generator[
    tuple[str, Generator[Generator[PVEvent, Any, None], Any, None]],
    None,
    None,
]:
    """Fixture to return a generator that streams 2 jobs, each with
    2 job ids consisting of 4 PVEvents."""
    event_types = ["A", "B", "C", "D"]
    job_names = ["Job_A", "Job_B"]

    def generator() -> Generator[
        tuple[str, Generator[Generator[PVEvent, Any, None], Any, None]],
        None,
        None,
    ]:
        """Creates a generator of tuples of job names to a generator of
        generators of PVEvents grouped by job name then job id."""
        for job_name in job_names:
            yield (job_name, job_id_generator(job_name, event_types))

    return generator()


@pytest.fixture
def mock_job_json_file() -> list[dict[str, Any]]:
    """Fixture to mock job json file."""
    return [
        {
            "eventId": "evt_001",
            "eventType": "START",
            "jobId": "job_id_001",
            "timestamp": "2024-09-01T07:45:00Z",
            "applicationName": "BackupService",
            "jobName": "TempFilesCleanup",
            "previousEventIds": [],
        },
        {
            "eventId": "evt_002",
            "eventType": "A",
            "jobId": "job_id_001",
            "timestamp": "2024-09-01T08:15:00Z",
            "applicationName": "BackupService",
            "jobName": "TempFilesCleanup",
            "previousEventIds": ["evt_001"],
        },
        {
            "eventId": "evt_003",
            "eventType": "END",
            "jobId": "job_id_001",
            "timestamp": "2024-09-02T09:00:00Z",
            "applicationName": "BackupService",
            "jobName": "TempFilesCleanup",
            "previousEventIds": ["evt_002"],
        },
    ]
