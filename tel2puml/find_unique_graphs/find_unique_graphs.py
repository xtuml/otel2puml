"""Module for finding unique graphs in a list of graphs from ingested
OpenTelemetry data."""
from typing import Iterable
import sqlalchemy as sa
import xxhash

from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    NodeModel, JobHash
)
from tel2puml.find_unique_graphs.otel_ingestion.otel_data_holder import (
    DataHolder, SQLDataHolder
)


def get_time_window(
    time_buffer: int, data_holder: DataHolder
) -> tuple[int, int]:
    """Get the time window for the unique graphs.

    :param time_buffer: The time buffer to add to the time window in minutes
    :type time_buffer: `int`
    :param data_holder: The data holder object containing the ingested data
    :type data_holder: :class:`DataHolder`
    :return: The time window for the unique graphs
    :rtype: `tuple`[`int`, `int`]
    :raises ValueError: If the time buffer is too large for the ingested data
    """
    time_buffer_in_nanoseconds = time_buffer * 60 * 1000000000
    buffer_min_timestamp = (
        data_holder.min_timestamp + time_buffer_in_nanoseconds
    )
    buffer_max_timestamp = (
        data_holder.max_timestamp - time_buffer_in_nanoseconds
    )
    if buffer_min_timestamp >= buffer_max_timestamp:
        raise ValueError(
            "The time buffer is too large for the ingested data. "
            "Please reduce the time buffer."
        )
    return (
        data_holder.min_timestamp + time_buffer_in_nanoseconds,
        data_holder.max_timestamp - time_buffer_in_nanoseconds,
    )


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
    temp_table = sa.Table(
        "temp_root_nodes",
        sql_data_holder.base.metadata,
        sa.Column("event_id", sa.String, unique=True, primary_key=True),
        prefixes=["TEMPORARY"],
    )

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
            .where(NodeModel.parent_event_id.is_(None)).subquery()
        )
        session.execute(sa.schema.CreateTable(temp_table))
        session.execute(temp_table.insert().from_select(["event_id"], stmt))
        session.commit()

    return temp_table


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
    nodes: Iterable[NodeModel]
) -> dict[str, list[NodeModel]]:
    """Create a map of event IDs to their child nodes.

    :param nodes: The list of nodes
    :type nodes: `Iterable`[`NodeModel`]
    :return: The map of event IDs to their child nodes
    :rtype: `dict`[`str`, `list`[`NodeModel`]]
    """
    event_id_to_child_nodes_map: dict[str, list[NodeModel]] = {}
    for node in nodes:
        event_id = str(node.event_id)
        if event_id not in event_id_to_child_nodes_map:
            event_id_to_child_nodes_map[event_id] = []
        if node.parent_event_id is not None:
            parent_event_id = str(node.parent_event_id)
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
    string_to_hash = str(node.event_type)
    if node.event_id in node_to_children:
        children = node_to_children[str(node.event_id)]
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
        JobHash(job_id=node.job_id, job_hash=compute_graph_hash_from_event_ids(
            node, node_to_children
        ))
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
        {str(node.job_id) for node in root_nodes}, sql_data_holder
    )
    node_to_children = create_event_id_to_child_nodes_map(batch_nodes)
    job_ids_hashes = compute_graph_hashes_from_root_nodes(
        root_nodes, node_to_children
    )
    insert_job_hashes(job_ids_hashes, sql_data_holder)
