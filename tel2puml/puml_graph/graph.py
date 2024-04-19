"""Module for creating PlantUML graph."""

from typing import Hashable, Optional
from abc import ABC, abstractmethod
from copy import copy

from networkx import (
    DiGraph, topological_sort, dfs_successors, weakly_connected_components
)

from tel2puml.tel2puml_types import (
    PUMLEvent,
    PUMLOperator,
    PUMLOperatorNodes,
    NXEdgeAttributes,
    NXNodeAttributes,
    DUMMY_START_EVENT
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
        parent_graph_node: Hashable | None = None,
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
            field: True
            for field, event_type in zip(
                ["is_branch", "is_break", "is_merge"],
                [PUMLEvent.BRANCH, PUMLEvent.BREAK, PUMLEvent.MERGE],
            )
            if event_type in self.event_types
        }
        self.parent_graph_node = parent_graph_node
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

        if self.extra_info.get("is_branch", False):
            if self.branch_number is None:
                raise RuntimeError(
                    "Branch number is not provided but event is a branch event"
                )
            branch_info += (
                f",BCNT,user={self.node_type},name=BC{self.branch_number}"
            )
        blocks = []
        blocks.append(f"{' ' * indent}:{self.node_type}{branch_info};")
        if self.extra_info.get("is_break", False):
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


