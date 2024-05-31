"""A module to detect all loops in a graph."""
from typing import Self, Optional, Union, Iterable, Generator
from logging import getLogger

from networkx import (
    DiGraph, simple_cycles, all_simple_paths, weakly_connected_components,
    has_path
)

from tel2puml.utils import check_is_sub_list


class Loop:
    """A class to represent a loop in a graph."""

    def __init__(self, nodes: list[str]) -> None:
        self.nodes = nodes
        self.sub_loops: list[Loop] = []
        self.edges_to_remove: set[tuple[str, str]] = set()
        self.break_edges: set[tuple[str, str]] = set()
        self.break_points: set[str] = set()
        self.exit_points: set[str] = set()
        self.merge_processed = False
        self.break_point_edges_to_remove: set[tuple[str, str]] = set()

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
        index_of_start = self.nodes.index([
            start_point for start_point in self.start_points
        ][0])
        ordered_nodes = self.nodes[index_of_start:] + self.nodes[
            :index_of_start
        ]
        other_index = other.nodes.index([
            start_point for start_point in other.start_points
        ][0])
        other_ordered_nodes = other.nodes[other_index:] + other.nodes[
            :other_index
        ]
        return check_is_sub_list(other_ordered_nodes, ordered_nodes)

    def add_edge_to_remove(self, edge: tuple[str, str]) -> None:
        """Add an edge to remove from the loop.

        :param edge: The edge to remove.
        :type edge: `tuple`[`str`, `str`]
        """
        if self.merge_processed:
            raise RuntimeError("Method not available after merge")
        self.edges_to_remove.add(edge)

    def add_break_point_edges_to_remove(
        self,
        graph: DiGraph,
    ) -> None:
        """Add the break point edges to remove from the loop.

        :param graph: The graph to get the break point edges from.
        :type graph: `DiGraph`
        """
        break_edges = get_break_point_edges_to_remove_from_loop(graph, self)
        for break_edge in break_edges:
            self.break_point_edges_to_remove.add(break_edge)

    def add_break_edge(self, break_edge: tuple[str, str]) -> None:
        """Add a break edge to the loop.

        :param break_point: The break edge to add.
        :type break_point: `tuple`[`str`, `str`]
        """
        if not self.merge_processed:
            raise RuntimeError("Method not available before merge")
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
        self.edges_to_remove.difference_update(sub_loop.edges_to_remove)

    def set_merged(self) -> None:
        """Set the merge_processed property to True."""
        self.merge_processed = True

    def set_exit_points(self, exit_points: set[str]) -> None:
        """Set the exit point of the loop.

        :param exit_points: The exit point of the loop.
        :type exit_points: `set`[`str`]
        """
        self.exit_points = exit_points

    @property
    def all_edges_to_remove(self) -> set[tuple[str, str]]:
        """Return all the edges to remove from the loop and subloops.

        :return: The edges to remove.
        :rtype: `set`[`tuple`[`str`, `str`]]
        """
        return self.edges_to_remove.union(self.break_point_edges_to_remove)

    @property
    def start_points(self) -> set[str]:
        """Return the start points of the loop.

        :return: The start points of the loop.
        :rtype: `set`[`str`]
        """
        return {edge[1] for edge in self.edges_to_remove}

    @property
    def end_points(self) -> set[str]:
        """Return the end points of the loop.

        :return: The end points of the loop.
        :rtype: `set`[`str`]
        """
        return {edge[0] for edge in self.edges_to_remove}.union(
            self.break_points
        )


def detect_loops(graph: DiGraph) -> list[Loop]:
    """Detect all loops in a graph.

    :param graph: The graph to detect the loops from.
    :type graph: `DiGraph`
    :return: A list of all loops in the graph.
    :rtype: `list`[`Loop`]
    """
    loops_with_ref = [Loop(loop_list) for loop_list in simple_cycles(graph)]
    edges = [(u, v) for u, v in graph.edges()]

    loops: list[Loop] = add_loop_edges_to_remove(
        loops_with_ref, edges
    )
    loops = update_subloops(loops)
    loops = merge_loops(loops)
    loops = update_break_edges_and_exits(loops, edges)
    loops = update_break_points(graph, loops)
    loops = merge_break_points(loops)
    update_break_point_edges_to_remove(graph, loops)
    return loops


