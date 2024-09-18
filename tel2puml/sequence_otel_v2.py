"""Module to sequence OTel data from grouped OTelEvents"""

from typing import Any, Generator, Iterable
from tel2puml.otel_to_pv.otel_to_pv_types import OTelEvent
from tel2puml.tel2puml_types import PVEvent
from tel2puml.utils import unix_nano_to_pv_string


def order_groups_by_start_timestamp(
    groups: list[list[OTelEvent]],
) -> list[list[OTelEvent]]:
    """Order groups by start timestamp.

    :param groups: A list of groups of OTelEvents.
    :type groups: `list`[`list`[:class:`OTelEvent`]]
    :return: A list of groups of OTelEvents ordered by start timestamp.
    :rtype: `list`[`list`[:class:`OTelEvent`]]
    """
    try:
        return sorted(
            [
                sorted(group, key=lambda x: x.start_timestamp)
                for group in groups
            ],
            key=lambda x: x[0].start_timestamp,
        )
    except IndexError:
        raise ValueError(
            "Groups in the input list must contain at least one OTelEvent."
        )


def sequence_groups_of_otel_events_asynchronously(
    groups: list[list[OTelEvent]],
) -> list[list[OTelEvent]]:
    """Sequence groups of OTelEvents asynchronously.

    :param groups: A list of groups of OTelEvents.
    :type groups: `list`[`list`[:class:`OTelEvent`]]
    :return: A list of groups of OTelEvents sequenced asynchronously.
    :rtype: `list`[`list`[:class:`OTelEvent`]]
    """
    ordered_groups = order_groups_by_start_timestamp(groups)
    if not ordered_groups:
        return []
    ordered_groups_async: list[list[OTelEvent]] = [ordered_groups[0]]
    max_timestamp = ordered_groups[0][-1].end_timestamp
    for group in ordered_groups[1:]:
        previous_group_last_event = ordered_groups_async[-1][-1]
        group_first_event = group[0]
        group_last_event = group[-1]
        if (
            previous_group_last_event.end_timestamp
            < group_first_event.start_timestamp
        ):
            ordered_groups_async.append(group)
        else:
            ordered_groups_async[-1].extend(group)
        max_timestamp = max(max_timestamp, group_last_event.end_timestamp)
    return ordered_groups_async


def group_events_using_async_information(
    events: list[OTelEvent],
    async_event_types: dict[str, str],
) -> list[list[OTelEvent]]:
    """Sequence events by async event type groups.

    :param events: A list of OTelEvents.
    :type events: `list`[`OTelEvent`]
    :param async_event_types: A dictionary mapping event types to groups of
    events that occur asynchronously.
    :return: A list of groups of OTelEvents sequenced by async event types.
    :rtype: `list`[`list`[`OTelEvent`]]
    """
    if not events:
        return []
    async_groups: dict[str, list[OTelEvent]] = {
        group_id: [] for group_id in async_event_types.values()
    }
    non_async_groups: list[list[OTelEvent]] = []
    for event in events:
        if event.event_type in async_event_types:
            async_groups[async_event_types[event.event_type]].append(event)
        else:
            non_async_groups.append([event])
    groups = list(async_groups.values()) + non_async_groups
    return groups


