# Configuring tel2puml/find_unique_graphs

## Table of Contents
<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#1-introduction">Introduction</a></li>
    <li><a href="#2-configuration-file-structure">Configuration File Structure</a></li>
    <li><a href="#3-understanding-configuration-settings">Understanding Configuration Settings</a>
      <ol>
        <li><a href="#31-understanding-the-path-structure">Understanding the path structure</a></li>
        <li><a href="#32-data_location">data_location</a></li>
        <li><a href="#33-header">header</a></li>
        <li><a href="#34-span_mapping">span_mapping</a></li>
        <li><a href="#35-field_mapping">field_mapping</a></li>
        <li><a href="#36-value_type-attribute">value_type attribute</a></li>
      </ol>
    </li>
    <li><a href="#4-examples">Examples</a>
      <ol>
        <li><a href="#example-1-simple-field-mapping">Simple field mapping</a></li>
        <li><a href="#example-2-referencing-a-header-attribute">Referencing a header attribute</a></li>
        <li><a href="#example-3-complex-field-mapping">Complex field mapping</a></li>
      </ol>
    </li>
    <li><a href="#5-troubleshooting">5.0 Troubleshooting</a></li>
  </ol>
</details>



## 1. Introduction
This document is a guide to configure json_data_converter to correctly parse JSON telemetry data and map it to the application schema used internally. The internal schema is detailed below for context:

```python
class OTelEvent(NamedTuple):
    """Named tuple for OTel event.

    :param job_name: The name of the job.
    :type job_name: `str`
    :param job_id: The ID of the job.
    :type job_id: `str`
    :param event_type: The type of the event.
    :type event_type: `str`
    :param event_id: The ID of the event.
    :type event_id: `str`
    :param start_timestamp: The start timestamp of the event.
    :type start_timestamp: `str`
    :param end_timestamp: The end timestamp of the event.
    :type end_timestamp: `str`
    :param application_name: The application name.
    :type application_name: `str`
    :param parent_event_id: The ID of the parent event.
    :type parent_event_id: `Optional`[`str`]
    :param child_event_ids: A list of IDs of child events. Defaults to `None`
    :type child_event_ids: Optional[`list`[`str`]]
    """

    job_name: str
    job_id: str
    event_type: str
    event_id: str
    start_timestamp: str
    end_timestamp: str
    application_name: str
    parent_event_id: Optional[str]
    child_event_ids: Optional[list[str]] = None
```


## 2. Configuration File Structure

The configuration for tel2puml/find_unique_graphs is defined in `config.yaml`. This file specifies how to locate and interpret JSON telemetry data. See below for the basic structure:

```yaml
data_sources:
    json:
        dirpath: path/to/json/directory
        filepath: path/to/json/file
        data_location: 
        header:
            paths: [] 
        span_mapping:
            spans:
                key_paths: []
        field_mapping:
            job_name:
                key_paths: []
                key_value: []
                value_paths: []
                value_type:
            job_id:
            event_type:
            event_id:
            start_timestamp:
            end_timestamp:
            application_name:
            parent_event_id:
            child_event_ids:
```

## 3. Understanding Configuration Settings

### JSON Example
The following JSON data will be used within the examples below:

```json
{
    "resource_spans": [
        {
            "resource": {
                "attributes": [
                    {
                        "key": "service.name",
                        "value": {
                            "Value": {
                                "StringValue": "Test App"
                            }
                        }
                    },
                    {
                        "key": "service.version",
                        "value": {
                            "Value": {
                                "StringValue": "1.0"
                            }
                        }
                    }
                ]
            },
            "scope_spans": [
                {
                    "scope": {
                        "name": "Group 1"
                    },
                    "spans": [
                        {
                            "trace_id": "trace001",
                            "span_id": "span001",
                            "parent_span_id": null,
                            "name": "/delete",
                            "start_time_unix_nano": 1723544132228102912,
                            "end_time_unix_nano": 1723544132228219285,
                            "attributes": [
                                {
                                    "key": "http.method",
                                    "value": {
                                        "Value": {
                                            "StringValue": "GET"
                                        }
                                    }
                                },
                                {
                                    "key": "http.host",
                                    "value": {
                                        "Value": {
                                            "StringValue": "Render"
                                        }
                                    }
                                },
                                {
                                    "key": "http.response",
                                    "value": {
                                        "Value": {
                                            "IntValue": "200"
                                        }
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}
```

### 3.1 Understanding the path structure
Simply, a nested object is represented by a `:`, and an array is represented by a `::`.

For example `resource:attributes`, `attributes` is a key within the `resource` object.

Conversely with `scope_spans::scope:name`, `scope_spans` is an array, so `::` is used to indicate that `scope` is a key within that array. `name` is a key within the `scope` object, so it is separated by `:`.

### 3.2 data_location
The `data_location` field specifies where the main data array/object is located in the JSON structure. This is typically at the root of the telemetry data.

