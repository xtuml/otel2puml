"""Module to stream OTel data from a data source and store it within a
data holder."""

import yaml
from typing import Any

from tel2puml.find_unique_graphs.otel_ingestion.otel_data_holder import (
    SQLDataHolder,
    DataHolder,
)
from tel2puml.find_unique_graphs.otel_ingestion.otel_data_source import (
    JSONDataSource,
    OTELDataSource,
)
from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    SQLDataHolderConfig,
    JSONDataSourceConfig,
)


class IngestData:
    """Class to stream OTel data from a data source and store in within a data
    holder."""

    def __init__(
        self, otel_data_source: OTELDataSource, data_holder: DataHolder
    ) -> None:
        """Constructor method.

        :param otel_data_source: The class that returns an OTelEvent object
        :type otel_data_source: :class: `OTELDataSource`
        :param data_holder: The class that handles data holder operations
        :type data_holder: `DataHolder`
        """
        self.data_holder = data_holder
        self.data_source = otel_data_source

    def load_to_data_holder(self) -> None:
        """Streams OTelEvent objects to data holder."""

        with self.data_holder:
            for data in self.data_source:
                self.data_holder.save_data(data)


def fetch_data_source(config: Any, data_source_type: str) -> OTELDataSource:
    """Returns the subclass of OTelDataSource based on the config.

    :param config: The config
    :type config: `Any`
    :param data_source_type: The data source specified in the config
    :type data_source_type: `str`
    :return: The subclass of OTelDataSource
    :rtype: :class: `OTelDataSource`
    """
    if data_source_type == "json":
        source_dict = config["data_sources"]["json"]
        json_config = JSONDataSourceConfig(
            filepath=source_dict["filepath"],
            dirpath=source_dict["dirpath"],
            data_location=source_dict["data_location"],
            header=source_dict["header"],
            span_mapping=source_dict["span_mapping"],
            field_mapping=source_dict["field_mapping"],
        )
        return JSONDataSource(json_config)

    raise ValueError(f"{data_source_type} is not a valid data source type.")


def fetch_data_holder(config: Any, data_holder_type: str) -> DataHolder:
    """Returns the subclass of DataHolder based on the config.

    :param config: The config
    :type config: `Any`
    :param data_holder_type: The data source specified in the config
    :type data_holder_type: `str`
    :return: The subclass of DataHolder
    :rtype: :class: `DataHolder`
    """
    if data_holder_type == "sql":
        holder_dict = config["data_holders"]["sql"]
        sql_config = SQLDataHolderConfig(
            db_uri=holder_dict["db_uri"],
            batch_size=holder_dict["batch_size"],
            time_buffer=holder_dict["time_buffer"],
        )
        return SQLDataHolder(sql_config)

    raise ValueError(f"{data_holder_type} is not a valid data holder type.")


if __name__ == "__main__":
    with open("tel2puml/find_unique_graphs/config.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    data_source_type = config["ingest_data"]["data_source"]
    data_holder_type = config["ingest_data"]["data_holder"]

    data_source = fetch_data_source(config, data_source_type)
    data_holder = fetch_data_holder(config, data_holder_type)

    ingest_data = IngestData(data_source, data_holder)
    ingest_data.load_to_data_holder()
