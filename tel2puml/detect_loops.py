"""A module to detect all loops in a graph."""
from typing import Self, Optional

from networkx import DiGraph, simple_cycles


class Loop:
    """A class to represent a loop in a graph."""

    def __init__(self, nodes: list[str]):
        self.nodes = nodes
        self.sub_loops: list[Loop] = []
        self.edges_to_remove: set[tuple[str, str]] = set()
        self.merge_processed = False

    def __len__(self) -> int:
        """Return the length of the loop.

        :return: The number of nodes in the loop.
        :rtype: `int`
        """
        return len(self.nodes)

    def get_node_cycles(self) -> list[str]:
        """Return all possible cycles of the loop.

        :return: A list of all possible cycles of the loop.
        :rtype: `list`[`str`]
        """
        if self.merge_processed:
            raise RuntimeError("Method not available after merge")
        index = 0
        cycles = []
        while index < len(self.nodes):
            cycles.append(self.nodes[index:] + self.nodes[:index])
            index += 1

        return cycles

    def check_subloop(self, other: Self) -> bool:
        """Check if the other loop is a subloop of the current loop.

        :param other: The other loop to check.
        :type other: `Loop`
        :return: whether is a subloop or not.
        :rtype: `bool`
        """
        if self.merge_processed:
            raise RuntimeError("Method not available after merge")
        if other.nodes in self.get_node_cycles():
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
        if self.merge_processed:
            raise RuntimeError("Method not available after merge")
        self.sub_loops.append(sub_loop)

    def set_merged(self) -> None:
        """Set the merge_processed property to True."""
        self.merge_processed = True


def detect_loops(graph: DiGraph) -> list[Loop]:
    """Detect all loops in a graph.

    :param graph: The graph to detect the loops from.
    :type graph: `DiGraph`
    :return: A list of all loops in the graph.
    :rtype: `list`[`Loop`]
    """
    loops_with_ref = [Loop(loop_list) for loop_list in simple_cycles(graph)]
    edges = [(u, v) for u, v in graph.edges()]

    loops = add_loop_edges_to_remove(loops_with_ref, edges)
    loops = update_subloops(loops)
    return merge_loops(loops)


def add_loop_edges_to_remove(
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
    for loop in loops:
        if len(loop) == 1:
            loop.add_edge_to_remove((loop.nodes[0], loop.nodes[0]))
        else:
            entries: set[str] = set()
            exits: set[str] = set()
            for u, v in edges:
                if u not in loop.nodes and v in loop.nodes:
                    entries.add(v)
                elif u in loop.nodes and v not in loop.nodes:
                    exits.add(u)

            if entries and exits:
                possible_edges = {
                    (u, v)
                    for u, v in edges
                    if v in entries and u in exits
                }

                for edge in possible_edges:
                    loop.add_edge_to_remove(edge)

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
