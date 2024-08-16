"""Module containing classes to save processed OTel data into a data holder."""

from abc import ABC, abstractmethod

from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    OTelEvent,
)


class DataHolder(ABC):
    """An abstract class to handle saving processed OTel data."""

    @abstractmethod
    def save_data(self, otel_event: OTelEvent) -> None:
        """Method for batching and saving OTel data.

        :param otel_event: An OTelEvent object
        :type otel_event: :class: `OTelEvent`
        """
        pass
