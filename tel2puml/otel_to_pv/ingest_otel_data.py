"""Module to stream OTel data from a data source and store it within a
data holder."""
from typing import TypedDict, Type
from tel2puml.otel_to_pv.data_holders import (
    SQLDataHolder,
    DataHolder,
)
from tel2puml.otel_to_pv.data_sources import (
    JSONDataSource,
    OTELDataSource,
)
from tel2puml.otel_to_pv.config import IngestDataConfig


class DataSourcesTypedDict(TypedDict):
    """Typed dict for DataSources."""

    json: Type[JSONDataSource]


class DataHoldersTypedDict(TypedDict):
    """Typed dict for DataHolders."""

    sql: Type[SQLDataHolder]


DATASOURCES = DataSourcesTypedDict(json=JSONDataSource)


DATAHOLDERS = DataHoldersTypedDict(sql=SQLDataHolder)


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


def fetch_data_source(config: IngestDataConfig) -> OTELDataSource:
    """Returns the subclass of OTelDataSource based on the config.

    :param config: The config
    :type config: :class: `IngestDataConfig`
    :return: The subclass of OTelDataSource
    :rtype: :class: `OTelDataSource`
    """
    data_source_type = config.ingest_data.data_source
    if data_source_type not in config.data_sources:
        raise ValueError(
            f"{data_source_type} is not present in the data source config."
        )
    return DATASOURCES[data_source_type](config.data_sources[data_source_type])


def fetch_data_holder(config: IngestDataConfig) -> DataHolder:
    """Returns the subclass of DataHolder based on the config.

    :param config: The config
    :type config: :class: `IngestDataConfig`
    :return: The subclass of DataHolder
    :rtype: :class: `DataHolder`
    """
    data_holder_type = config.ingest_data.data_holder
    data_holders = config.data_holders
    if data_holder_type not in data_holders:
        raise ValueError(
            f"{data_holder_type} is not present in the data holder config."
        )
    return DATAHOLDERS[data_holder_type](data_holders[data_holder_type])


def ingest_data_into_dataholder(config: IngestDataConfig) -> DataHolder:
    """Ingests data into data holder.

    :param config: The config
    :type config: :class:`IngestDataConfig`
    """
    data_source = fetch_data_source(config)
    data_holder = fetch_data_holder(config)

    ingest_data = IngestData(data_source, data_holder)
    ingest_data.load_to_data_holder()
    return data_holder
