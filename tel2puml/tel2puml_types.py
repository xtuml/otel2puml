"""TypedDicts for tel2puml"""

from typing import TypedDict, NotRequired, Any, Optional
from enum import Enum

from tel2puml.otel_to_pv.config import IngestDataConfig


class PVEvent(TypedDict):
    """A PV event"""

    jobId: str
    eventId: str
    timestamp: str
    previousEventIds: NotRequired[list[str] | str]
    applicationName: str
    jobName: str
    eventType: str


class NestedEvent(TypedDict):
    """A nested event"""

    eventType: str
    previousEventIds: NotRequired[dict[str, "NestedEvent"]]


class NXNodeAttributes(TypedDict):
    """Attributes for a NetworkX node"""

    node_type: str
    extra_info: dict[str, str]


class NXEdgeAttributes(TypedDict):
    """Attributes for a NetworkX edge"""

    start_node_attr: NXNodeAttributes
    end_node_attr: NXNodeAttributes


class PUMLEvent(Enum):
    """PlantUML event types"""

    NORMAL = "NORMAL"
    BRANCH = "BRANCH"
    MERGE = "MERGE"
    BREAK = "BREAK"
    LOOP = "LOOP"


class PUMLOperatorNodes(Enum):
    """PlantUML operators and a tuple of their corresponding PUML nodes"""

    START_XOR = ("START", "XOR")
    PATH_XOR = ("PATH", "XOR")
    END_XOR = ("END", "XOR")
    START_AND = ("START", "AND")
    PATH_AND = ("PATH", "AND")
    END_AND = ("END", "AND")
    START_OR = ("START", "OR")
    PATH_OR = ("PATH", "OR")
    END_OR = ("END", "OR")
    START_LOOP = ("START", "LOOP")
    END_LOOP = ("END", "LOOP")


class PUMLOperator(Enum):
    """PlantUML operators with their corresponding PUML nodes"""

    XOR = (
        PUMLOperatorNodes.START_XOR,
        PUMLOperatorNodes.END_XOR,
        PUMLOperatorNodes.PATH_XOR,
    )
    AND = (
        PUMLOperatorNodes.START_AND,
        PUMLOperatorNodes.END_AND,
        PUMLOperatorNodes.PATH_AND,
    )
    OR = (
        PUMLOperatorNodes.START_OR,
        PUMLOperatorNodes.END_OR,
        PUMLOperatorNodes.PATH_OR,
    )
    LOOP = (PUMLOperatorNodes.START_LOOP, PUMLOperatorNodes.END_LOOP)


class PlantUMLEventAttributes(TypedDict):
    """Attributes for a PlantUML event"""

    is_branch: NotRequired[bool]
    is_break: NotRequired[bool]
    is_merge: NotRequired[bool]


DUMMY_START_EVENT = "|||START|||"

DUMMY_END_EVENT = "|||END|||"

DUMMY_EVENT = "|||DUMMY|||"


class OtelSpan(TypedDict):
    """TypedDict for OtelSpan"""

    name: str
    span_id: str
    parent_span_id: NotRequired[str]
    trace_id: str
    start_time_unix_nano: int
    end_time_unix_nano: int
    attributes: NotRequired[list[dict[str, Any]]]
    scope: NotRequired[dict[str, Any]]
    resource: NotRequired[list[dict[str, Any]]]
    events: NotRequired[Any]
    operation: NotRequired[str]
    status: NotRequired[dict[str, Any]]
    kind: NotRequired[int]


class OtelPumlOptions(TypedDict):
    """Typed dict for options for otel_to_puml"""

    config: IngestDataConfig
    ingest_data: bool


class PVPumlOptions(TypedDict):
    """Typed dict for options for pv_to_puml"""

    file_directory: Optional[str]
    file_list: Optional[list[str]]
    job_name: str
    group_by_job_id: bool
