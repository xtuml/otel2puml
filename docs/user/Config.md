# OTel to PUML Config file
# ========================

This file details the configuration options for the ingestion and sequencing of data for the OTel to PUML converter.

## Configuration File Format
The configuration file is provided as a yaml file. The configuration file is divided into four sections: 
* `ingest_data`
* `data_holders`
* `data_sources`
* `sequencer`

An example configuration file is provided below:

```yaml

ingest_data:
    data_source: json
    data_holder: sql
data_holders:
    sql:
        db_uri: 'sqlite:///:memory:'
        batch_size: 5
        time_buffer: 30
data_sources:
    json:
        dirpath: /path/to/json/directory
        filepath: /path/to/json/file.json
        json_per_line: false
        field_mapping: <field mapping config>
sequencer: <sequencer config>
```

## Configuration Options

### `ingest_data`
This section contains the configuration for the ingestion of data. The following options are available:
* `data_source`: The data source to use for the ingestion of data. This should be one of the keys in the `data_sources` section. Currently, only `json` is supported and any other value will result in an error.
* `data_holder`: The data holder to use for the storage of data. This should be one of the keys in the `data_holders` section. Currently, only `sql` is supported and any other value will result in an error.

### `data_holders`
This section contains the configuration for the data holders. The following options are available:
* `sql`: The configuration for the SQL data holder. The following options are available:
    * `db_uri`: The URI for the database to use. This should be a valid SQLAlchemy URI. The default value is `sqlite:///:memory:`.
    * `batch_size`: The number of events to add to the database in a single batch. The default value is `5`.
    * `time_buffer`: The time buffer in minutes to use when processing events. The default value is `30`. This value creates a time buffer around the data ingestion period. It removes traces that contain spans that fall entirely outside this buffer. For example, if all data is ingested between 100 and 1000 minutes, and the time buffer is 10 minutes, the system will remove any traces with spans that are completely outside the 110 to 990 minutes range.

### `data_sources`
This section contains the configuration for the data sources. The following options are available:
* `json`: The configuration for the JSON data source. The following options are available:
    * `dirpath`: The path to the directory containing the JSON files. This is required if `filepath` is not provided.
    * `filepath`: The path to the JSON file. This is required if `dirpath` is not provided.
    * `json_per_line`: A boolean value indicating whether each line in the JSON file is a separate JSON object. The default value is `false`.
    * `field_mapping`: The field mapping configuration. The details of how this is used can be found in the [JSON Data Converter HOW TO](/docs/user/json_data_converter_HOWTO.md) section. This is required is `jq_query` is not provided and cannot be used in conjunction with `jq_query`.
    * `jq_query`: A jq query to use to extract the data from the JSON file. This is required if `field_mapping` is not provided and cannot be used in conjunction with `field_mapping`. The jq query should return objects representing single events ([OTel Event](/docs/user/json_data_converter_HOWTO.md#1-introduction)). JQ usage can be found at https://jqlang.github.io/jq/.

### `sequencer`
This option is not required and can be omitted if the sequencer is not being used or synchronous sequencing is being used.

Information on the sequencer configuration can be found in the [Sequencer HOW TO](/docs/user/sequencer_HOWTO.md) section.

