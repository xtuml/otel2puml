"""Module to analyse memgraph database for unique graphs based on graph nodes
event_type and grouping by job name"""

import time
from neo4j import GraphDatabase
from collections import defaultdict

URI = "bolt://host.docker.internal:7687"
AUTH = ("", "")


def get_all_root_events(neo4j_client: GraphDatabase) -> list[tuple[str, str]]:
    """Function to return a list of root nodes within the graph.

    :param neo4j_client: The neo4j client
    :type neo4j_client: :class:`GraphDatabase`
    :return: A list of tuples of node job names and trace IDs
    :rtype: `list`[`tuple`[`str`, `str`]]
    """
    query = """
        MATCH (n)
        WHERE NOT EXISTS (()-[:PARENT]->(n))
        RETURN n.job_name AS job_name, n.trace_id AS trace_id
        """

    result = neo4j_client.execute_query(query)
    return [
        (record["job_name"], record["trace_id"]) for record in result.records
    ]


def add_graph_hashes_to_job_map(
    neo4j_client: GraphDatabase,
    job_name: str,
    trace_id_batch: list[str],
    job_to_hash_trace_map: dict[str, dict[str, str]],
) -> None:
    """Function that takes a list of trace ids, calculates the weisfeler lehman
    graph hash for each graph based on the graph nodes event_type attribute,
    then stores the result in a dictionary.

    :param neo4j_client: The neo4j client
    :type neo4j_client: :class:`GraphDatabase`
    :param job_name: The job name
    :type job_name: `str`
    :param trace_id_batch: The batch of trace ids to use in the cypher query
    :type trace_id_batch: `list`[`str`]
    :param job_to_hash_trace_map: The dictionary to store the results
    :type job_to_hash_trace_map: `dict`[`str`,`dict[`str`,`str`]]
    """
    cypher_query = """
    UNWIND $trace_id_batch AS trace_id
    MATCH p=(n:event {trace_id: trace_id})-[:PARENT*0..]->
    (m:event {trace_id: trace_id})
    WITH trace_id, project(p) AS event_graph
    CALL graph_hash_weisfeiler_lehman.calculate_graph_hash(event_graph)
    YIELD graph_hash
    WITH trace_id, graph_hash
    RETURN trace_id, graph_hash AS trace_graph_hash
    """

    query_result = neo4j_client.execute_query(
        cypher_query, trace_id_batch=trace_id_batch
    )
    hash_trace_pairs = query_result[0]

    for trace_id, graph_hash in hash_trace_pairs:
        job_to_hash_trace_map[job_name][graph_hash] = trace_id


def get_unique_event_graphs() -> dict[str, dict[str, str]]:
    """
    Retrieves unique event graphs for each job name by
    trace ID and computes their hashes.

    :return: A dictionary mapping job names to their
    unique graph hashes and trace IDs
    :rtype: `dict`[`str`,`dict`[`str`,`str`]]
    """
    with GraphDatabase.driver(URI, auth=AUTH) as db_client:
        db_client.verify_connectivity()

        print("Fetching root events...")
        root_events = get_all_root_events(db_client)
        print(f"Retrieved {len(root_events)} root events")

        job_to_traces = defaultdict(set)
        for job_name, trace_id in root_events:
            job_to_traces[job_name].add(trace_id)

        job_to_hash_trace_map: dict[str, dict[str, str]] = defaultdict(dict)
        processed_count = 0
        batch_size = 200

        for job_name, trace_ids in job_to_traces.items():
            for i in range(0, len(trace_ids), batch_size):
                current_batch = list(trace_ids)[i: i + batch_size]
                add_graph_hashes_to_job_map(
                    db_client, job_name, current_batch, job_to_hash_trace_map
                )

                processed_count += len(current_batch)
                print(f"Processed {processed_count} event graphs")

        return job_to_hash_trace_map


if __name__ == "__main__":
    start_time = time.time()
    job_hash_trace_map = get_unique_event_graphs()
    print(f"Total time: {time.time() - start_time:.2f} seconds")
    print(
        f"""
        Unique graphs found: {
        sum(len(hashes) for hashes in job_hash_trace_map.values())}"""
    )
