"""Module for finding unique graphs in a list of graphs from ingested
OpenTelemetry data."""

import sqlalchemy as sa

from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    NodeModel,
)
from tel2puml.find_unique_graphs.otel_ingestion.otel_data_holder import (
    DataHolder,
    SQLDataHolder,
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
    :rtype: `tuple[int, int]`
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
    :type time_window: `tuple[int, int]`
    :param sql_data_holder: The SQL data holder object containing the ingested
        data
    :type sql_data_holder: :class:`SQLDataHolder`
    :return: The temporary table with the root nodes in the time window
    :rtype: :class:`sa.Table`
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
            sa.select(NodeModel.event_id)
            .join(stmt, NodeModel.job_id == stmt.c.job_id)
            .where(NodeModel.parent_event_id.is_(None))
        )
        session.execute(sa.schema.CreateTable(temp_table))
        session.execute(temp_table.insert().from_select(["event_id"], stmt))
        session.commit()

    return temp_table
