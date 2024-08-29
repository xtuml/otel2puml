"""This module converts JSON OTel data to adhere to the application schema."""

import flatdict
import logging

from typing import Any, Literal

from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    JSONDataSourceConfig,
    FieldSpec,
)

MAX_SEGMENT_COUNT = 50  # TODO have a think about this
LOGGER = logging.getLogger(__name__)


def _flatten_json_dict(
    data: dict[str, Any] | list[dict[str, Any]],
) -> flatdict.FlatterDict:
    """Function to flatten a dictionary or list.

    :param data: The JSON data to flatten.
    :param data: `dict`[`str`,`Any`] | `list`[`dict`[`str`, `Any`]]
    :return: The flattened json as a dictionary
    :rtype: :class: `flatdict.FlatterDict`
    """
    return flatdict.FlatterDict(data)


def _map_data_to_json_schema(
    json_config: JSONDataSourceConfig,
    flattened_data: Any,
    config_key: Literal["field_mapping"],
    header_dict: dict[str, Any],
) -> dict[str, Any]:
    """
    Function that maps flattened JSON data to a schema defined in the
    json_config.

    :param json_config: The mapping config pulled from the yaml config file
    :type json_config: :class:`JSONDataSourceConfig`
    :param flattened_data: JSON data as a flattened dictionary
    :type flattened_data: `Any`
    :param config_key: The key for the json config fields
    :type config_key: `Literal`["field_mapping"]
    :param header_dict: A dictionary of flattened json data containing header
    data
    :type header_dict: `dict`[`str`, `Any`]
    :return: The mapped data
    :rtype: `dict`[`str`, `Any`]
    """
    result: dict[str, Any] = {}
    field_mapping: dict[str, Any] = json_config[config_key]
    # Cache results within lists to avoid looping over them again
    field_cache: dict[str, str] = {}
    for field_name, field_config in field_mapping.items():
        _process_field(
            field_name,
            field_config,
            flattened_data,
            result,
            field_cache,
            header_dict,
        )
    return result


def _process_field(
    field_name: str,
    field_config: FieldSpec,
    flattened_data: Any,
    result: dict[str, Any],
    field_cache: dict[str, str],
    header_dict: dict[str, Any],
) -> None:
    """
    Function that processes a single field according to its configuration.

    :param field_name: The field name within the mapping config
    :type field_name: `str`
    :param field_config: The config for the field name
    :type field_config: :class: `FieldSpec`
    :param flattened_data: JSON data as a flattened dictionary
    :type flattened_data: `Any`
    :param result: The mapped data
    :type result: `dict`[`str`, `Any`]
    :param field_cache: Cache for optimising field access and path generation
    in flattened JSON data
    :type field_cache: `dict`[`str`, [`str`]]
    :param header_dict: A dictionary of flattened json data containing header
    data
    :type header_dict: `dict`[`str`, `Any`]
    """
    for index, key_path in enumerate(field_config["key_paths"]):
        path_segments = key_path.split(":")
        if "" in path_segments:
            field_cache_key = key_path.split("::")[0]
            # Indicates that we are handling a list within the json data
            _handle_empty_segments(
                field_name,
                field_config,
                flattened_data,
                index,
                result,
                field_cache,
                field_cache_key,
                header_dict,
            )
        else:
            full_path = ":".join(path_segments)
            _handle_regular_path(
                field_name,
                field_config,
                full_path,
                flattened_data,
                result,
                header_dict,
            )


