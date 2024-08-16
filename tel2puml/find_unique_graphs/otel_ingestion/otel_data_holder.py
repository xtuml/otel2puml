"""Module containing classes to save processed OTel data into a data holder."""

import yaml
from abc import ABC, abstractmethod

from sqlalchemy.engine.base import Engine
from sqlalchemy import (
    create_engine
)
from sqlalchemy.orm import Session

from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    OTelEvent,
    SQLDataHolderConfig,
    NodeModel,
    Base,
    NODE_ASSOCIATION
)


class DataHolder(ABC):
    """An abstract class to handle saving processed OTel data."""

    @abstractmethod
    def save_data(self, otel_event: OTelEvent) -> None:
        """Method for batching and saving OTel data.

        :param otel_event: An OTelEvent object
        :type otel_event: :class: `OTelEvent`
        """
        pass


class SQLDataHolder(DataHolder):
    """A class to handle saving data in SQL databases using SQLAlchemy."""

    def __init__(self, config: SQLDataHolderConfig) -> None:
        """Constructor method."""

        self.data_to_save: list[OTelEvent] = []
        self.batch_size: int = config["batch_size"]
        self.engine: Engine = create_engine(
            config["db_uri"], echo=False
        )
        self.session: Session = Session(bind=self.engine)
        self.base = Base()

    def create_db_tables(self) -> None:
        """Create the database tables based on the defined models."""
        self.base.metadata.create_all(self.engine)
        

    def save_data(self, otel_event: OTelEvent) -> None:
        """Method for batching and saving OTel data to SQL database.

        :param otel_event: An OTelEvent object
        :type otel_event: :class: `OTelEvent`
        """
        pass

if __name__ == "__main__":
    with open("tel2puml/find_unique_graphs/config.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    sdh = SQLDataHolder(config["data_holders"]["sql"])
    sdh.create_db_tables()
