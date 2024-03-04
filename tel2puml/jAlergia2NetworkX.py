"""
This module provides functions to extract nodes and edges from input data,
convert them into a NetworkX graph, and optionally write the graph to a file.

Functions:
- get_nodes: Extracts nodes from the given data and updates the node_reference,
    events_reference, and node_list.
- get_edges: Extracts edges from the given data and populates the
    edge_list dictionary.
- convert_to_networkx: Converts the given events reference and edge list
    into a NetworkX graph.

Usage:
1. Import the module: `import jAlergia2NetworkX`
2. Call the functions as needed, providing the required arguments.
3. Optionally, specify the `write` parameter in `convert_to_networkx` to write
    the graph to a file.

"""

import re
import networkx as nx


def get_nodes(data: str):
    """
    Extracts nodes from the given data and updates the node_reference,
        events_reference, and node_list.

    Args:
        data (str): The input data containing node information.

    Returns:
        tuple: A tuple containing the updated node_reference, events_reference,
            and node_list.

    These returns are formatted as following:
    node_reference   - {'event': 'node', ..}
    events_reference - {'node': ['event1', 'event2', ..], ..}
    node_list        - ["node1", "node2", ..]
    """

    node_reference = {}
    events_reference = {}
    node_list = []

    for node in re.findall(
        r"^ *(q\d+) *\[(shape=\".*?\",)?label=\"(.*?)\"",
        data,
        re.M
    ):

        labelNode = node[2]

        if labelNode not in node_reference:
            node_reference[labelNode] = [node[0]]
            events_reference[node[0]] = labelNode
            node_list.append(labelNode)
        else:
            node_reference[labelNode].append([node[0]])
            events_reference[node[0]] = labelNode

    return node_reference, events_reference, node_list


def get_edges(data: str):
    """
    Extracts edges from the given data and populates the edge_list dictionary.

    Args:
        data (str): The input data containing edge information.

    Returns:
        dict: The updated edge_list dictionary.

    edge_list has the following format;
        {("edgestart", "edgeend"): {"weight":5, ..}, ..}
    """

    edge_list = {}

    for edge in re.findall(
        r"^ *(.*?) *-> *(.*?) *\[label=\"(.*?)\"", data, re.M
    ):
        if edge[0] != "__start0 ":
            if edge[2] != "":
                edge_list[(edge[0], edge[1])] = {"weight": str(edge[2])}
            else:
                edge_list[(edge[0], edge[1])] = {}

    return edge_list


def convert_to_networkx(
    events_reference: dict = {}, edge_list: dict = {}, out_path: str = ""
):
    """
    Converts the given events reference and edge list into a NetworkX graph.

    Args:
        events_reference (dict): A dictionary containing the events reference.
        edge_list (dict): A dictionary containing the edge list.
        write (bool, optional): Indicates whether to write the graph to a file.
            Defaults to False.

    Returns:
        graph (nx.MultiDiGraph): The converted NetworkX graph.
    """

    graph = nx.MultiDiGraph()

    for item in events_reference:
        graph.add_node(item, label=events_reference[item])
    for item in edge_list:
        if "__start0" not in item:
            if "type" in edge_list[item]:
                graph.add_edge(
                    str(item[0]),
                    str(item[1]),
                    label=str(edge_list[item]["type"]),
                )
            else:
                graph.add_edge(
                    str(item[0]),
                    str(item[1]),
                    label=str(edge_list[item]["weight"]),
                )
    if out_path != "":
        graph.edges(data=True)
        nx.nx_agraph.write_dot(graph, out_path)

    return graph


if __name__ == "__main__":

    node_reference = {}
    events_reference = {}
    node_list = []
    edge_list = {}

    with open("Jalergia2PUML/jAlergiaModel.dot", "r") as file:
        data = file.read()

    node_reference, events_reference, node_list = get_nodes(data)
    edge_list = get_edges(data)

    convert_to_networkx(events_reference, edge_list, write=True)
