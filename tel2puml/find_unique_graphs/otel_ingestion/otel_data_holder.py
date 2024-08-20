"""Module containing classes to save processed OTel data into a data holder."""

from datetime import datetime
from abc import ABC, abstractmethod

from sqlalchemy import create_engine, insert
from sqlalchemy.orm import Session
from sqlalchemy.engine.base import Engine

from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    OTelEvent,
    SQLDataHolderConfig,
    NodeModel,
    Base,
    NODE_ASSOCIATION,
)


class DataHolder(ABC):
    """An abstract class to handle saving processed OTel data."""

    @abstractmethod
    def save_data(self, otel_event: OTelEvent) -> None:
        """Abstract method for batching and saving OTel data.

        :param otel_event: An OTelEvent object
        :type otel_event: :class: `OTelEvent`
        """
        pass

    @abstractmethod
    def clean_up(self) -> None:
        """Abstract method for any clean up tasks."""

        pass


class SQLDataHolder(DataHolder):
    """A class to handle saving data in SQL databases using SQLAlchemy."""

    def __init__(self, config: SQLDataHolderConfig) -> None:
        """Constructor method.

        :param config: Configuration parameters.
        :type config: :class: `SQLDataHolderConfig`
        """

        self.node_models_to_save: list[NodeModel] = []
        self.node_relationships_to_save: list[dict[str, str]] = []
        self.batch_size: int = config["batch_size"]
        self.engine: Engine = create_engine(config["db_uri"], echo=False)
        self.session: Session = Session(bind=self.engine)
        self.base: Base = Base()
        self.create_db_tables()

    def create_db_tables(self) -> None:
        """Method to create the database tables based on the defined models."""

        self.base.metadata.create_all(self.engine)

    def save_data(self, otel_event: OTelEvent) -> None:
        """Method for batching and saving OTel data to SQL database.

        :param otel_event: An OTelEvent object.
        :type otel_event: :class: `OTelEvent`
        """

        node_model = self.convert_otel_event_to_node_model(otel_event)

        self.node_models_to_save.append(node_model)
        self.add_node_relations(otel_event)

        if len(self.node_models_to_save) >= self.batch_size:
            self.commit_batched_data_to_database()

    def commit_batched_data_to_database(self) -> None:
        """Method to commit batched node models, and their relationships to
        a SQL database.
        """

        try:
            self.batch_insert_node_models()
            self.batch_insert_node_associations()
            # Reset batch
            self.node_models_to_save = []
            self.node_relationships_to_save = []
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Unexpected error during data saving: {e}")

    def batch_insert_node_models(self) -> None:
        """Method to batch insert NodeModel objects into database."""

        with self.session as session:
            session.add_all(self.node_models_to_save)
            session.commit()

    def batch_insert_node_associations(self) -> None:
        """Method to batch insert node associations into database."""

        if len(self.node_relationships_to_save) > 0:
            with self.session as session:
                stmt = insert(NODE_ASSOCIATION)
                session.execute(stmt, self.node_relationships_to_save)
                session.commit()

    def add_node_relations(self, otel_event: OTelEvent) -> None:
        """Method to add parent-child node relations.

        :param otel_event: An OTelEvent object
        :type otel_event: :class: `OTelEvent`
        """

        if otel_event.child_event_ids:
            for child_event_id in otel_event.child_event_ids:
                self.node_relationships_to_save.append(
                    {
                        "parent_id": otel_event.event_id,
                        "child_id": child_event_id,
                    }
                )

    def convert_otel_event_to_node_model(
        self, otel_event: OTelEvent
    ) -> NodeModel:
        """Method to convert an OTelEvent object to a NodeModel object.

        :param otel_event: An OTelEvent object
        :type otel_event: :class: `OTelEvent`
        :return: A NodeModel object
        :rtype: :class:`NodeModel`
        """
        return NodeModel(
            job_name=otel_event.job_name,
            job_id=otel_event.job_id,
            event_type=otel_event.event_type,
            event_id=otel_event.event_id,
            start_timestamp=datetime.strptime(
                otel_event.start_timestamp, "%Y-%m-%d %H:%M:%S"
            ),
            end_timestamp=datetime.strptime(
                otel_event.end_timestamp, "%Y-%m-%d %H:%M:%S"
            ),
            application_name=otel_event.application_name,
            parent_event_id=otel_event.parent_event_id or None,
        )

    def clean_up(self) -> None:
        """Method to save commit remaining items within the batch to the
        database.
        """

        self.commit_batched_data_to_database()
