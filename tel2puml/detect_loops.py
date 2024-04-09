"""A module to detect all loops in a graph."""
from typing import Self, Optional, Union

from networkx import DiGraph, simple_cycles, all_simple_paths


class Loop:
    """A class to represent a loop in a graph."""

    def __init__(self, nodes: list[str]):
        self.nodes = nodes
        self.sub_loops: list[Loop] = []
        self.edges_to_remove: set[tuple[str, str]] = set()
        self.break_edges: set[tuple[str, str]] = set()
        self.break_points: set[str] = set()
        self.exit_point: Optional[str] = None
        self.merge_processed = False

    def __len__(self) -> int:
        """Return the length of the loop.

        :return: The number of nodes in the loop.
        :rtype: `int`
        """
        return len(self.nodes)

    def get_edges(self) -> set[tuple[str, str]]:
        """Return the edges of the loop.

        :return: The edges of the loop.
        :rtype: `set`[`tuple`[`str`, `str`]]
        """
        if self.merge_processed:
            raise RuntimeError("Method not available after merge")

        return {
            (u, v)
            for u, v in zip(self.nodes, self.nodes[1:] + self.nodes[:1])
        }

    def check_subloop(self, other: Self) -> bool:
        """Check if the other loop is a subloop of the current loop.

        :param other: The other loop to check.
        :type other: `Loop`
        :return: whether is a subloop or not.
        :rtype: `bool`
        """
        if self.merge_processed:
            raise RuntimeError("Method not available after merge")
        if other.get_edges() == self.get_edges():
            return False
        for sublist in self.get_sublist_of_length(self.nodes, len(other)):
            if sublist == other.nodes:
                return True
        return False

    def add_edge_to_remove(self, edge: tuple[str, str]) -> None:
        """Add an edge to remove from the loop.

        :param edge: The edge to remove.
        :type edge: `tuple`[`str`, `str`]
        """
        if self.merge_processed:
            raise RuntimeError("Method not available after merge")
        self.edges_to_remove.add(edge)

    def add_break_edge(self, break_edge: tuple[str, str]) -> None:
        """Add a break edge to the loop.

        :param break_point: The break edge to add.
        :type break_point: `tuple`[`str`, `str`]
        """
        if self.merge_processed:
            raise RuntimeError("Method not available after merge")
        self.break_edges.add(break_edge)

    def add_break_point(self, break_point: str) -> None:
        """Add a break point to the loop.

        :param break_point: The break point to add.
        :type break_point: `str`
        """
        self.break_points.add(break_point)

    @staticmethod
    def get_sublist_of_length(
            list: list[str],
            length: int
    ) -> list[list[str]]:
        """Return all possible sublists of a given length.

        :param list: The list to get the sublists from.
        :type list: `list`[`str`]
        :param length: The length of the sublists.
        :type length: `int`
        :return: A list of all possible sublists of the given length.
        :rtype: `list`[`list`[`str`]]
        """
        non_overlap = [
            list[i:i+length]
            for i in range(len(list)-length+1)
        ]
        overlap = [
            list[-i:] + list[:-i+length]
            for i in range(length-1, 0, -1)
        ]
        return non_overlap + overlap

    def add_subloop(self, sub_loop: Self) -> None:
        """Add a subloop to the current loop.

        :param sub_loop: The subloop to add.
        :type sub_loop: `Loop`
        """
        self.sub_loops.append(sub_loop)

    def set_merged(self) -> None:
        """Set the merge_processed property to True."""
        self.merge_processed = True

    def set_exit_point(self, exit_point: str) -> None:
        """Set the exit point of the loop.

        :param exit_point: The exit point of the loop.
        :type exit_point: `str`
        """
        self.exit_point = exit_point


def detect_loops(graph: DiGraph) -> list[Loop]:
    """Detect all loops in a graph.

    :param graph: The graph to detect the loops from.
    :type graph: `DiGraph`
    :return: A list of all loops in the graph.
    :rtype: `list`[`Loop`]
    """
    loops_with_ref = [Loop(loop_list) for loop_list in simple_cycles(graph)]
    edges = [(u, v) for u, v in graph.edges()]

    loops = add_loop_edges_to_remove_and_breaks(
        loops_with_ref, edges
    )
    loops = update_subloops(loops)
    loops = merge_loops(loops)
    loops = update_break_points(graph, loops)
    return merge_break_points(loops)


