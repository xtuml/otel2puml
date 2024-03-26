from networkx import DiGraph, simple_cycles


class Loop:
    
    def __init__(self, nodes: list[str]):
        self.nodes = nodes
        self.sub_loops: list[Loop] = []


def detect_loops(
        graph: DiGraph, 
        references: dict[str, dict]
) -> list[Loop]:
    result = list(simple_cycles(graph))
    result_with_ref = [
        _update_with_references(res, references) for res in result
    ]
    result_with_ref.sort(key=lambda x: len(x))

    return [Loop(res) for res in result_with_ref]

def _update_with_references(
        loop: list, 
        references: dict[str, dict]
) -> None:
    return [references["event_reference"][label] for label in loop]
