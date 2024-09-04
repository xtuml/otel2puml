"""Module to sequence OTel data from grouped OTelEvents"""

from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    OTelEvent,
)


def order_groups_by_start_timestamp(
    groups: list[list[OTelEvent]],
) -> list[list[OTelEvent]]:
    """Order groups by start timestamp.

    :param groups: A list of groups of OTelEvents.
    :type groups: `list`[`list`[`OTelEvent`]]
    :return: A list of groups of OTelEvents ordered by start timestamp.
    :rtype: `list`[`list`[`OTelEvent`]]
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