def _handle_empty_segments(
    field_name: str,
    field_config: FieldSpec,
    flattened_data: Any,
    index: int,
    result: dict[str, Any],
    field_cache: dict[str, str],
    field_cache_key: str,
    header_dict: dict[str, Any],
) -> None:
    """
    Function that handles paths with empty segments, indicating a list within
    the JSON data.

    :param field_name: The field name within the mapping config
    :type field_name: :class: `FieldSpec`
    :param field_config: The config for the field name
    :type field_config: `dict`[`str`,`Any`]
    :param flattened_data: JSON data as a flattened dictionary
    :type flattened_data: `Any`
    :param index: The index of the field config
    :type index: `int`
    :param result: The mapped data
    :type result: `dict`[`str`, `Any`]
    :param field_cache: Cache for optimising field access and path generation
    in flattened JSON data
    :type field_cache: `dict`[`str`, [`str`]]
    :param field_cache_key: The key of the field cache
    :type field_cache_key: `str`
    :param header_dict: A dictionary of flattened json data containing header
    data
    :type header_dict: `dict`[`str`, `Any`]
    """
    full_path = field_config["key_paths"][index]
    key = full_path.split("::")[-1]

    if full_path.split(":")[0] == "HEADER":
        _handle_data_from_header(
            field_name,
            field_config,
            index,
            result,
            header_dict,
            key,
            full_path,
        )
        return

    # TODO Have a think about this number
    for segment_count in range(MAX_SEGMENT_COUNT):
        try:
            full_path = _update_full_path(full_path, segment_count)

            cache_entry = _get_or_create_cache_entry(
                field_cache, field_cache_key, key
            )

            # check for case where key value is not specifed, indicating
            # that the path within key_paths is the full path and the value
            # at that path is what we want.
            if (
                "key_value" not in field_config
                or not field_config["key_value"][index]
            ):
                if flattened_data.get(full_path):
                    result[field_name] = flattened_data.get(full_path)
                    return

            # Check the cache to see if the value that we are looking for has
            # already been looped over and stored.
            # If the value is not found within the cache, we start looking at
            # the value of 'count' that is stored within the cache, as we have
            # already checked values up until count - 1.
            value_to_check = _get_key_value(field_config, index)
            full_path = _get_cached_path(
                cache_entry, value_to_check, full_path, segment_count
            )

            if _is_matching_data(flattened_data, full_path, value_to_check):
                _update_cache(cache_entry, flattened_data, full_path)
                _process_matching_data(
                    field_name,
                    field_config,
                    index,
                    flattened_data,
                    full_path,
                    key,
                    result,
                )
                return
            _update_cache(cache_entry, flattened_data, full_path)

        except (KeyError, TypeError):
            # Keep a record of the count so that we don't have to iterate
            # through the tried keys again. We get KeyError and TypeErrors when
            # we try accessing a key within the field config dictionary that
            # doesn't exist.
            cache_entry["count"] += 1
        except Exception as e:
            print(f"An error occured - {e}")

    raise RuntimeError(
        f"Could not find data for '{field_name}' within {MAX_SEGMENT_COUNT}"
        " segments"
    )


def _handle_data_from_header(
    target_field_name: str,
    field_config: FieldSpec,
    config_index: int,
    result_dict: dict[str, Any],
    header_data: dict[str, Any],
    initial_header_key: str,
    full_header_path: str,
) -> None:
    """Function that handles instances where HEADER is used within the config,
    indicating that information stored within the header_dict is to be used.

    :param target_field_name: The field name within the mapping config
    :type target_field_name: `str`
    :param field_config: The configuration for the target field
    :type field_config: :class: `FieldSpec`
    :param config_index: The index of the current field in the configuration
    :type config_index: `int`
    :param result_dict: The dictionary to store the mapped data
    :type result_dict: `dict`[`str`, `Any`]
    :param header_data: A dictionary containing flattened JSON header data
    :type header_data: `dict`[`str`, `Any`]
    :param initial_header_key: The initial key to look up in the header_data
    :type initial_header_key: `str`
    :param full_header_path: The full path given in the 'key_paths' config
    :type full_header_path: `str`
    """
    # Remove the 'HEADER:' prefix from the full path
    clean_header_path = full_header_path.split("HEADER:", 1)[1]

    if "::" not in clean_header_path:
        # Resolves simple case
        extracted_value = header_data[clean_header_path]
    else:
        # If a list is involvd, split segments
        path_segments = clean_header_path.split("::")

        # The last segment is the key we're searching for in the header_data
        target_key = path_segments[-1]

        # Update the header key to the key within 'value_paths' if a specific
        # 'key_value' needs to be matched
        if (
            field_config.get("key_value")
            and field_config["key_value"][config_index]
        ):
            header_key = _get_value_path(field_config, config_index)
        else:
            header_key = initial_header_key

        # Navigate through the nested structure of header_data
        current_header_level = header_data
        for segment in path_segments[:-1]:
            current_header_level = current_header_level[segment]

        # Extract the value from header_data
        if header_key == target_key:
            extracted_value = current_header_level[header_key]
        else:
            extracted_value = _find_matching_header_value(
                current_header_level,
                target_key,
                field_config,
                config_index,
                header_key,
            )

    # Get the value type from the field config
    value_type = _get_value_type(field_config)

    # Add or append the value to the result dictionary
    _add_or_append_value(
        target_field_name, extracted_value, result_dict, value_type
    )


