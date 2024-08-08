"""Module for handling saving processed OTel data"""

import yaml
from abc import ABC, abstractmethod
from typing import Any

from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    OTelEvent,
)


class DataHolder(ABC):
    """An abstract class to handle saving processed OTel data."""

    def __init__(self) -> None:
        self.yaml_config = self.get_yaml_config()
        self.valid_types = ["sql"]
        self.type = self.set_data_holder_type()

    def get_yaml_config(self) -> Any:
        """Returns the yaml config as a dictionary.

        :return: Config file represented as a dictionary,
        :rtype: `Any`
        """
        with open("tel2puml/find_unique_graphs/config.yaml", "r") as f:
            return yaml.load(f, Loader=yaml.SafeLoader)

    def set_data_holder_type(self) -> str:
        """Set the data holder type.

        :return: The data holder type.
        :rtype: `str`
        """
        holder_type: str = self.yaml_config["ingest_data"]["data_holder"]
        if holder_type not in self.valid_types:
            raise ValueError(
                f"""
                '{holder_type}' is not a valid data holder type.
                Please edit config.yaml and select from
                {self.valid_types}
                """
            )
        return holder_type

    @abstractmethod
    def save_data(self, otel_event: OTelEvent) -> None:
        """Method for batching and saving OTel data.

        :param otel_event: An OTelEvent object
        :type otel_event: :class: `OTelEvent`
        """
        pass
