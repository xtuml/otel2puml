from typing import Any


def create_span(file_no: int, i: int, j: int, no_spans: int) -> dict[str, Any]:
    return {
        "trace_id": f"{file_no}_trace_id_{i}",
        "span_id": f"{file_no}_span_{i}_{j}",
        "parent_span_id": f"{file_no}_span_{i}_{j-1}" if j > 0 else None,
        "child_span_ids": (
            [f"{file_no}_span_{i}_{j+1}"] if j < no_spans - 1 else []
        ),
        "name": "/update",
        "start_time_unix_nano": 1723544132228288000,
        "end_time_unix_nano": 1723544132229038947,
        "attributes": [
            {
                "key": "http.method",
                "value": {"Value": {"StringValue": f"method_{i}_{j}"}},
            },
            {
                "key": "http.target",
                "value": {"Value": {"StringValue": f"target_{i}_{j}"}},
            },
            {
                "key": "http.host",
                "value": {"Value": {"StringValue": f"host_{i}_{j}"}},
            },
            {
                "key": "coral.operation",
                "value": {"Value": {"StringValue": f"operation_{i}_{j}"}},
            },
            {
                "key": "coral.service",
                "value": {"Value": {"StringValue": f"service_{i}_{j}"}},
            },
            {
                "key": "coral.namespace",
                "value": {"Value": {"StringValue": f"namespace_{i}_{j}"}},
            },
            {"key": "http.status_code", "value": {"Value": {"IntValue": 200}}},
        ],
        "status": {},
        "resource": {
            "attributes": [
                {
                    "key": "service.name",
                    "value": {"Value": {"StringValue": f"name_{i}_{j}"}},
                },
                {
                    "key": "service.version",
                    "value": {"Value": {"StringValue": f"version_{i}_{j}"}},
                },
                {
                    "key": {"other_key": "test_string"},
                    "value": {"Value": {"StringValue": "4.8"}},
                },
            ]
        },
        "scope": {"name": f"{file_no}_name_{j}"},
    }


def create_header(
    service_name: str, service_version: str
) -> list[dict[str, Any]]:
    return [
        {
            "key": "service.name",
            "value": {"Value": {"StringValue": service_name}},
        },
        {
            "key": "service.version",
            "value": {"Value": {"StringValue": service_version}},
        },
    ]


def create_resource_span(
    header: list[dict[str, Any]], spans: list[dict[str, Any]]
) -> dict[str, Any]:
    return {
        "resource": {"attributes": header},
        "scope_spans": [
            {
                "scope": {"name": "TestJob"},
                "spans": spans,
            }
        ],
    }


def generate_resource_spans(
    file_no: int, no_resource_spans: int, no_spans: int
) -> list[dict[str, Any]]:
    headers = {
        "service_name": ["Frontend", "Backend", "Cloud", "Docker", "DB"],
        "service_version": ["1.0", "2.0", "3.0", "4.0", "5.0"],
    }
    resource_spans = {"resource_spans": []}

    for i in range(no_resource_spans):
        header = create_header(
            headers["service_name"][i], headers["service_version"][i]
        )
        spans = []
        for j in range(no_spans):
            span = create_span(file_no, i, j, no_spans)
            spans.append(span)
        resource_spans["resource_spans"].append(
            create_resource_span(header, spans)
        )

    return resource_spans