def _find_matching_header_value(
    header_level: dict[str, str],
    target_key: str,
    field_config: FieldSpec,
    config_index: int,
    header_key: str,
) -> str:
    """
    Find the matching header value based on the target key and configuration.

    :param header_level: The current level of the header dictionary
    :type header_level: `dict`[`str`, `str`]
    :param target_key: The key to search for in the header
    :type target_key: `str`
    :param field_config: The configuration for the field
    :type field_config: :class: `FieldSpec`
    :param config_index: The index of the current field in the configuration
    :type config_index: `int`
    :param header_key: The key to use for extracting the final value
    :type header_key: `int`
    :return: The extracted value from the header
    :rtype: `str`
    """
    if not header_level:
        raise ValueError("No data within header dictionary.")

    for key, value in header_level.items():
        key_suffix = key.split(":", 1)[-1]
        if (
            key_suffix == target_key
            and value == field_config["key_value"][config_index]
        ):
            key_prefix = key.split(":", 1)[0]
            full_header_key = f"{key_prefix}:{header_key}"

            try:
                return header_level[full_header_key]
            except KeyError:
                raise KeyError(f"{header_key} is an invalid key.")

    raise KeyError(f"No matching value found for key: {target_key}")


def _update_full_path(full_path: str, segment_count: int) -> str:
    """
    Function that updates the full path by replacing segment count placeholders
    with actual segment counts.

    :param full_path: The original path containing placeholders
    :type full_path: `str`
    :param segment_count: The current segment count to be inserted into
    the path
    :type segment_count: `int`
    :return: The updated path with the correct segment count
    :rtype: `str`
    """
    if segment_count == 0:
        return full_path.replace("::", f":{str(segment_count)}:")
    return full_path.replace(f":{segment_count - 1}:", f":{segment_count}:")


def _get_or_create_cache_entry(
    field_cache: dict[str, Any], field_cache_key: str, key: str
) -> dict[str, Any]:
    """
    Function that retrieves an existing cache entry or creates a new one if it
    doesn't exist.

    :param field_cache: The cache dictionary containing field entries
    :type field_cache: `dict`[`str`, `Any`]
    :param field_cache_key: The key to look up or create in the field cache
    :type field_cache_key: `str`
    :param key: The key within the field cache
    :type key: `str`
    :return: The existing or newly created cache entry for the given key
    :rtype: `dict`[`str`,`Any`]
    """
    field_cache.setdefault(field_cache_key, {})
    field_cache[field_cache_key].setdefault(key, {"count": 0})

    cache_entry = field_cache[field_cache_key][key]

    if not isinstance(cache_entry, dict):
        raise TypeError("Field cache entry should be of type dict.")

    return cache_entry


