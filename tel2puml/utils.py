"""Utils for the tel2puml package."""
from datetime import datetime, UTC
from itertools import permutations
from typing import Optional, Generator, Any, TypeVar, Iterable, Hashable

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

T = TypeVar("T")


def get_weighted_cover(
    event_sets: set[frozenset[Any]],
    universe: frozenset[Any]
) -> Optional[set[Any]]:
    """
    Get the weighted cover of the event set with respect to the universe, if it
    exists. The weighted cover is a set of elements from the event set that
    cover all elements in the universe, with a penalty on set size.

    :param event_set: The set of events from which to choose covering elements.
    :type event_set: `set`
    :param universe: The set of elements to be covered by the weighted cover.
    :type universe: `set`
    :return: The weighted cover of the event set with respect to the universe.
    :rtype: `set` or `None`
    """
    if universe in event_sets:
        event_sets.remove(universe)
    # if the event set is empty, return None otherwise there is a zero division
    if not event_sets:
        return None
    weighted_cover: set[Any] = set()
    while universe:
        subset = max(
            event_sets,
            key=lambda s: len(s & universe) / len(s)**2
        )

        pre_size = len(universe)
        weighted_cover.add(subset)
        universe -= subset

        if pre_size == len(universe):
            return None

    for event_set in event_sets:
        for cover_set in weighted_cover:
            if event_set & cover_set == cover_set:
                event_set -= cover_set
        if len(event_set) > 0:
            return None

    for x, y in permutations(weighted_cover, 2):
        if len(x & y) > 0:
            return None

    return weighted_cover


def convert_nested_generator_to_generator_of_list(
    nested_generator: Generator[Generator[T, Any, None], Any, None]
) -> Generator[list[T], Any, None]:
    """Convert a nested generator to a generator of lists.

    :param nested_generator: The nested generator to be converted.
    :type nested_generator: `Generator[Generator[T, Any, None], Any, None]`
    :return: A generator of lists.
    :rtype: `Generator[list[T], Any, None]`

    """
    for item in nested_generator:
        yield list(item)


def get_graphviz_plot(
    nx_graph: "nx.DiGraph[Any]", figsize: tuple[int, int] | None = (10, 10)
) -> Figure:
    """Creates a :class:`plt.Figure` object containing the plot of the
    input graph

    :param nx_graph: the networkx Directed Graph to plot
    :type nx_graph: :class:`nx.DiGraph`[`Any`]
    :return: Returns a :class:`Figure` objects containing the plot
    :rtype: :class:`Figure`
    """
    pos = nx.nx_agraph.graphviz_layout(nx_graph, prog="dot")
    fig, axis = plt.subplots(figsize=figsize)
    nx.draw(
        nx_graph,
        pos,
        ax=axis,
        with_labels=True,
        arrows=True,
        node_size=1500,
        font_size=22,
        font_weight="bold",
        font_color="k",
        node_color="C1",
        width=5.0,
        style="dotted",
        edge_color="C0",
    )
    return fig


def check_has_path_not_through_nodes(
    graph: "nx.DiGraph[Any]",
    source_node: Hashable,
    target_node: Hashable,
    nodes_to_avoid: Iterable[Hashable]
) -> bool:
    """Checks if there is a path between the source and target nodes that
    does not pass through any of the nodes to avoid.

    :param graph: The graph to check.
    :type graph: :class:`DiGraph`[`Any`]
    :param source_node: The source node to check.
    :type source_node: :class:`Hashable`
    :param target_node: The target node to check.
    :type target_node: :class:`Hashable`
    :param nodes_to_avoid: The nodes to avoid.
    :type nodes_to_avoid: `Iterable[:class:`Hashable`]`
    :return: Whether there is a path between the source and target nodes
    that does not pass through any
    of the nodes to avoid.
    :rtype: `bool`
    """
    if source_node == target_node:
        return True
    if not nx.has_path(graph, source_node, target_node):
        return False
    for node_to_avoid in nodes_to_avoid:
        if (
            nx.has_path(graph, source_node, node_to_avoid)
        ) and (
            nx.has_path(graph, node_to_avoid, target_node)
        ):
            return False
    return True


def check_has_path_between_all_nodes(
    graph: "nx.DiGraph[Any]", source_nodes: Iterable[Hashable],
    target_nodes: Iterable[Hashable]
) -> bool:
    """Checks if there is a path between all source and target nodes.

    :param graph: The graph to check.
    :type graph: :class:`DiGraph`[`Any`]
    :param source_nodes: The source nodes to check.
    :type source_nodes: `Iterable[:class:`Hashable`]`
    :param target_nodes: The target nodes to check.
    :type target_nodes: `Iterable[:class:`Hashable`]`
    :rtype: `bool`
    """
    for source_node in source_nodes:
        for target_node in target_nodes:
            if source_node == target_node:
                continue
            if not nx.has_path(graph, source_node, target_node):
                return False
    return True


