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
    Sequence
)

import yaml
from pydantic import BaseModel, ConfigDict as PYDConfigDict


class HeaderSpec(TypedDict):
    """Typed dict for HeaderSpec."""

    paths: list[str]


class SpanSpec(TypedDict):
    """Typed dict for SpanSpec."""

    key_paths: list[str]


class FieldSpec(TypedDict):
    """Typed dict for FieldSpec."""

    key_paths: list[str | Iterable[str]]
    key_value: Optional[list[Optional[Union[str, Iterable[str | None]]]]]
    value_paths: Optional[list[Optional[Union[str, Iterable[str | None]]]]]
    value_type: Union[str, int]


class JQFieldSpec:
    """Class that provides the validation and conversion from FieldSpec to
    concrete types that can be used for pulling out information from JSON files
    using `jq`.

    :param key_paths: The key paths
    :type key_paths: `Sequence`[`tuple`[`str`, ...]]
    :param key_values: The key values
    :type key_values: `Sequence`[`tuple`[`str` |
    `None`, ...]]
    :param value_paths: The value paths
    :type value_paths: `Sequence`[`tuple`[`str` |
    `None`, ...]]
    :param value_type: The value type
    :type value_type: `Union`[`str`, `int`]
    """

    def __init__(
        self,
        key_paths: Sequence[tuple[str, ...]],
        key_values: Sequence[tuple[str | None, ...]],
        value_paths: Sequence[tuple[str | None, ...]],
        value_type: Union[str, int],
    ) -> None:
        """Constructor method."""
        self.validate_key_values_with_key_paths(key_values, key_paths)
        self.validate_value_paths_with_key_values(value_paths, key_values)
        self.key_paths = key_paths
        self.key_values = key_values
        self.value_paths = value_paths
        self.value_type = value_type

    @staticmethod
    def validate_key_values_with_key_paths(
        key_values: Sequence[tuple[str | None, ...]],
        key_paths: Sequence[tuple[str, ...]],
    ) -> None:
        """Validates key values with key paths.

        :param key_values: The key values
        :type key_values: `Sequence`[`tuple`[`str` |
        `None`, ...]]
        :param key_paths: The key paths
        :type key_paths: `Sequence`[`tuple`[`str`, ...]]
        """
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
        value_paths: Sequence[tuple[str | None, ...]],
        key_values: Sequence[tuple[str | None, ...]],
    ) -> None:
        """Validates value paths with key values.

        :param value_paths: The value paths
        :type value_paths: `Sequence`[`tuple`[`str` |
        `None`, ...]]
        :param key_values: The key values
        :type key_values: `Sequence`[`tuple`[`str` |
        `None`, ...]]
        """
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
    def field_spec_key_path_to_jq_key_path(
        key_path: str | Iterable[str],
    ) -> tuple[str, ...]:
        """Converts field spec key path to jq key path.

        :param key_path: The key path
        :type key_path: `str` | `Iterable`[`str`]
        :return: The jq key path
        :rtype: `tuple`[`str`, ...]
        """
        if isinstance(key_path, str):
            return (key_path,)
        try:
            priority_key_path = tuple(iter(key_path))
            for key in priority_key_path:
                if not isinstance(key, str):
                    raise TypeError(
                        "Priority key path, within an iterable, must be a "
                        "string"
                    )
            return priority_key_path
        except TypeError:
            raise TypeError("Key path must be iterable or a string")

    @staticmethod
    def field_spec_key_paths_to_jq_field_spec_key_paths(
        key_paths: Sequence[str | Iterable[str]],
    ) -> list[tuple[str, ...]]:
        """Converts field spec key paths to jq field spec key paths.

        :param key_paths: The key paths
        :type key_paths: :class:`Sequence`[`str` | `Iterable`[`str`]]
        :return: The jq field spec key paths
        :rtype: `list`[`tuple`[`str`, ...]]
        """
        updated_key_paths: list[tuple[str, ...]] = []
        for key_path in key_paths:
            updated_key_paths.append(
                JQFieldSpec.field_spec_key_path_to_jq_key_path(key_path)
            )
        return updated_key_paths

    @staticmethod
    def optional_list_value_to_jq_optional_list_value(
        optional_list_value: Optional[Union[str, Iterable[str | None]]],
        jq_key_path: tuple[str, ...],
    ) -> tuple[None, ...] | tuple[str | None, ...]:
        """Converts optional list value to jq optional list value.

        :param optional_list_value: The optional list value
        :type optional_list_value: `Optional`[`Union`[`str`,
        `Iterable`[`str` | `None`]]]
        :param jq_key_path: The jq key path
        :type jq_key_path: `tuple`[`str`, ...]
        :return: The jq optional list value
        :rtype: `tuple`[`str` | `None`, ...]
        """
        if optional_list_value is None:
            return tuple([None] * len(jq_key_path))
        elif isinstance(optional_list_value, str):
            return (optional_list_value,)
        else:
            try:
                priority_optional_list = tuple(iter(optional_list_value))
                for key in priority_optional_list:
                    if not isinstance(key, str) and key is not None:
                        raise TypeError(
                            "Priority key value, within an iterable, must be "
                            "a string or None"
                        )
                return tuple(priority_optional_list)
            except TypeError:
                raise TypeError(
                    "Key value must be iterable or a string"
                )

    @staticmethod
    def optional_list_to_jq_optional_list(
        optional_list: Optional[
            Sequence[Optional[Union[str, Iterable[str | None]]]]
        ],
        jq_key_paths: Sequence[tuple[str, ...]],
    ) -> list[tuple[str | None, ...]]:
        """Converts optional list to jq optional list.

        :param optional_list: The optional list
        :type optional_list: `Optional`[`Sequence`[`Optional`[
        `Union`[`str`, `Iterable`[`str` | `None`]]
        ]]]
        :param jq_key_paths: The jq key paths
        :type jq_key_paths: `Sequence`[`tuple`[`str`, ...]]
        :return: The jq optional list
        :rtype: `list`[`tuple`[`str` | `None`, ...
        ]]
        """
        updated_optional_list: list[tuple[str | None, ...]] = []
        if optional_list is None:
            optional_list = [None] * len(jq_key_paths)
        for key_value, key_path in zip(optional_list, jq_key_paths):
            updated_optional_list.append(
                JQFieldSpec.
                optional_list_value_to_jq_optional_list_value(
                    key_value, key_path
                )
            )
        return updated_optional_list

    @classmethod
    def from_field_spec(cls, field_spec: FieldSpec) -> Self:
        """Converts from field spec.

        :param field_spec: The field spec
        :type field_spec: :class:`FieldSpec`
        :return: The jq field spec
        :rtype: :class:`JQFieldSpec`
        """
        jq_field_spec_key_paths = (
            cls.field_spec_key_paths_to_jq_field_spec_key_paths(
                field_spec["key_paths"]
            )
        )
        jq_field_spec_key_values = (
            cls.optional_list_to_jq_optional_list(
                field_spec["key_value"], jq_field_spec_key_paths
            )
        )
        jq_field_spec_value_paths = (
            cls.optional_list_to_jq_optional_list(
                field_spec["value_paths"], jq_field_spec_key_paths
            )
        )
        return cls(
            key_paths=jq_field_spec_key_paths,
            key_values=jq_field_spec_key_values,
            value_paths=jq_field_spec_value_paths,
            value_type=field_spec["value_type"],
        )

    def __eq__(self, value: object) -> bool:
        """Equality method.

        :param value: The value
        :type value: `object`
        :return: Whether the value is equal
        :rtype: `bool`
        """
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
