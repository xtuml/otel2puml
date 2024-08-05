"""TypedDicts for graph solutions"""

from typing import TypedDict, NotRequired


class NodeData(TypedDict):
    """TypedDict for NodeData"""

    id: str
    labels: list[str]
    properties: dict[str, str]
    type: str


class NodeRelationshipData(TypedDict):
    """TypedDict for NodeRelationshipData"""

    id: str
    end: str
    start: str
    label: str
    properties: dict[str, str]
    type: str


class OtelData(TypedDict):
    """TypedDict for OtelData"""

    span_id: str
    trace_id: str
    event_type: str
    prev_span_id: NotRequired[str]
    job_name: str
