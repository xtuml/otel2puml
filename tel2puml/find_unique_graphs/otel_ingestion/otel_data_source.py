"""Module containing classes to handle different OTel data sources."""

import yaml
import os
import ijson
from abc import ABC, abstractmethod
from typing import Self, Any, Iterator

from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    OTelEvent,
)


class OTELDataSource(ABC):
    """Abstract class for returning a OTelEvent object from a data source."""

    def __init__(self) -> None:
        """Constructor method."""
        self.yaml_config = self.get_yaml_config()
        self.valid_data_sources = ["json"]
        self.data_source = self.set_data_source()

    def get_yaml_config(self) -> Any:
        """Returns the yaml config as a dictionary.

        :return: Config file represented as a dictionary,
        :rtype: `Any`
        """
        with open("tel2puml/find_unique_graphs/config.yaml", "r") as f:
            return yaml.load(f, Loader=yaml.SafeLoader)

    def set_data_source(self) -> str:
        """Set the data source.

        :return: The type of file used.
        :rtype: `str`
        """
        data_source: str = self.yaml_config["ingest_data"]["data_source"]
        if data_source not in self.valid_data_sources:
            raise ValueError(
                f"""
                '{data_source}' is not a valid data source.
                Please edit config.yaml and select from
                {self.valid_data_sources}
                """
            )
        return data_source

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
    """Class to handle parsing JSON OTel data from a file or directory,
    returning OTelEvent objects.
    """

    def __init__(self) -> None:
        """Constructor method."""
        super().__init__()
        self.current_file_index = 0
        self.current_parser: Iterator[OTelEvent] | None = None
        self.dirpath = self.set_dirpath()
        self.filepath = self.set_filepath()
        if not self.dirpath and not self.filepath:
            raise FileNotFoundError(
                """No directory or files found. Please check yaml config."""
            )
        self.file_list = self.get_file_list()

    def set_dirpath(self) -> str | None:
        """Set the directory path.

        :return: The directory path
        :rtype: `str` | `None`
        """
        dirpath: str = self.yaml_config["data_sources"][f"{self.data_source}"][
            "dirpath"
        ]

        if not dirpath:
            return None
        elif not os.path.isdir(dirpath):
            raise ValueError(f"{dirpath} directory does not exist.")
        return dirpath

    def set_filepath(self) -> str | None:
        """Set the filepath.

        :return: The filepath
        :rtype: `str` | `None`
        """
        filepath: str = self.yaml_config["data_sources"][
            f"{self.data_source}"
        ]["filepath"]

        if not filepath:
            return None
        elif not filepath.endswith(f".{self.data_source}"):
            raise ValueError(
                f"File provided is not .{self.data_source} format."
            )
        elif not os.path.isfile(filepath):
            raise ValueError(f"{filepath} does not exist.")
        return filepath

    def get_file_list(self) -> list[str]:
        """Get a list of filepaths to process.

        :return: A list of filepaths.
        :rtype: `list`[`str`]
        """
        if self.dirpath:
            return [
                os.path.join(self.dirpath, f)
                for f in os.listdir(self.dirpath)
                if f.endswith(f".{self.data_source}")
            ]
        elif self.filepath:
            return [self.filepath]
        raise ValueError("Directory/Filepath not set.")

    def parse_json_stream(self, filepath: str) -> Iterator[OTelEvent]:
        """Parse JSON file. ijson iteratively parses the json file.

        :return: An OTelEvent object
        :rtype: `Iterator`[`OTelEvent`]
        """
        with open(filepath, "rb") as file:
            for record in ijson.items(file, "item"):
                yield self.create_otel_object(record)

    def create_otel_object(self, record: dict[str, Any]) -> OTelEvent:
        """Creates an OTelEvent object from a JSON record.

        :return: OTelEvent object
        :rtype: :class:`OTelEvent`
        """
        return OTelEvent(
            job_name=record["job_name"],
            job_id=record["job_id"],
            event_type=record["event_type"],
            event_id=record["event_id"],
            start_timestamp=record["start_timestamp"],
            end_timestamp=record["end_timestamp"],
            application_name=record["application_name"],
            parent_event_id=record["parent_event_id"],
            child_event_ids=record.get("child_event_ids", None),
        )

    def __next__(self) -> OTelEvent:
        """Returns the next OTelEvent in the sequence.

        :return: An OTelEvent object.
        :rtype: :class: `OTelEvent`
        """
        while self.current_file_index < len(self.file_list):
            if self.current_parser is None:
                self.current_parser = self.parse_json_stream(
                    self.file_list[self.current_file_index]
                )
            try:
                return next(self.current_parser)
            except StopIteration:
                self.current_file_index += 1
                self.current_parser = None

        raise StopIteration
