"""Module for finding unique graphs in a list of graphs from ingested
OpenTelemetry data."""

from tel2puml.find_unique_graphs.otel_ingestion.otel_data_holder import (
    DataHolder,
)


def get_time_window(time_buffer: int, data_holder: DataHolder) -> int:
    """Get the time window for the unique graphs.

    :param time_buffer: The time buffer to add to the time window in minutes
    :type time_buffer: `int`
    :param data_holder: The data holder object containing the ingested data
    :type data_holder: :class:`DataHolder`
    :return: The time window for the unique graphs
    :rtype: `int`
    :raises ValueError: If the time buffer is too large for the ingested data
    """
    time_buffer_in_nanoseconds = time_buffer * 60 * 1000000000
    buffer_min_timestamp = (
        data_holder.min_timestamp + time_buffer_in_nanoseconds
    )
    buffer_max_timestamp = (
        data_holder.max_timestamp - time_buffer_in_nanoseconds
    )
    if buffer_min_timestamp >= buffer_max_timestamp:
        raise ValueError(
            "The time buffer is too large for the ingested data. "
            "Please reduce the time buffer."
        )
    return (
        data_holder.min_timestamp + time_buffer_in_nanoseconds,
        data_holder.max_timestamp - time_buffer_in_nanoseconds,
    )
