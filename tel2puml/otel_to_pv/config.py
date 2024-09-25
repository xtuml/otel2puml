"""Config schemas for otel_to_pv."""
from typing import (
    TypedDict,
    NotRequired,
    Literal,
    Any,
)

import yaml
from pydantic import BaseModel, ConfigDict as PYDConfigDict

from .data_sources.data_sources_config import DataSources


class SQLDataHolderConfig(TypedDict):
    """Typed dict for SQLDataHolderConfig."""

    db_uri: str
    batch_size: int
    time_buffer: int


class DataHolders(TypedDict):
    """Typed dict for DataHolders."""

    sql: NotRequired[SQLDataHolderConfig]


class IngestTypes(BaseModel):
    """Typed dict for IngestTypes."""

    model_config = PYDConfigDict(extra="forbid")

    data_source: Literal["json"]
    data_holder: Literal["sql"]


class IngestDataConfig(TypedDict):
    """Typed dict for IngestData config."""

    data_sources: DataSources
    data_holders: DataHolders
    ingest_data: IngestTypes


def load_config_from_dict(config: dict[str, Any]) -> IngestDataConfig:
    """Loads config from yaml string.

    :param config_string: The config string
    :type config_string: `dict`[`str`, `Any`]
    :return: The config
    :rtype: :class:`IngestDataConfig`
    """
    for field in ["data_sources", "data_holders", "ingest_data"]:
        assert field in config
    return IngestDataConfig(
        data_sources=config["data_sources"],
        data_holders=config["data_holders"],
        ingest_data=IngestTypes(**config["ingest_data"]),
    )


def load_config_from_yaml(file_path: str) -> IngestDataConfig:
    """Loads config from yaml file.

    :param file_path: File path to config.yaml
    :type file_path: `str`
    :return: The config
    :rtype: :class:`IngestDataConfig`
    """
    with open(file_path, 'r') as file:
        return load_config_from_dict(yaml.safe_load(file))