def _get_cached_path(
    cache_entry: dict[str, Any],
    value_to_check: str,
    full_path: str,
    segment_count: int,
) -> str:
    """
    Function that retrieves a cached path or generates a new one at the 'count'
    specified within the cache.

    :param cache_entry: The cache entry containing paths and a count
    indicating how many times we have iterated over a given key
    :type cache_entry: `dict`[`str`, `Any`]
    :param value_to_check: The value to look up in the cache entry
    :type value_to_check: `Any`
    :param full_path: The original full path to modify if the value is not
    found in the cache
    :type full_path: `str`
    :param segment_count: The current segment count in the full path to
    be replaced
    :type segment_count: `int`
    :return: The cached path if found, otherwise a new path with updated
    segment count
    :rtype: `str`
    """
    # Get the cached path, or replace segment count with cache_entry['count']
    # as we have already tried (count - 1) iterations through the full path.
    cached_path = cache_entry.get(
        value_to_check,
        full_path.replace(f":{segment_count}:", f":{cache_entry['count']}:"),
    )
    if isinstance(cached_path, str):
        return cached_path
    else:
        raise TypeError("Path should be of type string.")


def _is_matching_data(
    flattened_data: dict[str, str], full_path: str, value_to_check: str
) -> bool:
    """
    Function that checks if the data at the given path in flattened_data
    matches the value_to_check.

    :param flattened_data: The flattened JSON data to check
    :type flattened_data: `dict`[`str`, `str`]
    :param full_path: The path to check in the flattened data
    :type full_path: `str`
    :param value_to_check: The value to compare against the data at full_path
    :type value_to_check: `str`
    :return: True if the data matches, False otherwise
    :rtype: `bool`
    """
    return (
        full_path in flattened_data
        and flattened_data[full_path] == value_to_check
    )


def _process_matching_data(
    field_name: str,
    field_config: FieldSpec,
    index: int,
    flattened_data: dict[str, Any],
    full_path: str,
    key: str,
    result: dict[str, Any],
) -> None:
    """Function to process data that matches the search requirements. The
    result is either added as a new value or appended to an existing one.

    :param field_name: The field name within the mapping config
    :type field_name: `str`
    :param field_config: The config for the field name
    :type field_config: :class: `FieldSpec`
    :param index: The index of the field config
    :type index: `int`
    :param flattened_data: JSON data as a flattened dictionary
    :type flattened_data: `Any`
    :param full_path: The original path containing placeholders
    :type full_path: `str`
    :param key: The key within the full path to replace
    :type key: `str`
    :param result: The mapped data
    :type result: `dict`[`str`, `Any`]
    """
    value_path = full_path.replace(key, _get_value_path(field_config, index))
    value_type = _get_value_type(field_config)
    _add_or_append_value(
        field_name, flattened_data[value_path], result, value_type
    )


def _update_cache(
    cache_entry: dict[str, Any],
    flattened_data: dict[str, str],
    full_path: str,
) -> None:
    """Function to update the cache.

    :param cache_entry: The current entry within the cache
    :type cache_entry: `dict`[str, `Any`]
    :param flattened_data: JSON data as a flattened dictionary
    :type flattened_data: `Any`
    :param full_path: The path to update within the cache
    :type full_path: `str`
    """
    cache_entry[flattened_data[full_path]] = full_path
    cache_entry["count"] += 1


