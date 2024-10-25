"""TypedDicts for tel2puml"""

from typing import TypedDict, NotRequired, Any, Optional, Type, Literal, Self
from enum import Enum

from pydantic import (
    BaseModel,
    Field,
    DirectoryPath,
    FilePath,
    field_validator,
    model_validator,
    StrictBool,
)

from tel2puml.otel_to_pv.config import IngestDataConfig


class PVEventMappingConfig(BaseModel):
    """Mapping configuration for PVEvent"""

    jobId: str = "jobId"
    eventId: str = "eventId"
    timestamp: str = "timestamp"
    previousEventIds: str = "previousEventIds"
    applicationName: str = "applicationName"
    jobName: str = "jobName"
    eventType: str = "eventType"


class PVEvent(TypedDict):
    """A PV event"""

    jobId: str
    eventId: str
    timestamp: str
    previousEventIds: NotRequired[list[str] | str]
    applicationName: str
    jobName: str
    eventType: str


class PVEventModel(BaseModel):
    """Pydantic model for PVEvent"""

    jobId: str
    eventId: str
    timestamp: str
    previousEventIds: Optional[list[str]] = Field([])
    applicationName: str
    jobName: str
    eventType: str

    @model_validator(mode="before")
    def check_prev_event_ids(
        cls: Type["PVEventModel"], values: dict[str, Any]
    ) -> dict[str, Any]:
        """Check if previousEventIds is a string and convert it to a list
        of strings."""
        previous_event_ids = values.get("previousEventIds")
        if previous_event_ids and isinstance(previous_event_ids, str):
            values["previousEventIds"] = [previous_event_ids]
        return values


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
    save_events: bool
    find_unique_graphs: bool
    mapping_config: NotRequired[Optional[PVEventMappingConfig]]


class PVPumlOptions(TypedDict):
    """Typed dict for options for pv_to_puml"""

    file_list: list[str]
    job_name: str
    group_by_job_id: bool
    mapping_config: NotRequired[PVEventMappingConfig]


class OtelToPVArgs(BaseModel):
    """Pydantic model for shared CLI arguments for otel2puml and oteltopv."""

    config_file: FilePath = Field(
        ..., description="Path to configuration file"
    )
    ingest_data: StrictBool = Field(
        default=True,
        description="Flag to indicate whether to load data into the data"
        " holder",
    )
    find_unique_graphs: StrictBool = Field(
        default=False,
        description="Flag to indicate whether to find unique graphs within"
        " the data holder",
    )
    command: Literal["otel2puml", "otel2pv"] = Field(
        ..., description="Command used within CLI"
    )

    save_events: StrictBool = Field(
        default=False,
        description="Flag indicating whether to save events to the output"
        " directory",
    )
    mapping_config_file: FilePath | None = Field(
        default=None, description="Path to mapping configuration file"
    )

    @field_validator("config_file")
    @classmethod
    def check_file_extension(
        cls: Type["OtelToPVArgs"], file_path: FilePath
    ) -> FilePath:
        """Check that file_path ends with .yaml"""
        if file_path and not str(file_path).endswith(".yaml"):
            raise ValueError(f"File path {file_path} does not end with .yaml")
        return file_path

    @model_validator(mode="after")
    def check_save_events(self) -> Self:
        """Check that save events is not True when otel2puml is selected."""
        if self.command == "otel2puml" and self.save_events:
            raise ValueError(
                "save_events must be False if otel2puml is selected."
            )
        return self

    @model_validator(mode="after")
    def check_mapping_config(self) -> Self:
        """Check that mapping_config_file is not set when otel2puml is
        selected."""
        if self.command == "otel2puml" and self.mapping_config_file:
            raise ValueError(
                "mapping_config_file must not be set if otel2puml is selected."
            )
        return self


class PvToPumlArgs(BaseModel):
    """Pydantic model for PvToPuml CLI arguments."""

    folder_path: Optional[DirectoryPath] = Field(
        None, description="Path to folder containing job json files"
    )
    file_paths: Optional[list[FilePath]] = Field(
        None, description="Input files containing job data in json format"
    )
    job_name: str = Field(
        default="default_name",
        description="Name given to the puml sequence diagram and prefix for "
        "the output puml file",
    )
    group_by_job: StrictBool = Field(
        default=False, description="Group events by job ID"
    )
    mapping_config_file: FilePath | None = Field(
        default=None, description="Path to mapping configuration file"
    )

    @model_validator(mode="after")
    def check_folder_path_file_paths(self) -> Self:
        """Check that folder path and file paths haven't both been set."""
        folder_path = self.folder_path
        file_paths = self.file_paths

        if folder_path and file_paths:
            raise ValueError(
                "Only folder path or file paths is required, not both."
            )
        if not folder_path and not file_paths:
            raise ValueError("Either folder path or file paths is required.")
        return self
