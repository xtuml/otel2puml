"""Module with methods used to check the equivalency of two puml strings"""

from typing import Any, Generator, Literal

from networkx import DiGraph

from test_event_generator.io.parse_puml import (
    get_unparsed_job_defs,
    parse_raw_job_def_lines,
    EventData,
)


class Node:
    def __init__(self, node_id, node_type):
        self.node_id = node_id
        self.node_type = node_type

    def __repr__(self):
        return f"{self.node_id}"

    def __hash__(self) -> int:
        return hash(self.node_id)


def parse_raw_job_def(puml_string: str) -> Generator[list[str], Any, None]:
    raw_job_def_tuples = get_unparsed_job_defs(puml_string)
    for raw_job_def_tuple in raw_job_def_tuples:
        raw_job_def_lines = raw_job_def_tuple[1].split("\n")
        # pre-parse
        pre_parse = parse_raw_job_def_lines(raw_job_def_lines)
        yield pre_parse


def create_networkx_graph_from_parsed_puml(
    parsed_puml: list[
        EventData
        | tuple[
            Literal["START", "END", "PATH"],
            Literal["XOR", "AND", "OR", "LOOP"],
        ]
    ],
) -> DiGraph:
    logic_list: list[tuple[Node, Node]] = []
    prev_node = None
    prev_parsed_line = None
    graph = DiGraph()
    counters = {"XOR": 0, "AND": 0, "OR": 0, "LOOP": 0}
    prev_parsed_lines = [None] + parsed_puml[:-1]
    for parsed_line, prev_parsed_line in zip(parsed_puml, prev_parsed_lines):
        # check if parsed_line is an EventData object. If not handle as logic
        # or loop
        if isinstance(parsed_line, EventData):
            node = Node(parsed_line.event_tuple, parsed_line.event_type)
        else:
            if parsed_line[0] == "START":
                counters[parsed_line[1]] += 1
                logic_nodes = (
                    Node(
                        (*parsed_line, str(counters[parsed_line[1]])),
                        "_".join(parsed_line),
                    ),
                    Node(
                        ("END", parsed_line[1], str(counters[parsed_line[1]])),
                        f"END_{parsed_line[1]}",
                    ),
                )
                logic_list.append(logic_nodes)
                node = logic_nodes[0]
            elif parsed_line[0] == "PATH":
                if isinstance(prev_parsed_line, tuple):
                    if prev_parsed_line[0] == "START":
                        pass
                    elif prev_parsed_line[0] == "END":
                        graph.add_edge(prev_node, logic_list[-1][1])
                        prev_node = logic_list[-1][0]
                else:
                    graph.add_edge(prev_node, logic_list[-1][1])
                    prev_node = logic_list[-1][0]
                continue
            elif parsed_line[0] == "END":
                graph.add_edge(prev_node, logic_list[-1][1])
                popped_logic = logic_list.pop()
                prev_node = popped_logic[1]
                continue
        if prev_node is not None:
            graph.add_edge(prev_node, node)
        prev_node = node
    return graph