def _handle_regular_path(
    field_name: str,
    field_config: FieldSpec,
    full_path: str,
    flattened_data: Any,
    result: dict[str, Any],
    header_dict: dict[str, Any],
) -> None:
    """
    Function that handles regular paths without empty segments.

    :param field_name: The field name within the mapping config
    :type field_name: `str`
    :param field_config: The config for the field name
    :type field_config: :class: `FieldSpec`
    :param full_path: The key of the flattened data
    :type full_path: `str`
    :param flattened_data: JSON data as a flattened dictionary
    :type flattened_data: `Any`
    :param result: The mapped data
    :type result: `dict`[`str`, `Any`]
    :param header_dict: A dictionary of flattened json data containing header
    data
    :type header_dict: `dict`[`str`, `Any`]
    """
    try:
        if full_path.split(":")[0] == "HEADER":
            # Remove 'HEADER:' from full_path
            full_path = "".join(full_path.split("HEADER:")[1:])
            value_type = _get_value_type(field_config)
            value = header_dict[full_path]
            _add_or_append_value(field_name, value, result, value_type)
            return

        flattened_data = dict(flattened_data)
        if flattened_data[full_path]:
            value_type = _get_value_type(field_config)
            _add_or_append_value(
                field_name, flattened_data[full_path], result, value_type
            )
            return
    except KeyError:
        # Check if we are dealing with a list like child_span_ids.
        count = 0
        full_path = full_path + ":" + str(count)
        # Continue whilst valid keys are found within flattened_data
        while flattened_data.get(full_path):
            value_type = _get_value_type(field_config)
            # Create a list to append values to
            if field_name not in result:
                result[field_name] = []
            result[field_name].append(flattened_data.get(full_path))
            # Increment the index within full path
            full_path = full_path.replace(f":{str(count)}", f":{str(count+1)}")
            count += 1
    except Exception as e:
        print(f"An error occurred - {e}")


def _get_value_type(field_config: FieldSpec) -> str:
    """Function that returns the type of the field. Eg. "string", "unix_nano"

    :param field_config: The config for the field name
    :type field_config: :class: `FieldSpec`
    :return: The field type
    :rtype: `str`
    """
    expected_value_types = ["unix_nano", "string"]
    try:
        value_type = field_config["value_type"]
    except KeyError:
        raise KeyError("Field config must include a 'value_type' section.")

    if not isinstance(value_type, str):
        raise TypeError(
            f"value_type should be a string, got '{type(value_type)}' instead."
        )

    if value_type not in expected_value_types:
        raise ValueError(
            "Supported value types include "
            f"'{','.join(expected_value_types)}', got '{value_type}' instead."
        )
    return value_type


def _add_or_append_value(
    field_name: str, value: str | int, result: dict[str, Any], value_type: str
) -> None:
    """
    Function that adds a new value or appends to an existing one in the result
    dictionary.

    :param field_name: The field name within the mapping config
    :type field_name: `str`
    :param value: The value pulled from the JSON data
    :type value: `str` | `int`
    :param result: The mapped data
    :type result: `dict`[`str`, `Any`]
    :param value_type: The field type
    :type value_type: `str`
    """
    if value_type == "unix_nano":
        if not isinstance(value, int):
            raise TypeError(
                f"Datetime should be of type 'int', got '{type(value)}'."
            )
    else:
        if not isinstance(value, str):
            value = str(value)

    if field_name not in result:
        result[field_name] = value
    else:
        result[field_name] += f" {value}"


def flatten_and_map_data(
    json_config: JSONDataSourceConfig,
    raw_json: dict[str, Any],
    header_dict: dict[str, Any],
) -> dict[str, str]:
    """Function to handle flattening raw json and mapping the data to the
    specified configuration.

    :param json_config: The json config
    :type json_config: :class: `JSONDataSourceConfig`
    :param raw_json: The JSON data to flatten.
    :param raw_json: `dict`[`str`,`Any`]
    :param header_dict: Dictionary containing information about header values
    :type header_dict: `dict`[`str`, `Any`]
    :return: The mapped data
    :rtype: `dict`[`str`, `str`]
    """
    flattened_data = _flatten_json_dict(raw_json)
    return _map_data_to_json_schema(
        json_config, flattened_data, "field_mapping", header_dict
    )


def process_header(
    json_config: JSONDataSourceConfig, json_data: dict[str, Any]
) -> dict[str, Any]:
    """Process the header within the json data.

    :param json_config: The json config
    :type json_config: :class:`JSONDataSourceConfig`
    :param json_data: The JSON data to flatten.
    :type json_data: `dict`[`str`, `Any`]
    :return: A dictionary mapping header paths to a value of a flattened dict
    or a string
    :rtype: `dict`[`str`, `Any`]
    """
    header_dict: dict[str, Any] = {}

    for path in json_config["header"]["paths"]:
        value = _extract_value_from_path(json_data, path)
        _update_header_dict(header_dict, path, value)

    return header_dict


