from networkx import DiGraph, simple_cycles


class Loop:
    
    def __init__(self):
        self.sub_loops: list[Loop] = []


def detect_loops(graph: DiGraph) -> list[Loop]:
    _ = simple_cycles(graph)
    return [Loop()]
