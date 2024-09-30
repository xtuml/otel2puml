"""Module for creating PlantUML graph."""

from typing import Hashable, Optional, Callable, Union
from abc import ABC, abstractmethod

from networkx import (
    DiGraph, topological_sort, dfs_successors, dfs_predecessors
)

from tel2puml.tel2puml_types import (
    PUMLEvent,
    PUMLOperator,
    PUMLOperatorNodes,
    NXEdgeAttributes,
    NXNodeAttributes,
    DUMMY_START_EVENT,
    DUMMY_END_EVENT
)
from tel2puml.check_puml_equiv import NXNode
from tel2puml.loop_detection.loop_types import DUMMY_BREAK_EVENT_TYPE

# Mapping of operator nodes to PlantUML strings, the number of indents to
# be added to the block proceeding the operator node and the number of indents
# to add to the next line within the block

OPERATOR_NODE_PUML_MAP = {
    ("START", "XOR"): (("switch (XOR)", "case ()"), 2, 0),
    ("PATH", "XOR"): (("case ()",), 0, 1),
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


OPERATOR_PATH_FUNCTION_MAP: dict[
    PUMLOperatorNodes, Callable[[int], Union["PUMLOperatorNode", None]]
] = {
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
    PUMLOperatorNodes.START_LOOP: lambda x: None
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
            if PUMLEvent.BREAK in self.event_types:
                blocks.append(f"{' ' * indent}break")
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
        if PUMLEvent.BREAK in self.event_types:
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


class PUMLGraph(DiGraph):  # type: ignore[type-arg]
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
        :param parent_graph_node: The parent graph node, defaults to `None`.
        :type parent_graph_node: `Hashable`, optional
        :return: The event node.
        :rtype: :class:`PUMLEventNode`
        """
        if not event_types:
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
        self.add_puml_node(node)
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
        nodes: list[PUMLOperatorNode] = []
        for operator_node in operator.value[:2]:
            node = PUMLOperatorNode(
                operator_type=operator_node,
                occurrence=self.get_occurrence_count(operator_node.value),
            )
            self.add_puml_node(
                node,
            )
            self.increment_occurrence_count(operator_node.value)
            nodes.append(node)
        return (nodes[0], nodes[1])

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
        self.add_puml_node(
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
        self.add_puml_node(node)
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

    def add_puml_node(self, node: PUMLNode) -> None:
        """Adds a node to the PlantUML graph.

        :param node: The node to be added.
        :type node: :class:`PUMLNode`
        """
        attrs = NXNodeAttributes(
            node_type=node.node_type, extra_info=node.extra_info
        )
        super().add_node(node, **attrs)

    def add_puml_edge(self, start_node: PUMLNode, end_node: PUMLNode) -> None:
        """Adds an edge to the PlantUML graph.

        :param start_node: The start node of the edge.
        :type start_node: :class:`PUMLNode`
        :param end_node: The end node of the edge.
        :type end_node: :class:`PUMLNode`
        """
        attrs = NXEdgeAttributes(
            start_node_attr=NXNodeAttributes(
                node_type=start_node.node_type,
                extra_info=start_node.extra_info
            ),
            end_node_attr=NXNodeAttributes(
                node_type=end_node.node_type, extra_info=end_node.extra_info
            )
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
            PUMLNode,
            list[PUMLNode]
        ]
    ) -> list[PUMLNode]:
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
            # assert isinstance(
            #     node,
            #     (PUMLOperatorNode, PUMLEventNode, PUMLKillNode)
            # )
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

    def __copy__(self) -> "PUMLGraph":
        """Creates a copy of the PlantUML graph. This is a shallow copy."""
        copy_graph: PUMLGraph = self.copy()  # type: ignore[assignment]
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

    def remove_dummy_end_event_nodes(
        self
    ) -> None:
        """Loops through the nodes of the instance and removes any dummy end
        event nodes that are present.
        """
        nodes_to_remove = [
            node
            for node in self.nodes
            if isinstance(node, PUMLEventNode)
            and node.node_type == DUMMY_END_EVENT
        ]
        for node in nodes_to_remove:
            self.remove_node(node)

    def add_sub_graph_to_puml_nodes_with_ref(
        self, sub_graph: "PUMLGraph", ref: Hashable
    ) -> None:
        """Adds a subgraph to the PlantUML nodes with a parent reference.

        :param sub_graph: The subgraph to add.
        :type sub_graph: :class:`PUMLGraph`
        :param ref: The parent reference.
        :type ref: `Hashable`
        """
        if ref not in self.parent_graph_nodes_to_node_ref:
            raise KeyError(
                "Node not found in parent graph nodes to node ref"
            )
        for puml_event_node in self.parent_graph_nodes_to_node_ref[ref]:
            puml_event_node.sub_graph = sub_graph


def remove_dummy_start_and_end_events_from_nested_graphs(
    nested_graph: PUMLGraph
) -> None:
    """Removes the dummy start and end events from the nested graphs.

    :param nested_graph: The nested graph to remove the dummy start and end
    events from.
    :type nested_graph: :class:`PUMLGraph`
    """
    nested_graph.remove_dummy_start_event_nodes()
    nested_graph.remove_dummy_end_event_nodes()
    for node in nested_graph.nodes:
        if isinstance(node, PUMLEventNode):
            if node.sub_graph is not None:
                remove_dummy_start_and_end_events_from_nested_graphs(
                    node.sub_graph
                )


def update_graph_for_dummy_break_event_node(
    dummy_break_event_node: PUMLEventNode, graph: PUMLGraph
) -> None:
    """Updates the graph for a dummy break event node. This method is used to
    remove the dummy break event node and replace it with the event node that
    precedes it. If there are nested start operator nodes that are XOR, between
    the event node and the dummy break event node, then the event node is
    brought down to all branches and child branches of the top level XOR
    operator. Note this will fail if the dummy break event node is beneath an
    AND operator or an END_ operator of all types.

    :param dummy_break_event_node: The dummy break event node to update the
    graph for.
    :type dummy_break_event_node: :class:`PUMLEventNode`
    :param graph: The graph to update.
    :type graph: :class:`PUMLGraph`
    """
    dummy_break_event_in_node: PUMLNode = list(
        graph.in_edges([dummy_break_event_node])
    )[0][0]
    dummy_break_event_out_node: PUMLNode = list(
        graph.out_edges([dummy_break_event_node])
    )[0][1] if list(graph.out_edges([dummy_break_event_node])) else None
    if isinstance(dummy_break_event_in_node, PUMLEventNode):
        graph.remove_node(dummy_break_event_node)
        if dummy_break_event_out_node is not None:
            graph.add_puml_edge(
                dummy_break_event_in_node,
                dummy_break_event_out_node
            )
        dummy_break_event_in_node.event_types = (
            *dummy_break_event_node.event_types,
            PUMLEvent.BREAK,
        )
        return
    predecessors: dict[PUMLNode, PUMLEventNode | PUMLOperatorNode] = (
        dfs_predecessors(graph)
    )
    ancestry: list[PUMLEventNode | PUMLOperatorNode] = [dummy_break_event_node]
    while True:
        ancestry.append(predecessors[ancestry[-1]])
        if isinstance(ancestry[-1], PUMLOperatorNode):
            if ancestry[-1].operator_type in [
                PUMLOperatorNodes.START_AND,
                PUMLOperatorNodes.END_AND,
                PUMLOperatorNodes.START_OR,
                PUMLOperatorNodes.END_OR,
                PUMLOperatorNodes.END_XOR
            ]:
                raise NotImplementedError(
                    "Break event has an operator ancestor that is not "
                    "START_XOR"
                )
        if isinstance(ancestry[-1], PUMLEventNode):
            break
    ancestry.pop(0)
    event_node = ancestry.pop()
    if not isinstance(event_node, PUMLEventNode):
        raise RuntimeError(
            "Break event node does not have an event node predecessor"
        )
    event_node_in_node: PUMLNode = list(graph.in_edges([event_node]))[0][0]
    event_node_out_node: PUMLNode = list(graph.out_edges([event_node]))[0][1]
    graph.remove_node(event_node)
    graph.add_puml_edge(event_node_in_node, event_node_out_node)
    reversed_ancestry = list(reversed(ancestry))
    for operator_node, child_operator in zip(
        reversed_ancestry, reversed_ancestry[1:] + [None]
    ):
        if not isinstance(operator_node, PUMLOperatorNode):
            raise RuntimeError(
                "Break event node does not have an operator node ancestor"
            )
        if operator_node.operator_type != PUMLOperatorNodes.START_XOR:
            raise RuntimeError(
                "Break event node does not have a stat XOR operator node"
                " ancestor"
            )
        for _, out_node in list(graph.out_edges([operator_node])):
            if out_node == child_operator:
                pass
            else:
                new_event_node = graph.create_event_node(
                    event_name=event_node.node_type,
                    event_types=event_node.event_types,
                    sub_graph=event_node.sub_graph,
                    parent_graph_node=event_node.parent_graph_node,
                )
                if out_node == dummy_break_event_node:
                    graph.remove_node(dummy_break_event_node)
                    graph.add_puml_edge(
                        new_event_node,
                        dummy_break_event_out_node
                    )
                    new_event_node.event_types = (
                        *new_event_node.event_types,
                        PUMLEvent.BREAK,
                    )
                else:
                    graph.remove_edge(operator_node, out_node)
                    graph.add_puml_edge(new_event_node, out_node)
                graph.add_puml_edge(operator_node, new_event_node)


def update_graph_for_dummy_break_event_nodes(graph: PUMLGraph) -> None:
    """Updates the graph for dummy break event nodes. This method is used to
    remove all dummy break event nodes from the graph and replace them with the
    event nodes that precede them. If there are nested start operator nodes
    that are XOR, between the event node and the dummy break event node, then
    the event node is brought down to all branches and child branches of the
    top level XOR operator. Note this will fail if the dummy break event node
    is beneath an AND operator or an END_ operator of all types.

    :param graph: The graph to update.
    :type graph: :class:`PUMLGraph`
    """
    dummy_break_event_nodes = [
        node
        for node in graph.nodes
        if isinstance(node, PUMLEventNode)
        and node.node_type == DUMMY_BREAK_EVENT_TYPE
    ]
    for dummy_break_event_node in dummy_break_event_nodes:
        update_graph_for_dummy_break_event_node(dummy_break_event_node, graph)


def update_nested_sub_graphs_for_dummy_break_event_nodes(
    graph: PUMLGraph,
) -> None:
    """Updates the nested subgraphs for dummy break event nodes. This method is
    used to remove all dummy break event nodes from the nested subgraphs and
    replace them with the event nodes that precede them. If there are nested
    start operator nodes that are XOR, between the event node and the dummy
    break event node, then the event node is brought down to all branches and
    child branches of the top level XOR operator. Note this will fail if the
    dummy break event node is beneath an AND operator or an END_ operator of
    all types.

    :param graph: The graph to update.
    :type graph: :class:`PUMLGraph`
    """
    update_graph_for_dummy_break_event_nodes(graph)
    for node in graph.nodes:
        if isinstance(node, PUMLEventNode):
            if node.sub_graph is not None:
                update_nested_sub_graphs_for_dummy_break_event_nodes(
                    node.sub_graph
                )
