"""Config schemas for otel_to_pv."""

from typing import (
    Optional,
    TypedDict,
    Union,
    NotRequired,
    Literal,
    Any,
    Iterable,
    Self,
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


class JQFieldSpec:
    """Typed dict for JQFieldSpec."""

    def __init__(
        self,
        key_paths: list[tuple[str, ...]],
        key_values: list[tuple[str | None, ...]],
        value_paths: list[tuple[str | None, ...]],
        value_type: Union[str, int],
    ) -> None:
        self.validate_key_values_with_key_paths(key_values, key_paths)
        self.validate_value_paths_with_key_values(value_paths, key_values)
        self.key_paths = key_paths
        self.key_values = key_values
        self.value_paths = value_paths
        self.value_type = value_type

    @staticmethod
    def validate_key_values_with_key_paths(
        key_values: list[tuple[str | None, ...]],
        key_paths: list[tuple[str, ...]],
    ) -> None:
        if len(key_values) != len(key_paths):
            raise ValueError(
                "Input key values and input key paths must have the same "
                "length"
            )
        for priority_key_values, priority_key_paths in zip(
            key_values, key_paths
        ):
            if len(priority_key_values) != len(priority_key_paths):
                raise ValueError(
                    "Input Priority key values and priority key paths must "
                    "be interables of the same length, single strings or None,"
                    " or a combination of the two that is consitent in terms "
                    "of length"
                )

    @staticmethod
    def validate_value_paths_with_key_values(
        value_paths: list[tuple[str | None, ...]],
        key_values: list[tuple[str | None, ...]],
    ) -> None:
        if len(value_paths) != len(key_values):
            raise ValueError(
                "Input value paths and input key values must have the same "
                "length"
            )
        for priority_value_paths, priority_key_values in zip(
            value_paths, key_values
        ):
            if len(priority_key_values) != len(priority_value_paths):
                raise ValueError(
                    "Input priority value paths and priority key values must "
                    "be interables of the same length, single strings or None,"
                    " or a combination of the two that is consitent in terms "
                    "of length"
                )
            for value_path, key_value in zip(
                priority_value_paths, priority_key_values
            ):
                if value_path is None and key_value is not None:
                    raise ValueError(
                        "If a key value is provided, a value path must also be"
                        " provided"
                    )

    @staticmethod
    def field_spec_key_paths_to_jq_field_spec_key_paths(
        key_paths: list[str | Iterable[str]],
    ) -> list[tuple[str, ...]]:
        updated_key_paths: list[tuple[str, ...]] = []
        for key_path in key_paths:
            if isinstance(key_path, str):
                updated_key_paths.append((key_path,))
            else:
                try:
                    priority_key_path = list(iter(key_path))
                    for key in priority_key_path:
                        if not isinstance(key, str):
                            raise RuntimeError(
                                "Priority key path, within an iterable, "
                                "must be a string"
                            )
                    updated_key_paths.append(tuple(priority_key_path))
                except TypeError:
                    raise RuntimeError("Key path must be iterable or a string")
        return updated_key_paths

    @staticmethod
    def field_spec_optional_list_to_jq_field_spec_optional_list(
        optional_list: Optional[
            list[Optional[Union[str, Iterable[str | None]]]]
        ],
        jq_key_paths: list[tuple[str, ...]],
    ) -> list[tuple[str | None, ...]]:
        updated_optional_list: list[tuple[str | None, ...]] = []
        if optional_list is None:
            for jq_key_path in jq_key_paths:
                updated_optional_list.append(tuple([None] * len(jq_key_path)))
            return updated_optional_list
        for key_value, key_path in zip(optional_list, jq_key_paths):
            if key_value is None:
                updated_optional_list.append(tuple([None] * len(key_path)))
            elif isinstance(key_value, str):
                updated_optional_list.append((key_value,))
            else:
                try:
                    priority_optional_list = list(iter(key_value))
                    updated_optional_list.append(tuple(priority_optional_list))
                except TypeError:
                    raise RuntimeError(
                        "Key value must be iterable or a string"
                    )
        return updated_optional_list

    @classmethod
    def from_field_spec(cls, field_spec: FieldSpec) -> Self:
        jq_field_spec_key_paths = (
            cls.field_spec_key_paths_to_jq_field_spec_key_paths(
                field_spec["key_paths"]
            )
        )
        jq_field_spec_key_values = (
            cls.field_spec_optional_list_to_jq_field_spec_optional_list(
                field_spec["key_value"], jq_field_spec_key_paths
            )
        )
        jq_field_spec_key_values = (
            cls.field_spec_optional_list_to_jq_field_spec_optional_list(
                field_spec["value_paths"], jq_field_spec_key_paths
            )
        )
        return cls(
            key_paths=jq_field_spec_key_paths,
            key_values=jq_field_spec_key_values,
            value_paths=jq_field_spec_key_values,
            value_type=field_spec["value_type"],
        )

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, JQFieldSpec):
            return False
        return (
            self.key_paths == value.key_paths
            and self.key_values == value.key_values
            and self.value_paths == value.value_paths
            and self.value_type == value.value_type
        )


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
    :rtype: :class:`IngestData
    """
    for field in ["data_sources", "data_holders", "ingest_data"]:
        assert field in config
    return IngestDataConfig(
        data_sources=config["data_sources"],
        data_holders=config["data_holders"],
        ingest_data=IngestTypes(**config["ingest_data"]),
    )
