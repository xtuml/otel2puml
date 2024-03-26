"""Module for creating PlantUML graph."""

from typing import Hashable, Optional
from abc import ABC, abstractmethod

from networkx import DiGraph, topological_sort, dfs_successors

from tel2puml.tel2puml_types import (
    PUMLEvent,
    PUMLOperator,
    PUMLOperatorNodes,
    NXEdgeAttributes,
    NXNodeAttributes,
)
from tel2puml.check_puml_equiv import NXNode

# Mapping of operator nodes to PlantUML strings, the number of indents to
# be added to the block proceeding the operator node and the number of indents
# to add to the next line within the block

OPERATOR_NODE_PUML_MAP = {
    ("START", "XOR"): (("switch (XOR)", "case"), 2, 0),
    ("PATH", "XOR"): (("case",), 0, 1),
    ("END", "XOR"): (("endswitch",), -2, 2),
    ("START", "AND"): (("fork",), 1, 0),
    ("PATH", "AND"): (("fork again",), 0, 1),
    ("END", "AND"): (("end fork",), -1, 1),
    ("START", "OR"): (("split",), 1, 0),
    ("PATH", "OR"): (("split again",), 0, 1),
    ("END", "OR"): (("end split",), -1, 1),
    ("START", "LOOP"): (("repeat",), 1, 0),
    ("END", "LOOP"): (("repeat while",), -1, 1),
}


