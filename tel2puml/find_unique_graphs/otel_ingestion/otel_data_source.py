"""Module containing classes to handle different OTel data sources."""

import os
import yaml
import time
import ijson
from abc import ABC, abstractmethod
from typing import Self, Any, Iterator

from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    OTelEvent,
    JSONDataSourceConfig,
)
from tel2puml.find_unique_graphs.otel_ingestion import json_data_converter


class OTELDataSource(ABC):
    """Abstract class for returning a OTelEvent object from a data source."""

    def __init__(self) -> None:
        """Constructor method."""
        self.valid_data_sources = ["json"]

    def __iter__(self) -> Self:
        """Returns the iterator object.

        :return: The iterator object
        :rtype: `self`
        """
        return self

    @abstractmethod
    def __next__(self) -> tuple[OTelEvent, str]:
        """Returns the next item in the sequence.

        :return: The next OTelEvent in the sequence, with the header
        :rtype: `tuple`[:class:`OTelEvent`, `str`]
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
        self.current_parser: Iterator[tuple[OTelEvent, str]] | None = None
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

    def process_record(
        self, record: dict[str, Any]
    ) -> Iterator[tuple[OTelEvent, str]]:
        """Process a single record and yield OTelEvent objects with headers.

        :param record: The record to process
        :type record: `dict`[`str`,`Any`]
        :return: An iterator of tuples containing OTelEvent and header
        :rtype: Iterator[tuple[OTelEvent, Any]]
        """
        header = json_data_converter.process_header(self.config, record)
        spans = json_data_converter.process_spans(self.config, record)
        for span in spans:
            if isinstance(span, dict):
                processed_json = json_data_converter.flatten_and_map_data(
                    self.config, span
                )
                yield (
                    self.create_otel_object(processed_json),
                    header,
                )
            else:
                raise TypeError("json is not of type dict.")
        print("=" * 50)

    def parse_json_stream(
        self, filepath: str
    ) -> Iterator[tuple[OTelEvent, str]]:
        """Function that parses a json file, maps the json to the application
            structure through the config specified in the config.yaml file.
            ijson iteratively parses the json file so that large files can be
            processed.

        :param filepath: The path to the JSON file to parse
        :return: An iterator of tuples containing OTelEvent and header
        :rtype: `Iterator`[`tuple`[`OTelEvent`, `str`]]
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
            parent_event_id=record["parent_event_id"],
            child_event_ids=record.get("child_event_ids", None),
        )

    def __next__(self) -> tuple[OTelEvent, str]:
        """Returns the next OTelEvent in the sequence, with the header.

        :return: An OTelEvent object.
        :rtype: `tuple`[:class:`OTelEvent`, `str`]
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


if __name__ == "__main__":
    time_start = time.time()
    with open("tel2puml/find_unique_graphs/config.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    json_data_source = JSONDataSource(config["data_sources"]["json"])

    grouped_spans: dict[str, list[OTelEvent]] = dict()
    for data, header in json_data_source:
        grouped_spans.setdefault(header, [])
        grouped_spans[header].append(data)

    print(time.time() - time_start)
