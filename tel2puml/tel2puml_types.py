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
