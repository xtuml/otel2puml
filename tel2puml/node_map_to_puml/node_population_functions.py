"""
This module contains functions for populating node data, printing outgoing
    nodes, and retrieving data from PUML files.
"""

from networkx import find_cycle
from tel2puml.node_map_to_puml.node import Node
import tel2puml.jAlergiaPipeline as jAlergiaPipeline


def populate_incoming(node, lookup_table, graph):
    """
    Populates the list of incoming nodes based on the lookup table
        and graph.

    Args:
        lookup_table: A dictionary mapping node data to Node objects.
        graph: The graph containing the nodes.

    Returns:
        None
    """
    for predecessor in graph.predecessors(node.uid):
        node.incoming.append(lookup_table[predecessor])


def populate_outgoing(
    node, graph, lookup_table, depth=0, max_depth=10, cycle_depth=-1
):
    """
    Populates the list of outgoing nodes based on the graph, lookup table,
        and maximum depth.

    Args:
        graph: The graph containing the nodes.
        lookup_table: A dictionary mapping node data to Node objects.
        max_depth: The maximum depth to traverse.

    Returns:
        The updated lookup table.
    """
    if depth < max_depth:

        successors = list(graph.successors(node.uid))
        for child in successors:

            print(child)
            if cycle_depth == -1:
                try:
                    cycle_depth = len(find_cycle(graph, child))
                except Exception:
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
        except Exception:
            pass
        if cycle != [["", ""]]:
            lookup_table[cycle[-1][0]].outgoing.insert(
                0, Node(uid="repeat while (unconstrained)", outgoing=[])
            )

    return lookup_table


def print_outgoing(node, depth=0, max_depth=10):
    """
    Prints the outgoing nodes recursively up to the specified maximum
        depth.

    Args:
        depth: The current depth of the recursion.
        max_depth: The maximum depth to print.

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


def get_puml_data_and_analyse_with_jalergia(
    puml_files: list, print_output: bool
):
    """
    Retrieves the PUML data and performs analysis using jAlergia.

    Args:
        puml_files (list): A list of PUML files.
        print_output (bool): Flag indicating whether to print the output.

    Returns:
        tuple: A tuple containing the graph list and event references.
    """
    graph_list, event_references = jAlergiaPipeline.main(
        puml_files=puml_files, print_output=print_output
    )

    return graph_list, event_references


def convert_to_nodes(graph_list, event_references, print_output: bool = False):
    """
    Retrieves data from the given graph list and returns lookup tables, node
        trees, and event references.

    Args:
        graph_list (list): A list of graphs.
        event_references: A list of references.
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


def copy_node(
    node: Node,
    uid=None,
    incoming=None,
    outgoing=None,
    incoming_logic=None,
    outgoing_logic=None,
):
    """
    Creates a copy of a given node with optional modifications to its
        attributes.

    Args:
        node (Node): The node to be copied.
        uid (Any, optional): The modified data for the copied node.
            Defaults to None.
        incoming (List[Edge], optional): The modified incoming edges for the
            copied node. Defaults to None.
        outgoing (List[Edge], optional): The modified outgoing edges for the
            copied node. Defaults to None.
        incoming_logic (Any, optional): The modified incoming logic for the
            copied node. Defaults to None.
        outgoing_logic (Any, optional): The modified outgoing logic for the
            copied node. Defaults to None.

    Returns:
        Node: The copied node with optional modifications.
    """
    return Node(
        uid=node.uid if uid is None else uid,
        incoming=node.incoming if incoming is None else incoming,
        outgoing=node.outgoing if outgoing is None else outgoing,
        incoming_logic=(
            node.incoming_logic if incoming_logic is None else incoming_logic
        ),
        outgoing_logic=(
            node.outgoing_logic if outgoing_logic is None else outgoing_logic
        ),
    )


if __name__ == "__main__":

    print_output = True

    graph_list, event_references = get_puml_data_and_analyse_with_jalergia(
        "simple_test", print_output
    )
    lookup_tables, node_trees, event_references = convert_to_nodes(
        graph_list, event_references, True
    )
