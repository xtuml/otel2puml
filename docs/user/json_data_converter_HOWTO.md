# Configuring JSON data extraction and mapping 

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
        <li><a href="#32-field_mapping">field_mapping</a></li>
        <li><a href="#33-value_type-attribute">value_type attribute</a></li>
      </ol>
    </li>
    <li><a href="#4-examples">Examples</a>
      <ol>
        <li><a href="#example-1-simple-field-mapping">Simple field mapping</a></li>
        <li><a href="#example-2-complex-field-mapping">Complex field mapping</a></li>
        <li><a href="#example-3-example-with-header-data">Example with header data</a></li>
        <li><a href="#example-4-example-for-obtaining-the-full-otelevent-schema-wihtout-child_event_ids">Example for obtaining the full OTelEvent schema (wihtout child_event_ids)</a></li>
      </ol>
    </li>
    <li><a href="#5-troubleshooting">5.0 Troubleshooting</a></li>
  </ol>
</details>



## 1. Introduction
This document is a guide to the configuration used to correctly parse JSON telemetry data and map it to the application schema used internally. The internal schema is detailed below for context:

```python
class OTelEvent(NamedTuple):

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

The idea is to extract records of this type from a JSON file and map the fields to the corresponding fields in the application schema. This is done by specifying the paths to the fields in the JSON file and the data types of the fields in the application schema.

The code used follows the jq language (https://jqlang.github.io/jq/) for JSON data extraction. The jq language is a lightweight and flexible command-line JSON processor. Within the configuration, the same pathing structure as jq is used to extract data from the JSON file.

## 2. Configuration File Structure
Configuration is provided to the application in the form of a YAML file (see [User Config](/docs/user/Config.md) for details on all configuration fields). 
This file specifies how to locate and interpret JSON telemetry data as part of the `data_sources` field that is used to ingest the raw Open Telemetry files. See below for the basic structure of the `data_sources.json` section of the file:

```yaml
data_sources:
    json:
        dirpath: path/to/json/directory
        filepath: path/to/json/file
        json_per_line: false
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
        jq_query: <jq_query>
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
                                    "key": "http.response",
                                    "value": {
                                        "Value": {
                                            "IntValue": "200"
                                        }
                                    }
                                }
                            ]
                        },
                        {
                            "trace_id": "trace002",
                            "span_id": "span002",
                            "name": "/put",
                            "start_time_unix_nano": 1723544132228102912,
                            "end_time_unix_nano": 1723544132228219285,
                            "attributes": [
                                {
                                    "key": "http.method",
                                    "value": {
                                        "Value": {
                                            "StringValue": "PUT"
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
Simply, a nested object is represented by a `.`, and an array is represented by a `.[].`. For example `resource.attributes`, `attributes` is a key within the `resource` object.

Conversely with `scope_spans.[].scope.name`, `scope_spans` is an array, so `.[].` is used to indicate that `scope` is a key within all the objects of that array. `name` is a key within the `scope` object, so it is separated by `.`.

Every object within an array will be flattened and treated separately. Nested arrays are then also flattened and treated separately. Using the JSON example above, we could have `resource_spans.[].scope_spans.[].spans.[].attributes.[].key` to access all the keys within the `attributes` array within the `spans` array within the `scope_spans` array within the `resource_spans` array which would provide the following exploded list of keys:

```json
["http.method", "http.response"]
```

Many different fields will be accessed this way and as such the pathing structure is crucial to correctly access the data. Each field must be consistent with all other fields in the configuration file. Consistency primarily depends upon the nesting of arrays in the path. 

With two field paths, if one accesses an object in a path three arrays deep and another accesses an object in a path in the same array then these will be consistent and each object will be matched at the same index in the array.
For example, the following two paths are consistent with each other, and each object in the `attributes` will then match the `key` object and the `value.Value` object:
 * `resource_spans.[].scope_spans.[].spans.[].attributes.[].key`
 * `resource_spans.[].scope_spans.[].spans.[].attributes.[].value.Value`

This produces the following exploded lists of keys for the first and second paths, respectively:
```json
["http.method", "http.response", "http.method", "http.response"]
[{"StringValue": "GET"}, {"IntValue": "200"}, {"StringValue": "PUT"}, {"IntValue": "200"}]
```

If one field path accesses an object in a path four levels deep and another field path accesses an object in a path three levels deep then the second field will be duplicated for each object in the fourth level array.
For example, the following two paths are consistent with each other and mean `.name` object will be duplicated across all the `.key` objects in the `attributes` array:
 * `resource_spans.[].scope_spans.[].spans.[].attributes.[].key`
 * `resource_spans.[].scope_spans.[].scope.name`

This produces the following exploded lists of keys for the first and second paths, respectively:
```json
["http.method", "http.response", "http.method", "http.response"]
["Group 1", "Group 1", "Group 1", "Group 1"]
```
### 3.2 field_mapping

The `field_mapping` section is the core of the configuration, defining how to map fields from the input JSON to the application schema. Each field in the application schema is defined here. For example:

```yaml
field_mapping:
    event_type:
        key_paths: [
            "resource_spans.[].scope_spans.[].spans.[].attributes.[].key"
        ]
        key_value: [http.method]
        value_paths: [value.Value.StringValue]
        value_type: string
```

This example would return `GET` for span with `span_id=span001` from the [JSON example](#json-example).

It should be noted that if a value in the `key_paths` field is a path that contains at least one array i.e. `.[].` is in the path, then that path must be surrounded by quoatation marks. This is necessary because the YAML file is processed the `[]` will be interpreted as a list and not as a string unless it is encapsulated in quotes that signal it part of a string.

#### Key Components:

Required Fields:

    key_paths: Specifies the path to the key in the JSON.
    value_type: Defines the data type of the value (e.g., string, int).

Optional Fields:

    key_value: Used when there are multiple key-value pairs.
    value_paths: Specifies the path to the value in the JSON (this must be a valid path in the object in the array).

#### How It Works:

1. The system follows the key_paths to find the relevant key in the JSON.
2. If key_value is provided, it checks if the key's value matches this value.
3. It then follows the value_paths to retrieve the actual value.
4. Finally, the specified value_type ensures the data is configured correctly.

#### JSON Structure

The optional fields are used when we want to access only one member of an array and need to identify it by a certain value e.g. below where maybe the user would like to grab the value `value.Value.StringValue` under the `key` equals `http.method`:

```json
{
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

```
So the user would specify the following in the `field_mapping`:
```yaml
field_mapping:
    event_type:
        key_paths: ["attributes.[].key"]
        key_value: [http.method]
        value_paths: [value.Value.StringValue]
        value_type: string
```
As opposed to a singular key-value pair, such as below where the user may want to grabbing all the `trace_id` values of objects in the array:
```json
{
    "attributes": [
        {
            "trace_id": "001",
        },
        {
            "trace_id": "002",
        }
    ]
}
```
the user would specify the following in the `field_mapping`:
```yaml
field_mapping:
    event_type:
        key_paths: ["attributes.[].trace_id"]
        value_type: string
```
#### Concatenation

If the user wants to concatenate multiple values, they can specify multiple key_paths, key_values, and value_paths. For example, if the user wants to concatenate the `name` value and `http.response` values (concatenated by an underscore in the order provided) from the [JSON example](#json-example) and map it to `event_type`:

```yaml
field_mapping:
    event_type:
        key_paths: [
            "resource_spans.[].scope_spans.[].spans.[].name",
            "resource_spans.[].scope_spans.[].spans.[].attributes.[].key"
        ]
        key_value: [null, http.response]
        value_paths: [null, value.Value.IntValue]
        value_type: string
```
This would return `/delete_200` for span with `span_id=span001` from the [JSON example](#json-example).

We must provide `null` in the `key_value` and `value_paths` if they are not required for that specific key_path.

#### Fallback priority values

In some cases, the user may want to provide a fallback value if the primary value is not found. This can be done by providing multiple key_paths (and key_values and value_paths if required) within an array (`[]`). The system will check the first key_path and if the key_value is not found, it will check the second key_path and so on. For example from the [JSON example](#json-example), if the user wishes to concatenate the `name` value with, in the first case the value of `not_here` (which doesn't exist) but fall back to `http.response` value and map it to `event_type`:

```yaml
field_mapping:
    event_type:
        key_paths: [
            "resource_spans.[].scope_spans.[].spans.[].name",
            [
                "resource_spans.[].scope_spans.[].spans.[].not_here", # this is not a valid path
                "resource_spans.[].scope_spans.[].spans.[].attributes.[].key" # this is the fallback path
            ]
        ]
        key_value: [null, [null, http.response]]
        value_paths: [null, [null, value.Value.IntValue]]
        value_type: string
```
As can be seen above the `key_paths` are given in concatenation order. Then for when priority values are to be used an array is used to specify the fallback values in order of priority. The `key_value` and `value_paths` are also given in the same order as the `key_paths` and the `null` values are used to indicate that the value is not required for that specific key_path in each array. So for:
* `resource_spans.[].scope_spans.[].spans.[].name` the `key_value` and `value_paths` are `null` as they are not required.
* the next concatenated key path value the priority values are:
    * `resource_spans.[].scope_spans.[].spans.[].not_here` the `key_value` is `null` and the `value_paths` is `null`.
    * `resource_spans.[].scope_spans.[].spans.[].attributes.[].key` the `key_value` is `http.response` and the `value_paths` is `value.Value.IntValue`.

### 3.6 value_type attribute
Currently the following single value type is supported:

* string

## 4. Examples

### Example 1: Simple field mapping

To extract `trace_id` from the [JSON example](#json-example) and map it to `job_id`:

```yaml
field_mapping:
    job_id:
        key_paths: ["resource_spans.[].scope_spans.[].spans.[].trace_id"]
        value_type: string
    event_id:
        key_paths: ["resource_spans.[].scope_spans.[].spans.[].span_id"]
        value_type: string
```

Note the fields `key_value` and `value_paths` as a specific object from an array is not required. This would then provide the following output records for the [JSON example](#json-example):
```json
{
    "job_id": "trace001",
    "event_id": "span001"
}
{
    "job_id": "trace002",
    "event_id": "span002"
}
```

### Example 2: Complex field mapping

For more complex scenarios, such as concatenating multiple values and having fallback values, paths and values are added to a list:

```yaml
field_mapping:
    event_type:
        key_paths: [
            "resource_spans.[].scope_spans.[].spans.[].name",
            [
                "resource_spans.[].scope_spans.[].spans.[].not_here", # this is not a valid path
                "resource_spans.[].scope_spans.[].spans.[].attributes.[].key" # this is the fallback path
            ]
        ]
        key_value: [null, [null, http.response]]
        value_paths: [null, [null, value.Value.IntValue]]
        value_type: string
    job_name:
        key_paths: ["resource_spans.[].resource.attributes.[].key"]
        key_value: [service.name]
        value_paths: [value.Value.StringValue]
        value_type: string
    event_id:
        key_paths: ["resource_spans.[].scope_spans.[].spans.[].span_id"]
        value_type: string
    start_timestamp:
        key_paths: [
            "resource_spans.[].scope_spans.[].spans.[].start_time_unix_nano"
        ]
        value_type: string
    end_timestamp:
        key_paths: [
            "resource_spans.[].scope_spans.[].spans.[].end_time_unix_nano"
        ]
        value_type: string
```

This will return the following output records for the [JSON example](#json-example):
```json
{
    "event_type": "/delete_200"
}
{
    "event_type": "/put_200"
}
``` 

### Example 3: Example with header data
In this example the user want to extract the field `job_name` that is a value in an array a few levels above the span records i.e. header information that will be applied to all the records extracted.

```yaml
field_mapping:
    job_name:
        key_paths: ["resource_spans.[].resource.attributes.[].key"]
        key_value: [service.name]
        value_paths: [value.Value.StringValue]
        value_type: string
    job_id:
        key_paths: ["resource_spans.[].scope_spans.[].spans.[].trace_id"]
        value_type: string
    event_id:
        key_paths: ["resource_spans.[].scope_spans.[].spans.[].span_id"]
        value_type: string
```

This will return the following output records for the [JSON example](#json-example):
```json
{
    "job_name": "Test App",
    "job_id": "trace001",
    "event_id": "span001"
}
{
    "job_name": "Test App",
    "job_id": "trace002",
    "event_id": "span002"
}
```

### Example 4: Example for obtaining the full OTelEvent schema (wihtout child_event_ids)
In this example the user wants to extract all the fields in the OTelEvent schema except for `child_event_ids` which is not present in the JSON data.

```yaml
field_mapping:
    job_name:
        key_paths: ["resource_spans.[].resource.attributes.[].key"]
        key_value: [service.name]
        value_paths: [value.Value.StringValue]
        value_type: string
    job_id:
        key_paths: ["resource_spans.[].scope_spans.[].spans.[].trace_id"]
        value_type: string
    event_type:
        key_paths: [
            "resource_spans.[].scope_spans.[].spans.[].name",
            [
                "resource_spans.[].scope_spans.[].spans.[].not_here", # this is not a valid path
                "resource_spans.[].scope_spans.[].spans.[].attributes.[].key" # this is the fallback path
            ]
        ]
        key_value: [null, [null, http.response]]
        value_paths: [null, [null, value.Value.IntValue]]
        value_type: string
    event_id:
        key_paths: ["resource_spans.[].scope_spans.[].spans.[].span_id"]
        value_type: string
    start_timestamp:
        key_paths: [
            "resource_spans.[].scope_spans.[].spans.[].start_time_unix_nano"
        ]
        value_type: string
    end_timestamp:
        key_paths: [
            "resource_spans.[].scope_spans.[].spans.[].end_time_unix_nano"
        ]
        value_type: string
    application_name:
        key_paths: ["resource_spans.[].scope_spans.[].scope.name"]
        value_type: string
    parent_event_id:
        key_paths: ["resource_spans.[].scope_spans.[].spans.[].parent_span_id"]
        value_type: string
```

This will return the following output records for the [JSON example](#json-example):
```json
{
    "job_name": "Test App",
    "job_id": "trace001",
    "event_type": "/delete_200",
    "event_id": "span001",
    "start_timestamp": "1723544132228102912",
    "end_timestamp": "1723544132228219285",
    "application_name": "Group 1",
    "parent_event_id": null
}
{
    "job_name": "Test App",
    "job_id": "trace002",
    "event_type": "/put_200",
    "event_id": "span002",
    "start_timestamp": "1723544132228102912",
    "end_timestamp": "1723544132228219285",
    "application_name": "Group 1",
    "parent_event_id": null
}
```
## 5. Troubleshooting

Common issues and solutions:

#### Issue: Field mapping not extracting expected values
Solution: Verify the key_paths, key_value, and value_paths within field mapping.

#### Issue: Incorrect data types
Solution: Ensure value_type is set correctly (`string`).
