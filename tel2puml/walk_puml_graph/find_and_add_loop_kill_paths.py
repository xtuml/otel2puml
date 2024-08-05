"""Module for finding and adding loop kill paths to the node map."""

from networkx import DiGraph

from tel2puml.loop_detection.calculate_loop_components import (
    get_all_kill_edges_from_loop_nodes_and_end_points,
)
from tel2puml.walk_puml_graph.node import Node, SubGraphNode
from tel2puml.walk_puml_graph.node_update import (
    get_node_to_node_map_from_edges,
    add_loop_kill_paths_for_nodes,
)


def find_and_add_loop_kill_paths_to_nested_graphs(
    graph: "DiGraph[Node]",
) -> None:
    """Finds and adds loop kill paths to all the nested graphs in the given
    graph.

    :param graph: The graph to find and add loop kill paths to
    :type graph: :class:`DiGraph`[:class:`Node`]
    """
    # get all subgraph nodes
    subgraph_nodes = [
        node for node in graph.nodes if isinstance(node, SubGraphNode)
    ]
    for subgraph_node in subgraph_nodes:
        find_and_add_loop_kill_paths_to_sub_graph_node(subgraph_node)
        find_and_add_loop_kill_paths_to_nested_graphs(subgraph_node.sub_graph)


def find_and_add_loop_kill_paths_to_sub_graph_node(
    sub_graph_node: SubGraphNode,
) -> None:
    """Finds and adds loop kill paths to the given sub graph node.

    :param sub_graph_node: The sub graph node to find and add loop kill paths
    to
    :type sub_graph_node: :class:`SubGraphNode`
    """
    # get the end points using the uid
    end_point = [
        node
        for node in sub_graph_node.sub_graph.nodes
        if node.uid == sub_graph_node.end_uid
    ].pop()
    start_point = [
        node
        for node in sub_graph_node.sub_graph.nodes
        if node.uid == sub_graph_node.start_uid
    ].pop()
    # get all the kill edges and convert these to strings of uid to uid
    kill_edges = list(
        get_all_kill_edges_from_loop_nodes_and_end_points(
            sub_graph_node.sub_graph,
            sub_graph_node.sub_graph.nodes,
            {end_point},
            {start_point},
        )
    )
    kill_edge_uids: list[tuple[str, str]] = []
    for edge in kill_edges:
        if edge[0].uid is None:
            raise ValueError("Edge start uid is None.")
        if edge[1].uid is None:
            raise ValueError("Edge end uid is None.")
        kill_edge_uids.append((edge[0].uid, edge[1].uid))
    # get node to node map and add loop kill paths for nodes
    node_to_node_map = get_node_to_node_map_from_edges(kill_edge_uids)
    add_loop_kill_paths_for_nodes(node_to_node_map, sub_graph_node.sub_graph)
