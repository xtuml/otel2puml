"""DataHolder subclasses for SQL databases and finding unique OTel trees"""

from types import TracebackType
from typing import Any, Generator, TypeVar, Iterable
from itertools import groupby
import logging

import sqlalchemy as sa
from sqlalchemy import create_engine, insert, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.orm.exc import DetachedInstanceError
from sqlalchemy.engine.base import Engine
import xxhash

from tel2puml.otel_to_pv.data_holders.sql_data_holder.data_model import (
    NodeModel,
    Base,
    NODE_ASSOCIATION,
    JobHash,
)
from ..base import DataHolder, get_time_window
from tel2puml.otel_to_pv.config import SQLDataHolderConfig
from tel2puml.otel_to_pv.otel_to_pv_types import OTelEvent

T = TypeVar("T")


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
    def convert_otel_event_to_node_model(otel_event: OTelEvent) -> NodeModel:
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
                child_event_ids=[child.event_id for child in node.children],
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
                output[str(node.event_id)] = self.node_to_otel_event(node)
            yield output

    def find_unique_graphs(self) -> dict[str, set[str]]:
        """Method to find unique graphs from OTel data in the data holder.

        :return: A dictionary mapping job names to a set of unique job_ids
        :rtype: `dict`[`str`, `set`[`str`]]
        """
        return find_unique_graphs(self.time_buffer, self.batch_size, self)

    def stream_job_name_batches(
        self,
        session: Session,
        job_name_to_job_ids_map: dict[str, set[str]] | None = None,
        filter_job_names: set[str] | None = None,
    ) -> Generator[OTelEvent, None, None]:
        """
        Stream OTelEvents from the database.

        :param session: SQLAlchemy Session object.
        :type session: :class: `sqlalchemy.orm.Session`
        :param job_name_to_job_ids_map: Optional mapping of job names to job
        IDs to filter. Defaults to None.
        :type job_name_to_job_ids_map: `Optional`[`dict`[`str`, `set`[`str`]]]
        :param filter_job_names: Optional set of job names to filter. Defaults
        to None.
        :type filter_job_names: `Optional`[`set`[`str`]]
        :return: Generator yielding OtelEvent objects
        :rtype: `Generator`[:class:`OTelEvent`, `None`, `None`]
        """
        query = session.query(NodeModel)
        # Apply filters
        if filter_job_names:
            query = query.filter(NodeModel.job_name.in_(filter_job_names))
        if job_name_to_job_ids_map:
            job_filters = [
                (NodeModel.job_name == job_name)
                & (NodeModel.job_id.in_(job_ids))
                for job_name, job_ids in job_name_to_job_ids_map.items()
            ]
            query = query.filter(or_(*job_filters))

        # Order by job_name and job_id to use groupby later on.
        # Limit query object to batch_size
        query = query.order_by(NodeModel.job_name, NodeModel.job_id).yield_per(
            self.batch_size
        )

        for node in query:
            yield self.node_to_otel_event(node)

    def stream_data(
        self,
        job_name_to_job_ids_map: dict[str, set[str]] | None = None,
        filter_job_names: set[str] | None = None,
    ) -> Generator[
        tuple[str, Generator[Generator[OTelEvent, None, None], None, None]],
        None,
        None,
    ]:
        """
        Stream data grouped by job_name from the SQL data holder.

        :param job_name_to_job_ids_map: Optional mapping of job names to job
        IDs to filter. Defaults to None.
        :type job_name_to_job_ids_map: `Optional`[`dict`[`str`, `set`[`str`]]]
        :param filter_job_names: Optional set of job names to filter. Defaults
        to None.
        :type filter_job_names: `Optional`[`set`[`str`]]
        :return: Generator yielding tuples of (job_name, generator of
        generators of OtelEvents grouped by job_id).
        :rtype: `Generator`[`tuple`[`str`, `Generator`[`Generator`
        [:class:`OTelEvent`, `None`, `None`]], `None`, `None`],`None`,
        `None`]
        """
        with self.session as session:
            job_name_event_generator = self.stream_job_name_batches(
                session, job_name_to_job_ids_map, filter_job_names
            )

            for job_name, job_name_group in groupby(
                job_name_event_generator, key=lambda x: x.job_name
            ):
                # For each job_name, create a generator of generator of 
                # OtelEvents grouped by job_id
                otel_event_gen = (
                    (event for event in job_id_group)
                    for _, job_id_group in groupby(
                        job_name_group, key=lambda x: x.job_id
                    )
                )
                yield job_name, otel_event_gen


def intialise_temp_table_for_root_nodes(
    sql_data_holder: SQLDataHolder,
) -> sa.Table:
    """Initialise a temporary table for the root nodes.

    :param sql_data_holder: The SQL data holder object containing the ingested
        data
    :type sql_data_holder: :class:`SQLDataHolder`
    :return: The temporary table for the root nodes
    :rtype: :class:`sa`.`Table`
    """
    temp_table = sa.Table(
        "temp_root_nodes",
        sql_data_holder.base.metadata,
        sa.Column("event_id", sa.String, unique=True, primary_key=True),
        prefixes=["TEMPORARY"],
    )
    with sql_data_holder.session as session:
        session.execute(sa.schema.CreateTable(temp_table))
        session.commit()
    return temp_table


