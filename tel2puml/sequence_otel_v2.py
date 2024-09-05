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


def sequence_events_by_async_event_types(
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
        async_event_type: []
        for async_event_type in async_event_types.values()
    }
    non_async_groups: list[list[OTelEvent]] = []
    for event in events:
        if event.event_type in async_event_types:
            async_groups[async_event_types[event.event_type]].append(event)
        else:
            non_async_groups.append([event])
    groups = list(async_groups.values()) + non_async_groups
    return order_groups_by_start_timestamp(groups)
