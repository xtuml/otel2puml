"""Test cases for pv_to_tel module"""
from typing import Any, Generator
import os
import json
import pytest
from datetime import datetime, timezone

from tel2puml.tel2puml_types import OtelSpan, PVEvent
from tel2puml.pv_to_tel import (
    pv_event_to_otel,
    convert_timestamp_to_unix_nano,
    puml_to_otel_file,
)


def test_pv_event_to_otel(
    sample_pv_events: list[PVEvent], expected_otel_span_events: list[OtelSpan]
) -> None:
    """Test pv_event_to_otel"""
    for index, pv_event in enumerate(sample_pv_events):
        assert pv_event_to_otel(pv_event) == expected_otel_span_events[index]


def test_convert_timestamp_to_unix_nano() -> None:
    """Test convert_timestamp_to_unix_nano"""
    iso_timestamp: str = "2024-01-01T00:00:00Z"
    expected_unix_nano: int = int(
        datetime(2024, 1, 1, tzinfo=timezone.utc).timestamp() * 1e9
    )
    assert convert_timestamp_to_unix_nano(iso_timestamp) == expected_unix_nano


def test_puml_to_otel_file(
    monkeypatch: pytest.MonkeyPatch,
    sample_pv_events: list[PVEvent],
    expected_otel_json_output_sample_test_1: dict[str, list[dict[str, Any]]],
) -> None:
    """Test puml_to_otel_file"""

    def mock_generate_test_data_event_sequences_from_puml(
        input_puml_file: str
    ) -> Generator[list[PVEvent], Any, None]:
        """Mock generate_test_data_event_sequences_from_puml"""
        yield [sample_pv_events[0]]

    monkeypatch.setattr(
        "tel2puml.pv_to_tel.generate_test_data_event_sequences_from_puml",
        mock_generate_test_data_event_sequences_from_puml,
    )

    puml_file_path: str = "test.puml"
    otel_output_folder_path: str = "tests/pv_to_tel/otel_output"
    job_name: str = "TestJob"
    application_name: str = "TestApp"
    file_name_prefix: str = "test_prefix"

    if not os.path.exists(otel_output_folder_path):
        os.mkdir(otel_output_folder_path)

    puml_to_otel_file(
        puml_file_path=puml_file_path,
        otel_output_folder_path=otel_output_folder_path,
        job_name=job_name,
        application_name=application_name,
        file_name_prefix=file_name_prefix,
    )

    assert os.path.exists(
        f"{otel_output_folder_path}/{file_name_prefix}_1.json"
    )

    with open(
        f"{otel_output_folder_path}/{file_name_prefix}_1.json", "r"
    ) as file:
        data = json.load(file)
        assert data == expected_otel_json_output_sample_test_1

    os.remove(f"{otel_output_folder_path}/{file_name_prefix}_1.json")
    os.removedirs(otel_output_folder_path)

    assert not os.path.exists(otel_output_folder_path)
