"""Module to process OTel data into JSON to be ingested by memgraph database"""

import json
import uuid

from graph_solution_poc.graph_types import (
    NodeData,
    NodeRelationshipData,
    OtelData,
)


def create_node_json(data: OtelData) -> NodeData:
    """Returns a dictionary that represents a node within a graph database.

    :param data: An event within the Otel JSON data
    :type data: `str`
    :return: A dictionary of properties of a node
    :rtype: `dict`[`str`,`str` | `dict`[`str`,`str`]]
    """
    return dict(
        id=data["span_id"],
        labels=["event"],
        properties={
            "trace_id": data["trace_id"],
            "event_type": data["event_type"],
            "job_name": data["job_name"],
            "span_id": data["span_id"],
        },
        type="node",
    )


def create_relationship_json(
    start_span_id: str, end_span_id: str, trace_id: str
) -> NodeRelationshipData:
    """Function to return a dictionary that represents an edge between two
    nodes within a graph database.

    :param start_span_id: The span ID of the start node of the edge
    :type start_span_id: `str`
    :param end_span_id: The span ID of the end node of the edge
    :type end_span_id: `str`
    :param trace_id: The trace ID for the graph
    :type trace_id: `str`
    :return: A dictionary representing an edge within a graph
    :rtype: `dict`[`str`,`str` | `dict`[`str`,`str`]]
    """
    return dict(
        id=str(uuid.uuid4()),
        end=end_span_id,
        start=start_span_id,
        label="PARENT",
        properties={"trace_id": trace_id},
        type="relationship",
    )


def process_json_for_graph_database(filepath: str) -> None:
    """Function to parse dummy OTel data and convert it to JSON to be
    ingested by memgraph database.

    :param filepath: The file path to the dummy data
    :type filepath: `str`
    """
    output_json: list[NodeData | NodeRelationshipData] = []
    with open(filepath) as f:
        event_data = json.load(f)
        for data in event_data:
            output_json.append(create_node_json(data))
            if data["prev_span_id"]:
                output_json.append(
                    create_relationship_json(
                        data["prev_span_id"], data["span_id"], data["trace_id"]
                    )
                )
    # Save to file
    with open("./memgraph_poc/converted_dummy_trace_data.json", "w") as f:
        json.dump(output_json, f, indent=2)


if __name__ == "__main__":
    filepath = "graph_solution_poc/data/dummy_trace_data.json"
    process_json_for_graph_database(filepath)
