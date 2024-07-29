"""Module to convert a stream of PV events to OTel"""

import os
import json
from datetime import datetime, timezone

from tel2puml.tel2puml_types import PVEvent, OtelSpan
from tel2puml.pipelines.data_creation import (
    generate_test_data_event_sequences_from_puml,
)


def convert_timestamp_to_unix_nano(iso_timestamp: str) -> int:
    """
    Function to turn a ISO 8601 timestamp to unix nano format

    :param timestamp: Timestamp in ISO 8601 format.
    :type timestamp: `str`
    :return Timestamp in unix nano format
    :rtype `int`
    """
    # Parse the ISO 8601 timestamp to a datetime object
    dt = datetime.fromisoformat(iso_timestamp.rstrip("Z")).replace(
        tzinfo=timezone.utc
    )
    # Convert the datetime object to a Unix timestamp in seconds
    unix_timestamp = dt.timestamp()
    # Convert the Unix timestamp to nanoseconds
    unix_nano = int(unix_timestamp * 1e9 + dt.microsecond * 1e3)
    return unix_nano


def pv_event_to_otel(event: PVEvent) -> OtelSpan:
    """
    Converts a pv event to otel

    param event: A singular pv event
    type event: :class:`PVEvent`
    return: A singular otel event
    rtype: :class:`OtelSpan`
    """
    span = OtelSpan(
        name=event["applicationName"],
        span_id=event["eventId"],
        trace_id=event["jobId"],
        start_time_unix_nano=convert_timestamp_to_unix_nano(
            event["timestamp"]
        ),
        end_time_unix_nano=convert_timestamp_to_unix_nano(
            event["timestamp"]
        ),
        attributes=(
            [
                {
                    "key": "coral.operation",
                    "value": {
                        "Value": {"StringValue": event["eventType"]}
                    },
                }
            ]
            if "eventType" in event
            else []
        ),
    )
    if "previousEventIds" in event:
        if isinstance(event["previousEventIds"], list):
            span["parent_span_id"] = event["previousEventIds"][0]
        else:
            span["parent_span_id"] = event["previousEventIds"]
    return span


def puml_to_otel_file(
    puml_file_path: str,
    otel_output_folder_path: str,
    job_name: str,
    application_name: str,
    file_name_prefix: str,
) -> None:
    """
    Converts a PUML file to a OtelSpan json file.

    :param puml_file_path: Path to the PUML file.
    :type puml_file_path: str
    :param otel_output_folder_path: Path to otel output folder
    :type otel_output_folder_path: str
    :param job_name: Job name
    :type job_name: str
    :param application_name: Application name
    :type application_name: str
    :param file_name_prefix: Filename prefix
    :type file_name_prefix: str
    """
    pv_events_generators = (
        generate_test_data_event_sequences_from_puml(
            input_puml_file=puml_file_path
        )
    )
    otel_spans: list[OtelSpan] = []
    max_otel_spans_per_file: int = 50
    otel_spans_processed: int = 0
    file_number: int = 1
    for pv_events in pv_events_generators:
        for pv_event in pv_events:
            otel_spans.append(pv_event_to_otel(pv_event))
            otel_spans_processed += 1
            if otel_spans_processed % max_otel_spans_per_file == 0:
                write_to_file(
                    otel_spans=otel_spans,
                    otel_output_folder_path=otel_output_folder_path,
                    job_name=job_name,
                    application_name=application_name,
                    file_name_prefix=file_name_prefix,
                    file_number=file_number,
                )
                otel_spans = []
                file_number += 1
    if otel_spans:
        write_to_file(
            otel_spans=otel_spans,
            otel_output_folder_path=otel_output_folder_path,
            job_name=job_name,
            application_name=application_name,
            file_name_prefix=file_name_prefix,
            file_number=file_number,
        )


def write_to_file(
    otel_spans: list[OtelSpan],
    otel_output_folder_path: str,
    job_name: str,
    application_name: str,
    file_name_prefix: str,
    file_number: int,
) -> None:
    """
    Write OtelSpans to a json file.

    :param otel_spans: List of OtelSpan objects
    :type otel_spans: list[:class:`OtelSpan`]
    :param otel_output_folder_path: Path to otel output folder
    :type otel_output_folder_path: str
    :param job_name: Job name
    :type job_name: str
    :param application_name: Application name
    :type application_name: str
    :param file_name_prefix: Filename prefix
    :type file_name_prefix: str
    """
    otel_json_output = {
        "resource_spans": [
            {
                "resource": {
                    "attributes": [
                        {
                            "key": "service.name",
                            "value": {
                                "Value": {"StringValue": application_name}
                            },
                        },
                        {
                            "key": "service.version",
                            "value": {"Value": {"StringValue": "1.0"}},
                        },
                    ]
                },
                "scope_spans": [
                    {"scope": {"name": job_name}, "spans": otel_spans}
                ],
            }
        ]
    }
    if not os.path.exists(otel_output_folder_path):
        os.mkdir(otel_output_folder_path)

    filepath: str = (
        f"{otel_output_folder_path}/{file_name_prefix}_{file_number}.json"
    )
    with open(filepath, "w") as file:
        file.write(json.dumps(otel_json_output))

    return


if __name__ == "__main__":
    puml_file_path = "puml_files/simple_sequence.puml"
    otel_output_folder_path = "data"
    job_name = "Test_job_name"
    application_name = "Test_application_name"
    file_name_prefix = "otel_simple_sequence"
    puml_to_otel_file(
        puml_file_path=puml_file_path,
        otel_output_folder_path=otel_output_folder_path,
        job_name=job_name,
        application_name=application_name,
        file_name_prefix=file_name_prefix,
    )