def _extract_value_from_path(
    data: dict[str, Any], path: str
) -> dict[str, Any] | str | list[dict[str, Any]]:
    """Extract a value from nested JSON data using a path string.

    :param data: The JSON data to traverse
    :type data: `dict`[`str`, `Any`]
    :param path: The path string to follow
    :type path: `str`
    :return: The extracted value
    :rtype: `dict`[`str`, `Any`] | `str` | `list`[`dict`[`str`, `Any`]]
    """
    if "::" in path:
        return _extract_nested_value(data, path)
    else:
        return _extract_simple_value(data, path)


def _extract_nested_value(data: dict[str, Any], path: str) -> dict[str, Any]:
    """Extract a nested value from JSON data using a complex path.

    :param data: The JSON data to traverse
    :type data: `dict`[`str`, `Any`]
    :param path: The complex path string
    :type path: `str`
    :return: A nested dictionary with the extracted value
    :rtype: `dict`[`str`, `Any`]
    """
    path_segments = path.split(":")
    parsed_data: dict[str, Any] | str | list[dict[str, Any]] = data
    for segment in path_segments:
        if isinstance(parsed_data, dict):
            parsed_data = _navigate_dict(parsed_data, segment)
        elif isinstance(parsed_data, list):
            parsed_data = _navigate_list(parsed_data)

    path_segments = ":".join(path_segments).split("::")

    return _build_nested_dict(path_segments, parsed_data)


def _build_nested_dict(
    path_segments: list[str],
    parsed_data: dict[str, Any] | str | list[dict[str, Any]],
) -> dict[str, Any]:
    """Generates a nested dictionary by building it from the inside out.

    :param path_segments: The segments within the path, split by ::
    :type path_segments: `list`[`str`]
    :param parsed_data: The parsed data within the json
    :type parsed_data: `dict`[`str`, `Any`] | `str` |
    `list`[`dict`[`str`, `Any`]]
    :return: The nested dictionary
    :rtype: `dict`[`str`, `Any`]
    """
    result = parsed_data
    for key in reversed(path_segments[1:]):
        result = {key: result}

    if isinstance(result, dict):
        return result
    else:
        raise TypeError(f"Expected type dict, got {type(result)} instead.")


def _extract_simple_value(
    data: dict[str, Any], path: str
) -> dict[str, Any] | str | list[dict[str, Any]]:
    """Extract a simple value from JSON data using a path.

    :param data: The JSON data to traverse
    :type data: `dict`[`str`, `Any`]
    :param path: The simple path string
    :type path: `str`
    :return: The extracted value
    :rtype: `dict`[`str`, `Any`] | `str` | `list`[`dict`[`str`, `Any`]]
    """
    parsed_data: dict[str, Any] | str | list[dict[str, Any]] = data
    segments = path.split(":")
    for segment in segments:
        if isinstance(parsed_data, dict):
            parsed_data = _navigate_dict(parsed_data, segment)

    return parsed_data


def _navigate_dict(
    data: dict[str, Any], segment: str
) -> dict[str, Any] | str | list[dict[str, Any]]:
    """Navigate through a dictionary of the JSON data.

    :param data: The current data object
    :type data: `dict`[`str`, `Any`]
    :param segment: The segment to navigate
    :type segment: `str`
    :return: The value at the end of the navigation
    :rtype: `dict`[`str`, `Any`] | `str` | `list`[`dict`[`str`, `Any`]]
    """
    try:
        data_to_return = data[segment]
        if isinstance(data_to_return, (dict, list, str)):
            return data_to_return
        else:
            raise TypeError(
                "Error navigating header - value should be of type dict,"
                f" list or str - got {type(data[segment])} instead."
            )
    except KeyError:
        raise KeyError(f"{segment} is not a valid key.")


