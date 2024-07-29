"""Module to utilise SQLite databse to find unique graphs based on graph nodes
event_type and grouping by job name"""

import json
import time
import hashlib
from collections import defaultdict

from sqlalchemy import (
    create_engine,
    Column,
    String,
    ForeignKey,
)
from sqlalchemy.orm import sessionmaker, declarative_base

# Create a database on disk
engine = create_engine("sqlite:///node_database.db", echo=False)

# Use in-memory database
# engine = create_engine("sqlite:///:memory:", echo=False)
Base = declarative_base()


class Node(Base):
    """Represents a node in the graph structure."""

    __tablename__ = "nodes"

    span_id = Column(String, primary_key=True)
    trace_id = Column(String)
    event_type = Column(String)
    job_name = Column(String)
    prev_span_id = Column(String, ForeignKey("nodes.span_id"))

    def __repr__(self) -> str:
        return f"""<Node(span_id='{self.span_id}',\n
        trace_id='{self.trace_id}', event_type='{self.event_type}',\n
        job_name='{self.job_name}')>"""


def create_db() -> None:
    """Create the database tables based on the defined models."""
    Base.metadata.create_all(engine)


def load_nodes_from_json(json_file_path: str) -> None:
    """Load nodes from a JSON file and save them to the database.

    :param json_file_path: Path to the JSON file containing node data
    :type json_file_path: `str`
    """
    Session = sessionmaker(bind=engine)
    with open(json_file_path, "r") as file:
        nodes_data = json.load(file)

    with Session() as session:
        nodes = [Node(**node_data) for node_data in nodes_data]
        session.bulk_save_objects(nodes)
        session.commit()


def compute_recursive_node_hash(
    node: Node, node_to_children: dict[str, list[Node]]
) -> str:
    """Compute a hash for a node based on its event type and its children's
    hashes.

    :param node: The node for which to compute the hash
    :type node: `Node`
    :param node_to_children: Mapping of node IDs to their children nodes
    :type node_to_children: `dict`[`str`, `list`[`Node`]]
    :return: The computed hash for the node
    :rtype: `str`
    """
    node_children = node_to_children.get(node.span_id, [])

    if not node_children:
        return hashlib.sha256(node.event_type.encode()).hexdigest()

    # Compute hash for child nodes recursively
    child_hashes = sorted(
        compute_recursive_node_hash(child, node_to_children)
        for child in node_children
    )
    combined_string = node.event_type + "".join(child_hashes)

    # Compute hash for the current node based on its event type and children
    return hashlib.sha256(combined_string.encode()).hexdigest()


def get_all_nodes_for_batch(trace_ids: set[str]) -> list[Node]:
    """Retrieve all nodes for a given set of trace IDs.

    :param trace_ids: Set of trace IDs to query
    :type trace_ids: `set`[`str`]
    :return: List of all nodes for the given trace IDs
    :rtype: `list`[`Node`]
    """
    return session.query(Node).filter(Node.trace_id.in_(trace_ids)).all()


def create_node_to_children_map(
    nodes: list[Node],
) -> defaultdict[str, list[Node]]:
    """Create a mapping of node span IDs to their children.

    :param nodes: List of nodes to process
    :type nodes: `list`[`Node`]
    :return: Mapping of node span IDs to their children
    :rtype: `dict`[`str`, `list`[`Node`]]
    """
    node_span_id_to_child_nodes = defaultdict(list)
    for node in nodes:
        if node.prev_span_id:
            node_span_id_to_child_nodes[node.prev_span_id].append(node)
    return node_span_id_to_child_nodes


def add_graph_hash_to_sets(
    graph_hash: str,
    root_node: Node,
    job_name_to_graph_hash_set: defaultdict[str, set[str]],
    trace_id_to_hash: defaultdict[str, list[str]],
    job_name: str,
) -> None:
    """Add a graph hash to the hash set and trace ID mapping.

    :param graph_hash: The computed hash for the graph
    :type graph_hash: `str`
    :param root_node: The root node of the graph
    :type root_node: `Node`
    :param job_name_to_graph_hash_set: Set of unique graph hashes split by
    job names
    :type job_name_to_graph_hash_set: `dict`[`str`, `set`[`str`]]
    :param trace_id_to_hash: Mapping of graph hashes to trace IDs
    :type trace_id_to_hash: `dict`[`str`, `list`[`str`]]
    :param job_name: The job name associated with the graph
    :type job_name: `str`
    """
    job_name_to_graph_hash_set[job_name].add(graph_hash)
    trace_id_to_hash[graph_hash].append(root_node.trace_id)


def compute_graph_hashes_for_batch(
    root_nodes_batch: list[Node],
    job_name_to_graph_hash_set: defaultdict[str, set[str]],
    trace_id_to_hash: defaultdict[str, list[str]],
    job_name: str,
) -> None:
    """Compute unique hashes for a batch of graphs and add them to the hash
    set.

    :param root_nodes_batch: List of root nodes for the graphs
    :type root_nodes_batch: `list`[`Node`]
    :param job_name_to_graph_hash_set: Set of unique graph hashes split by
    job names
    :type job_name_to_graph_hash_set: `dict`[`str`, `set`[`str`]]
    :param trace_id_to_hash: Mapping of graph hashes to trace IDs
    :type trace_id_to_hash: `dict`[`str`, `list`[`str`]]
    :param job_name: The job name associated with the graphs
    :type job_name: `str`
    """
    trace_ids_in_batch = {node.trace_id for node in root_nodes_batch}
    all_graph_nodes_in_batch = get_all_nodes_for_batch(trace_ids_in_batch)
    node_to_children = create_node_to_children_map(all_graph_nodes_in_batch)

    for root_node in root_nodes_batch:
        graph_hash = compute_recursive_node_hash(root_node, node_to_children)
        add_graph_hash_to_sets(
            graph_hash,
            root_node,
            job_name_to_graph_hash_set,
            trace_id_to_hash,
            job_name,
        )


def retrieve_unique_graphs() -> defaultdict[str, set[str]]:
    """Retrieve unique graphs from the database.

    :return: A dictionary of unique graph hashes split by job names
    :rtype: `defaultdict`[`str`, `set`[`str`]]
    """

    job_names = session.query(Node.job_name).distinct()
    job_name_to_graph_hash_set: defaultdict[str, set[str]] = defaultdict(set)
    trace_id_to_hash: defaultdict[str, list[str]] = defaultdict(list)
    processed_count = 0
    batch_size = 500
    for job_name in job_names:
        root_nodes = (
            session.query(Node)
            .filter_by(prev_span_id=None, job_name=job_name[0])
            .all()
        )
        for i in range(0, len(root_nodes), batch_size):
            current_batch = root_nodes[i: i + batch_size]
            compute_graph_hashes_for_batch(
                root_nodes[i: i + batch_size],
                job_name_to_graph_hash_set,
                trace_id_to_hash,
                job_name[0],
            )

            processed_count += len(current_batch)
            print(f"Processed {processed_count} event graphs")

    return job_name_to_graph_hash_set


if __name__ == "__main__":
    Base.metadata.drop_all(engine)
    create_db()
    load_nodes_from_json("graph_solution_poc/data/dummy_trace_data.json")
    Session = sessionmaker(bind=engine)
    time_start = time.time()
    with Session() as session:
        job_name_to_graph_hash_set = retrieve_unique_graphs()
        print(
            f"""Total unique graph structures:\n
            {sum(len(hashes)
                 for hashes in job_name_to_graph_hash_set.values())}"""
        )

    print(f"Time taken {time.time() - time_start}")
