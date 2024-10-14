"""Module for JSON config."""

from typing import Optional, Union, NotRequired, Iterable, Self, Sequence
from typing_extensions import TypedDict

from pydantic import BaseModel, model_validator, Field, ConfigDict


class FieldSpec(TypedDict):
    """Typed dict for FieldSpec."""

    key_paths: Union[Sequence[str | Iterable[str]], str]
    key_value: NotRequired[
        Optional[
            Union[
                Sequence[Optional[Union[str, Iterable[str | None]]]],
                str
            ]
        ]
    ]
    value_paths: NotRequired[
        Optional[
            Union[
                Sequence[Optional[Union[str, Iterable[str | None]]]],
                str
            ]
        ]
    ]
    value_type: str


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
    :type value_type: `str`
    """

    def __init__(
        self,
        key_paths: Sequence[tuple[str, ...]],
        key_values: Sequence[tuple[str | None, ...]],
        value_paths: Sequence[tuple[str | None, ...]],
        value_type: str,
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
        key_paths: Union[Sequence[str | Iterable[str]], str],
    ) -> list[tuple[str, ...]]:
        """Converts field spec key paths to jq field spec key paths.

        :param key_paths: The key paths
        :type key_paths: `Union`[`Sequence`[`str` | `Iterable`[`str`]],
        `str`]
        :return: The jq field spec key paths
        :rtype: `list`[`tuple`[`str`, ...]]
        """
        if isinstance(key_paths, str):
            key_paths = [key_paths]
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
                raise TypeError("Key value must be iterable or a string")

    @staticmethod
    def optional_list_to_jq_optional_list(
        optional_list: Optional[
            Union[
                Sequence[Optional[Union[str, Iterable[str | None]]]],
                str
            ]
        ],
        jq_key_paths: Sequence[tuple[str, ...]],
    ) -> list[tuple[str | None, ...]]:
        """Converts optional list to jq optional list.

        :param optional_list: The optional list
        :type optional_list: `Optional`[`Union`[`Sequence`[`Optional`[`Union`[
        `str`, `Iterable`[`str` | `None`]]]], `str`]]
        :param jq_key_paths: The jq key paths
        :type jq_key_paths: `Sequence`[`tuple`[`str`, ...]]
        :return: The jq optional list
        :rtype: `list`[`tuple`[`str` | `None`, ...
        ]]
        """
        if isinstance(optional_list, str):
            optional_list = [optional_list]
        updated_optional_list: list[tuple[str | None, ...]] = []
        if optional_list is None:
            optional_list = [None] * len(jq_key_paths)
        for key_value, key_path in zip(optional_list, jq_key_paths):
            updated_optional_list.append(
                JQFieldSpec.optional_list_value_to_jq_optional_list_value(
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
        jq_field_spec_key_values = cls.optional_list_to_jq_optional_list(
            field_spec["key_value"] if "key_value" in field_spec else None,
            jq_field_spec_key_paths,
        )
        jq_field_spec_value_paths = cls.optional_list_to_jq_optional_list(
            field_spec["value_paths"] if "value_paths" in field_spec else None,
            jq_field_spec_key_paths,
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


def field_spec_mapping_to_jq_field_spec_mapping(
    field_mapping: dict[str, FieldSpec],
) -> dict[str, JQFieldSpec]:
    """Converts field mapping to jq field mapping.

    :param field_mapping: The field mapping
    :type field_mapping: `dict`[`str`, :class:`FieldSpec`]
    :return: The jq field mapping
    :rtype: `dict`[`str`, :class:`JQFieldSpec`]
    """
    return {
        key: JQFieldSpec.from_field_spec(value)
        for key, value in field_mapping.items()
    }


class OTelFieldMapping(BaseModel):
    """BaseModel for OTelFieldMapping - the expected mapping of fields in the
    used for the JSON data source."""
    job_name: FieldSpec
    job_id: FieldSpec
    event_type: FieldSpec
    event_id: FieldSpec
    start_timestamp: FieldSpec
    end_timestamp: FieldSpec
    application_name: FieldSpec
    parent_event_id: FieldSpec
    child_event_ids: FieldSpec | None = None

    def to_field_mapping(self) -> dict[str, FieldSpec]:
        """Converts to field mapping.

        :return: The field mapping
        :rtype: `dict`[`str`, :class:`FieldSpec`]
        """
        field_mapping = {
            "job_name": self.job_name,
            "job_id": self.job_id,
            "event_type": self.event_type,
            "event_id": self.event_id,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "application_name": self.application_name,
            "parent_event_id": self.parent_event_id,
        }
        if self.child_event_ids is not None:
            field_mapping["child_event_ids"] = self.child_event_ids
        return field_mapping


class JSONDataSourceConfig(BaseModel):
    """BaseModel for JSONDataSourceConfig."""

    model_config = ConfigDict(
        strict=True,
        extra="forbid",
    )

    filepath: Optional[str] = Field(None, description="The file path")
    dirpath: Optional[str] = Field(None, description="The directory path")
    json_per_line: bool = Field(False, description="Flag for JSON per line")
    field_mapping: Optional[OTelFieldMapping] = Field(
        None, description="The field mapping"
    )
    jq_query: Optional[str] = Field(None, description="The jq query")

    @model_validator(mode="after")
    def verify_field_mapping_jq_query(self) -> Self:
        """Verify field mapping jq query."""
        if self.field_mapping is None and self.jq_query is None:
            raise ValueError(
                "Either field_mapping or jq_query must be provided"
            )
        if self.field_mapping is not None and self.jq_query is not None:
            raise ValueError(
                "Only one of field_mapping or jq_query should be provided"
            )
        return self

    @model_validator(mode="after")
    def verify_file_path_dir_path(self) -> Self:
        """Verify file path dir path."""
        if self.filepath is None and self.dirpath is None:
            raise ValueError("Either filepath or dirpath must be provided")
        return self