def add_loop_edges_to_remove_and_breaks(
        loops: list[Loop],
        edges: list[tuple[str, str]]
) -> list[Loop]:
    """Add the edges to remove from the loops to the edge_to_remove property of
    the Loop.

    :param loops: The loops to add the edges to remove.
    :type loops: `list`[`Loop`]
    :param edges: The edges to add to the loops.
    :type edges: `list`[`tuple`[`str`, `str`]]
    :return: The updated loops.
    :rtype: `list`[`Loop`]
    """
    loop_edges = {
        edge
        for loop in loops
        for edge in loop.get_edges()
    }
    for loop in loops:
        if len(loop) == 1:
            loop.add_edge_to_remove((loop.nodes[0], loop.nodes[0]))
        else:
            entries: set[str] = set()
            exits: set[tuple[str, str]] = set()
            for u, v in edges:
                if u not in loop.nodes and v in loop.nodes:
                    entries.add(v)
                elif u in loop.nodes and v not in loop.nodes:
                    exits.add((u, v))

            if entries and exits:
                edges_to_remove = {
                    (u, v)
                    for u, v in loop_edges
                    if v in entries
                    and u in {u for u, _ in exits}
                }

                breaks = {
                    (u, v)
                    for u, v in exits.difference(loop_edges)
                    if u not in {u for u, _ in edges_to_remove}
                }

                for break_point in breaks:
                    loop.add_break_edge(break_point)

                exit_points = set()
                for u, v in edges_to_remove:
                    loop.add_edge_to_remove((u, v))
                    for loop_exit, exit_point in exits.difference(loop_edges):
                        if u == loop_exit:
                            exit_points.add(exit_point)

                if len(exit_points) == 1:
                    loop.set_exit_point(exit_points.pop())
                else:
                    raise ValueError("Multiple exit points")
            else:
                raise ValueError("No entries or no exits")

    return loops


def update_subloops(loops: list[Loop]) -> list[Loop]:
    """Update the subloops of the loops. Remove any loops that are subsequently
    defined as subloops of another loop.

    :param loops: The loops to update the subloops.
    :type loops: `list`[`Loop`]
    :return: The updated loops.
    :rtype: `list`[`Loop`]
    """
    updated_loops = []
    loops.sort(key=lambda x: len(x))

    while len(loops) > 0:
        potential_subloop = loops.pop(0)
        is_subloop = False
        current_filter_length: Optional[int] = None
        for loop in loops:
            if loop.check_subloop(potential_subloop):
                if not is_subloop:
                    loop.add_subloop(potential_subloop)
                    is_subloop = True
                    current_filter_length = len(loop)
                elif len(loop) <= current_filter_length:
                    loop.add_subloop(potential_subloop)
                else:
                    break

        if not is_subloop:
            updated_loops.append(potential_subloop)

    return updated_loops


def merge_loops(loops: list[Loop]) -> list[Loop]:
    """Merge the loops which have common edges to remove.

    :param loops: The loops to merge.
    :type loops: `list`[`Loop`]
    :return: The merged loops.
    :rtype: `list`[`Loop`]
    """
    merged_loops: list[Loop] = []
    while len(loops) > 0:
        loop = loops.pop(0)
        loop.sub_loops = merge_loops(loop.sub_loops)
        merged = False
        for merged_loop in merged_loops:
            if loop.edges_to_remove.issubset(merged_loop.edges_to_remove):
                for node in loop.nodes:
                    if node not in merged_loop.nodes:
                        merged_loop.nodes.append(node)
                for sub_loop in loop.sub_loops:
                    if sub_loop not in merged_loop.sub_loops:
                        merged_loop.sub_loops.append(sub_loop)
                loop.set_merged()
                merged = True
                break

        if not merged:
            loop.set_merged()
            merged_loops.append(loop)

    return merged_loops


def update_break_points(
        graph: DiGraph,
        loops: list[Loop],
        sub_loop: bool = False,
) -> Union[list[Loop], list[str]]:
    """Update the break points of the loops. Add any break points from subloops
    by recursively calling this function.

    :param graph: The graph to get the paths from.
    :type graph: `DiGraph`
    :param loops: The loops to update the break points.
    :type loops: `list`[`Loop`]
    :param sub_loop: Whether the loops are subloops or not.
    :type sub_loop: `bool`
    :return: The updated loops.
    :rtype: `list`[`Loop`]
    """
    breaks_from_subloops = []
    for loop in loops:
        from_subloops = update_break_points(
            graph,
            loop.sub_loops,
            sub_loop=True
        )
        for node in from_subloops:
            if node not in loop.nodes:
                loop.nodes.append(node)
                breaks_from_subloops.append(node)

        for _, v in loop.break_edges:
            paths = list(all_simple_paths(graph, v, loop.exit_point))
            if len(paths) == 1:
                path, = paths
                for node in path[:-1]:
                    if node not in loop.nodes:
                        loop.nodes.append(node)
                        breaks_from_subloops.append(node)
                loop.add_break_point(path[-2])

            elif len(paths) > 1:
                raise ValueError("Multiple paths")
            else:
                raise ValueError("No paths")

    if sub_loop:
        return breaks_from_subloops
    return loops


def merge_break_points(loops: list[Loop]) -> list[Loop]:
    """Merge the break points of the loops.

    :param loops: The loops to merge the break points.
    :type loops: `list`[`Loop`]
    :return: The merged loops.
    :rtype: `list`[`Loop`]
    """
    merged_loops: list[Loop] = []
    loops.sort(key=lambda x: len(x), reverse=True)
    while len(loops) > 0:
        loop = loops.pop(0)
        loop.sub_loops = merge_break_points(loop.sub_loops)
        merged = False
        for merged_loop in merged_loops:
            if set(loop.nodes).issubset(set(merged_loop.nodes)):
                merged_loop.add_subloop(loop)
                merged_loop.sub_loops = merge_break_points(
                    merged_loop.sub_loops
                )
                merged = True
                break

        if not merged:
            merged_loops.append(loop)

    return merged_loops