class PUMLKillNode(PUMLNode):
    """Class for creating PlantUML kill node.

    :param occurrence: The occurrence of the kill node.
    :type occurrence: `int`
    """
    def __init__(
        self,
        occurrence: int
    ) -> None:
        """Constructor method."""
        node_type = "KILL"
        node_id = (node_type, occurrence)
        super().__init__(node_id, node_type)

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
        blocks = [f"{' ' * indent}kill"]
        next_indent_diff_total = 0 * tab_size
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
        self.kill_counts: int = 0
        self.parent_graph_nodes_to_node_ref: dict[
            Hashable, list[PUMLEventNode]
        ] = {}
        self.subgraph_nodes: set[PUMLEventNode] = set()
        super().__init__()

    def create_event_node(
        self,
        event_name: str,
        event_types: PUMLEvent | tuple[PUMLEvent, ...] | None = None,
        sub_graph: Optional["PUMLGraph"] = None,
        parent_graph_node: Hashable | None = None,
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
            parent_graph_node=parent_graph_node,
        )
        self.add_node(node)
        self.increment_occurrence_count(event_name)
        if parent_graph_node is not None:
            self.add_parent_graph_node_to_node_ref(parent_graph_node, node)
        return node

    def add_parent_graph_node_to_node_ref(
        self,
        parent_graph_node: Hashable,
        node_ref: PUMLEventNode
    ) -> None:
        """Adds a parent graph node to a node reference.

        :param parent_graph_node: The parent graph node.
        :type parent_graph_node: `Hashable`
        :param node_ref: The node reference.
        :type node_ref: :class:`PUMLEventNode`
        """
        if parent_graph_node not in self.parent_graph_nodes_to_node_ref:
            self.parent_graph_nodes_to_node_ref[parent_graph_node] = []
        self.parent_graph_nodes_to_node_ref[parent_graph_node].append(node_ref)

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

    def create_kill_node(self) -> PUMLKillNode:
        """Creates a kill node.

        :return: The kill node.
        :rtype: :class:`PUMLKillNode`
        """
        node = PUMLKillNode(self.kill_counts)
        self.add_node(node)
        self.kill_counts += 1
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

    def write_uml_blocks(
        self, indent: int = 0, tab_size: int = 4
    ) -> list[str]:
        """Writes the PlantUML block for the graph.

        :param indent: The number of indents to be added to the block.
        :type indent: `int`
        :param tab_size: The size of the tab, defaults to 4.
        :type tab_size: `int`, optional
        :return: The PlantUML blocks for the graph.
        :rtype: `list[str]`
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

    def write_puml_string(
        self,
        name: str = "default_name",
        tab_size: int = 4
    ) -> str:
        """Writes the PlantUML string for the graph.

        :return: The PlantUML string for the graph.
        :rtype: `str`
        """
        lines = [
            "@startuml", tab_size * " " + f'partition "{name}" ' + "{",
            2 * tab_size * " " + "group " + f'"{name}"',
            *self.write_uml_blocks(indent=3 * tab_size, tab_size=tab_size),
            2 * tab_size * " " + "end group", tab_size * " " + "}", "@enduml"
        ]
        return "\n".join(lines)

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

    def add_graph_node_to_set_from_reference(
        self, node_set: set[PUMLEventNode], node_ref: Hashable
    ) -> None:
        """Adds graph nodes to a set from a reference given that relates to the
        parent graph.

        :param node_set: The set to add the graph nodes to.
        :type node_set: `set[:class:`PUMLEventNode`]`
        :param node_ref: The reference to the parent graph.
        :type node_ref: `Hashable`
        """
        if node_ref not in self.parent_graph_nodes_to_node_ref:
            raise KeyError(
                "Node not found in parent graph nodes to node ref"
            )
        for graph_node in self.parent_graph_nodes_to_node_ref[node_ref]:
            node_set.add(graph_node)

    def replace_subgraph_node_from_start_and_end_nodes(
        self, start_node: PUMLNode, end_node: PUMLNode, node_name: str,
        event_types: PUMLEvent | tuple[PUMLEvent, ...] | None = None
    ) -> PUMLEventNode:
        """Extracts and replaces a subgraph inclusively between the start and
        end nodes given with a new subgraph node created. The extraction
        removes the edge into the start node and out of the end node. The
        subgraph node contains the extracted subgraph. A name for the nodes
        must be specified. Can add event types if required.

        :param start_node: The start node of the subgraph.
        :type start_node: :class:`PUMLNode`
        :param end_node: The end node of the subgraph.
        :type end_node: :class:`PUMLNode`
        :param node_name: The name of the new subgraph node.
        :type node_name: `str`
        :param event_types: The event types of the new subgraph node, defaults
        to `None`.
        :type event_types: :class:`PUMLEvent` |
        `tuple[:class:`PUMLEvent`, `...`]` | `None`, optional
        :return: The new subgraph node.
        :rtype: :class:`PUMLEventNode`
        """
        copy_graph = copy(self)
        if len(self.in_edges(start_node)) > 1:
            raise RuntimeError(
                "Start node has more than one incoming edge"
            )
        if len(self.out_edges(end_node)) > 1:
            raise RuntimeError(
                "End node has more than one outgoing edge"
            )
        if (
            len(self.in_edges(start_node)) == 0
            and len(self.out_edges(end_node)) == 0
        ):
            raise RuntimeError(
                "Start and end nodes have no incoming or outgoing edges and "
                "there will be no subgraph to create"
            )
        start_node_in_edge = list(self.in_edges(start_node))
        end_node_out_edge = list(self.out_edges(end_node))
        copy_graph.remove_edges_from(start_node_in_edge)
        copy_graph.remove_edges_from(end_node_out_edge)
        connected_components = list(weakly_connected_components(copy_graph))
        if len(connected_components) == 1:
            raise RuntimeError(
                "Graph is not disconnected after removing start node in edges "
                "and end node out edges so there is no subgraph to create"
            )
        for nodes in connected_components:
            nodes_to_remove = list(nodes)
            if start_node in nodes_to_remove and end_node in nodes_to_remove:
                self.remove_nodes_from(nodes_to_remove)
            else:
                copy_graph.remove_nodes_from(nodes_to_remove)
        subgraph_node = self.create_event_node(
            node_name,
            sub_graph=copy_graph,
            event_types=event_types
        )
        for edge in start_node_in_edge:
            self.add_edge(edge[0], subgraph_node)
        for edge in end_node_out_edge:
            self.add_edge(subgraph_node, edge[1])
        self.subgraph_nodes.add(subgraph_node)
        return subgraph_node

    def __copy__(self) -> "PUMLGraph":
        """Creates a copy of the PlantUML graph. This is a shallow copy."""
        copy_graph = self.copy()
        copy_graph.node_counts = self.node_counts
        copy_graph.branch_counts = self.branch_counts
        copy_graph.kill_counts = self.kill_counts
        copy_graph.parent_graph_nodes_to_node_ref = (
            self.parent_graph_nodes_to_node_ref
        )
        return copy_graph

    def remove_dummy_start_event_nodes(
        self
    ) -> None:
        """Loops through the nodes of the instance and removes any dummy start
        event nodes that are present.
        """
        nodes_to_remove = [
            node
            for node in self.nodes
            if isinstance(node, PUMLEventNode)
            and node.node_type == DUMMY_START_EVENT
        ]
        for node in nodes_to_remove:
            self.remove_node(node)
