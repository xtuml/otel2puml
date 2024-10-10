"""Config schemas for otel_to_pv."""

from typing import (
    Literal,
    Any,
    NotRequired
)
from typing_extensions import TypedDict

from pydantic import BaseModel, ConfigDict as PYDConfigDict

from .data_sources.data_sources_config import DataSources
from .otel_to_pv_types import OTelEventTypeMap


class SequenceModelConfig(BaseModel):
    """PyDantic model for SequenceModelConfig."""

    model_config = PYDConfigDict(extra="forbid")

    async_event_groups: dict[str, dict[str, dict[str, str]]] = {}
    async_flag: bool = False
    event_name_map_information: dict[str, dict[str, OTelEventTypeMap]] = {}


class SQLDataHolderConfig(BaseModel):
    """BaseModel for SQLDataHolderConfig."""

    db_uri: str = "sqlite:///:memory:"
    batch_size: int = 1000
    time_buffer: int = 0


class DataHolders(TypedDict):
    """Typed dict for DataHolders."""
    sql: NotRequired[SQLDataHolderConfig]


class IngestTypes(BaseModel):
    """Base model for IngestTypes."""

    model_config = PYDConfigDict(extra="forbid")

    data_source: Literal["json"]
    data_holder: Literal["sql"]


class IngestDataConfig(BaseModel):
    """Base model for IngestData config."""

    model_config = PYDConfigDict(extra="forbid")

    data_sources: DataSources
    data_holders: DataHolders
    ingest_data: IngestTypes
    sequencer: SequenceModelConfig = SequenceModelConfig()


def load_config_from_dict(config: dict[str, Any]) -> IngestDataConfig:
    """Loads config from yaml string.

    :param config_string: The config string
    :type config_string: `dict`[`str`, `Any`]
    :return: The config
    :rtype: :class:`IngestDataConfig`
    """
    return IngestDataConfig(
        **config
    )
