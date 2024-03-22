"""TypedDicts for tel2puml"""
from typing import TypedDict, NotRequired


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
