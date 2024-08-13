"""This module converts JSON OTel data to adhere to the application schema."""

import flatdict
from typing import Any, Literal
from datetime import datetime

from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    JSONDataSourceConfig,
)

MAX_SEGMENT_COUNT = 50  # TODO have a think about this


def _flatten_json_dict(json_data: dict[str, Any]) -> Any:
    """Function to flatten a nested dictionary.

    :param json_data: The JSON data to flatten.
    :param json_data: `dict`[`str`,`Any`]
    :return: The flattened json as a dictionary
    :rtype: `Any`
    """
    return flatdict.FlatterDict(json_data)


def _map_data_to_json_schema(
    json_config: JSONDataSourceConfig,
    flattened_data: Any,
    config_key: Literal["header_mapping", "field_mapping"],
) -> dict[str, str]:
    """
    Function that maps flattened JSON data to a schema defined in the
    json_config.

    :param json_config: The mapping config pulled from the yaml config file
    :type json_config: :class:`JSONDataSourceConfig`
    :param flattened_data: JSON data as a flattened dictionary
    :type flattened_data: `Any`
    :param config_key: The key for the json config fields
    :type config_key: `Literal`["header_mapping", "field_mapping"]
    :return: The mapped data
    :rtype: `dict`[`str`, `str`]
    """
    result: dict[str, str] = {}
    field_mapping: dict[str, Any] = json_config[config_key]
    # Cache results within lists to avoid looping over them again
    field_cache: dict[str, str] = {}
    for field_name, field_config in field_mapping.items():
        _process_field(
            field_name, field_config, flattened_data, result, field_cache
        )
    return result


def _process_field(
    field_name: str,
    field_config: dict[str, Any],
    flattened_data: Any,
    result: dict[str, str],
    field_cache: dict[str, str],
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
    :param field_cache: Cache for optimising field access and path generation
    in flattened JSON data
    :type field_cache: `dict`[`str`, [`str`]]
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
            )
        else:
            full_path = ":".join(path_segments)
            _handle_regular_path(
                field_name,
                field_config,
                full_path,
                flattened_data,
                result,
            )


def _handle_empty_segments(
    field_name: str,
    field_config: dict[str, Any],
    flattened_data: Any,
    index: int,
    result: dict[str, str],
    field_cache: dict[str, str],
    field_cache_key: str,
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
    :param field_cache: Cache for optimising field access and path generation
    in flattened JSON data
    :type field_cache: `dict`[`str`, [`str`]]
    :param field_cache_key: The key of the field cache
    :type field_cache_key: `str`
    """
    full_path = ":".join(field_config["key_paths"][index].split(":"))
    key = full_path.split("::")[-1]

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
            if not field_config.get("key_value") and flattened_data.get(
                full_path
            ):
                result[field_name] = flattened_data.get(full_path)
                return

            # Check the cache to see if the value that we are looking for has 
            # already been looped over and stored.
            # If the value is not found within the cache, we start looking at
            # the value of 'count' that is stored within the cache, as we have
            # already checked values up until count - 1.
            value_to_check = field_config["key_value"][index]
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
            # we try accessing a key within the dictionary that doesn't exist.
            cache_entry["count"] += 1
        except Exception as e:
            print(f"An error occured - {e}")

    raise RuntimeError(
        f"Could not find data for '{field_name}' within {MAX_SEGMENT_COUNT}"
        " segments"
    )


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
    field_config: dict[str, Any],
    index: int,
    flattened_data: dict[str, Any],
    full_path: str,
    key: str,
    result: dict[str, str],
) -> None:
    """Function to process data that matches the search requirements. The
    result is either added as a new value or appended to an existing one.

    :param field_name: The field name within the mapping config
    :type field_name: `str`
    :param field_config: The config for the field name
    :type field_config: `dict`[`str`,`Any`]
    :param index: The index of the field config
    :type index: `int`
    :param flattened_data: JSON data as a flattened dictionary
    :type flattened_data: `Any`
    :param full_path: The original path containing placeholders
    :type full_path: `str`
    :param key: The key within the full path to replace
    :type key: `str`
    :param result: The mapped data
    :type result: `dict`[`str`, `str`]
    """
    value_path = full_path.replace(key, field_config["value_paths"][index])
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
    field_config: dict[str, Any],
    full_path: str,
    flattened_data: Any,
    result: dict[str, Any],
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
    :type result: `dict`[`str`, `Any`]
    """
    try:
        flattened_data = dict(flattened_data)
        if flattened_data[full_path]:
            value_type = _get_value_type(field_config)
            _add_or_append_value(
                field_name, flattened_data[full_path], result, value_type
            )
    except KeyError:
        # Check if we are dealing with a list like child_span_ids
        count = 0
        full_path = full_path + ":" + str(count)
        while flattened_data.get(full_path):
            value_type = _get_value_type(field_config)
            if field_name not in result:
                result[field_name] = []
            result[field_name].append(flattened_data.get(full_path))
            full_path = full_path.replace(f":{str(count)}", f":{str(count+1)}")
            count += 1
    except Exception as e:
        print(f"An error occurred - {e}")


def _get_value_type(field_config: dict[str, str]) -> str:
    """Function that returns the type of the field. Eg. "string", "unix_nano"

    :param field_config: The config for the field name
    :type field_config: `dict`[`str`,`Any`]
    :return: The field type
    :rtype: `str`
    """
    return field_config["value_type"]


def _add_or_append_value(
    field_name: str, value: str | int, result: dict[str, str], value_type: str
) -> None:
    """
    Function that adds a new value or appends to an existing one in the result
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
            value = _unix_nano_to_datetime_str(value)
    if not isinstance(value, str):
        value = str(value)
    if field_name not in result:
        result[field_name] = value
    else:
        result[field_name] += f" {value}"


def _unix_nano_to_datetime_str(unix_nano: int) -> str:
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
    :param raw_json: The JSON data to flatten.
    :param raw_json: `dict`[`str`,`Any`]
    return: The mapped data
    :rtype: `dict`[`str`, `str`]
    """
    flattened_data = _flatten_json_dict(raw_json)
    return _map_data_to_json_schema(
        json_config, flattened_data, "field_mapping"
    )


def process_header(
    json_config: JSONDataSourceConfig, json_data: dict[str, Any]
) -> str:
    """Process the header within the json data.

    :param json_config: The json config
    :type json_config: :class: `JSONDataSourceConfig`
    :param json_data: The JSON data to flatten.
    :param json_data: `dict`[`str`,`Any`]
    return: The header
    :rtype: `str`
    """
    return _map_data_to_json_schema(
        json_config, _flatten_json_dict(json_data), "header_mapping"
    )["header"]


def process_spans(
    json_config: JSONDataSourceConfig, json_data: dict[str, Any]
) -> list[dict[str, Any]]:
    """Process the spans within the json data.

    :param json_config: The json config
    :type json_config: :class: `JSONDataSourceConfig`
    :param json_data: The JSON data to flatten.
    :param json_data: `dict`[`str`,`Any`]
    return: A list of spans
    :rtype: `list`[`dict`[`str`, `Any`]]
    """

    path_segments = json_config["span_mapping"]["spans"]["key_paths"][0].split(
        ":"
    )

    data = json_data
    found_sub_segment = False
    for segment in path_segments:
        if segment == "":
            found_sub_segment = True
            if isinstance(data, list):
                data = data[0]
            else:
                raise TypeError("Sub segment should be a list.")
            continue
        if found_sub_segment:
            data = data[segment]
            continue

        data = data[segment]

    if isinstance(data, list):
        return data
    else:
        raise TypeError("Spans should be within a list.")
