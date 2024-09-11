"""init file for data_sources module"""
from .base import OTELDataSource as OTELDataSource
from .json_data_source.json_datasource import JSONDataSource as JSONDataSource

__all__ = ["OTELDataSource", "JSONDataSource"]
