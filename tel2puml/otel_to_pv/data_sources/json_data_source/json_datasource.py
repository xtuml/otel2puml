"""Module containing DataSource sub class responsible for JSON ingestion."""

import os
from typing import Iterator, Any
import json
from logging import getLogger

from tqdm import tqdm
from pydantic import ValidationError
import jq  # type: ignore[import-not-found]

from tel2puml.otel_to_pv.otel_to_pv_types import OTelEvent
from ..base import OTELDataSource
from .json_jq_converter import (
    generate_records_from_compiled_jq,
    field_mapping_to_compiled_jq,
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
        self.compiled_jq = self.get_compiled_jq_from_config(self.config)
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

    @staticmethod
    def get_compiled_jq_from_config(config: JSONDataSourceConfig) -> Any:
        """Get the compiled jq query from the config.

        :param config: The JSONDataSourceConfig object
        :type config: :class:`JSONDataSourceConfig`
        :return: The compiled jq query
        :rtype: `Any`
        """
        if config.field_mapping is not None:
            return field_mapping_to_compiled_jq(
                config.field_mapping.to_field_mapping()
            )
        elif config.jq_query is not None:
            return jq.compile(config.jq_query)
        else:
            raise ValueError("No field mapping or jq query found in config.")

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
            if self.config.json_per_line:
                jsons = (json.loads(line, strict=False) for line in file)
            else:
                jsons = (data for data in [json.load(file, strict=False)])
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
