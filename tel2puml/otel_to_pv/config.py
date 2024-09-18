"""Config schemas for otel_to_pv."""
from typing import (
    Optional,
    TypedDict,
    Union,
    NotRequired,
    Literal,
    Any,
)

from pydantic import BaseModel, ConfigDict as PYDConfigDict


class HeaderSpec(TypedDict):
    """Typed dict for HeaderSpec."""

    paths: list[str]


class SpanSpec(TypedDict):
    """Typed dict for SpanSpec."""

    key_paths: list[str]


class FieldSpec(TypedDict):
    """Typed dict for FieldSpec."""

    key_paths: list[str | tuple[str, ...]]
    key_value: Optional[list[Optional[Union[str, tuple[str | None, ...]]]]]
    value_paths: Optional[list[Optional[Union[str, tuple[str | None, ...]]]]]
    value_type: Union[str, int]


class JQFieldSpec(TypedDict):
    """Typed dict for JQFieldSpec."""

    key_paths: list[tuple[str, ...]]
    key_value: list[tuple[str | None, ...]]
    value_paths: list[tuple[str | None, ...]]
    value_type: Union[str, int]


class JSONDataSourceConfig(TypedDict):
    """Typed dict for JSONDataSourceConfig."""

    filepath: str
    dirpath: str
    data_location: str
    header: dict[str, HeaderSpec]
    span_mapping: dict[str, SpanSpec]
    field_mapping: dict[str, FieldSpec]


class SQLDataHolderConfig(TypedDict):
    """Typed dict for SQLDataHolderConfig."""

    db_uri: str
    batch_size: int
    time_buffer: int


class DataSources(TypedDict):
    """Typed dict for DataSources."""

    json: NotRequired[JSONDataSourceConfig]


class DataHolders(TypedDict):
    """Typed dict for DataHolders."""

    sql: NotRequired[SQLDataHolderConfig]


class IngestTypes(BaseModel):
    """Typed dict for IngestTypes."""
    model_config = PYDConfigDict(extra='forbid')

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
    :rtype: :class:`IngestData
    """
    for field in ["data_sources", "data_holders", "ingest_data"]:
        assert field in config
    return IngestDataConfig(
        data_sources=config["data_sources"],
        data_holders=config["data_holders"],
        ingest_data=IngestTypes(**config["ingest_data"]),
    )
