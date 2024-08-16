# Configuring tel2puml/find_unique_graphs

## Table of Contents
1. Introduction
2. Configuration File Structure
3. Understanding Configuration Settings
   3.1 Path Structure Explanation 
   3.2 data_location
   3.3 header
   3.4 span_mapping
   3.5 field_mapping
   3.6 value_type attribute
4. Detailed Examples
   4.1 Simple span attribute
   4.2 Referencing a header attribute
   4.3 Complex field mapping
6. Troubleshooting
7. Conclusion and Next Steps

# 1.0 Introduction
This guide will walk you through the process of configuring json_data_converter to correctly parse your JSON telemetry data and map it to the required output format.


## 2.0 Configuration File Structure

The configuration for tel2puml/find_unique_graphs is defined in a YAML file named `config.yaml`. This file specifies how to locate and interpret your telemetry data. Here's the basic structure:

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

## 3.0 Understanding Configuration Settings

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
The `data_location` field specifies where the main data array/object is located in your JSON structure. This is typically the root of your telemetry data.

Example:
```yaml
data_location: resource_spans
```

### 3.3 header
The header section defines paths to important metadata that applies to all spans within a group. It uses a list of paths to locate this information:

```yaml
header:
    paths: [resource:attributes, scope_spans::scope:name] 
```
* resource:attributes - Metadata about the resource (e.g., service name and version)
* scope_spans::scope:name - The name of the scope for the spans

This header information can be referenced in the field_mapping section using the `HEADER:` prefix. 

### 3.4 span_mapping

The span_mapping section defines where to find the individual span data within the JSON structure. In this configuration:

```yaml
span_mapping:
  spans:
    key_paths: [scope_spans::spans]
```

This indicates that the span data is located in the "spans" array within the "scope_spans" array.

NB. spans must always be located within an array, or an error will be thrown.

### 3.5 field_mapping

The `field_mapping` section is the core of the configuration, defining how to map fields from the input JSON to your desired output structure. Each field in your target schema is defined here. For example:

```yaml
field_mapping:
    event_type:
        key_paths: [attributes::key, attributes::key]
        key_value: [http.method, http.response]
        value_paths: [value:Value:StringValue, value:Value:IntValue]
        value_type: string
```

Returns "GET 200" from the JSON example.

#### The two required fields are `key_paths` and `value_type`.

This mapping for `event_type`:

1. Loops over two locations (using `key_paths`).

2. The key_path identifies the location of the nested key that will identify the value we are searching for.

3. If the `key_value` attribute is provided, that tells us the structure of the data looks like:

```json
{
    "key": "http.method",
    "value": {
        "Value": {
            "StringValue": "GET"
        }
    }
}
```
as opposed to:
```json
{
    "key": "value"
}
```


4. Checks if the `key`'s value matches `http.method` in the first path.

3. Retrieves the value from the specified `value_paths`. For the first path it's specified as `value:Value:StringValue`, giving us a value of "GET".

4. Defines the `value_type` as a `string`

5. Results of the second path are concatenated to the first, giving a final output of "GET 200".

Each field in the field_mapping section follows a similar structure, allowing you to precisely define how to extract and transform data from the input JSON to your desired output format.

When creating your configuration, ensure that each field mapping accurately reflects the structure of your input JSON and the requirements of your target schema.

### 3.6 value_type attribute
Currently the following two value types are supported
* string
* unix_nano (represents date in unix nano format eg. 1723544132228102912)

## 4.0 Examples

### Example 1: Simple span attribute

To extract `trace_id` we specify the following:

```yaml
job_id:
    key_paths: [trace_id]
    value_type: string
```

Note the fields `key_value` and `value_paths` are not required.

### Example 2: Referencing a header attribute

Given a header mapping of:

```yaml
header:
    paths: [resource:attributes] 
```

We are now able to access the following json that can be referenced within field_mapping:
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

If we wanted `application_name` to reference "Test App 1.0" we would specify the following config, that concatenates "Test App" with "1.0":

```yaml
application_name:
    key_paths: [HEADER:resource:attributes::key, HEADER:resource:attributes::key]
    key_value: [service.name, service.version]
    value_paths: [value:Value:StringValue, value:Value:StringValue]
    value_type: string
```

### Example 3: Complex field mapping

For more complex scenarios, like concatenating multiple values:

```yaml
event_type:
    key_paths: [attributes::key, attributes::key]
    key_value: [http.method, http.response]
    value_paths: [value:Value:StringValue, value:Value:IntValue]
    value_type: string
```

## 5.0 Troubleshooting

Common issues and solutions:

#### Issue: Data not found at specified location. 
Solution: Double-check your JSON structure and ensure data_location is correct

#### Issue: Field mapping not extracting expected values
Solution: Verify the key_paths, key_value, and value_paths in your field mapping

#### Issue: Incorrect data types
Solution: Ensure value_type is set correctly (either string or unix_nano)

#### Issue: Header information not accessible
Solution: Check that header paths are correctly specified and prefixed with HEADER: in field mappings