def create_temp_table_of_root_nodes_in_time_window(
    time_window: tuple[int, int], sql_data_holder: SQLDataHolder
) -> sa.Table:
    """Create a temporary table with the root nodes in the time window.

    :param time_window: The time window for the unique graphs
    :type time_window: `tuple`[`int`, `int`]`
    :param sql_data_holder: The SQL data holder object containing the ingested
        data
    :type sql_data_holder: :class:`SQLDataHolder`
    :return: The temporary table with the root nodes in the time window
    :rtype: :class:`sa`.`Table`
    """
    temp_table = intialise_temp_table_for_root_nodes(sql_data_holder)

    with sql_data_holder.session as session:
        stmt = (
            session.query(NodeModel.job_id)
            .group_by(NodeModel.job_id)
            .having(
                sa.func.count(1).filter(
                    (
                        (NodeModel.start_timestamp <= time_window[1])
                        & (NodeModel.start_timestamp >= time_window[0])
                    )
                    | (
                        (NodeModel.end_timestamp <= time_window[1])
                        & (NodeModel.end_timestamp >= time_window[0])
                    )
                )
                > 0
            )
            .subquery()
        )
        stmt = (
            session.query(NodeModel.event_id)
            .join(stmt, NodeModel.job_id == stmt.c.job_id)
            .where(NodeModel.parent_event_id.is_(None))
            .subquery()
        )
        session.execute(temp_table.insert().from_select(["event_id"], stmt))
        session.commit()

    return temp_table


def get_root_nodes(
    start_row: int,
    batch_size: int,
    temp_table: sa.Table,
    data_holder: SQLDataHolder,
) -> list[NodeModel]:
    """Get the root nodes from the temporary table.

    :param start_row: The starting row to get the root nodes from
    :type start_row: `int`
    :param batch_size: The batch size to get the root nodes in
    :type batch_size: `int`
    :param temp_table: The temporary table with the root nodes
    :type temp_table: :class:`sa`.`Table`
    :param data_holder: The SQL data holder object containing the ingested
    data
    :type data_holder: :class:`SQLDataHolder`
    :return: The root nodes from the temporary table
    :rtype: `list`[:class:`NodeModel`]
    """
    if start_row < 0:
        raise ValueError("The start row must be greater than or equal to 0.")
    if batch_size < 0:
        raise ValueError("The batch size must be greater than or equal to 0.")
    with data_holder.session:
        stmt = (
            data_holder.session.query(temp_table.c.event_id)
            .slice(start_row, start_row + batch_size)
            .subquery()
        )
        root_nodes = (
            data_holder.session.query(NodeModel)
            .join(stmt, NodeModel.event_id == stmt.c.event_id)
            .all()
        )
    return root_nodes


def get_sql_batch_nodes(
    job_ids: set[str], data_holder: SQLDataHolder
) -> list[NodeModel]:
    """Get the nodes for each job ID in the batch.

    :param job_ids: The set of job IDs to get the nodes for
    :type job_ids: `set[str]`
    :param data_holder: The SQL data holder object containing the ingested
    data
    :type data_holder: :class:`SQLDataHolder`
    :return: The nodes for each job ID in the batch
    :rtype: `list[NodeModel]`
    """
    with data_holder.session:
        nodes = (
            data_holder.session.query(NodeModel)
            .filter(NodeModel.job_id.in_(job_ids))
            .all()
        )
    return nodes


def create_event_id_to_child_nodes_map(
    nodes: Iterable[NodeModel],
) -> dict[str, list[NodeModel]]:
    """Create a map of event IDs to their child nodes.

    :param nodes: The list of nodes
    :type nodes: `Iterable`[`NodeModel`]
    :return: The map of event IDs to their child nodes
    :rtype: `dict`[`str`, `list`[`NodeModel`]]
    """
    event_id_to_child_nodes_map: dict[str, list[NodeModel]] = {}
    for node in nodes:
        event_id = node.event_id
        if event_id not in event_id_to_child_nodes_map:
            event_id_to_child_nodes_map[event_id] = []
        if node.parent_event_id is not None:
            parent_event_id = node.parent_event_id
            if parent_event_id not in event_id_to_child_nodes_map:
                event_id_to_child_nodes_map[parent_event_id] = []
            event_id_to_child_nodes_map[parent_event_id].append(node)
    return event_id_to_child_nodes_map