For the [JSON example](#json-example), the main data array is located within `scope_spans`:
```yaml
data_location: resource_spans
```

### 3.3 header
The header section defines paths to important metadata that applies to all spans within a group. It comprises of a list of paths:

For the [JSON example](#json-example), the following config could be set:

```yaml
header:
    paths: [resource:attributes, scope_spans::scope:name] 
```
* resource:attributes gives access to the following json:

```json
{"resource": {
        "attributes": [
            {
                "key": "service.name",
                "value": {
                    "Value": {
                        "StringValue": "Test App"
                    }
                }
            },
            {
                "key": "service.version",
                "value": {
                    "Value": {
                        "StringValue": "1.0"
                    }
                }
            }
        ]
    }
}
```


* scope_spans::scope:name gives access to the following json:

```json
{"scope_spans": [
        {
            "scope": {
                "name": "Group 1"
            }
        }
    ]
}
```

This header information can now be referenced in the field_mapping section using the `HEADER:` prefix.

For example, to reference "Group 1" within a field_mapping path and map it to `job_name`, specify the following
```yaml
job_name:
    key_paths: [HEADER:scope_spans::scope:name]
    value_type: string
```

### 3.4 span_mapping

The span_mapping section defines where to find the individual span data within the JSON structure. In this configuration for the [JSON example](#json-example):

```yaml
span_mapping:
  spans:
    key_paths: [scope_spans::spans]
```

This indicates that the span data is located in the "spans" array within the "scope_spans" array.

NB. spans must always be located within an array, or an error will be thrown.

### 3.5 field_mapping

The `field_mapping` section is the core of the configuration, defining how to map fields from the input JSON to the application schema. Each field in the application schema is defined here. For example:

```yaml
field_mapping:
    event_type:
        key_paths: [attributes::key]
        key_value: [http.method]
        value_paths: [value:Value:StringValue]
        value_type: string
```

This example would return `GET` from the [JSON example](#json-example).

#### Key Components:

Required Fields:

    key_paths: Specifies the path to the key in the JSON.
    value_type: Defines the data type of the value (e.g., string, unix_nano).

Optional Fields:

    key_value: Used when there are multiple key-value pairs.
    value_paths: Specifies the path to the value in the JSON.

#### How It Works:

1. The system follows the key_paths to find the relevant key in the JSON.
2. If key_value is provided, it checks if the key's value matches this value.
3. It then follows the value_paths to retrieve the actual value.
4. Finally, the specified value_type ensures the data is configured correctly.

#### JSON Structure

The optional fields are required when there are multiple key-value pairs, such as:

```json
{
    "attributes": [
        {
            "key": "http.method",
            "another-key":"another-value",
            "value": {
                "Value": {
                    "StringValue": "GET"
                }
            }
        }
    ]
}
```
As opposed to a singular key-value pair, such as:
```json
{
    "attributes": [
        {
            "trace_id": "001",
        }
    ]
}
```


### 3.6 value_type attribute
Currently the following two value types are supported:

* string
* unix_nano (represents date in unix nano format eg. 1723544132228102912)

## 4. Examples

### Example 1: Simple field mapping

To extract `trace_id` from the [JSON example](#json-example) and map it to `job_id`:

```yaml
job_id:
    key_paths: [trace_id]
    value_type: string
```

Note the fields `key_value` and `value_paths` are not required as trace_id is a singular key-value pair.

### Example 2: Referencing a header attribute

Given a header mapping within the [JSON example](#json-example):

```yaml
header:
    paths: [resource:attributes] 
```

The following json can now be referenced within field_mapping:
```json
{
    "resource": {
                "attributes": [
                    {
                        "key": "service.name",
                        "value": {
                            "Value": {
                                "StringValue": "Test App"
                            }
                        }
                    },
                    {
                        "key": "service.version",
                        "value": {
                            "Value": {
                                "StringValue": "1.0"
                            }
                        }
                    }
                ]
            }
}
```

To map `Test App` within the [JSON example](#json-example) to `application_name`:

```yaml
application_name:
    key_paths: [HEADER:resource:attributes::key]
    key_value: [service.name]
    value_paths: [value:Value:StringValue]
    value_type: string
```

### Example 3: Complex field mapping

For more complex scenarios, such as concatenating multiple values, paths and values are added to a list:

```yaml
event_type:
    key_paths: [attributes::key, attributes::key]
    key_value: [http.method, http.response]
    value_paths: [value:Value:StringValue, value:Value:IntValue]
    value_type: string
```

This will return `GET 200` from the [JSON example](#json-example) and map it to `event_type`.

## 5. Troubleshooting

Common issues and solutions:

#### Issue: Data not found at specified location. 
Solution: Double-check the JSON structure and ensure data_location is correct.

#### Issue: Field mapping not extracting expected values
Solution: Verify the key_paths, key_value, and value_paths within field mapping.

#### Issue: Incorrect data types
Solution: Ensure value_type is set correctly (either string or unix_nano).

#### Issue: Header information not accessible
Solution: Check that header paths are correctly specified and prefixed with `HEADER:` in field mappings.
