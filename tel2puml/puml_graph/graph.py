"""Module for creating PlantUML graph."""

from typing import Hashable
from abc import ABC, abstractmethod

from networkx import DiGraph, topological_sort

from tel2puml_types import (
    PUMLEvent,
    PUMLOperator,
    PUMLOperatorNodes,
    NXEdgeAttributes,
    NXNodeAttributes,
)
from tel2puml.check_puml_equiv import NXNode


operator_node_puml_map = {
    ("START", "XOR"): (("switch (XOR)", "case"), 2, 0),
    ("PATH", "XOR"): (("case"), 0, 1),
    ("END", "XOR"): (("endswitch"), -2, 1),
    ("START", "AND"): (("fork"), 1, 0),
    ("PATH", "AND"): (("fork again"), 0, 1),
    ("END", "AND"): (("end fork"), -1, 1),
    ("START", "OR"): (("split"), 1, 0),
    ("PATH", "OR"): (("split again"), 0, 1),
    ("END", "OR"): (("end split"), -1, 1),
    ("START", "LOOP"): (("repeat"), 1, 0),
    ("END", "LOOP"): (("repeat while"), -1, 1),
}


class PUMLNode(NXNode, ABC):
    """Abstract class for creating PlantUML node.

    :param node_id: The unique identifier for the node.
    :type node_id: `Hashable`
    :param node_type: The type of the node.
    :type node_type: `str`
    :param extra_info: The extra information about the node, defaults to None.
    :type extra_info: `dict[str, bool]`, optional
    """
    def __init__(
        self,
        node_id: Hashable,
        node_type: str,
        extra_info: dict[str, bool] | None = None,
    ) -> None:
        """Constructor method."""
        super().__init__(
            node_id=node_id, node_type=node_type, extra_info=extra_info
        )

    @abstractmethod
    def write_uml_block(
        self,
        indent: int = 0,
        surrounding_lines: tuple[str, str] = ("", ""),
        tab_size: int = 4,
    ) -> tuple[str, int]:
        """Writes the PlantUML block for the node and returns the number of
        indents to be added to the next line.

        :param indent: The number of indents to be added to the block.
        :type indent: `int`
        :param surrounding_lines: The lines to be added before and after the
        block, defaults to ("", "").
        :type surrounding_lines: `tuple[str, str]`, optional
        :param tab_size: The size of the tab, defaults to 4.
        :type tab_size: `int`, optional
        """
        pass


class PUMLEventNode(PUMLNode):
    """Class for creating PlantUML event node.

    :param event_name: The name of the event node.
    :type event_name: `str`
    :param occurrence: The occurrence of the event node.
    :type occurrence: `int`
    :param event_types: The type of the event node.
    :type event_types: :class:`PUMLEvent` or `tuple[:class:`PUMLEvent`, `...`]`
    :param sub_graph: The sub graph of the event node, defaults to `None`.
    :type sub_graph: :class:`PUMLGraph`, optional
    :param branch_number: The branch number of the event node, defaults to
    `None`.
    :type branch_number: `int`, optional
    """
    def __init__(
        self,
        event_name: str,
        occurrence: int,
        event_types: tuple[PUMLEvent, ...],
        sub_graph: "PUMLGraph" | None = None,
        branch_number: int | None = None,
    ) -> None:
        """Constructor method."""
        node_type = event_name
        node_id = (event_name, occurrence)
        extra_info = {
            "is_branch": PUMLEvent.BRANCH in event_types,
            "is_break": PUMLEvent.BREAK in event_types,
            "is_merge": PUMLEvent.MERGE in event_types,
        }
        super().__init__(
            node_id=node_id, node_type=node_type, extra_info=extra_info
        )
        self.sub_graph = sub_graph
        self.branch_number = branch_number
        self.event_types = event_types

    def write_uml_block(
        self,
        indent: int = 0,
        surrounding_lines: tuple[str, str] = ("", ""),
        tab_size: int = 4,
    ) -> tuple[str, int]:
        """Writes the PlantUML block for the node and returns the number of
        indents to be added to the next line.

        :param indent: The number of indents to be added to the block.
        :type indent: `int`
        :param surrounding_lines: The lines to be added before and after the
        block, defaults to ("", "").
        :type surrounding_lines: `tuple[str, str]`, optional
        :param tab_size: The size of the tab, defaults to 4.
        :type tab_size: `int`, optional
        """
        if self.sub_graph is not None:
            block = self.sub_graph.write_uml_block(indent)
            next_indent_diff_total = 0 * tab_size
        else:
            block, next_indent_diff_total = self.write_event_block(indent)
        return (
            surrounding_lines[0] + block + surrounding_lines[1],
            next_indent_diff_total,
        )

    def write_event_block(
        self,
        indent: int = 0,
    ) -> str:
        """Writes the PlantUML block for the event node."""
        branch_info = ""
        if self.extra_info["is_branch"]:
            branch_info += (
                f",BCNT,user={self.node_type},name=BC{self.branch_number}"
            )
        block = f"{' ' * indent}:{self.node_type}{branch_info};\n"
        if self.extra_info["is_break"]:
            block += f"{' ' * indent}break\n"
        return block, 0


