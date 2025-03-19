"""Module containing DataSource sub class responsible for JSON ingestion."""

import os
from typing import Generator, Iterator, Any
import json
from logging import getLogger
from io import TextIOWrapper

from tqdm import tqdm
from pydantic import ValidationError

from tel2puml.otel_to_pv.otel_to_pv_types import OTelEvent
from ..base import OTELDataSource
from .json_jq_converter import (
    generate_records_from_compiled_jq,
    compile_jq_query,
    get_jq_query_from_config,
)
from .json_config import JSONDataSourceConfig

LOGGER = getLogger(__name__)


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
        self.jq_query = get_jq_query_from_config(self.config)
        self.compiled_jq = compile_jq_query(self.jq_query)
        self.file_pbar = tqdm(
            total=len(self.file_list),
            desc="Ingesting JSON files",
            unit="files",
            position=0,
        )
        self.events_pbar = tqdm(
            desc="Events processed correctly",
            unit="events",
            position=1,
        )
        self.event_error_pbar = tqdm(
            desc="Events with errors",
            unit="events",
            position=2,
        )

    def set_dirpath(self) -> str | None:
        """Set the directory path.

        :return: The directory path
        :rtype: `str` | `None`
        """

        if not self.config.dirpath:
            return None
        elif not os.path.isdir(self.config.dirpath):
            raise ValueError(
                f"{self.config.dirpath} directory does not exist."
            )
        return self.config.dirpath

    def set_filepath(self) -> str | None:
        """Set the filepath.

        :return: The filepath
        :rtype: `str` | `None`
        """

        if not self.config.filepath:
            return None
        elif not os.path.isfile(self.config.filepath):
            raise ValueError(f"{self.config.filepath} does not exist.")
        return self.config.filepath

    def get_file_list(self) -> list[str]:
        """Get a list of filepaths to process.

        :return: A list of filepaths.
        :rtype: `list`[`str`]
        """
        if self.dirpath is not None:
            # Recursively search through directories for files
            return [
                os.path.join(root, filename)
                for root, _, filenames in os.walk(self.dirpath)
                for filename in filenames
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
            jsons = get_jsons_from_file(
                file, filepath, self.config.json_per_line
            )
            for data in jsons:
                for record in generate_records_from_compiled_jq(
                    data, self.compiled_jq
                ):
                    try:
                        yield OTelEvent(**record)
                        self.events_pbar.update(1)
                    except ValidationError as e:
                        self.event_error_pbar.update(1)
                        LOGGER.warning(
                            f"Error coercing data in file: {filepath}\n"
                            f"Validation Error: {e}\n"
                            f"Record: {record}\n"
                            "Skipping record - if this is a persistent error, "
                            "please check the field mapping or jq query in the"
                            " input config.yaml."
                        )

    def __next__(self) -> OTelEvent:
        """Returns the next OTelEvent in the sequence

        :return: An OTelEvent object.
        :rtype: :class:`OTelEvent`
        """
        while self.current_file_index < len(self.file_list):
            if self.current_parser is None:
                self.file_pbar.update(1)
                self.current_parser = self.parse_json_stream(
                    self.file_list[self.current_file_index]
                )
            try:
                return next(self.current_parser)
            except StopIteration:
                self.current_file_index += 1
                self.current_parser = None
        self.file_pbar.close()
        self.events_pbar.close()
        self.event_error_pbar.close()
        raise StopIteration


def get_jsons_from_file(
    file_io: TextIOWrapper, filepath: str, json_per_line: bool = False
) -> Generator[Any, Any, None]:
    """Generator function to yield JSON data from a file.

    :param file_io: The file object to read from
    :type file_io: :class:`TextIOWrapper`
    :param filepath: The path to the file
    :type filepath: `str`
    :param json_per_line: Whether the JSON data is formatted with one JSON
    object per line. Defaults to `False`.
    :type json_per_line: `bool`
    :return: A generator yielding JSON objects
    :rtype: `Generator`[:class:`Any`, `Any`, `None`]
    """
    counter = 0
    if json_per_line:
        try:
            for line in file_io:
                yield json.loads(line, strict=False)
                counter += 1
            return
        except json.JSONDecodeError:
            pass
    try:
        yield json.load(file_io, strict=False)
    except json.JSONDecodeError:
        LOGGER.error(
            f"Error decoding JSON data in file: {filepath}\n"
            "However, if the current line counter for the file is"
            "greater than 0 then that number of lines was able to"
            f" be decoded: {counter} lines."
        )
