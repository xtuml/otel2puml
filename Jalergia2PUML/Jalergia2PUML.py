import re
import networkx as nx


def getNodes(
    data: str, nodeReference: dict, eventsReference: dict, nodeList: list
):
    """
    Extracts nodes from the given data and updates the nodeReference, eventsReference, and nodeList.

    Args:
        data (str): The input data containing node information.
        nodeReference (dict): A dictionary to store the node references.
        eventsReference (dict): A dictionary to store the event references.
        nodeList (list): A list to store the node names.

    Returns:
        tuple: A tuple containing the updated nodeReference, eventsReference, and nodeList.

    These returns are formatted as following:
    nodeReference   - {'event': 'node', ..}
    eventsReference - {'node': ['event1', 'event2', ..], ..}
    nodeList        - ["node1", "node2", ..]
    """
    for node in re.findall(r"(.*?) \[shape=\".*?\",label=\"(.*?)\"", data):
        if node[1] not in nodeReference:
            nodeReference[node[1]] = [node[0]]
            eventsReference[node[0]] = node[1]
            nodeList.append(node[1])
        else:
            nodeReference[node[1]].append([node[0]])
            eventsReference[node[0]] = node[1]

    return nodeReference, eventsReference, nodeList


def getEdges(data: str, edgeList: dict):
    """
    Extracts edges from the given data and populates the edgeList dictionary.

    Args:
        data (str): The input data containing edge information.
        edgeList (dict): The dictionary to store the extracted edges.

    Returns:
        dict: The updated edgeList dictionary.

    edgeList has the following format; {("edgestart", "edgeend"): {"weight":5, ..}, ..}
    """
    for edge in re.findall(r"(.*?)->(.*?) \[label=\"(.*?)\"", data):
        if edge[0] != "__start0 ":
            if edge[2] != "":
                edgeList[(edge[0], edge[1])] = {"weight": str(edge[2])}
            else:
                edgeList[(edge[0], edge[1])] = {}

    return edgeList


def convertToNetworkX(eventsReference: dict, edgeList: dict, write=False):

    graph = nx.MultiDiGraph()

    for item in eventsReference:
        graph.add_node(item, label=eventsReference[item])
    for item in edgeList:
        graph.add_edge(
            str(item[0]), str(item[1]), label=str(edgeList[item]["weight"])
        )
    if write:
        graph.edges(data=True)
        nx.nx_agraph.write_dot(graph, "./graphtest.dot")

    return graph


if __name__ == "__main__":

    nodeReference = {}
    eventsReference = {}
    nodeList = []
    edgeList = {}

    with open("Jalergia2PUML/jAlergiaModel.dot", "r") as file:
        data = file.read()

    nodeReference, eventsReference, nodeList = getNodes(
        data, nodeReference, eventsReference, nodeList
    )
    edgeList = getEdges(data, edgeList)

    convertToNetworkX(eventsReference, edgeList, write=True)
