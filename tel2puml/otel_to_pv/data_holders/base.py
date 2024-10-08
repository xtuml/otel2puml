"""Module containing base abstract class for DataHolders, providing required
interfaces."""

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self, Optional, Any, Generator
import logging


from tel2puml.otel_to_pv.otel_to_pv_types import OTelEvent


LOGGER = logging.getLogger(__name__)


class DataHolder(ABC):
    """An abstract class to handle saving processed OTel data."""

    def __init__(self) -> None:
        """Constructor method."""

        self.min_timestamp: int = 999999999999999999999999999999999999999
        self.max_timestamp: int = 0

    def save_data(self, otel_event: OTelEvent) -> None:
        """Method to save an OTelEvent, and keep track of the min and max
        timestamps.

        :param otel_event: An OTelEvent object
        :type otel_event: :class: `OTelEvent`
        """
        self.min_timestamp = min(
            self.min_timestamp, otel_event.start_timestamp
        )
        self.max_timestamp = max(self.max_timestamp, otel_event.end_timestamp)
        self._save_data(otel_event)

    def __enter__(self) -> Self:
        """Method for configuring the setup tasks within the context manager.

        :return: The object itself
        :rtype: :class:`Self`
        """

        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Method for configuring the tear down tasks within the context
        manager.

        :param exc_type: The exception type
        :type exc_type: `Optional`[`type`[:class:`BaseException`]]
        :param exc_val: The exception value
        :type exc_val: `Optional`[:class:`BaseException`]
        :param exc_tb: The exception traceback
        :type exc_tb: `Optional`[:class:`TracebackType`]
        """

        if exc_type:
            raise

    @abstractmethod
    def _save_data(self, otel_event: OTelEvent) -> None:
        """Abstract method for batching and saving OTel data.

        :param otel_event: An OTelEvent object
        :type otel_event: :class: `OTelEvent`
        """
        pass

    @abstractmethod
    def get_otel_events_from_job_ids(
        self, job_ids: set[str]
    ) -> Generator[dict[str, OTelEvent], Any, None]:
        """Abstract method to get OTelEvents from job_ids.

        :param job_ids: A set of job_ids
        :type job_ids: `set`[`str`]
        :return: A generator of dictionaries mapping event ids to OTelEvent
        objects
        :rtype: :class:`Generator`[`dict`[`str`, :class:`OTelEvent`], `Any`,
        `None`]
        """

    @abstractmethod
    def find_unique_graphs(self) -> dict[str, set[str]]:
        """Abstract method to find unique graphs from OTel data in the data
        holder. Returns a dictionary mapping job names to a set of unique
        job_ids.

        :return: A dictionary mapping job names to a set of unique job_ids
        :rtype: `dict`[`str`, `set`[`str`]]
        """
        pass

    @abstractmethod
    def stream_data(
        self,
        job_name_to_job_ids_map: dict[str, set[str]] | None = None,
        filter_job_names: set[str] | None = None,
    ) -> Generator[
        tuple[str, Generator[Generator[OTelEvent, None, None], None, None]],
        None,
        None,
    ]:
        """
        Abstract methods to stream data from the data holder.

        :param job_name_to_job_ids_map: Optional mapping of job names to job
        IDs to filter.
        :type job_name_to_job_ids_map: `dict`[`str`, `set`[`str`]] | `None`
        :param filter_job_names: Optional set of job names to filter.
        :type filter_job_names: `set`[`str`] | `None`
        :return: Generator yielding tuples of (job_name, generator of
        generators of OtelEvents grouped by job_id).
        :rtype: `Generator`[`tuple`[`str`, `Generator`[`Generator`
        [:class:`OTelEvent`, `None`, `None`]], `None`, `None`],`None`,
        `None`]
        """
        pass

    @abstractmethod
    def update_job_names_by_root_span(self) -> None:
        """Abstract method to update job names for job ids using the job name
        of the root span.
        """

    @abstractmethod
    def remove_inconsistent_jobs(self) -> None:
        """Abstract method to remove spans associated with job ids that contain
        disconnected spans.
        """
        pass

    @abstractmethod
    def remove_jobs_outside_of_time_window(
        self
    ) -> None:
        """Abstract method to remove jobs outside of the time window.
        """
        pass


def get_time_window(
    time_buffer: int, data_holder: DataHolder
) -> tuple[int, int]:
    """Get the time window for the unique graphs.

    :param time_buffer: The time buffer to add to the time window in minutes
    :type time_buffer: `int`
    :param data_holder: The data holder object containing the ingested data
    :type data_holder: :class:`DataHolder`
    :return: The time window for the unique graphs
    :rtype: `tuple`[`int`, `int`]
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
