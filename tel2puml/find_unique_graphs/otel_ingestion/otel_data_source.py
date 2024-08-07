"""Module containing classes to handle different OTel data sources."""

import yaml
import os
from abc import ABC, abstractmethod
from typing import Self, Any, Dict

from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    OTelEvent,
)


class OTELDataSource(ABC):
    """Abstract class for returning a OTelEvent object from a data source."""

    def __init__(self) -> None:
        """Constructor method."""
        self.yaml_config = self.get_yaml_config()
        self.valid_file_exts = ["json"]
        self.file_ext = self.set_file_ext()
        self.dirpath = self.set_dirpath()
        self.filepath = self.set_filepath()
        if not self.dirpath and not self.filepath:
            raise FileNotFoundError(
                """No directory or files found. Please check yaml config."""
            )

    def get_yaml_config(self) -> Dict[str, Any]:
        """Returns the yaml config as a dictionary.

        :return: Config file represented as a dictionary,
        :rtype: `Dict`[`str`,`Any`]
        """
        with open("tel2puml/find_unique_graphs/config.yaml", "r") as f:
            return yaml.load(f, Loader=yaml.SafeLoader)

    def set_file_ext(self) -> str:
        """Set the file ext.

        :return: The file extension used.
        :rtype: `str`
        """
        file_ext = self.yaml_config["ingest_data"]["data_source"]
        if file_ext not in self.valid_file_exts:
            raise ValueError(
                f"""
                '{file_ext}' is not a valid file ext.
                Please edit config.yaml and select from {self.valid_file_exts}
                """
            )
        return file_ext

    def set_dirpath(self) -> str | None:
        """Set the directory path.

        :return: The directory path
        :rtype: `str`
        """
        file_ext = self.yaml_config["ingest_data"]["data_source"]
        dirpath = self.yaml_config["data_sources"][f"{file_ext}"]["dirpath"]

        if not dirpath:
            return None
        elif not os.path.isdir(dirpath):
            raise ValueError(f"{dirpath} directory does not exist.")
        return dirpath

    def set_filepath(self) -> str | None:
        """Set the filepath.

        :return: The filepath
        :rtype: `str`
        """
        file_ext = self.yaml_config["ingest_data"]["data_source"]
        filepath = self.yaml_config["data_sources"][f"{file_ext}"]["filepath"]

        if not filepath:
            return None
        elif not filepath.endswith(f".{file_ext}"):
            raise ValueError(f"File provided is not .{file_ext} format.")
        elif not os.path.isfile(filepath):
            raise ValueError(f"{filepath} does not exist.")
        return filepath

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


class JSONDataSource(OTELDataSource):
    """Class to handle parsing JSON OTel data, returning OTelEvent ojects"""

    def __next__(self) -> OTelEvent:
        """Returns the next item in the sequence.

        :return: The next OTelEvent in the sequence
        :rtype: :class: `OTelEvent`
        """
        pass
