"""Utils for the tel2puml package."""

from itertools import permutations
from typing import Optional, Generator, Any, TypeVar, Iterable, Hashable

import networkx as nx
import matplotlib.pyplot as plt

T = TypeVar("T")


def get_weighted_cover(
        event_sets: set[set[Any] | frozenset[Any]],
        universe: set[Any]
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
    nx_graph: nx.DiGraph, figsize: tuple | None = (10, 10)
) -> plt.Figure:
    """Creates a :class:`plt.Figure` object containing the plot of the
    input graph

    :param nx_graph: the networkx Directed Graph to plot
    :type nx_graph: :class:`nx.DiGraph`
    :return: Returns a :class:`plt.Figure` objects containing the plot
    :rtype: :class:`plt.Figure`
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
    graph: nx.DiGraph,
    source_node: Hashable,
    target_node: Hashable,
    nodes_to_avoid: Iterable[Hashable]
) -> bool:
    """Checks if there is a path between the source and target nodes that
    does not pass through any of the nodes to avoid.

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
    graph: nx.DiGraph, source_nodes: Iterable[Hashable],
    target_nodes: Iterable[Hashable]
) -> bool:
    """Checks if there is a path between all source and target nodes.

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