def _navigate_list(
    data: list[dict[str, Any]],
) -> dict[str, Any]:
    """Navigate through a list of the JSON data.

    :param data: The current data object
    :type data: `list`[`dict`[`str`, `Any`]]
    :return: The value at index 0 of the list
    :rtype: `dict`[`str`, `Any`]
    """
    if not data:
        raise IndexError("Cannot return a value for an empty list.")

    if len(data) > 1:
        raise ValueError(
            "Code is structured to process lists that have one item. "
            f"Got {len(data)} items instead."
        )

    return data[0]


def _update_header_dict(
    header_dict: dict[str, Any],
    path: str,
    value: dict[str, Any] | str | list[dict[str, Any]],
) -> None:
    """Updates the header dictionary with the extracted value. If the value is
    a dictionary or list, flatten it first.

    :param header_dict: The header dictionary to update
    :type header_dict: `dict`[`str`, `Any`]
    :param path: The original path string
    :type path: `str`
    :param value: The value to add to header_dict
    :type value: `dict`[`str`, `Any`] | `str` | `list`[`dict`[`str`, `Any`]]
    """
    key = path.split("::")[0]
    if isinstance(value, (dict, list)):
        header_dict[key] = _flatten_json_dict(value)
    else:
        header_dict[key] = value


def process_spans(
    json_config: JSONDataSourceConfig, json_data: dict[str, Any]
) -> list[dict[str, Any]]:
    """Process the spans within the json data.

    :param json_config: The json config
    :type json_config: :class: `JSONDataSourceConfig`
    :param json_data: The JSON data containing the spans
    :param json_data: `dict`[`str`,`Any`]
    return: A list of spans
    :rtype: `list`[`dict`[`str`, `Any`]]
    """

    path_segments = json_config["span_mapping"]["spans"]["key_paths"][0].split(
        ":"
    )

    data = json_data
    for segment in path_segments:
        if segment == "":
            if isinstance(data, list):
                if len(data) > 1:
                    raise ValueError(
                        "Code is structured to process lists that have one"
                        f" item. Got {len(data)} items instead."
                    )
                data = data[0]
            else:
                raise TypeError("Sub segment should be a list.")
            continue

        data = data[segment]

    if isinstance(data, list):
        if not data:
            LOGGER.warning(
                "Encountered an empty list whilst processing spans."
            )
        return data
    else:
        raise TypeError("Spans should be within a list.")


def _get_key_value(field_spec: FieldSpec, index: int) -> str:
    """Helper function to get key value within field spec mapping.

    :param field_spec: The field spec specified in the config file
    :type field_spec: :class: `FieldSpec`
    :param index: The index within the key_value list
    :type index: `int`
    :return: The value within the key_value list, or None
    :rtype: `str` | `None`
    """
    try:
        key_values = field_spec["key_value"]
    except KeyError:
        raise KeyError("key_value field not set.")

    try:
        key_value = key_values[index]
    except IndexError:
        raise IndexError(f"Index {index} is out of range for key_value.")

    if not key_value:
        raise ValueError(f"key_value at index {index} should not return None.")

    return key_value


def _get_value_path(field_spec: FieldSpec, index: int) -> str:
    """Helper function to get value path within field spec mapping.

    :param field_spec: The field spec specified in the config file
    :type field_spec: :class: `FieldSpec`
    :param index: The index within the value_paths list
    :type index: `int`
    :return: The value within the value_paths list, or None
    :rtype: `str`
    """
    try:
        value_paths = field_spec["value_paths"]
    except KeyError:
        raise KeyError("value_paths field not set.")

    try:
        value_path = value_paths[index]
    except IndexError:
        raise IndexError(f"Index {index} is out of range for value_paths.")

    if not value_path:
        raise ValueError(f"value_path at index {index} is empty or None.")

    return value_path