OPERATOR_PATH_FUNCTION_MAP = {
    PUMLOperatorNodes.START_XOR: lambda x: (
        None if x == 0
        else PUMLOperatorNode(PUMLOperatorNodes.PATH_XOR, x)
    ),
    PUMLOperatorNodes.START_AND: lambda x: (
        None if x == 0
        else PUMLOperatorNode(PUMLOperatorNodes.PATH_AND, x)
    ),
    PUMLOperatorNodes.START_OR: lambda x: (
        None if x == 0
        else PUMLOperatorNode(PUMLOperatorNodes.PATH_OR, x)
    ),
    PUMLOperatorNodes.START_LOOP: lambda x: (
        None if x == 0
        else PUMLOperatorNode(PUMLOperatorNodes.PATH_LOOP, x)
    )
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
    def write_uml_blocks(
        self,
        indent: int = 0,
        tab_size: int = 4,
    ) -> tuple[list[str], int]:
        """Writes the PlantUML block for the node and returns the number of
        indents to be added to the next line.

        :param indent: The number of indents to be added to the block.
        :type indent: `int`
        :param tab_size: The size of the tab, defaults to 4.
        :type tab_size: `int`, optional
        :return: The PlantUML blocks for the node and the number of indents to
        be added to the next line.
        :rtype: `tuple[list[str], int]`
        """
        pass


class PUMLEventNode(PUMLNode):
    """Class for creating PlantUML event node.

    :param event_name: The name of the event node.
    :type event_name: `str`
    :param occurrence: The occurrence of the event node.
    :type occurrence: `int`
    :param event_types: The type of the event node, defaults to `None`.
    :type event_types: :class:`PUMLEvent` or `tuple[:class:`PUMLEvent`, `...`]`
    | `None`, optional
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
        event_types: tuple[PUMLEvent, ...] | None = None,
        sub_graph: Optional["PUMLGraph"] = None,
        branch_number: int | None = None,
    ) -> None:
        """Constructor method."""
        node_type = event_name
        node_id = (event_name, occurrence)
        self.sub_graph = sub_graph
        self.branch_number = branch_number
        self.event_types = (
            event_types if event_types is not None else (PUMLEvent.NORMAL,)
        )
        extra_info = {
            "is_branch": PUMLEvent.BRANCH in self.event_types,
            "is_break": PUMLEvent.BREAK in self.event_types,
            "is_merge": PUMLEvent.MERGE in self.event_types,
        }
        super().__init__(
            node_id=node_id, node_type=node_type, extra_info=extra_info
        )

    def write_uml_blocks(
        self,
        indent: int = 0,
        tab_size: int = 4,
    ) -> tuple[list[str], int]:
        """Writes the PlantUML block for the node and returns the number of
        indents to be added to the next line.

        :param indent: The number of indents to be added to the block.
        :type indent: `int`
        :param tab_size: The size of the tab, defaults to 4.
        :type tab_size: `int`, optional
        :return: The PlantUML blocks for the node and the number of indents to
        be added to the next line.
        :rtype: `tuple[list[str], int]`
        """
        if self.sub_graph is not None:
            if PUMLEvent.LOOP in self.event_types:
                blocks = (
                    [" " * indent + "repeat"]
                    + self.sub_graph.write_uml_blocks(
                        indent + tab_size, tab_size=tab_size
                    ) + [" " * indent + "repeat while"]
                )
            else:
                blocks = self.sub_graph.write_uml_blocks(
                    indent, tab_size=tab_size
                )
        else:
            blocks = self._write_event_blocks(indent)
        next_indent_diff_total = 0 * tab_size
        return (
            blocks,
            next_indent_diff_total,
        )

    def _write_event_blocks(
        self,
        indent: int = 0,
    ) -> list[str]:
        """Writes the PlantUML block for the event node."""
        branch_info = ""
        if self.extra_info["is_branch"]:
            if self.branch_number is None:
                raise RuntimeError(
                    "Branch number is not provided but event is a branch event"
                )
            branch_info += (
                f",BCNT,user={self.node_type},name=BC{self.branch_number}"
            )
        blocks = []
        blocks.append(f"{' ' * indent}:{self.node_type}{branch_info};")
        if self.extra_info["is_break"]:
            blocks.append(f"{' ' * indent}break")
        return blocks


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

    def write_uml_blocks(
        self,
        indent: int = 0,
        tab_size: int = 4,
    ) -> tuple[list[str], int]:
        """Writes the PlantUML block for the node and returns the number of
        indents to be added to the next line.

        :param indent: The number of indents to be added to the block.
        :type indent: `int`
        :param tab_size: The size of the tab, defaults to 4.
        :type tab_size: `int`, optional
        :return: The PlantUML blocks for the node and the number of indents to
        be added to the next line.
        :rtype: `tuple[list[str], int]`
        """
        operator_puml_strings, indent_diff, unindent = OPERATOR_NODE_PUML_MAP[
            self.operator_type.value
        ]
        if indent <= 0:
            indent = 0
            unindent = 0
        blocks = []
        for i, operator_puml_string in enumerate(operator_puml_strings):
            line_indent = (i - unindent) * tab_size + indent
            blocks.append(f"{' ' * line_indent}{operator_puml_string}")
        next_indent_diff_total = indent_diff
        return (
            blocks,
            next_indent_diff_total,
        )


class PUMLGraph(DiGraph):
    """Class for creating PlantUML graph."""

    def __init__(self) -> None:
        """Initializes the PlantUML graph."""
        self.node_counts: dict[Hashable, int] = {}
        self.branch_counts: int = 0
        super().__init__()

    def create_event_node(
        self,
        event_name: str,
        event_types: PUMLEvent | tuple[PUMLEvent, ...] | None = None,
        sub_graph: Optional["PUMLGraph"] = None,
    ) -> PUMLEventNode:
        """Adds a node to the PlantUML graph.

        :param event_name: The name of the event node.
        :type event_name: `str`
        :param event_types: The type of the event node.
        :type event_types: :class:`PUMLEvent` |
        `tuple[:class:`PUMLEvent`, `...`]`
        :param sub_graph: The sub graph of the event node, defaults to `None`.
        :type sub_graph: :class:`PUMLGraph`, optional
        :return: The event node.
        :rtype: :class:`PUMLEventNode`
        """
        if event_types is None:
            event_types = (PUMLEvent.NORMAL,)
        if isinstance(event_types, PUMLEvent):
            event_types = (event_types,)
        if PUMLEvent.BRANCH in event_types:
            branch_number = self.branch_counts
            self.branch_counts += 1
        else:
            branch_number = None
        node = PUMLEventNode(
            event_name=event_name,
            occurrence=self.get_occurrence_count(event_name),
            event_types=event_types,
            sub_graph=sub_graph,
            branch_number=branch_number,
        )
        self.add_node(node)
        self.increment_occurrence_count(event_name)
        return node

    def create_operator_node_pair(
        self, operator: PUMLOperator
    ) -> tuple[PUMLOperatorNode, PUMLOperatorNode]:
        """Creates a pair of operator nodes.

        :param operator: The operator node.
        :type operator: :class:`PUMLOperator`
        :return: A pair of operator nodes for the start and end of the
        operator block.
        :rtype: `tuple[:class:`PUMLOperatorNode`, :class:`PUMLOperatorNode`]`
        """
        nodes = []
        for operator_node in operator.value[:2]:
            node = PUMLOperatorNode(
                operator_type=operator_node,
                occurrence=self.get_occurrence_count(operator_node.value),
            )
            self.add_node(
                node,
            )
            self.increment_occurrence_count(operator_node.value)
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
            operator_type=operator.value[2],
            occurrence=self.get_occurrence_count(operator.value[2].value),
        )
        self.add_node(
            node,
        )
        self.increment_occurrence_count(operator.value[2].value)
        return node

    def get_occurrence_count(self, node_type: Hashable) -> int:
        """Returns the occurrence count of a node type.

        :param node_type: The type of the node.
        :type node_type: `Hashable`
        """
        return self.node_counts.get(node_type, 0)

    def increment_occurrence_count(self, node_type: Hashable) -> None:
        """Increments the occurrence count of a node type.

        :param node_type: The type of the node.
        :type node_type: `Hashable`
        """
        self.node_counts[node_type] = self.get_occurrence_count(node_type) + 1

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

    def write_uml_blocks(self, indent: int = 0, tab_size: int = 4) -> str:
        """Writes the PlantUML block for the graph.

        :param indent: The number of indents to be added to the block.
        :type indent: `int`
        :param tab_size: The size of the tab, defaults to 4.
        :type tab_size: `int`, optional
        """
        # get the head node of the graph
        head_node = list(topological_sort(self))[0]
        # get the ordered nodes from the depth-first search successors
        sorted_nodes = self._order_nodes_from_dfs_successors_dict(
            head_node, dfs_successors(self, head_node)
        )
        # create the uml lines for the nodes
        blocks = []
        for node in sorted_nodes:
            node_block, indent_diff = node.write_uml_blocks(
                indent, tab_size=tab_size
            )
            blocks.extend(node_block)
            indent += indent_diff * tab_size
        return blocks

    @staticmethod
    def _order_nodes_from_dfs_successors_dict(
        node: PUMLNode,
        dfs_successor_dict: dict[
            PUMLEventNode | PUMLOperatorNode,
            list[PUMLEventNode | PUMLOperatorNode]
        ]
    ) -> list[PUMLEventNode | PUMLOperatorNode]:
        """Orders the nodes in the graph based on the depth-first search
        successors. If the node is an operator node that is the start of the
        operator, it adds a path node based how many paths have been traversed
        from the operator node.

        :param node: The node to start the ordering from.
        :type node: :class:`PUMLNode`
        :param dfs_successor_dict: The depth-first search successors of the
        nodes.
        :type dfs_successor_dict: `dict[:class:`PUMLNode`,
        list[:class:`PUMLNode`]]`
        """
        ordered_nodes = [node]
        if node in dfs_successor_dict:
            # loop over the successors in reverse order to get the correct
            # order of the nodes
            for i, successor in enumerate(reversed(dfs_successor_dict[node])):
                # check if the successor is an operator node
                if isinstance(node, PUMLOperatorNode):
                    # check if the operator node is the start of the operator
                    if node.operator_type in OPERATOR_PATH_FUNCTION_MAP:
                        # get a path node if the path is not the first path
                        path_node = OPERATOR_PATH_FUNCTION_MAP[
                            node.operator_type
                        ](i)
                        if path_node is not None:
                            ordered_nodes.append(path_node)
                # recursively order the successors of the successor node and
                # add them to the ordered nodes
                ordered_nodes.extend(
                    PUMLGraph._order_nodes_from_dfs_successors_dict(
                        successor, dfs_successor_dict
                    )
                )
        return ordered_nodes