def gen_strings_from_files(
    file_names: Iterable[str]
) -> Generator[str, Any, None]:
    """Generates strings from utf-8 files.

    :param file_names: The names of the files to read.
    :type file_names: `Iterable`[`str`]
    :return: A generator of strings.
    :rtype: `Generator`[`str`, Any, None]
    """
    for file_name in file_names:
        with open(
            file_name, "r", encoding="utf-8"
        ) as file:
            yield file.read()


def circularly_identical(list1: list[Any], list2: list[Any]) -> bool:
    """Check if two lists are circularly identical.

    :param list1: The first list to compare.
    :type list1: `list`
    :param list2: The second list to compare.
    :type list2: `list`
    :return: Whether the lists are circularly identical.
    :rtype: `bool`
    """
    # doubling list
    compare_list = list1 * 2

    # traversal in twice of list1
    for i in range(len(compare_list)):

        # check if sliced list1 is equal to list2
        if list2 == compare_list[i: i + len(list2)]:

            return True
    return False


def datetime_to_pv_string(date_time: datetime) -> str:
    """Convert a datetime object to a pv string.

    :param date_time: The datetime object to convert.
    :type date_time: `datetime`
    :return: The pv string.
    :rtype: `str`
    """
    return date_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def unix_nano_to_pv_string(unix_nano: int) -> str:
    """Convert a unix nano timestamp to a pv string.

    :param unix_nano: The unix nano timestamp to convert.
    :type unix_nano: `int`
    :return: The pv string.
    :rtype: `str`
    """
    return datetime_to_pv_string(
        datetime.fromtimestamp(unix_nano / 1e9, tz=UTC)
    )


def check_is_sub_list(
    sub_list: list[Any], super_list: list[Any]
) -> bool:
    """Check if the first list is a sublist of the second list.

    :param sub_list: The sublist to check.
    :type sub_list: `list`
    :param super_list: The superlist to check.
    :type super_list: `list`
    :return: Whether the first list is a sublist of the second list.
    :rtype: `bool`
    """
    return any(
        super_list[idx: idx + len(sub_list)] == sub_list
        for idx in range(len(super_list) - len(sub_list) + 1)
    )


def get_nodes_with_outedges_not_in_set(
    nodes: set[T], nodes_to_check: set[T],
    graph: "nx.DiGraph[T]"
) -> set[T]:
    """Get the subset of nodes that have out edges that do not lead to nodes
    in the given set of nodes.

    :param nodes: The set of nodes to get the out edges from
    :type nodes: `set`[:class:`Any`]
    :param nodes_to_check: The set of nodes to check if the out edges lead to
    :type nodes_to_check: `set`[:class:`Any`]
    :param graph: The graph to find the out edges from
    :type graph: :class:`DiGraph`[:class:`Any`]
    :return: The out edges of the nodes that do not lead to nodes in the
    given set of nodes
    :rtype: `set`[`tuple`[:class:`Any`, :class:`Any`]]
    """
    return set(
        edge[0]
        for edge in graph.out_edges(nodes)
        if edge[1] not in nodes_to_check
    )


def get_nodes_with_outedges_in_set(
    nodes: set[T], nodes_to_check: set[T],
    graph: "nx.DiGraph[T]"
) -> set[T]:
    """Get the subset of nodes that have out edges that lead to nodes in the
    given set of nodes.

    :param nodes: The set of nodes to get the out edges from
    :type nodes: `set`[:class:`Any`]
    :param nodes_to_check: The set of nodes to check if the out edges lead to
    :type nodes_to_check: `set`[:class:`Any`]
    :param graph: The graph to find the out edges from
    :type graph: :class:`DiGraph`[:class:`Any`]
    :return: The out edges of the nodes that lead to nodes in the given set
    of nodes
    :rtype: `set`[`tuple`[:class:`Any`, :class:`Any`]]
    """
    return set(
        edge[0]
        for edge in graph.out_edges(nodes)
        if edge[1] in nodes_to_check
    )


def get_outnodes_not_in_set(
    nodes: set[T], nodes_to_check: set[T],
    graph: "nx.DiGraph[T]"
) -> set[T]:
    """Get the subset of nodes that have out edges that do not lead to nodes
    in the given set of nodes.

    :param nodes: The set of nodes to get the out edges from
    :type nodes: `set`[:class:`Any`]
    :param nodes_to_check: The set of nodes to check if the out edges lead to
    :type nodes_to_check: `set`[:class:`Any`]
    :param graph: The graph to find the out edges from
    :type graph: :class:`DiGraph`[:class:`Any`]
    :return: The out edges of the nodes that do not lead to nodes in the
    given set of nodes
    :rtype: `set`[:class:`Any`]
    """
    return set(
        edge[1]
        for edge in graph.out_edges(nodes)
        if edge[1] not in nodes_to_check
    )


