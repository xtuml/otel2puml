"""Module containing classes to handle different OTel data sources."""

import os
import ijson
from abc import ABC, abstractmethod
from typing import Self, Any, Iterator

from tel2puml.otel_to_pv.otel_ingestion.otel_data_model import (
    OTelEvent,
    JSONDataSourceConfig,
)
from tel2puml.otel_to_pv.data_sources.json_data_source import json_data_converter


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

        :return: The next OTelEvent in the sequence, with the header
        :rtype: :class:`OTelEvent`
        """
        pass


class JSONDataSource(OTELDataSource):
    """Class to handle parsing JSON OTel data from a file or directory,
    returning OTelEvent objects.
    """

    def __init__(self, config: JSONDataSourceConfig) -> None:
        """Constructor method."""
        super().__init__()
        self.config = config
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
        dirpath: str = self.config["dirpath"]

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
        filepath: str = self.config["filepath"]

        if not filepath:
            return None
        elif not filepath.endswith(".json"):
            raise ValueError("File provided is not .json format.")
        elif not os.path.isfile(filepath):
            raise ValueError(f"{filepath} does not exist.")
        return filepath

    def get_file_list(self) -> list[str]:
        """Get a list of filepaths to process.

        :return: A list of filepaths.
        :rtype: `list`[`str`]
        """
        if self.dirpath:
            # Recursively search through directories for .json files
            return [
                os.path.join(root, filename)
                for root, _, filenames in os.walk(self.config["dirpath"])
                for filename in filenames
                if filename.endswith(".json")
            ]
        elif self.filepath:
            return [self.filepath]
        raise ValueError("Directory/Filepath not set.")

    def process_record(self, record: dict[str, Any]) -> Iterator[OTelEvent]:
        """Process a single record and yield OTelEvent objects.

        :param record: The record to process
        :type record: `dict`[`str`,`Any`]
        :return: An iterator of tuples containing OTelEvent and header
        :rtype: `Iterator`[:class: `OTelEvent`]
        """
        header_dict: dict[str, Any] = json_data_converter.process_header(
            self.config, record
        )
        spans = json_data_converter.process_spans(self.config, record)
        for span in spans:
            if isinstance(span, dict):
                processed_json = json_data_converter.flatten_and_map_data(
                    self.config, span, header_dict
                )
                yield (self.create_otel_object(processed_json))
            else:
                raise TypeError("json is not of type dict.")

    def parse_json_stream(self, filepath: str) -> Iterator[OTelEvent]:
        """Function that parses a json file, maps the json to the application
        structure through the config specified in the config.yaml file.
        ijson iteratively parses the json file so that large files can be
        processed.

        :param filepath: The path to the JSON file to parse
        :return: An iterator of tuples containing OTelEvent and header
        :rtype: `Iterator`[:class:`OTelEvent`]
        """
        with open(filepath, "rb") as file:
            data = ijson.items(file, self.config["data_location"])
            for records in data:
                if isinstance(records, dict):
                    yield from self.process_record(records)
                elif isinstance(records, list):
                    for record_data in records:
                        yield from self.process_record(record_data)

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
            parent_event_id=record.get("parent_event_id", None),
            child_event_ids=record.get("child_event_ids", None),
        )

    def __next__(self) -> OTelEvent:
        """Returns the next OTelEvent in the sequence

        :return: An OTelEvent object.
        :rtype: :class:`OTelEvent`
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