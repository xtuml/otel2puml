"""Config schemas for otel_to_pv."""
from typing import (
    TypedDict,
    NotRequired,
    Literal,
    Any,
)

from pydantic import BaseModel, ConfigDict as PYDConfigDict

from .data_sources.data_sources_config import DataSources


class SequenceModelConfig(BaseModel):
    model_config = PYDConfigDict(extra="forbid")

    async_event_groups: dict[str, dict[str, dict[str, str]]]


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
    sequencer: NotRequired[SequenceModelConfig]


class Defaults(TypedDict):
    sequencer: SequenceModelConfig


DEFAULTS = Defaults(
    sequencer=SequenceModelConfig(
        async_event_groups={}
    )
)


def load_config_from_dict(config: dict[str, Any]) -> IngestDataConfig:
    """Loads config from yaml string.

    :param config_string: The config string
    :type config_string: `dict`[`str`, `Any`]
    :return: The config
    :rtype: :class:`IngestDataConfig`
    """
    for field in [
        "data_sources", "data_holders", "ingest_data"
    ]:
        assert field in config
    otel_to_pv_config = IngestDataConfig(
        data_sources=config["data_sources"],
        data_holders=config["data_holders"],
        ingest_data=IngestTypes(**config["ingest_data"]),
    )
    # unrequired fields with defaults
    for field in ["sequencer"]:
        if field in config:
            otel_to_pv_config[field] = SequenceModelConfig(
                **config[field]
            )
        else:
            otel_to_pv_config[field] = DEFAULTS[field]
    return otel_to_pv_config