def add_loop_edges_to_remove(
    loops: list[Loop],
    edges: list[tuple[str, str]]
) -> list[Loop]:
    """Add the edges to remove from the loops to the edge_to_remove property of
    the Loop.
    :param loops: The loops to add the edges to remove.
    :type loops: `list`[`Loop`]
    :param edges: The edges from the graph.
    :type edges: `list`[`tuple`[`str`, `str`]]
    :return: The updated loops.
    :rtype: `list`[`Loop`]
    """
    graph = DiGraph(edges)
    root_node = [node for node, degree in graph.in_degree() if degree == 0][0]
    loop_edges = {
        edge
        for loop in loops
        for edge in loop.get_edges()
    }
    for loop in loops:
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
                and u in {w for w, _ in exits}
            }
            for edge in edges_to_remove:
                # make sure the edge loops back
                if (
                    loop.nodes.index(edge[0]) + 1
                ) % len(loop) == loop.nodes.index(edge[1]):
                    # create a copy of the graph and remove all other nodes
                    # that could start the loop from the other edges to remove
                    copy_graph = graph.copy()
                    for other_edge in edges_to_remove:
                        if other_edge[1] != edge[1]:
                            if other_edge[1] in copy_graph.nodes:
                                copy_graph.remove_node(other_edge[1])
                    # check that the potential start node can be reached from
                    # the root node without passing through the other nodes
                    # that could start the loop
                    if has_path(copy_graph, root_node, edge[1]):
                        loop.add_edge_to_remove(edge)
        else:
            raise ValueError("No entries or no exits")

    return loops


def update_break_edges_and_exits(
    loops: list[Loop],
    edges: list[tuple[str, str]]
) -> list[Loop]:
    """Add the break edges and exits to the loops.

    :param loops: The loops to add the break edges and exits.
    :type loops: `list`[`Loop`]
    :param edges: The edges from the graph.
    :type edges: `list`[`tuple`[`str`, `str`]]
    :return: The updated loops.
    :rtype: `list`[`Loop`]
    """
    graph = DiGraph(edges)
    for loop in loops:
        entries: set[str] = set()
        exits: set[tuple[str, str]] = set()
        for u, v in graph.edges:
            if u not in loop.nodes and v in loop.nodes:
                entries.add(v)
            elif u in loop.nodes and v not in loop.nodes:
                exits.add((u, v))

        if entries and exits:
            # filter exits for kill points
            exits = filter_exits_for_kill_exits(
                exits, loop.edges_to_remove, graph
            )
            breaks = {
                (u, v)
                for u, v in exits
                if u not in {w for w, _ in loop.edges_to_remove}
            }

            for break_point in breaks:
                loop.add_break_edge(break_point)

            exit_points = set()
            if len(loop) == 1:
                for _, exit_point in exits:
                    exit_points.add(exit_point)
            else:
                for u, v in loop.edges_to_remove:
                    for loop_exit, exit_point in exits:
                        if u == loop_exit:
                            exit_points.add(exit_point)

            loop.set_exit_points(exit_points)
        else:
            raise ValueError("No entries or no exits")
        loop.sub_loops = update_break_edges_and_exits(loop.sub_loops, edges)
    return loops


