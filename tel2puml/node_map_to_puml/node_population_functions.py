"""
This module contains functions for populating node data, printing outgoing
    nodes, and retrieving data from PUML files.
"""

from networkx import find_cycle, exception
from tel2puml.node_map_to_puml.node import Node
import tel2puml.jAlergiaPipeline as jAlergiaPipeline


def populate_incoming(node: Node, lookup_table: dict, graph):
    """
    Populates the list of incoming nodes based on the lookup table
        and graph.

    Args:
        node (Node): The node for which the incoming list needs to be
            populated.
        lookup_table (dict): A dictionary mapping node UIDs to their
            corresponding nodes.
        graph: The graph containing the nodes.

    Returns:
        None
    """
    for predecessor in graph.predecessors(node.uid):
        node.incoming.append(lookup_table[predecessor])


def populate_outgoing(
    node: Node,
    graph,
    lookup_table: dict,
    depth: int = 0,
    max_depth: int = 10,
    cycle_depth: int = -1,
):
    """
    Populates the list of outgoing nodes based on the graph, lookup table,
        and maximum depth.

    Args:
        node (Node): The node for which to populate the outgoing nodes.
        graph: The graph containing the nodes.
        lookup_table (dict): A dictionary mapping node IDs to Node objects.
        depth (int, optional): The current depth of recursion. Defaults to 0.
        max_depth (int, optional): The maximum depth of recursion.
            Defaults to10.
        cycle_depth (int, optional): The depth of the cycle in the graph.
            Defaults to -1.

    Returns:
        dict: The updated lookup table with the populated outgoing nodes.
    """

    if depth < max_depth:

        successors = list(graph.successors(node.uid))
        for child in successors:

            print(child)
            if cycle_depth == -1:
                try:
                    cycle_depth = len(find_cycle(graph, child))
                except exception.NetworkXNoCycle:
                    cycle_depth = -1

            if child not in lookup_table:
                lookup_table[child] = Node(child)

            if cycle_depth != 0:
                lookup_table = populate_outgoing(
                    lookup_table[child],
                    graph,
                    lookup_table,
                    depth + 1,
                    max_depth,
                    cycle_depth - 1,
                )

                if lookup_table[child] not in node.outgoing:
                    node.outgoing.append(lookup_table[child])
            else:
                cycle_depth = -1

    if depth == 0:
        cycle = [["", ""]]
        try:
            cycle = find_cycle(graph)
        except exception.NetworkXNoCycle:
            pass
        if cycle != [["", ""]]:
            lookup_table[cycle[-1][0]].outgoing.insert(
                0, Node(uid="repeat while (unconstrained)", outgoing=[])
            )

    return lookup_table


def print_outgoing(node: Node, depth: int = 0, max_depth: int = 10):
    """
    Prints the outgoing nodes recursively up to the specified maximum
        depth.

    Args:
        node (Node): The head node of the tree to print.
        depth (int): The current depth of the recursion.
        max_depth (int): The maximum depth to print.

    Returns:
        None
    """
    space_chars = "  "
    if depth < max_depth:
        print(f"{space_chars*(depth)}-> {node.uid}")
        if len(node.outgoing) > 1:
            for child_node in node.outgoing:
                print_outgoing(
                    node=child_node, depth=depth + 1, max_depth=max_depth
                )

        elif len(node.outgoing) > 0:
            print_outgoing(
                node=node.outgoing[-1], depth=depth + 1, max_depth=max_depth
            )


def convert_to_nodes(
    graph_list: list, event_references: list, print_output: bool = False
):
    """
    Retrieves data from the given graph list and returns lookup tables, node
        trees, and event references.

    Args:
        graph_list (list): A list of graphs.
        event_references (list): A list of references.
        print_output (bool, optional): Whether to print the output. Defaults to
            False.

    Returns:
        tuple: A tuple containing lookup tables, node trees, and event
            references.
    """
    head_nodes = []
    lookup_tables = []
    lookup_table = {}
    node_trees = []

    for graph in graph_list:
        lookup_table = {}

        for node in graph.nodes():
            if graph.in_degree(node) == 0:
                head_nodes.append(node)
        # Assuming there is only one head node
        head_node = head_nodes[0] if head_nodes else None
        node = Node(head_node)
        lookup_table[node.uid] = node
        lookup_table = populate_outgoing(
            node=node, graph=graph, lookup_table=lookup_table, max_depth=10
        )

        for item in lookup_table:
            populate_incoming(lookup_table[item], lookup_table, graph)

        lookup_tables.append(lookup_table)
        node_trees.append(node)

        if print_output:
            print_outgoing(node)

    return lookup_tables, node_trees, event_references


def create_event_node_ref(
    lookup_table: dict[str, Node], node_references: dict[str, str]
) -> dict[str, list[Node]]:
    """Creates a reference to the nodes based on the event type from the
    network x uid nodes event reference and the lookup table containing the
    Nodes

    :param lookup_table: A dictionary containing the lookup table of the nodes
    :type lookup_table: `dict`[`str`, :class:`Node`]
    :param node_references: A dictionary containing the network x node
    references
    :type node_references: `dict`[`str`, `str`]
    :return: A dictionary containing the event type and the list of nodes
    :rtype: `dict`[`str`, `list`[:class:`Node`]]
    """
    node_ref = {}
    for event_type, nodes in node_references.items():
        node_ref[event_type] = []
        for uid in nodes:
            if uid not in lookup_table:
                raise ValueError(f"Node {uid} not found in lookup table")
            node = lookup_table[uid]
            node.event_type = event_type
            node_ref[event_type].append(node)
    return node_ref


if __name__ == "__main__":

    print_output = True

    graph_list, event_references = jAlergiaPipeline.process_puml_into_graphs(
        "simple_test", print_output
    )
    lookup_tables, node_trees, event_references = convert_to_nodes(
        graph_list, event_references, True
    )