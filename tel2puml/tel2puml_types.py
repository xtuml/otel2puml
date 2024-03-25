"""TypedDicts for tel2puml"""
from typing import TypedDict, NotRequired
from enum import Enum


class PVEvent(TypedDict):
    """A PV event"""
    jobId: str
    eventId: str
    timestamp: str
    previousEventIds: NotRequired[list[str]]
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
    NORMAL = "NORMAL"
    BRANCH = "BRANCH"
    MERGE = "MERGE"
    BREAK = "BREAK"
    LOOP = "LOOP"


class PUMLOperatorNodes(Enum):
    START_XOR = ("START", "XOR")
    PATH_XOR = ("PATH", "XOR")
    END_XOR = ("END", "XOR")
    START_AND = ("START", "AND")
    PATH_AND = ("PATH", "AND")
    END_AND = ("END", "AND")
    START_OR = ("START", "OR")
    PATH_OR = ("PATH", "OR")
    END_OR = ("END", "OR")
    LOOP = ("START", "LOOP")
    END_LOOP = ("END", "LOOP")


class PUMLOperator(Enum):
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
    LOOP = (PUMLOperatorNodes.LOOP, PUMLOperatorNodes.END_LOOP)


class PlantUMLEventAttributes(TypedDict):
    """Attributes for a PlantUML event"""
    is_branch: NotRequired[bool]
    is_break: NotRequired[bool]
    is_merge: NotRequired[bool]
