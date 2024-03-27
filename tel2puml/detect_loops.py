from typing import Self, Optional

from networkx import DiGraph, simple_cycles


class Loop:

    def __init__(self, nodes: list[str]):
        self.nodes = nodes
        self.sub_loops: list[Loop] = []
        self.edge_to_remove: Optional[tuple[str, str]] = None

    def __len__(self) -> int:
        return len(self.nodes)

    def get_node_cycles(self) -> list[str]:
        index = 0
        cycles = []
        while index < len(self.nodes):
            cycles.append(self.nodes[index:] + self.nodes[:index])
            index += 1

        return cycles

    def check_subloop(self, other: Self) -> bool:
        if other.nodes in self.get_node_cycles():
            return False
        for sublist in self.get_sublist_of_length(self.nodes, len(other)):
            if sublist == other.nodes:
                return True
        return False

    @staticmethod
    def get_sublist_of_length(
            list: list[str],
            length: int
    ) -> list[list[str]]:
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
        self.sub_loops.append(sub_loop)


def detect_loops(
        graph: DiGraph,
        references: dict[str, dict]
) -> list[Loop]:
    loops_with_ref = [
        _update_with_references(loop_list, references)
        for loop_list in simple_cycles(graph)
    ]
    loops_with_ref.sort(key=lambda x: len(x))
    loops = [Loop(res) for res in loops_with_ref]

    edges = [
        tuple(_update_with_references([u, v], references))
        for u, v in graph.edges()
    ]

    loops = _add_loop_edges_to_remove(loops, edges)
    return _update_subloops(loops)


def _update_with_references(
        loop_list: list,
        references: dict[str, dict]
) -> None:
    return [references["event_reference"][label] for label in loop_list]


def _add_loop_edges_to_remove(
        loops: list[Loop],
        edges: list[tuple[str, str]]
) -> list[Loop]:

    for loop in loops:
        if len(loop) == 1:
            loop.edge_to_remove = (loop.nodes[0], loop.nodes[0])
        else:
            entry: Optional[str] = None
            exits: list[str] = []
            for u, v in edges:
                if u not in loop.nodes and v in loop.nodes:
                    entry = v
                elif u in loop.nodes and v not in loop.nodes:
                    exits.append(u)
                continue
            if entry and exits:
                if len(exits) == 1:
                    loop.edge_to_remove = (exits[0], entry)
                else:
                    raise ValueError("Multiple exits found")
    return loops


def _update_subloops(loops: list[Loop]) -> list[Loop]:
    subloop_indices = []
    for loop in loops:
        for sub_loop in loops:
            if loop.check_subloop(sub_loop):
                loop.add_subloop(sub_loop)
                subloop_indices.append(loops.index(sub_loop))

    return [loop for i, loop in enumerate(loops) if i not in subloop_indices]