def get_innodes_not_in_set(
    nodes: set[T], nodes_to_check: set[T],
    graph: "nx.DiGraph[T]"
) -> set[T]:
    """Get a set of nodes that are the start node of a directed edge from
    the input set of nodes that do not come from the set of nodes to check.

    :param nodes: The set of nodes to get the in edges from
    :type nodes: `set`[:class:`Any`]
    :param nodes_to_check: The set of nodes to check if the in edges come
    from
    :type nodes_to_check: `set`[:class:`Any`]
    :param graph: The graph to find the in edges from
    :type graph: :class:`DiGraph`[:class:`Any`]
    :return: The in edges of the nodes that do not come from nodes in the
    given set of nodes
    :rtype: `set`[:class:`Any`]
    """
    return set(
        edge[0]
        for edge in graph.in_edges(nodes)
        if edge[0] not in nodes_to_check
    )


def get_nodes_with_inedge_not_in_set(
    nodes: set[T], nodes_to_check: set[T],
    graph: "nx.DiGraph[T]"
) -> set[T]:
    """Get the subset of nodes that have in edges that do not come from nodes
    in the given set of nodes.

    :param nodes: The set of nodes to get the in edges from
    :type nodes: `set`[:class:`Any`]
    :param nodes_to_check: The set of nodes to check if the in edges come from
    :type nodes_to_check: `set`[:class:`Any`]
    :param graph: The graph to find the in edges from
    :type graph: :class:`DiGraph`[:class:`Any`]
    :return: The in edges of the nodes that do not come from nodes in the
    given set of nodes
    :rtype: `set`[:class:`Any`]
    """
    return set(
        edge[1]
        for edge in graph.in_edges(nodes)
        if edge[0] not in nodes_to_check
    )


def has_path_back_to_chosen_nodes(
    node: T,
    nodes_to_find_path_from: set[T],
    graph: "nx.DiGraph[T]",
) -> bool:
    """Check if there is a path back to the chosen nodes.

    :param node: The node to check if there is a path back to the chosen nodes.
    :type node: :class:`T`
    :param nodes_to_find_path_from: The nodes to find a path from.
    :type nodes_to_find_path_from: `set`[:class:`T`]
    :param graph: The graph to find the path from.
    :type graph: :class:`DiGraph`[:class:`T`]
    :return: If there is a path back to the chosen nodes.
    :rtype: `bool`
    """
    for node_to_find_path_from in nodes_to_find_path_from:
        if nx.has_path(graph, node_to_find_path_from, node):
            return True
    return False


def identify_nodes_without_path_back_to_chosen_nodes(
    nodes: set[T],
    nodes_to_find_path_from: set[T],
    graph: "nx.DiGraph[T]",
) -> Generator[T, Any, None]:
    """Identify nodes that do not have a path back to the chosen nodes.

    :param nodes: The set of nodes to identify.
    :type nodes: `set`[:class:`T`]
    :param nodes_to_find_path_from: The set of nodes to find a path from.
    :type nodes_to_find_path_from: `set`[:class:`T`]
    :param graph: The graph to find the path from.
    :type graph: :class:`DiGraph`[:class:`T`]
    :return: A generator of nodes that do not have a path back to the chosen
    nodes.
    :rtype: `Generator`[:class:`T`, Any, None]
    """
    for node in nodes:
        if not has_path_back_to_chosen_nodes(
            node, nodes_to_find_path_from, graph
        ):
            yield node


def remove_nodes_without_path_back_to_loop(
    nodes: set[T],
    loop_nodes: set[T],
    graph: "nx.DiGraph[T]",
) -> None:
    """Remove nodes that do not have a path back to the loop nodes.

    :param nodes: The set of nodes to remove.
    :type nodes: `set`[:class:`T`]
    :param loop_nodes: The set of loop nodes.
    :type loop_nodes: `set`[:class:`T`]
    :param graph: The graph to remove the nodes from.
    :type graph: :class:`DiGraph`[:class:`T`]
    """
    nodes_without_path_back_to_loop_nodes = set(
        identify_nodes_without_path_back_to_chosen_nodes(
            set(nodes), loop_nodes, graph
        )
    )
    for node in nodes_without_path_back_to_loop_nodes:
        if node in graph.nodes:
            graph.remove_node(node)
