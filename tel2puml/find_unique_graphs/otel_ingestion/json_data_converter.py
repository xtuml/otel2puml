"""This module converts JSON OTel data to adhere to the application schema."""

import flatdict
from typing import Any
from datetime import datetime
from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    JSONDataSourceConfig,
)


def flatten_json_dict(json_data: dict[str, Any]) -> Any:
    """Function to flatten a nested dictionary.

    :param json_data: The JSON data to flatten.
    :param json_data: `dict`[`str`,`Any`]
    :return: The flattened json as a dictionary
    :rtype: `Any`
    """
    return flatdict.FlatterDict(json_data)


def map_data_to_json_schema(
    mapping_config: JSONDataSourceConfig, flattened_data: Any
) -> dict[str, str]:
    """
    Function that maps flattened JSON data to a schema defined in the
    mapping_config.

    :param mapping_config: The mapping config pulled from the yaml config file
    :type mapping_config: :class:`JSONDataSourceConfig`
    :param flattened_data: JSON data as a flattened dictionary
    :type flattened_data: `Any`
    :return: The mapped data
    :rtype: `dict`[`str`, `str`]
    """
    result: dict[str, str] = {}
    field_mapping: dict[str, Any] = mapping_config["field_mapping"]
    for field_name, field_config in field_mapping.items():
        process_field(field_name, field_config, flattened_data, result)
    return result


def process_field(
    field_name: str,
    field_config: dict[str, Any],
    flattened_data: Any,
    result: dict[str, str],
) -> None:
    """
    Function that processes a single field according to its configuration.

    :param field_name: The field name within the mapping config
    :type field_name: `str`
    :param field_config: The config for the field name
    :type field_config: `str` | `dict`[`str`,`Any`]
    :param flattened_data: JSON data as a flattened dictionary
    :type flattened_data: `Any`
    :param result: The mapped data
    :type result: `dict`[`str`, `str`]
    """
    for index, key_path in enumerate(field_config["key_paths"]):
        path_segments = key_path.split(":")
        if "" in path_segments:
            # Indicates that we are handling a list within the json data
            handle_empty_segments(
                field_name, field_config, index, flattened_data, result
            )
        else:
            full_path = ":".join(path_segments)
            handle_regular_path(
                field_name,
                field_config,
                index,
                full_path,
                flattened_data,
                result,
            )


def handle_empty_segments(
    field_name: str,
    field_config: dict[str, Any],
    index: int,
    flattened_data: Any,
    result: dict[str, str],
) -> None:
    """
    Function that handles paths with empty segments, indicating a list within
    the JSON data.

    :param field_name: The field name within the mapping config
    :type field_name: `str`
    :param field_config: The config for the field name
    :type field_config: `dict`[`str`,`Any`]
    :param index: The index of the field config
    :type index: `int`
    :param flattened_data: JSON data as a flattened dictionary
    :type flattened_data: `Any`
    :param result: The mapped data
    :type result: `dict`[`str`, `str`]
    """
    full_path = ":".join(field_config["key_paths"][index].split(":"))
    segment_count = 0
    key = full_path.split("::")[-1]
    full_path = full_path.replace("::", f":{str(segment_count)}:")

    # Avoid an infinite loop
    # TODO Have a think about this number
    while segment_count <= 50:
        try:
            if flattened_data[full_path] == field_config["key_value"][index]:
                full_path = full_path.replace(
                    key,
                    field_config["value_paths"][index],
                )
                value_type = get_value_type(field_config)
                add_or_append_value(
                    field_name, flattened_data[full_path], result, value_type
                )
                break
        except KeyError:
            # Key errors will occur as we are looping through a list trying to
            # find the key iteratively
            pass
        except Exception as e:
            raise RuntimeError(f"An error occured - {e}")

        full_path = full_path.replace(
            f":{str(segment_count)}:",
            f":{str(segment_count + 1)}:",
        )
        segment_count += 1

    if segment_count > 50:
        raise RuntimeError("Could not find attribute.")


def handle_regular_path(
    field_name: str,
    field_config: dict[str, Any],
    index: int,
    full_path: str,
    flattened_data: Any,
    result: dict[str, str],
) -> None:
    """
    Function that handles regular paths without empty segments.

    :param field_name: The field name within the mapping config
    :type field_name: `str`
    :param field_config: The config for the field name
    :type field_config: `dict`[`str`,`Any`]
    :param index: The index of the field config
    :type index: `int`
    :param full_path: The key of the flattened data
    :type full_path: `str`
    :param flattened_data: JSON data as a flattened dictionary
    :type flattened_data: `Any`
    :param result: The mapped data
    :type result: `dict`[`str`, `str`]
    """
    try:
        if not field_config.get(["keys"][index]):
            if flattened_data.get(full_path):
                value_type = get_value_type(field_config)
                add_or_append_value(
                    field_name, flattened_data[full_path], result, value_type
                )
    except Exception as e:
        print(f"An error occurred - {e}")


def get_value_type(field_config: dict[str, Any]) -> str:
    """Function that returns the type of the field.

    :param field_config: The config for the field name
    :type field_config: `dict`[`str`,`Any`]
    :return: The field type
    :rtype: `str`
    """
    if isinstance(field_config["value_type"], str):
        return field_config["value_type"]
    else:
        raise TypeError("Value should be a string")


def add_or_append_value(
    field_name: str, value: str | int, result: dict[str, str], value_type: str
) -> None:
    """
    Function that adds a new value or appends to an existingone in the result
    dictionary.

    :param field_name: The field name within the mapping config
    :type field_name: `str`
    :param value: The value pulled from the JSON data
    :type value: `str` | `int`
    :param result: The mapped data
    :type result: `dict`[`str`, `str`]
    :param value_type: The field type
    :return value_type: `str`
    """
    if value_type == "unix_nano":
        if isinstance(value, int):
            value = process_unix_nano(value)
    if not isinstance(value, str):
        value = str(value)
    if field_name not in result:
        result[field_name] = value
    else:
        result[field_name] += f" {value}"


def process_unix_nano(unix_nano: int) -> str:
    """Function to process time from unix nano to datetime string.

    :param unix_nano: The time in unix nano format
    :type unix_nano: `int`
    :return: The time in datetime string format
    :rtype: `str`
    """
    dt = datetime.fromtimestamp(unix_nano // 1000000000)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def flatten_and_map_data(
    json_config: JSONDataSourceConfig, raw_json: dict[str, Any]
) -> dict[str, str]:
    """Function to handle flattening raw json and mapping the data to the
    specified configuration.

    :param json_config: The json config
    :type json_config: :class: `JSONDataSourceConfig`
    :param json_data: The JSON data to flatten.
    :param json_data: `dict`[`str`,`Any`]
    return: The mapped data
    :rtype: `dict`[`str`, `str`]
    """
    flattened_data = flatten_json_dict(raw_json)
    return map_data_to_json_schema(json_config, flattened_data)