def filter_exits_for_kill_exits(
    exits: set[tuple[str, str]],
    edges_to_remove: set[tuple[str, str]],
    graph: DiGraph,
) -> set[tuple[str, str]]:
    """Filter the exits for kill exits.

    :param exits: The exits to filter.
    :type exits: `set`[`tuple`[`str`, `str`]]
    :param edges_to_remove: The edges to remove.
    :type edges_to_remove: `set`[`tuple`[`str`, `str`]]
    :param graph: The graph to check the paths.
    :type graph: `DiGraph`
    :return: The filtered exits.
    :rtype: `set`[`tuple`[`str`, `str`]]
    """
    # get the end nodes in the loop from the loop edges to remove
    loop_ends = {edge[0] for edge in edges_to_remove}
    # find the normal exits that are those exits that aren't break exits or
    # kill exits and then get a set of nodes that would succeed the loop
    normal_exits = {
        exit_point
        for exit_point in exits
        if exit_point[0] in loop_ends
    }
    normal_exit_nodes = {exit_point[1] for exit_point in normal_exits}
    # break exits found by checking if there is a path from the exit point to
    # any node that would succeed the loop
    break_exits = {
        exit_point
        for exit_point in exits.difference(normal_exits)
        if any(
            has_path(graph, exit_point[1], node)
            for node in normal_exit_nodes
        )
    }
    return normal_exits.union(break_exits)


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
                elif (
                        current_filter_length is not None
                        and len(loop) <= current_filter_length
                ):
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
        merged = False
        for merged_loop in merged_loops:
            # check that there are common nodes between the edges to remove
            # if so they can be merged
            if set(
                node
                for edge in loop.edges_to_remove
                for node in edge
            ).intersection(
                node
                for edge in merged_loop.edges_to_remove
                for node in edge
            ):
                for node in loop.nodes:
                    if node not in merged_loop.nodes:
                        merged_loop.nodes.append(node)
                merged_loop.edges_to_remove.update(loop.edges_to_remove)
                merged_loop.exit_points.update(loop.exit_points)
                for sub_loop in loop.sub_loops:
                    if sub_loop not in merged_loop.sub_loops:
                        merged_loop.sub_loops.append(sub_loop)
                loop.set_merged()
                merged = True
                break

        if not merged:
            loop.set_merged()
            merged_loops.append(loop)
    for merged_loop in merged_loops:
        merged_loop.sub_loops = merge_loops(merged_loop.sub_loops)

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
    :return: The updated loops or the nodes from the subloops.
    :rtype: `list`[`Loop`] | `list`[`str`]
    """
    breaks_from_subloops: list[str] = []
    for loop in loops:
        from_subloops: list[str] = update_break_points(
            graph,
            loop.sub_loops,
            sub_loop=True
        )
        for node in from_subloops:
            if node not in loop.nodes:
                loop.nodes.append(node)
                breaks_from_subloops.append(node)
        # removal of break edges set in case break edges pass through loop end
        # points
        break_edges_to_remove: set[tuple[str, str]] = set()
        for u, v in loop.break_edges:
            if len(loop.exit_points) == 0:
                raise ValueError("No exit points")
            paths_to_exits = [
                all_simple_paths(graph, v, exit_point)
                for exit_point in loop.exit_points
            ]
            unique_path = {
                tuple(path[:-1])
                for paths in paths_to_exits
                for path in paths
                if not loop.exit_points.intersection(path[:-1])
                and not loop.start_points.intersection(path[:-1])
                and not loop.end_points.intersection(path[:-1])
            }
            if len(unique_path) == 1:
                for node in (path := unique_path.pop()):
                    if node not in loop.nodes:
                        loop.nodes.append(node)
                        breaks_from_subloops.append(node)
                loop.add_break_point(path[-1])
            elif len(unique_path) > 1:
                raise ValueError("Multiple paths")
            else:
                # if there are no paths to the exit point then this can't be a
                # break point
                getLogger(__name__).info(
                    "No unique path to exit point"
                )
                break_edges_to_remove.add((u, v))
        # remove break edges that have no paths to exit points
        loop.break_edges.difference_update(break_edges_to_remove)

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


def get_break_point_edges_to_remove_from_loop(
    graph: DiGraph,
    loop: Loop,
) -> list[tuple[str, str]]:
    """Get the break point edges to remove from the loop.

    :param graph: The graph to get the break point out edges from.
    :type graph: `DiGraph`
    :param loop: The loop to get the break point edges to remove.
    :type loop: `Loop`
    """
    break_edges = []
    for break_point in loop.break_points:
        break_edges.extend(graph.out_edges(break_point))
    return break_edges


def update_break_point_edges_to_remove(
    graph: DiGraph,
    loops: list[Loop],
) -> None:
    """Update the break point edges to remove from the loops.

    :param graph: The graph to get the break point edges from.
    :type graph: `DiGraph`
    :param loops: The loops to update the break point edges to remove.
    :type loops: `list`[`Loop`]
    """
    for loop in loops:
        loop.add_break_point_edges_to_remove(graph)
        update_break_point_edges_to_remove(graph, loop.sub_loops)


def get_all_break_points_from_loops(loops: list[Loop]) -> set[str]:
    """Get all break points from the loops and subloops recursively

    :param loops: The loops to get the break points from.
    :type loops: `list`[`Loop`]
    :return: The break points.
    :rtype: `set`[`str`]"""
    break_points = set()
    for loop in loops:
        break_points.update(loop.break_points)
        break_points.update(get_all_break_points_from_loops(loop.sub_loops))
    return break_points


def get_all_break_edges_from_loops(loops: list[Loop]) -> set[tuple[str, str]]:
    """Get all break edges from the loops and subloops recursively

    :param loops: The loops to get the break edges from.
    :type loops: `list`[`Loop`]
    :return: The break edges.
    :rtype: `set`[`tuple`[`str`, `str`]]
    """
    break_edges = set()
    for loop in loops:
        break_edges.update(loop.break_edges)
        break_edges.update(get_all_break_edges_from_loops(loop.sub_loops))
    return break_edges


def get_all_lonely_merge_killed_edges_from_loops(
    graph: DiGraph,
    loops: list[Loop],
) -> set[tuple[str, str]]:
    """Get all lonely merge killed edges from the loops.

    :param graph: The graph to get the lonely merge killed edges from.
    :type graph: `DiGraph`
    :param loops: The loops to get the lonely merge killed edges from.
    :type loops: `list`[`Loop`]
    :return: The lonely merge killed edges.
    :rtype: `set`[`tuple`[`str`, `str`]]
    """
    lonely_merge_kill_edges: set[tuple[str, str]] = set()
    for loop in loops:
        for edge in get_all_lonely_merge_killed_edges_from_loop(
            graph, loop
        ):
            lonely_merge_kill_edges.add(edge)
    return lonely_merge_kill_edges


def get_all_lonely_merge_killed_edges_from_loop(
    graph: DiGraph,
    loop: Loop
) -> Generator[tuple[str, str], None, None]:
    """Get all lonely merge killed edges from the loop.

    :param graph: The graph to get the lonely merge killed edges from.
    :type graph: `DiGraph`
    :param loop: The loop to get the lonely merge killed edges from.
    :type loop: `Loop`
    :return: The lonely merge killed edges.
    :rtype: `Generator`[`tuple`[`str`, `str`], `None`, `None`]
    """
    loop_nodes = extract_loop_nodes_from_graph(graph, loop)
    yield from (
        get_all_lonely_merge_killed_edges_from_loop_nodes_and_end_points(
            graph, loop_nodes, loop.end_points
        )
    )
    for sub_loop in loop.sub_loops:
        yield from get_all_lonely_merge_killed_edges_from_loop(graph, sub_loop)


def extract_loop_nodes_from_graph(
    graph: DiGraph,
    loop: Loop,
) -> list[str]:
    """Extract the nodes from the graph that are in the loop.

    :param graph: The graph to extract the nodes from.
    :type graph: `DiGraph`
    :param loop: The loop to extract the nodes from.
    :type loop: `Loop`
    """
    graph_copy: DiGraph = graph.copy()
    for node in loop.start_points:
        graph_copy.remove_edges_from(graph.in_edges(node))
    for node in loop.end_points:
        graph_copy.remove_edges_from(graph.out_edges(node))
    for connected_nodes_generator in weakly_connected_components(
        graph_copy
    ):
        connected_nodes = list(connected_nodes_generator)
        if loop.start_points.issubset(connected_nodes):
            break
    else:
        raise RuntimeError("Loop not found in any connected graphs")
    return connected_nodes


def get_all_lonely_merge_killed_edges_from_loop_nodes_and_end_points(
    graph: DiGraph,
    loop_nodes: Iterable[str],
    end_points: set[str],
) -> Generator[tuple[str, str], None, None]:
    """Get all lonely merge killed edges from the loop nodes and end points.

    :param graph: The graph to get the lonely merge killed edges from.
    :type graph: `DiGraph`
    :param loop_nodes: The nodes from the loop.
    :type loop_nodes: `Iterable`[`Hashable`]
    :param end_points: The end points of the loop.
    :type end_points: `set`[`Hashable`]
    :return: The lonely merge killed edges.
    :rtype: `Generator`[`tuple`[`Hashable`, `Hashable`], `None`, `None`]
    """
    for node in loop_nodes:
        if node in end_points:
            continue
        out_edges = graph.out_edges(node)
        if len(out_edges) <= 1:
            continue
        killed_nodes = [
            edge[1]
            for edge in out_edges
            if all(
                not has_path(graph, edge[1], end_point)
                for end_point in end_points
            )
        ]
        if len(out_edges) - len(killed_nodes) == 1:
            for killed_node in killed_nodes:
                yield node, killed_node


def get_all_kill_edges_from_loops(
    graph: DiGraph,
    loops: list[Loop],
) -> set[tuple[str, str]]:
    """Get all kill edges from the loops.

    :param graph: The graph to get the kill edges from.
    :type graph: `DiGraph`
    :param loops: The loops to get the kill edges from.
    :type loops: `list`[`Loop`]
    :return: The kill edges.
    :rtype: `set`[`tuple`[`str`, `str`]]
    """
    kill_edges: set[tuple[str, str]] = set()
    for loop in loops:
        for edge in get_all_kill_edges_from_loop(graph, loop):
            kill_edges.add(edge)
    return kill_edges


def get_all_kill_edges_from_loop(
    graph: DiGraph,
    loop: Loop,
) -> Generator[tuple[str, str], None, None]:
    """Get all kill edges from the loop.

    :param graph: The graph to get the kill edges from.
    :type graph: `DiGraph`
    :param loop: The loop to get the kill edges from.
    :type loop: `Loop`
    :return: The kill edges.
    :rtype: `Generator`[`tuple`[`str`, `str`], `None`, `None`]
    """
    loop_nodes = extract_loop_nodes_from_graph(graph, loop)
    yield from (
        get_all_kill_edges_from_loop_nodes_and_end_points(
            graph, loop_nodes, loop.end_points,
            loop.start_points
        )
    )
    for sub_loop in loop.sub_loops:
        yield from get_all_kill_edges_from_loop(graph, sub_loop)


def get_all_kill_edges_from_loop_nodes_and_end_points(
    graph: DiGraph,
    loop_nodes: Iterable[str],
    end_points: set[str],
    start_points: set[str],
) -> Generator[tuple[str, str], None, None]:
    """Get all kill edges from the loop nodes and end points.

    :param graph: The graph to get the kill edges from.
    :type graph: `DiGraph`
    :param loop_nodes: The nodes from the loop.
    :type loop_nodes: `Iterable`[`Hashable`]
    :param end_points: The end points of the loop.
    :type end_points: `set`[`Hashable`]
    :return: The kill edges.
    :rtype: `Generator`[`tuple`[`Hashable`, `Hashable`], `None`, `None`]
    """
    if len(start_points) != 1:
        for start_point in start_points:
            if all(
                not has_path(graph, start_point, end_point)
                for end_point in end_points
            ):
                in_edges = graph.in_edges(start_point)
                if len(in_edges) != 1:
                    raise ValueError(
                        "Multiple in edges to start point in a loop with "
                        "multiple start points"
                    )
                yield in_edges[0]
    for node in loop_nodes:
        if node in end_points:
            continue
        out_edges = graph.out_edges(node)
        if len(out_edges) <= 1:
            continue
        for edge in out_edges:
            if all(
                not has_path(graph, edge[1], end_point)
                for end_point in end_points
            ):
                yield edge
