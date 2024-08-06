"""Module containing classes to handle different OTel data sources."""

from abc import ABC, abstractmethod
from typing import Self

from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    OTelEvent,
)


class OTELDataSource(ABC):
    """Abstract class for returning a OTelEvent object from a data source."""

    def __iter__(self) -> Self:
        """Returns the iterator object.

        :return: The iterator object
        :rtype: `self`
        """
        return self

    @abstractmethod
    def __next__(self) -> OTelEvent:
        """Returns the next item in the sequence.

        :return: The next OTelEvent in the sequence
        :rtype: :class: `OTelEvent`
        """
        pass
