"""This module contains the named tuple for OTel event."""
from typing import NamedTuple, Optional


class OTelEvent(NamedTuple):
    """Named tuple for OTel event.

    :param job_name: The name of the job.
    :type job_name: `str`
    :param job_id: The ID of the job.
    :type job_id: `str`
    :param event_type: The type of the event.
    :type event_type: `str`
    :param event_id: The ID of the event.
    :type event_id: `str`
    :param start_timestamp: The start timestamp of the event in unix nano.
    :type start_timestamp: `int`
    :param end_timestamp: The end timestamp of the event in unix nano.
    :type end_timestamp: :class: `int`
    :param application_name: The application name.
    :type application_name: `str`
    :param parent_event_id: The ID of the parent event.
    :type parent_event_id: `Optional`[`str`]
    :param child_event_ids: A list of IDs of child events. Defaults to `None`
    :type child_event_ids: Optional[`list`[`str`]]
    """

    job_name: str
    job_id: str
    event_type: str
    event_id: str
    start_timestamp: int
    end_timestamp: int
    application_name: str
    parent_event_id: Optional[str]
    child_event_ids: Optional[list[str]] = None
