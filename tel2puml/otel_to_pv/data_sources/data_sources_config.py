"""Module for DataSources typed dict."""
from typing import TypedDict, NotRequired

from .json_data_source.json_config import JSONDataSourceConfig


class DataSources(TypedDict):
    """Typed dict for DataSources."""

    json: NotRequired[JSONDataSourceConfig]
