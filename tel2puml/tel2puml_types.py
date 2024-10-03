"""TypedDicts for tel2puml"""

from typing import TypedDict, NotRequired, Any, Optional, Type
from enum import Enum

from pydantic import BaseModel, Field, DirectoryPath, FilePath, field_validator

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


class OtelPVOptions(TypedDict):
    """Typed dict for options for otel_to_pv"""

    config: IngestDataConfig
    ingest_data: bool


class PVPumlOptions(TypedDict):
    """Typed dict for options for pv_to_puml"""

    file_list: list[str]
    job_name: str
    group_by_job_id: bool


class OtelArgs(BaseModel):
    """Pydantic model for shared CLI arguments for otel2puml and oteltopv."""

    config_file: FilePath = Field(
        ..., description="Path to configuration file"
    )
    ingest_data: bool = Field(
        default=True,
        description="Flag to indicate whether to load data into the data"
        " holder",
    )
    find_unique_graphs: bool = Field(
        default=False,
        description="Flag to indicate whether to find unique graphs within"
        " the data holder",
    )


class OtelToPumlArgs(OtelArgs):
    """Pydantic model for OtelToPuml CLI arguments."""

    pass


class OtelToPvArgs(OtelArgs):
    """Pydantic model for OtelToPv CLI arguments."""

    save_events: bool = Field(
        default=False,
        description="Flag indicating whether to save events to the output directory",
    )


class PvToPumlArgs(BaseModel):
    """Pydantic model for PvToPuml CLI arguments."""

    folder_path: Optional[DirectoryPath] = Field(
        None, description="Path to folder containing job json files"
    )
    file_paths: Optional[list[FilePath]] = Field(
        None, description="Input .json files containing job data"
    )
    job_name: str = Field(
        default="default_name",
        description="Name given to the puml sequence diagram and prefix for the output puml file",
    )
    group_by_job: bool = Field(
        default=False, description="Group events by job ID"
    )

    @field_validator("file_paths")
    def check_file_extension(
        cls: Type["PvToPumlArgs"], file_path: FilePath
    ) -> FilePath:
        """Check that file_path ends with .json"""
        if file_path and not str(file_path).endswith(".json"):
            raise ValueError(f"File path {file_path} does not end with .json")
        return file_path
