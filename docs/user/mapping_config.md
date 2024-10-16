# OTel to PUML Mapping Config file
# ========================

The `tel2puml` tool allows a custom mapping configuration file to be specified using the `--mapping-config` or `-mc` flag. This mapping configuration file maps application-specific data fields to the corresponding fields in the `PVEvent` object, ensuring that the conversion process correctly translates the data.

## Example Mapping Configuration (`mapping_config.yaml`)

A typical `mapping_config.yaml` file would look like this:

```yaml
# Configuration file for mapping application data to user data for PVEvent objects.
jobId: jobIdNew
eventId: eventIdNew
timestamp: timestampNew
previousEventIds: previousEventIdsNew
applicationName: applicationNameNew
jobName: jobNameNew
eventType: eventTypeNew
```

Each key in the configuration file represents a field in the PVEvent object, and its value represents the corresponding key in the application data.

## When to Use a Custom Mapping Configuration

A custom `mapping_config.yaml` file is used when the structure of the data does not match the default `PVEvent` schema. Defining a custom mapping ensures that data fields are correctly translated into the required format for generating PlantUML diagrams or PV formats.

## Default Behaviour Without a Mapping Configuration

If no mapping configuration file is provided, `tel2puml` uses its default internal mappings for the `PVEvent` object. A custom mapping configuration is only necessary when the data structure deviates from the default schema.

## Example of Custom Mapping Configuration

In cases where application data fields do not match the default field names used in `PVEvent`, a custom mapping configuration can be defined. For instance, consider the following data structure for an event:

```json
{
    "job_identifier": "1234",
    "event_identifier": "abcd-efgh",
    "time_of_event": "2023-10-15T12:34:56Z",
    "previous_event_ids": ["prev-123"],
    "app_name": "my_application",
    "job_name": "test_job",
    "type_of_event": "A"
}
```

In this example, the default `PVEvent` field names such as `jobId`, `eventId`, and `timestamp` do not align with the application data field names. To handle this, a custom mapping_config.yaml file can be created to map the application fields to the corresponding `PVEvent` fields:

```yaml
# Custom mapping_config.yaml
jobId: job_identifier
eventId: event_identifier
timestamp: time_of_event
previousEventIds: previous_event_ids
applicationName: app_name
jobName: job_name
eventType: type_of_event
```
