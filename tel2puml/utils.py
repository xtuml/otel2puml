"""Utils for the tel2puml package."""

from itertools import permutations
from typing import Optional, Generator, Any, TypeVar

import networkx as nx
import matplotlib.pyplot as plt

T = TypeVar("T")


def get_weighted_cover(
        event_set: set[set | frozenset],
        universe: set
) -> Optional[set]:
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
    if universe in event_set:
        event_set.remove(universe)

    weighted_cover = set()
    while universe:
        subset = max(
            event_set,
            key=lambda s: len(s & universe) / len(s)**2
        )

        pre_size = len(universe)
        weighted_cover.add(subset)
        universe -= subset

        if pre_size == len(universe):
            return None

    for event_set in event_set:
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