def compute_graph_hash_from_event_ids(
    node: NodeModel,
    node_to_children: dict[str, list[NodeModel]],
) -> str:
    """Compute the hash of a graph from the nodes ancestors.

    :param node: The node to compute the hash for
    :type node: :class:`NodeModel`
    :param node_to_children: Mapping of node event IDs to their children
    :type node_to_children: `dict`[`str`, `list`[:class:`NodeModel`]]
    :return: The hash of the graph as a hex string
    """
    string_to_hash = node.event_type
    if node.event_id in node_to_children:
        children = node_to_children[node.event_id]
        string_to_hash += "".join(
            sorted(
                compute_graph_hash_from_event_ids(child, node_to_children)
                for child in children
            )
        )
    return xxhash.xxh64_hexdigest(string_to_hash)


def compute_graph_hashes_from_root_nodes(
    root_nodes: list[NodeModel], node_to_children: dict[str, list[NodeModel]]
) -> list[JobHash]:
    """Compute the hashes of the graphs from the root nodes.

    :param root_nodes: The root nodes to compute the hashes for
    :type root_nodes: `list`[:class:`NodeModel`]
    :param node_to_children: Mapping of node event IDs to their children
    :type node_to_children: `dict`[`str`, `list`[:class:`NodeModel`]]
    :return: The list of JobHash objects
    :rtype: `list`[:class:`JobHash`]
    """
    return [
        JobHash(
            job_id=node.job_id,
            job_hash=compute_graph_hash_from_event_ids(node, node_to_children),
            job_name=node.job_name,
        )
        for node in root_nodes
    ]


def insert_job_hashes(
    job_hashes: list[JobHash], sql_data_holder: SQLDataHolder
) -> None:
    """Insert the job hashes into the database.

    :param job_hashes: The list of JobHash objects
    :type job_hashes: `list`[:class:`JobHash`]
    :param sql_data_holder: The SQL data holder object containing the ingested
    data
    :type sql_data_holder: :class:`SQLDataHolder`
    """
    sql_data_holder.batch_insert_objects(job_hashes)


def compute_graph_hashes_for_batch(
    root_nodes: list[NodeModel], sql_data_holder: SQLDataHolder
) -> None:
    """Compute the hashes of the graphs for a batch of root nodes and commit
    them to the database.

    :param root_nodes: The root nodes to compute the hashes for
    :type root_nodes: `list`[:class:`NodeModel`]
    """
    batch_nodes = get_sql_batch_nodes(
        {node.job_id for node in root_nodes}, sql_data_holder
    )
    node_to_children = create_event_id_to_child_nodes_map(batch_nodes)
    job_ids_hashes = compute_graph_hashes_from_root_nodes(
        root_nodes, node_to_children
    )
    insert_job_hashes(job_ids_hashes, sql_data_holder)


def get_unique_graph_job_ids_per_job_name(
    sql_data_holder: SQLDataHolder,
) -> dict[str, set[str]]:
    """Get the unique graphs per job name.

    :param sql_data_holder: The SQL data holder object containing the ingested
    data
    :type sql_data_holder: :class:`SQLDataHolder`
    :return: The unique graphs per job name
    :rtype: `dict`[`str`, `set`[`str`]]
    """
    job_name_to_job_ids: dict[str, set[str]] = {}
    with sql_data_holder.session as session:
        stmt = sa.select(JobHash.job_name, JobHash.job_hash).group_by(
            JobHash.job_name, JobHash.job_hash
        )
        job_hashes = session.execute(stmt).fetchall()
        for job_name, job_id in job_hashes:
            if job_name not in job_name_to_job_ids:
                job_name_to_job_ids[job_name] = set()
            job_name_to_job_ids[job_name].add(job_id)
    return job_name_to_job_ids


def find_unique_graphs(
    time_buffer: int, batch_size: int, sql_data_holder: SQLDataHolder
) -> dict[str, set[str]]:
    """Find the unique graphs in the ingested OpenTelemetry data.

    :param time_buffer: The time buffer to add to the time window in minutes
    :type time_buffer: `int`
    :param batch_size: The batch size to get the root nodes in
    :type batch_size: `int`
    :param sql_data_holder: The SQL data holder object containing the ingested
    data
    :type sql_data_holder: :class:`SQLDataHolder`
    :return: The unique graph job ids per job name
    :rtype: `dict`[`str`, `set`[`str`]]
    """
    time_window = get_time_window(time_buffer, sql_data_holder)
    temp_table = create_temp_table_of_root_nodes_in_time_window(
        time_window, sql_data_holder
    )
    start_row = 0
    while True:
        root_nodes = get_root_nodes(
            start_row, batch_size, temp_table, sql_data_holder
        )
        if not root_nodes:
            break
        compute_graph_hashes_for_batch(root_nodes, sql_data_holder)
        start_row += batch_size
    job_name_to_job_ids_map = get_unique_graph_job_ids_per_job_name(
        sql_data_holder
    )
    with sql_data_holder.session as session:
        session.execute(sa.schema.DropTable(temp_table))
        session.commit()
    return job_name_to_job_ids_map
