"""Module containing classes to ingest OTel data into a data holder."""

from typing import NamedTuple, Optional, TypedDict

from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Table,
    Integer,
)
from sqlalchemy.orm import relationship, DeclarativeBase


class OTelEvent(NamedTuple):
    """Named tuple for OTel event.

    :param job_name: The name of the job.
    :type job_name: `str`
    :param job_id: The ID of the job.
    :type job_id: `str`
    :param event_type: The type of the event.
    :type event_type: `str`
    :param event_id: The ID of the event.
    :type event_id: `str`
    :param start_timestamp: The start timestamp of the event in unix nano.
    :type start_timestamp: `int`
    :param end_timestamp: The end timestamp of the event in unix nano.
    :type end_timestamp: :class: `int`
    :param application_name: The application name.
    :type application_name: `str`
    :param parent_event_id: The ID of the parent event.
    :type parent_event_id: `Optional`[`str`]
    :param child_event_ids: A list of IDs of child events. Defaults to `None`
    :type child_event_ids: Optional[`list`[`str`]]
    """

    job_name: str
    job_id: str
    event_type: str
    event_id: str
    start_timestamp: int
    end_timestamp: int
    application_name: str
    parent_event_id: Optional[str]
    child_event_ids: Optional[list[str]] = None


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models"""

    pass


NODE_ASSOCIATION = Table(
    "NODE_ASSOCIATION",
    Base.metadata,
    Column(
        "parent_id", String, ForeignKey("nodes.event_id"), primary_key=True
    ),
    Column("child_id", String, ForeignKey("nodes.event_id"), primary_key=True),
)


class NodeModel(Base):
    """SQLAlchemy model representing a node in the graph structure."""

    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True)
    job_name = Column(String, nullable=False)
    job_id = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    event_id = Column(String, unique=True, nullable=False)
    start_timestamp = Column(Integer, nullable=False)
    end_timestamp = Column(Integer, nullable=False)
    application_name = Column(String, nullable=False)
    parent_event_id = Column(String, ForeignKey("nodes.event_id"))

    children = relationship(
        "NodeModel",
        secondary=NODE_ASSOCIATION,
        primaryjoin=(event_id == NODE_ASSOCIATION.c.parent_id),
        secondaryjoin=(event_id == NODE_ASSOCIATION.c.child_id),
        backref="parents",
    )

    def __repr__(self) -> str:
        return f"""
        <NodeModel(
        job_name='{self.job_name}',
        job_id='{self.job_id}',
        event_type='{self.event_type}',
        event_id='{self.event_id}',
        start_timestamp='{self.start_timestamp}',
        end_timestamp='{self.end_timestamp}',
        application_name='{self.application_name},
        parent_event_id='{self.parent_event_id}'
        child_event_ids='{[child.event_id for child in self.children]}'
        )>
        """


class HeaderSpec(TypedDict):
    """Typed dict for HeaderSpec."""

    paths: list[str]


class SpanSpec(TypedDict):
    """Typed dict for SpanSpec."""

    key_paths: list[str]


class FieldSpec(TypedDict, total=False):
    """Typed dict for FieldSpec."""

    key_paths: list[str]
    key_value: list[Optional[str]]
    value_paths: list[Optional[str]]
    value_type: str


class JSONDataSourceConfig(TypedDict):
    """Typed dict for JSONDataSourceConfig."""

    filepath: str
    dirpath: str
    data_location: str
    header: dict[str, HeaderSpec]
    span_mapping: dict[str, SpanSpec]
    field_mapping: dict[str, FieldSpec]


class SQLDataHolderConfig(TypedDict):
    """Typed dict for SQLDataHolderConfig."""

    db_uri: str
    batch_size: int
    time_buffer: int


class IngestDataConfig(TypedDict):
    """Typed dict for IngestData config."""

    data_sources: dict[str, JSONDataSourceConfig]
    data_holders: dict[str, SQLDataHolderConfig]
    ingest_data: dict[str, str]


class JobHash(Base):
    """SQLAlchemy model representing job id mapped to a job hash."""

    __tablename__ = "job_hashes"

    job_id = Column(String, unique=True, nullable=False, primary_key=True)
    job_hash = Column(String, nullable=False)

    def __repr__(self) -> str:
        return f"""
        <JobHash(
        job_id='{self.job_id}',
        hash='{self.job_hash}'
        )>
        """
