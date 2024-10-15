"""Module containing SQL classes to ingest OTel data into a SQLDataHolder."""

from typing import Optional

from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Table,
    Integer,
)
from sqlalchemy.orm import relationship, DeclarativeBase, mapped_column, Mapped


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

    id: Mapped[str] = mapped_column(Integer, primary_key=True)
    job_name: Mapped[str] = mapped_column(String, nullable=False)
    job_id: Mapped[str] = mapped_column(String, nullable=False)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    event_id: Mapped[str] = mapped_column(String, nullable=False)
    start_timestamp: Mapped[int] = mapped_column(Integer, nullable=False)
    end_timestamp: Mapped[int] = mapped_column(Integer, nullable=False)
    application_name: Mapped[str] = mapped_column(String, nullable=False)
    parent_event_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("nodes.event_id")
    )

    children: Mapped[list["NodeModel"]] = relationship(
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


class JobHash(Base):
    """SQLAlchemy model representing job id mapped to a job hash."""

    __tablename__ = "job_hashes"

    job_id: Mapped[str] = mapped_column(
        String, unique=True, nullable=False, primary_key=True
    )
    job_name: Mapped[str] = mapped_column(String, nullable=False)
    job_hash: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self) -> str:
        return f"""
        <JobHash(
        job_id='{self.job_id}',
        job_name='{self.job_name}',
        hash='{self.job_hash}'
        )>
        """
