"""Module containing classes to save processed OTel data into a data holder."""

import yaml
from abc import ABC, abstractmethod

from sqlalchemy.engine.base import Engine
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError

from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    OTelEvent,
    SQLDataHolderConfig,
    NodeModel,
    Base,
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

        self.data_to_save: list[NodeModel] = []
        self.node_data: dict[str, NodeModel] = {}
        self.batch_size: int = config["batch_size"]
        self.engine: Engine = create_engine(config["db_uri"], echo=False)
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
        if len(self.data_to_save) >= self.batch_size:
            self.commit_batched_data_to_database()
            self.data_to_save = []
        else:
            node_model = self.convert_otel_event_to_node_model(otel_event)
            self.node_data[node_model.event_id] = node_model
            self.add_child_relations(otel_event)

    def commit_batched_data_to_database(self) -> None:
        try:
            self.session.add_all(self.data_to_save)
            self.session.commit()
        except OperationalError as e:
            print(f"Database operational error: {e}")
        except IntegrityError as e:
            print(f"Data integrity error: {e}")
        except Exception as e:
            print("Unexpected error during data saving:")
            self.session.rollback()

    # TODO have a think about how child relations will be captured.
    def add_child_relations(self, otel_event: OTelEvent) -> None:
        child_event_ids = otel_event.get("child_event_ids", [])
        if child_event_ids:
            for event_id in child_event_ids:
                pass

    def convert_otel_event_to_node_model(self, otel_event: OTelEvent) -> NodeModel:
        return NodeModel(
            job_name=otel_event.job_name,
            job_id=otel_event.job_id,
            event_type=otel_event.event_type,
            event_id=otel_event.event_id,
            start_timestamp=otel_event.start_timestamp,
            end_timestamp=otel_event.end_timestamp,
            application_name=otel_event.application_name,
            parent_event_id=otel_event.parent_event_id,
            children=otel_event.child_event_ids or [],
        )


if __name__ == "__main__":
    with open("tel2puml/find_unique_graphs/config.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    sdh = SQLDataHolder(config["data_holders"]["sql"])
    # sdh.create_db_tables()

    otel_event = OTelEvent(
        job_name="1",
        job_id="2",
        event_type="3",
        event_id="4",
        start_timestamp="5",
        end_timestamp="6",
        application_name="7",
        parent_event_id="8",
        child_event_ids=["asd", "eaef"],
    )

    nodemodel = sdh.convert_otel_event_to_node_model(otel_event)
    print(nodemodel)
