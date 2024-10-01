"""Module containing DataSource sub class responsible for JSON ingestion."""

import os
from typing import Iterator
import json

from tel2puml.otel_to_pv.otel_to_pv_types import OTelEvent
from ..base import OTELDataSource
from .json_jq_converter import (
    generate_records_from_compiled_jq,
    field_mapping_to_compiled_jq,
)
from .json_config import JSONDataSourceConfig


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
        self.compiled_jq = field_mapping_to_compiled_jq(
            self.config["field_mapping"]
        )

    def set_dirpath(self) -> str | None:
        """Set the directory path.

        :return: The directory path
        :rtype: `str` | `None`
        """

        if not self.config["dirpath"]:
            return None
        elif not os.path.isdir(self.config["dirpath"]):
            raise ValueError(
                f"{self.config['dirpath']} directory does not exist."
                )
        return self.config["dirpath"]

    def set_filepath(self) -> str | None:
        """Set the filepath.

        :return: The filepath
        :rtype: `str` | `None`
        """

        if not self.config["filepath"]:
            return None
        elif not self.config["filepath"].endswith(".json"):
            raise ValueError("File provided is not .json format.")
        elif not os.path.isfile(self.config["filepath"]):
            raise ValueError(f"{self.config['filepath']} does not exist.")
        return self.config["filepath"]

    def get_file_list(self) -> list[str]:
        """Get a list of filepaths to process.

        :return: A list of filepaths.
        :rtype: `list`[`str`]
        """
        if self.dirpath is not None:
            # Recursively search through directories for .json files
            return [
                os.path.join(root, filename)
                for root, _, filenames in os.walk(self.dirpath)
                for filename in filenames
                if filename.endswith(".json")
            ]
        elif self.filepath is not None:
            return [self.filepath]
        else:
            raise ValueError("Directory/Filepath not set.")

    def parse_json_stream(self, filepath: str) -> Iterator[OTelEvent]:
        """Function that parses a json file, maps the json to the application
        structure through the config specified in the config.yaml file.
        ijson iteratively parses the json file so that large files can be
        processed.

        :param filepath: The path to the JSON file to parse
        :return: An iterator of tuples containing OTelEvent and header
        :rtype: `Iterator`[:class:`OTelEvent`]
        """
        with open(filepath, "r", encoding="utf-8") as file:
            if self.config["json_per_line"]:
                jsons = (json.loads(line, strict=False) for line in file)
            else:
                jsons = (data for data in [json.load(file, strict=False)])
            for data in jsons:
                for record in generate_records_from_compiled_jq(
                    data, self.compiled_jq
                ):
                    yield OTelEvent(**record)

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
