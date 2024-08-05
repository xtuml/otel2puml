"""Module for updating the nodes with break points from loops."""
from typing import Iterable

from tel2puml.legacy_loop_detection.detect_loops import (
    Loop,
    get_all_break_points_from_loops,
)
from tel2puml.walk_puml_graph.node import Node
from tel2puml.tel2puml_types import PUMLEvent


def update_nodes_with_break_points(
    break_points: Iterable[str],
    event_node_reference: dict[str, list[Node]],
) -> None:
    """Updates the given nodes with the given break points.

    :param break_points: The break points to update the nodes with
    :type break_points: `Iterable`[`str`]
    :param event_node_reference: The event node reference to update
    :type event_node_reference: `dict`[`str`, `list`[:class:`Node`]]
    """
    for break_point in break_points:
        for node in event_node_reference[break_point]:
            node.update_event_types(PUMLEvent.BREAK)


def update_nodes_with_break_points_from_loops(
    loops: list[Loop],
    event_node_reference: dict[str, list[Node]],
) -> None:
    """Updates the given merged graph with the break points from the given
    loops.

    :param merged_graph: The merged graph to update with the break points
    :type merged_graph: :class:`DiGraph`
    :param loops: The loops to extract the break points from
    :type loops: `list`[:class:`Loop`]
    """
    break_points = get_all_break_points_from_loops(loops)
    update_nodes_with_break_points(break_points, event_node_reference)
