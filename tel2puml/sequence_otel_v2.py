"""Module to sequence OTel data from grouped OTelEvents"""

from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    OTelEvent,
)


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
        group_id: []
        for group_id in async_event_types.values()
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
    :param previous_event_ids: A list of previous event IDs.
    :type previous_event_ids: `list`[`str`] | `None`
    :param async_flag: A flag indicating whether to use async information.
    :type async_flag: `bool`
    :param event_to_async_group_map: A dictionary mapping event types to
    groups of events that occur asynchronously.
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
    child_events = [
        event_id_to_event_map[event_id]
        for event_id in event.child_event_ids
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