def sequence_otel_event_ancestors(
    event: OTelEvent,
    event_id_to_event_map: dict[str, OTelEvent],
    previous_event_ids: list[str] | None = None,
    async_flag: bool = False,
    event_to_async_group_map: dict[str, dict[str, str]] | None = None,
) -> dict[str, list[str]]:
    """Sequence OTel event ancestors using async information, if available.

    :param event: An OTelEvent.
    :type event: :class:`OTelEvent`
    :param event_id_to_event_map: A dictionary mapping event IDs to OTelEvents.
    :type event_id_to_event_map: `dict`[`str`, :class:`OTelEvent`]
    :param previous_event_ids: A list of previous event IDs, defaults to None.
    :type previous_event_ids: `list`[`str`] | `None`
    :param async_flag: A flag indicating whether to sequence event groups
    asynchronously or not, defaults to False.
    :type async_flag: `bool`
    :param event_to_async_group_map: A dictionary mapping event types to
    groups of events that occur asynchronously, defaults to None.
    :type event_to_async_group_map: `dict`[`str`, `dict`[`str`, `str`]] |
    `None`
    :return: A dictionary mapping event IDs to previous event IDs.
    :rtype: `dict`[`str`, `list`[`str`]]
    """
    # setup empty data structures if not provided
    if previous_event_ids is None:
        previous_event_ids = []
    if event_to_async_group_map is None:
        event_to_async_group_map = {}
    # create an empty mapping of event IDs to previous event IDs
    event_id_to_previous_event_ids: dict[str, list[str]] = {}
    # get the async groups for the event type, if available
    if event.event_type in event_to_async_group_map:
        event_type_to_group_map = event_to_async_group_map[event.event_type]
    else:
        event_type_to_group_map = {}
    # get the child events for the event
    if not isinstance(event.child_event_ids, list):
        raise ValueError(
            "All events must have a list of child event ids even if this list "
            f"is empty. Event ID: {event.event_id}"
        )
    child_events = [
        event_id_to_event_map[event_id] for event_id in event.child_event_ids
    ]
    # group the child events using async information
    event_groups = group_events_using_async_information(
        child_events, event_type_to_group_map
    )
    if async_flag:
        event_groups = sequence_groups_of_otel_events_asynchronously(
            event_groups
        )
    else:
        event_groups = order_groups_by_start_timestamp(event_groups)
    # sequence the child event groups by recursively calling this function
    # and updating the mapping of event IDs to previous event IDs
    # the previous event ids for the following group are the events in the
    # previous group
    for group in event_groups:
        for group_event in group:
            event_id_to_previous_event_ids.update(
                sequence_otel_event_ancestors(
                    group_event,
                    event_id_to_event_map,
                    previous_event_ids,
                    async_flag,
                    event_to_async_group_map,
                )
            )
        previous_event_ids = [group_event.event_id for group_event in group]
    # the final group will be the previous event ids for the current event
    event_id_to_previous_event_ids[event.event_id] = previous_event_ids
    return event_id_to_previous_event_ids


def get_root_event_from_event_id_to_event_map(
    event_id_to_event_map: dict[str, OTelEvent],
) -> OTelEvent:
    """Get the root event from a dictionary of OTelEvents.

    :param event_id_to_event_map: A dictionary mapping event IDs to OTelEvents.
    :type event_id_to_event_map: `dict`[`str`, :class:`OTelEvent`]
    :return: The root event.
    :rtype: :class:`OTelEvent`
    """
    events_without_parents = [
        event
        for event in event_id_to_event_map.values()
        if event.parent_event_id is None
    ]
    if len(events_without_parents) != 1:
        raise ValueError(
            "There should only be exactly one event without a parent event to"
            "act as the root event."
        )
    return events_without_parents[0]


def sequence_otel_event_job(
    event_id_to_event_map: dict[str, OTelEvent],
    async_flag: bool = False,
    event_to_async_group_map: dict[str, dict[str, str]] | None = None,
) -> Generator[PVEvent, Any, None]:
    """Sequence OTel events in a job.

    :param event_id_to_event_map: A dictionary mapping event IDs to OTelEvents.
    :type event_id_to_event_map: `dict`[`str`, :class:`OTelEvent`]
    :param async_flag: A flag indicating whether to sequence event groups
    asynchronously or not, defaults to False.
    :type async_flag: `bool`
    :param event_to_async_group_map: A dictionary mapping event types to
    groups of events that occur asynchronously, defaults to None.
    :type event_to_async_group_map: `dict`[`str`, `dict`[`str`, `str`]] |
    `None`
    :return: A generator of PVEvents.
    :rtype: `Generator`[:class:`PVEvent`, `Any`, `None`]
    """
    if event_to_async_group_map is None:
        event_to_async_group_map = {}
    root_event = get_root_event_from_event_id_to_event_map(
        event_id_to_event_map
    )
    event_id_to_previous_event_ids = sequence_otel_event_ancestors(
        root_event,
        event_id_to_event_map,
        async_flag=async_flag,
        event_to_async_group_map=event_to_async_group_map,
    )
    for event_id, event in event_id_to_event_map.items():
        yield PVEvent(
            jobId=event.job_id,
            eventId=event_id,
            eventType=event.event_type,
            timestamp=unix_nano_to_pv_string(event.end_timestamp),
            previousEventIds=event_id_to_previous_event_ids[event_id],
            applicationName=event.application_name,
            jobName=event.job_name,
        )


