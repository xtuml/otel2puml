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
        update_with_references(loop_list, references)
        for loop_list in simple_cycles(graph)
    ]
    loops_with_ref.sort(key=lambda x: len(x))
    loops = [Loop(res) for res in loops_with_ref]

    edges = [
        tuple(update_with_references([u, v], references))
        for u, v in graph.edges()
    ]

    loops = add_loop_edges_to_remove(loops, edges)
    return update_subloops(loops)


def update_with_references(
        loop_list: list,
        references: dict[str, dict]
) -> None:
    return [references["event_reference"][label] for label in loop_list]


def add_loop_edges_to_remove(
        loops: list[Loop],
        edges: list[tuple[str, str]]
) -> list[Loop]:

    for loop in loops:
        if len(loop) == 1:
            loop.edge_to_remove = (loop.nodes[0], loop.nodes[0])
        else:
            entries = []
            exits = []
            for u, v in edges:
                if u not in loop.nodes and v in loop.nodes:
                    entries.append(v)
                elif u in loop.nodes and v not in loop.nodes:
                    exits.append(u)
                continue
            if entries and exits:
                if len(exits) == 1 and len(entries) == 1:
                    loop.edge_to_remove = (exits[0], entries[0])
                else:
                    raise ValueError("Multiple entries/exits found")
    return loops


def update_subloops(loops: list[Loop]) -> list[Loop]:
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
