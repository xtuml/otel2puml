"""Module containing classes to save processed OTel data into a data holder."""

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self, Optional, TypeVar, Any, Generator
import logging

from sqlalchemy import create_engine, insert
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.orm.exc import DetachedInstanceError
from sqlalchemy.engine.base import Engine

from tel2puml.otel_to_pv.otel_ingestion.otel_data_model import (
    OTelEvent,
    SQLDataHolderConfig,
    NodeModel,
    Base,
    NODE_ASSOCIATION,
)
import tel2puml.otel_to_pv.find_unique_graphs as unique_graphs


LOGGER = logging.getLogger(__name__)


T = TypeVar("T")


class DataHolder(ABC):
    """An abstract class to handle saving processed OTel data."""

    def __init__(self) -> None:
        """Constructor method."""

        self.min_timestamp: int = 999999999999999999999999999999999999999
        self.max_timestamp: int = 0

    def save_data(self, otel_event: OTelEvent) -> None:
        """Method to save an OTelEvent, and keep track of the min and max
        timestamps.

        :param otel_event: An OTelEvent object
        :type otel_event: :class: `OTelEvent`
        """
        self.min_timestamp = min(
            self.min_timestamp, otel_event.start_timestamp
        )
        self.max_timestamp = max(self.max_timestamp, otel_event.end_timestamp)
        self._save_data(otel_event)

    def __enter__(self) -> Self:
        """Method for configuring the setup tasks within the context manager.

        :return: The object itself
        :rtype: :class:`Self`
        """

        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Method for configuring the tear down tasks within the context
        manager.

        :param exc_type: The exception type
        :type exc_type: `Optional`[`type`[:class:`BaseException`]]
        :param exc_val: The exception value
        :type exc_val: `Optional`[:class:`BaseException`]
        :param exc_tb: The exception traceback
        :type exc_tb: `Optional`[:class:`TracebackType`]
        """

        if exc_type:
            raise

    @abstractmethod
    def _save_data(self, otel_event: OTelEvent) -> None:
        """Abstract method for batching and saving OTel data.

        :param otel_event: An OTelEvent object
        :type otel_event: :class: `OTelEvent`
        """
        pass

    @abstractmethod
    def get_otel_events_from_job_ids(
        self, job_ids: set[str]
    ) -> Generator[dict[str, OTelEvent], Any, None]:
        """Abstract method to get OTelEvents from job_ids.

        :param job_ids: A set of job_ids
        :type job_ids: `set`[`str`]
        :return: A generator of dictionaries mapping event ids to OTelEvent
        objects
        :rtype: :class:`Generator`[`dict`[`str`, :class:`OTelEvent`], `Any`,
        `None`]
        """

    @abstractmethod
    def find_unique_graphs(self) -> dict[str, set[str]]:
        """Abstract method to find unique graphs from OTel data in the data
        holder. Returns a dictionary mapping job names to a set of unique
        job_ids.

        :return: A dictionary mapping job names to a set of unique job_ids
        :rtype: `dict`[`str`, `set`[`str`]]
        """
        pass


class SQLDataHolder(DataHolder):
    """A class to handle saving data in SQL databases using SQLAlchemy."""

    def __init__(self, config: SQLDataHolderConfig) -> None:
        """Constructor method.

        :param config: Configuration parameters.
        :type config: :class: `SQLDataHolderConfig`
        """
        super().__init__()
        self.node_models_to_save: list[NodeModel] = []
        self.node_relationships_to_save: list[dict[str, str]] = []
        self.batch_size: int = config["batch_size"]
        self.time_buffer: int = config["time_buffer"]
        self.engine: Engine = create_engine(config["db_uri"], echo=False)
        self.base: Base = Base()
        self.session: Session = Session(bind=self.engine)
        self.create_db_tables()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        Method to handle tear down tasks within the context manager.

        :param exc_type: The exception type
        :type exc_type: `Optional`[`type`[:class:`BaseException`]]
        :param exc_val: The exception value
        :type exc_val: `Optional`[:class:`BaseException`]
        :param exc_tb: The exception traceback
        :type exc_tb: `Optional`[:class:`TracebackType`]
        """
        super().__exit__(exc_type, exc_val, exc_tb)
        self.commit_batched_data_to_database()
        self.session.close()

    def create_db_tables(self) -> None:
        """Method to create the database tables based on the defined models."""

        self.base.metadata.create_all(self.engine)

    def _save_data(self, otel_event: OTelEvent) -> None:
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
        except (IntegrityError, OperationalError, Exception) as e:
            self.session.rollback()
            raise e

    def batch_insert_objects(self, objects: list[T]) -> None:
        """Method to batch insert objects into database.

        :param objects: A list of SQLAlchemy objects
        :type objects: `list`[:class:`T`]
        """

        with self.session as session:
            try:
                session.add_all(objects)
                session.commit()
            except (IntegrityError, OperationalError, Exception) as e:
                session.rollback()
                raise e

    def batch_insert_node_models(self) -> None:
        """Method to batch insert NodeModel objects into database."""
        self.batch_insert_objects(self.node_models_to_save)

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

    @staticmethod
    def convert_otel_event_to_node_model(
        otel_event: OTelEvent
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
            start_timestamp=otel_event.start_timestamp,
            end_timestamp=otel_event.end_timestamp,
            application_name=otel_event.application_name,
            parent_event_id=otel_event.parent_event_id or None,
        )

    @staticmethod
    def node_to_otel_event(node: NodeModel) -> OTelEvent:
        """Method to convert a NodeModel object to an OTelEvent object.

        :param: A NodeModel object
        :type node: :class:`NodeModel`
        :return: An OTelEvent object.
        :rtype: :class:`OTelEvent`
        """
        try:
            return OTelEvent(
                job_name=node.job_name,
                job_id=node.job_id,
                event_type=node.event_type,
                event_id=node.event_id,
                start_timestamp=node.start_timestamp,
                end_timestamp=node.end_timestamp,
                application_name=node.application_name,
                parent_event_id=node.parent_event_id,
                child_event_ids=[
                    child.event_id for child in node.children
                ],
            )
        except DetachedInstanceError:
            logging.error(
                "Likely not within a session so cannot access children."
            )
            raise

    def get_otel_events_from_job_ids(
        self, job_ids: set[str]
    ) -> Generator[dict[str, OTelEvent], Any, None]:
        """Method to get OTelEvents from job_ids

        :param job_ids: A set of job_ids
        :type job_ids: `set`[`str`]
        :return: A generator of dictionaries mapping event ids to OTelEvent
        objects
        :rtype: :class:`Generator`[`dict`[`str`, :class:`OTelEvent`], `Any`,
        `None`]
        """
        with self.session as session:
            nodes = (
                session.query(NodeModel)
                .filter(NodeModel.job_id.in_(job_ids))
                .order_by(NodeModel.job_id)
                .all()
            )
            output: dict[str, OTelEvent] = {}
            current_job_id: str | None = None
            for node in nodes:
                if current_job_id != node.job_id:
                    if current_job_id is not None:
                        yield output
                    output = {}
                    current_job_id = str(node.job_id)
                output[str(node.event_id)] = self.node_to_otel_event(
                    node
                )
            yield output

    def find_unique_graphs(self) -> dict[str, set[str]]:
        """Method to find unique graphs from OTel data in the data holder.

        :return: A dictionary mapping job names to a set of unique job_ids
        :rtype: `dict`[`str`, `set`[`str`]]
        """
        return unique_graphs.find_unique_graphs(
            self.time_buffer,
            self.batch_size,
            self
        )