def sequence_otel_jobs(
    jobs: Iterable[dict[str, OTelEvent]],
    async_flag: bool = False,
    event_to_async_group_map: dict[str, dict[str, str]] | None = None,
) -> Generator[Generator[PVEvent, Any, None], Any, None]:
    """Sequence OTel events in multiple jobs.

    :param jobs: An iterable of dictionaries mapping event IDs to
    OTelEvents.
    :type jobs: `Iterable`[`dict`[`str`, :class:`OTelEvent`]]
    :param async_flag: A flag indicating whether to sequence event groups
    asynchronously or not, defaults to False.
    :type async_flag: `bool`
    :param event_to_async_group_map: A dictionary mapping event types to
    groups of events that occur asynchronously, defaults to None.
    :type event_to_async_group_map: `dict`[`str`, `dict`[`str`, `str`]] |
    `None`
    :return: A generator of jobs (generators) of PVEvents.
    :rtype: `Generator`[`Generator`[:class:`PVEvent`, `Any`, `None`], `Any`,
    `None`]
    """
    for job in jobs:
        yield sequence_otel_event_job(
            job, async_flag, event_to_async_group_map
        )


def sequence_otel_job_id_streams(
    job_id_streams: Generator[Generator[OTelEvent, Any, None], Any, None],
    async_flag: bool = False,
    event_to_async_group_map: dict[str, dict[str, str]] | None = None,
) -> Generator[Generator[PVEvent, Any, None], Any, None]:
    """
    Sequence OTel events in multiple jobs.

    :param job_id_streams: A generator of generators, where each inner
    generator yields OTelEvent objects grouped by job ID.
    :type job_id_streams: `Generator`[`Generator`[:class:`OTelEvent`, `Any`,
    `None`], `Any`, `None`]
    :param async_flag: A flag indicating whether to sequence event groups
    asynchronously or not, defaults to False.
    :type async_flag: `bool`
    :param event_to_async_group_map: A dictionary mapping event types to
    groups of events that occur asynchronously, defaults to None.
    :type event_to_async_group_map: `dict`[`str`, `dict`[`str`, `str`]] |
    `None`
    :return: A generator of jobs (generators) of PVEvents.
    :rtype: `Generator`[`Generator`[:class:`PVEvent`, `Any`, `None`], `Any`,
    `None`]
    """
    yield from sequence_otel_jobs(
        job_ids_to_eventid_to_otelevent_map(job_id_streams),
        async_flag,
        event_to_async_group_map,
    )


def job_ids_to_eventid_to_otelevent_map(
    job_id_streams: Generator[Generator[OTelEvent, Any, None], Any, None],
) -> Generator[dict[str, OTelEvent], Any, None]:
    """
    Creates a mapping from event IDs to OTelEvent objects for each job.

    :param job_id_streams: A generator of generators, where each inner
    generator yields OTelEvent objects grouped by job ID.
    :type job_id_streams: `Generator`[`Generator`[:class:`OTelEvent`,
    `Any`, `None`], `Any`, `None`]
    :return: A generator of dictionaries mapping event IDs to OTelEvent
    objects for each job.
    :rtype: `Generator`[`dict`[`str`, :class:`OTelEvent`], `Any`, `None`]
    """
    for job_group in job_id_streams:
        yield {otel_event.event_id: otel_event for otel_event in job_group}