class PUMLOperatorNode(PUMLNode):
    """Class for creating PlantUML operator node.

    :param operator_type: The type of the operator node.
    :type operator_type: `PUMLOperatorNodes`
    :param occurrence: The occurrence of the operator node.
    :type occurrence: `int`
    """
    def __init__(
        self,
        operator_type: PUMLOperatorNodes,
        occurrence: int
    ) -> None:
        """Constructor method."""
        node_type = "_".join(operator_type.value)
        node_id = (*operator_type.value, occurrence)
        super().__init__(node_id, node_type)
        self.operator_type = operator_type

    def write_uml_block(
        self,
        indent: int = 0,
        surrounding_lines: tuple[str, str] = ("", ""),
        tab_size: int = 4,
    ) -> tuple[str, int]:
        """Writes the PlantUML block for the node and returns the number of
        indents to be added to the next line.

        :param indent: The number of indents to be added to the block.
        :type indent: `int`
        :param surrounding_lines: The lines to be added before and after the
        block, defaults to ("", "").
        :type surrounding_lines: `tuple[str, str]`, optional
        :param tab_size: The size of the tab, defaults to 4.
        :type tab_size: `int`, optional
        """
        operator_puml_strings, indent_diff, unindent = operator_node_puml_map[
            self.operator_type.value
        ]
        block = ""
        for i, operator_puml_string in enumerate(operator_puml_strings):
            line_indent = (i - unindent) * tab_size + indent
            block += f"{' ' * line_indent}{operator_puml_string}\n"
        next_indent_diff_total = indent_diff
        return (
            surrounding_lines[0] + block + surrounding_lines[1],
            next_indent_diff_total,
        )


class PUMLGraph(DiGraph):
    """Class for creating PlantUML graph."""

    def __init__(self):
        """Initializes the PlantUML graph."""
        self.node_counts: dict[Hashable, int] = {}
        self.branch_counts: int = 0
        super().__init__()

    def create_event_node(
        self,
        event_name: str,
        event_types: PUMLEvent | tuple[PUMLEvent, ...],
        sub_graph: "PUMLGraph" | None = None,
    ) -> PUMLNode:
        """Adds a node to the PlantUML graph.

        :param event_name: The name of the event node.
        :type event_name: `str`
        :param event_types: The type of the event node.
        :type event_types: :class:`PUMLEvent` |
        `tuple[:class:`PUMLEvent`, `...`]`
        :param sub_graph: The sub graph of the event node, defaults to `None`.
        :type sub_graph: :class:`PUMLGraph`, optional
        """
        if isinstance(event_types, PUMLEvent):
            event_types = (event_types,)
        if PUMLEvent.BRANCH in event_types:
            branch_counts = self.branch_counts
            self.branch_counts += 1
        else:
            branch_counts = None
        node = PUMLEventNode(
            event_name=event_name,
            occurrence=self.get_occurence_count(event_name),
            event_types=event_types,
            sub_graph=sub_graph,
            branch_counts=branch_counts,
        )
        self.add_node(node)
        self.increment_occurence_count(event_name)
        return node

    def create_operator_node_pair(
        self, operator: PUMLOperator
    ) -> tuple[PUMLNode, PUMLNode]:
        """Creates a pair of operator nodes.

        :param operator: The operator node.
        :type operator: :class:`PUMLOperator`
        """
        nodes = []
        for operator_node in operator.value[:2]:
            node = PUMLOperatorNode(
                operator_type=operator_node,
                occurrence=self.get_occurence_count(operator_node.value),
            )
            self.add_node(
                node,
            )
            self.increment_occurence_count(operator_node.value)
            nodes.append(node)
        return tuple(nodes)

    def create_operator_path_node(
        self,
        operator: PUMLOperator,
    ) -> PUMLNode:
        """Creates a path operator node.

        :param operator: The operator node.
        :type operator: :class:`PUMLOperator`
        """
        node = PUMLOperatorNode(
            operator_type=operator.value[2].value,
            occurrence=self.get_occurence_count(operator.value[2].value),
        )
        self.add_node(
            node,
        )
        self.increment_occurence_count(operator.value[2].value)
        return node

    def get_occurence_count(self, node_type: Hashable) -> int:
        """Returns the occurrence count of a node type.

        :param node_type: The type of the node.
        :type node_type: `Hashable`
        """
        return self.node_counts.get(node_type, 0)

    def increment_occurence_count(self, node_type: Hashable) -> None:
        """Increments the occurrence count of a node type.

        :param node_type: The type of the node.
        :type node_type: `Hashable`
        """
        self.node_counts[node_type] = self.get_occurence_count(node_type) + 1

    def add_node(self, node: PUMLNode) -> None:
        """Adds a node to the PlantUML graph.

        :param node: The node to be added.
        :type node: :class:`PUMLNode`
        """
        attrs = NXNodeAttributes(
            node_type=node.node_type, extra_info=node.extra_info
        )
        super().add_node(node, **attrs)

    def add_edge(self, start_node: PUMLNode, end_node: PUMLNode) -> None:
        """Adds an edge to the PlantUML graph.

        :param start_node: The start node of the edge.
        :type start_node: :class:`PUMLNode`
        :param end_node: The end node of the edge.
        :type end_node: :class:`PUMLNode`
        """
        attrs = NXEdgeAttributes(
            start_node_attr=self.nodes[start_node],
            end_node_attr=self.nodes[end_node]
        )
        super().add_edge(start_node, end_node, **attrs)

    def write_uml_block(self, indent: int = 0, tab_size: int = 4) -> str:
        """Writes the PlantUML block for the graph.

        :param indent: The number of indents to be added to the block.
        :type indent: `int`
        :param tab_size: The size of the tab, defaults to 4.
        :type tab_size: `int`, optional
        """
        sorted_nodes = topological_sort(self)
        block = ""
        for node in sorted_nodes:
            surrounding_lines = ("", "")
            if node.node_type == "LOOP":
                surrounding_lines = ("repeat\n", "repeat while\n")
            node_block, indent_diff = node.write_uml_block(
                indent, tab_size=tab_size, surrounding_lines=surrounding_lines
            )
            block += node_block
            indent += indent_diff * tab_size
        return block
