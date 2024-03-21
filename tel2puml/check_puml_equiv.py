"""Module with methods used to check the equivalency of two puml strings"""

from typing import Any, Generator, Literal, Hashable

from networkx import DiGraph

from test_event_generator.io.parse_puml import (
    get_unparsed_job_defs,
    parse_raw_job_def_lines,
    EventData,
)


class NXNode:
    """Class to represent a node in a networkx graph

    :param node_id: the id of the node
    :type node_id: `Hashable`
    :param node_type: the type of the node
    :type node_type: `str`
    """
    def __init__(self, node_id: Hashable, node_type: str) -> None:
        """Constructor method"""
        self.node_id = node_id
        self.node_type = node_type

    def __repr__(self) -> str:
        """Method to return a string representation of the node"""
        return f"{self.node_id}"

    def __hash__(self) -> int:
        """Method to return the hash of the node"""
        return hash(self.node_id)


def parse_raw_job_def(puml_string: str) -> Generator[list[str], Any, None]:
    """Method to parse a raw puml string into a list of parsed puml lines
    producing generator list of parsed puml lines

    :param puml_string: raw puml string
    :type puml_string: `str`
    :return: generator list of parsed puml lines
    :rtype: `Generator`[:class:`list`[:class:`str`], `Any`, `None`]
    """
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
    """Method to create a networkx DiGraph from a parsed puml list

    :param parsed_puml: list of parsed puml lines
    :type parsed_puml: `list`[:class:`EventData` |
    `tuple`[:class:`Literal`[`"START"`, `"END"`, `"PATH"`],
    :class:`Literal`[`"XOR"`, `"AND"`, `"OR"`, `"LOOP"`]]
    :return: networkx DiGraph
    :rtype: :class:`DiGraph`
    """
    logic_list: list[tuple[NXNode, NXNode]] = []
    prev_node = None
    prev_parsed_line = None
    graph = DiGraph()
    counters = {"XOR": 0, "AND": 0, "OR": 0, "LOOP": 0}
    prev_parsed_lines = [None] + parsed_puml[:-1]
    for parsed_line, prev_parsed_line in zip(parsed_puml, prev_parsed_lines):
        # check if parsed_line is an EventData object. If start create a logic
        # tuple of node otherwise handle paths and ends of logic
        if isinstance(parsed_line, EventData):
            # if just an event create a node
            node = NXNode(parsed_line.event_tuple, parsed_line.event_type)
        elif parsed_line[0] == "START":
            # if a start of logic or loop create a logic tuple of nodes add it
            # to the front of the logic list and make the node the first node
            # in the tuple
            counters[parsed_line[1]] += 1
            logic_nodes = (
                NXNode(
                    (*parsed_line, str(counters[parsed_line[1]])),
                    "_".join(parsed_line),
                ),
                NXNode(
                    ("END", parsed_line[1], str(counters[parsed_line[1]])),
                    f"END_{parsed_line[1]}",
                ),
            )
            logic_list.append(logic_nodes)
            node = logic_nodes[0]
        else:
            # if we then have a PATH or END we then handle starting the new
            # path or ending the current path then continue
            if parsed_line[0] == "PATH" and isinstance(
                prev_parsed_line, tuple
            ):
                # if there is a path and the previous line was the start of a
                # logic tuple then add do nothing and continue
                if prev_parsed_line[0] == "START":
                    continue
            # add the edge from the previous node to the end node of the
            # current logic tuple
            graph.add_edge(prev_node, logic_list[-1][1])
            # if the current line is an END then pop the last logic tuple and
            # set the previous node to the end node in that tuple. Otherwise
            # set the previous node to the start node of the current logic
            # tuple
            if parsed_line[0] == "END":
                prev_node = logic_list.pop()[1]
            else:
                prev_node = logic_list[-1][0]
            continue
        # add the edge from the previous node to the current node (in the
        # cases of EventData and START)
        if prev_node is not None:
            graph.add_edge(prev_node, node)
        prev_node = node
    return graph
