"""This module holds the 'node' class"""

from collections import Counter
from typing import Literal
from uuid import uuid4
import logging
from itertools import chain

from networkx import DiGraph, topological_sort, has_path
from networkx.exception import NetworkXError
from pm4py import ProcessTree
from pm4py.objects.process_tree.obj import Operator

from tel2puml.pipelines.logic_detection_pipeline import (
    Event,
    Operator as Logic_operator,
)
from tel2puml.puml_graph.graph import (
    PUMLEventNode,
    PUMLGraph,
    PUMLOperatorNode,
    PUMLNode,
)
from tel2puml.tel2puml_types import PUMLEvent, PUMLOperator
from tel2puml.utils import check_has_path_not_through_nodes


operator_name_map = {
    "PARALLEL": "AND",
    "XOR": "XOR",
    "OR": "OR",
    "BRANCH": "BRANCH",
}


class Node:
    """
    Represents a node in a graph.

    :param data: The data stored in the node i.e. uid, defaults to `None`
    :type data: `str` | `None`, optional
    :param uid: The unique identifier of the node, defaults to `None`
    :type uid: `str` | `None`, optional
    :param operator: The operator of the node, defaults to `None`
    :type operator: `str` | `None`, optional
    :param event_type: The event type of the node, defaults to `None`
    :type event_type: `str` | `None`, optional
    :param incoming: List of incoming nodes, defaults to `None`
    :type incoming: `list`[:class:`Node`] | `None`, optional
    :param outgoing: List of outgoing nodes, defaults to `None`
    :type outgoing: `list`[:class:`Node`] | `None`, optional
    :param incoming_logic: List of incoming logic, defaults to `None`
    :type incoming_logic: `list`[:class:`Node`] | `None`, optional
    :param outgoing_logic: List of outgoing logic, defaults to `None`
    :type outgoing_logic: `list`[:class:`Node`] | `None`, optional
    """

    def __init__(
        self,
        data: str | None = None,
        uid: str | None = None,
        operator: str | None = None,
        event_type: str | None = None,
        incoming: list["Node"] | None = None,
        outgoing: list["Node"] | None = None,
        incoming_logic: list["Node"] | None = None,
        outgoing_logic: list["Node"] | None = None,
        is_stub: bool = False,
        event_types: set["PUMLEvent"] | None = None,
    ) -> None:
        """Constructor method."""
        self.data = data if data is not None else operator
        self.incoming = [] if incoming is None else incoming
        self.outgoing = [] if outgoing is None else outgoing
        self.incoming_logic = [] if incoming_logic is None else incoming_logic
        self.outgoing_logic = [] if outgoing_logic is None else outgoing_logic
        self.uid = uid if uid is not None else self.data
        # this remains here until the code is refactored to be simpler
        if self.data is None:
            self.data = self.uid
        self.operator = operator
        self.event_type = event_type
        self.is_stub = is_stub

        self.event_types = set() if event_types is None else event_types

        self.branch_enum = ["AND", "OR", "XOR", "LOOP", "BRANCH"]

    def __repr__(self) -> str:
        return self.uid + ":" + (self.event_type or self.operator or "None")

    def __hash__(self) -> int:
        return hash(self.uid)

    def update_node_list_with_nodes(
        self, nodes: list["Node"], direction: Literal["incoming", "outgoing"]
    ) -> None:
        """Updates the node list with nodes.

        :param nodes: The nodes to add to the list.
        :type nodes: `list`[:class:`Node`]
        :param direction: The direction to update the list.
        :type direction: `Literal`[`"incoming"`, `"outgoing"`]
        """
        for node in nodes:
            self.update_node_list_with_node(node, direction)

    def update_node_list_with_node(
        self, node: "Node", direction: Literal["incoming", "outgoing"]
    ) -> None:
        """Updates the node list.

        :param node: The node to add to the list.
        :type node: :class:`Node`
        :param direction: The direction to update the list.
        :type direction: `Literal`[`"incoming"`, `"outgoing"`]
        """
        if direction not in ["incoming", "outgoing"]:
            raise ValueError(f"Invalid direction {direction}")
        if direction == "incoming":
            self.incoming.append(node)
        else:
            self.outgoing.append(node)

    @property
    def event_node_map_incoming(self) -> dict[str, "Node"]:
        """Returns a map of event types to nodes.

        :return: A map of event types to nodes.
        :rtype: `dict`[`str`, `Node`]
        """
        event_node_map = {}
        for node in self.incoming:
            if node.event_type is None:
                raise ValueError(
                    f"Node event type is not set for node with uid {self.uid}"
                )
            event_node_map[node.event_type] = node
        return event_node_map

    @property
    def event_node_map_outgoing(self) -> dict[str, "Node"]:
        """Returns a map of event types to nodes.

        :return: A map of event types to nodes.
        :rtype: `dict`[`str`, `Node`]
        """
        event_node_map = {}
        for node in self.outgoing:
            if node.event_type is None:
                raise ValueError(
                    f"Node event type is not set for node with uid {self.uid}"
                )
            event_node_map[node.event_type] = node
        return event_node_map

    def load_logic_into_list(
        self,
        logic_tree: ProcessTree,
        direction: Literal["incoming", "outgoing"],
    ) -> None:
        """Loads logic into the logic list.

        :param logic_tree: The logic tree to load.
        :type logic_tree: :class:`ProcessTree`
        :param direction: The direction to load the logic.
        :type direction: `Literal`[`"incoming"`, `"outgoing"`]
        """
        if direction not in ["incoming", "outgoing"]:
            raise ValueError(f"Invalid direction {direction}")
        if direction == "incoming":
            event_node_map = self.event_node_map_incoming
        else:
            event_node_map = self.event_node_map_outgoing
        if self.is_stub:
            return
        self._load_logic_into_logic_list(
            logic_tree, event_node_map, direction, self
        )

    def _load_logic_into_logic_list(
        self,
        logic_tree: ProcessTree,
        event_node_map: dict[str, "Node"],
        direction: Literal["incoming", "outgoing"],
        root_node: "Node",
    ) -> None:
        """Loads logic into the logic list.

        :param logic_tree: The logic tree to load.
        :type logic_tree: :class:`ProcessTree`
        :param event_node_map: The event node map.
        :type event_node_map: `dict`[`str`, :class:`Node`]
        :param direction: The direction to load the logic.
        :type direction: `Literal`[`"incoming"`, `"outgoing"`]
        """
        if (
            logic_tree.label is None
            and logic_tree.operator == Logic_operator.BRANCH
        ):
            if direction == "outgoing":
                root_node.event_types.add(PUMLEvent.BRANCH)
                for child in logic_tree.children:
                    self._load_logic_into_logic_list(
                        child, event_node_map, direction, root_node
                    )
                return

        if direction == "incoming":
            logic_list = self.incoming_logic
        else:
            logic_list = self.outgoing_logic

        if logic_tree.label is not None:
            if (
                logic_tree.label not in event_node_map
                and logic_tree.label != self.event_type
            ):
                node_id = str(uuid4())
                node_to_add = Node(
                    data=node_id,
                    uid=node_id,
                    event_type=logic_tree.label,
                    is_stub=True,
                )

                # Add the node to the appropriate node list
                getattr(root_node, direction).append(node_to_add)
                # Add the node to the event node map
                event_node_map[logic_tree.label] = node_to_add
                logging.getLogger().debug(
                    f"Stub node created on parent node with ID: {self.uid}\n"
                    f"The stub node has:\nEvent type: {logic_tree.label}\n"
                    f"Node ID: {node_id}"
                )

            # Add the node to the logic list and the appropriate node list if
            # the operator is a logic node
            if self.operator is not None:
                getattr(self, direction).append(
                    event_node_map[logic_tree.label]
                )
                logic_list.append(event_node_map[logic_tree.label])

        elif logic_tree.operator == Operator.SEQUENCE:
            for child in logic_tree.children:
                self._load_logic_into_logic_list(
                    child, event_node_map, direction, root_node
                )
        else:
            logic_operator_node = Node(
                operator=operator_name_map[logic_tree.operator.name],
            )
            for child in logic_tree.children:
                logic_operator_node._load_logic_into_logic_list(
                    child, event_node_map, direction, root_node
                )
            logic_list.append(logic_operator_node)

    def copy_node(
        self,
        uid: str = None,
        incoming: list = None,
        outgoing: list = None,
        incoming_logic: list = None,
        outgoing_logic: list = None,
    ):
        """
        Creates a copy of this node with optional modifications to its
            attributes.

        Args:
            uid (Any, optional): The modified data for the copied node.
                Defaults to None.
            incoming (List[Edge], optional): The modified incoming edges for
                the copied node. Defaults to None.
            outgoing (List[Edge], optional): The modified outgoing edges for
                the copied node. Defaults to None.
            incoming_logic (Any, optional): The modified incoming logic for
                the copied node. Defaults to None.
            outgoing_logic (Any, optional): The modified outgoing logic for
                the copied node. Defaults to None.

        Returns:
            Node: The copied node with optional modifications.
        """
        return Node(
            uid=self.uid if uid is None else uid,
            incoming=self.incoming if incoming is None else incoming,
            outgoing=self.outgoing if outgoing is None else outgoing,
            incoming_logic=(
                self.incoming_logic
                if incoming_logic is None
                else incoming_logic
            ),
            outgoing_logic=(
                self.outgoing_logic
                if outgoing_logic is None
                else outgoing_logic
            ),
        )

    def traverse_logic(
        self,
        direction: Literal["incoming", "outgoing"],
    ) -> list["Node"]:
        """Traverses the logic list.

        :param direction: The direction to traverse the logic list.
        :type direction: `Literal`[`"incoming"`, `"outgoing"`]
        :return: The list of nodes.
        :rtype: `list`[:class:`Node`]
        """
        nodes: list[Node] = []
        for node in getattr(self, direction + "_logic"):
            if node.operator is None:
                nodes.append(node)
            else:
                nodes.extend(node.traverse_logic(direction))
        return nodes

    def get_puml_event_types(self) -> tuple[PUMLEvent] | None:
        """Gets the PUML event types for the node if it is an event node or
        `None` otherwise.

        :return: The PUML event types for the node.
        :rtype: `tuple`[:class:`PUMLEvent`] | `None`
        """
        if self.event_types:
            return tuple(self.event_types)
        return None

    def get_operator_type(self) -> PUMLOperator | None:
        """Gets the PUML operator type for the node if it is a logic node or
        `None` otherwise.

        :return: The PUML operator type for the node.
        :rtype: :class:`PUMLOperator` | `None`
        """
        for operator in PUMLOperator:
            if self.operator == operator.name:
                return operator
        return None


def load_all_logic_trees_into_nodes(
    events: dict[str, Event],
    nodes: dict[str, list[Node]],
    direction: Literal["incoming", "outgoing"],
) -> None:
    """Loads all logic trees into the nodes.

    :param events: The events to load.
    :type events: `dict`[`str`, :class:`Event`]
    :param nodes: The nodes to load the logic into.
    :type nodes: `dict`[`str`, `list`[:class:`Node`]]
    :param direction: The direction to load the logic.
    :type direction: `Literal`[`"incoming"`, `"outgoing"`]
    """
    if direction not in ["incoming", "outgoing"]:
        raise ValueError(f"Invalid direction {direction}")
    for event_type, event in events.items():
        # catch the case when the event has no logic gate tree
        if event.logic_gate_tree is not None:
            load_logic_tree_into_nodes(
                event.logic_gate_tree, nodes[event_type], direction
            )


def load_logic_tree_into_nodes(
    logic_gate_tree: ProcessTree,
    nodes: list[Node],
    direction: Literal["incoming", "outgoing"],
) -> None:
    """Loads a logic tree into the nodes of a list

    :param logic_gate_tree: The logic gate tree to load into the nodes.
    :type logic_gate_tree: :class:`ProcessTree`
    :param nodes: The nodes to load the logic into.
    :type nodes: `list`[:class:`Node`]
    :param direction: The direction to load the logic.
    :type direction: `Literal`[`"incoming"`, `"outgoing"`]
    """
    for node in nodes:
        node.load_logic_into_list(logic_gate_tree, direction)


def create_networkx_graph_of_nodes_from_markov_graph(
    markov_graph: DiGraph,
    node_event_references: dict[str, str],
) -> tuple[DiGraph, dict[str, list[Node]]]:
    """Creates a NetworkX graph of nodes from a Markov graph.

    :param markov_graph: The Markov graph to create the NetworkX graph from.
    :type markov_graph: :class:`DiGraph`
    :param node_event_references: The node event references.
    :type node_event_references: `dict`[`str`, `str`]
    :return: A tuple containing the NetworkX graph and the event node
    reference.
    :rtype: `tuple`[:class:`DiGraph`, `dict`[`str`, `list`[:class:`Node`]]]
    """
    networkx_graph = DiGraph()
    uid_to_node = {}
    for node in markov_graph.nodes:
        node_class = Node(
            uid=node,
            event_type=node_event_references[node],
        )
        networkx_graph.add_node(node_class)
        uid_to_node[node] = node_class
    for node_class in networkx_graph.nodes:
        edges_to_node = markov_graph.in_edges(node_class.uid)
        for edge in edges_to_node:
            networkx_graph.add_edge(
                uid_to_node[edge[0]],
                uid_to_node[edge[1]],
            )
            node_class.incoming.append(uid_to_node[edge[0]])
        edges_from_node = markov_graph.out_edges(node_class.uid)
        for edge in edges_from_node:
            node_class.outgoing.append(uid_to_node[edge[1]])
    event_node_ref = create_event_node_ref(networkx_graph)
    return networkx_graph, event_node_ref


def create_event_node_ref(
    node_class_network_x_graph: DiGraph,
) -> dict[str, list[Node]]:
    """Creates an event node reference.

    :param node_class_network_x_graph: The node class NetworkX graph.
    :type node_class_network_x_graph: :class:`DiGraph`
    :return: The event node reference.
    :rtype: `dict`[`str`, `list`[:class:`Node`]]
    """
    event_node_ref = {}
    for node in node_class_network_x_graph.nodes:
        if node.event_type is None:
            raise ValueError(
                f"Node event type is not set for node with uid {node.uid}"
            )
        if node.event_type not in event_node_ref:
            event_node_ref[node.event_type] = []
        event_node_ref[node.event_type].append(node)
    return event_node_ref


def merge_markov_without_loops_and_logic_detection_analysis(
    markov_graph_ref_pair: tuple[DiGraph, dict[str, str]],
    incoming_logic_events: dict[str, Event],
    outgoing_logic_events: dict[str, Event],
) -> DiGraph:
    """Merges a Markov graph without loops and logic detection analysis.

    :param markov_graph_ref_pair: The Markov graph reference pair.
    :type markov_graph_ref_pair: `tuple`[:class:`DiGraph`,
    `dict`[`str`, `str`]]
    :param incoming_logic_events: The incoming logic events.
    :type incoming_logic_events: `dict`[`str`, :class:`Event`]
    :param outgoing_logic_events: The outgoing logic events.
    :type outgoing_logic_events: `dict`[`str`, :class:`Event`]
    :return: The NetworkX graph of :class:`Node`'s.
    :rtype: :class:`DiGraph`
    """
    markov_graph, node_event_references = markov_graph_ref_pair
    node_class_graph, event_node_map = (
        create_networkx_graph_of_nodes_from_markov_graph(
            markov_graph, node_event_references
        )
    )
    load_all_logic_trees_into_nodes(
        outgoing_logic_events, event_node_map, "outgoing"
    )
    return node_class_graph


class LogicBlockHolder:
    """Holds a logic block that keeps track of the logic blocks.

    :param start_node: The start node of the logic block.
    :type start_node: :class:`PUMLOperatorNode`
    :param end_node: The end node of the logic block.
    :type end_node: :class:`PUMLOperatorNode`
    :param logic_node: The logic node of the logic block.
    :type logic_node: :class:`Node`
    """

    def __init__(
        self,
        start_node: PUMLOperatorNode,
        end_node: PUMLOperatorNode,
        logic_node: Node,
    ) -> None:
        """Constructor method."""
        self.start_node = start_node
        self.end_node = end_node
        self.logic_node = logic_node
        self.paths = logic_node.outgoing_logic.copy()
        self.merge_nodes = [None] * len(self.paths)
        self.puml_nodes = [start_node] * len(self.paths)
        self.will_merge = False
        self.merge_counter = 0

    @property
    def current_path(self) -> Node | None:
        """Gets the current path."""
        if self.paths:
            return self.paths[-1]
        return None

    @property
    def current_path_puml_node(self) -> PUMLNode:
        """Gets the current path PlantUML node.

        :return: The current path PlantUML node.
        :rtype: :class:`PUMLNode`
        """
        return self.puml_nodes[-1]

    @current_path_puml_node.setter
    def current_path_puml_node(self, value: PUMLNode) -> None:
        """Sets the current path PlantUML node.

        :param value: The value to set.
        :type value: :class:`PUMLNode`
        """
        self.puml_nodes[-1] = value

    def set_path_node(self, pop: bool = False) -> Node | None:
        """Gets the next path in the block and returns it

        :return: The path node.
        :rtype: :class:`Node` | `None`
        """
        if self.will_merge:
            pop = True
        if self.paths and pop:
            self.paths.pop()
            self.merge_nodes.pop()
            self.puml_nodes.pop()
        return self.current_path

    def rotate_path(
        self, current_node_in_path: Node, current_puml_node_in_path: PUMLNode
    ) -> tuple[PUMLOperatorNode | PUMLNode, Node]:
        """Rotates the path by moving the current path to the end of the paths
        list.

        :return: The path node.
        :rtype: :class:`Node` | `None`
        """
        self.paths = [current_node_in_path] + self.paths[:-1]
        self.merge_nodes = [self.merge_nodes[-1]] + self.merge_nodes[:-1]
        self.puml_nodes = [current_puml_node_in_path] + self.puml_nodes[:-1]
        return self.current_path_puml_node, self.current_path,

    def handle_path_merge(self, potential_merge_node: Node) -> bool:
        """Handles a potential merge node. Checks if all paths have the same
        merge node and if they do then the merge is successful.

        Also increments the merge counter if the merge node is the same as the
        previous merge node, otherwise resets the merge counter.

        :param potential_merge_node: The potential merge node.
        :type potential_merge_node: :class:`Node`
        :return: Whether the merge was successful.
        :rtype: `bool`
        """
        if self.will_merge:
            return True
        if self.current_path is None:
            raise ValueError("No current path to merge")
        # increment the merge counter if nothing has changed
        if self.merge_nodes[-1] == potential_merge_node:
            self.merge_counter += 1
        else:
            self.merge_counter = 0
        self.merge_nodes[-1] = potential_merge_node
        # set previous merge nodes to the current merge nodes
        if len(set(self.merge_nodes)) == 1:
            self.will_merge = True
            return True
        return False


def create_puml_graph_from_node_class_graph(
    node_class_graph: DiGraph,
) -> PUMLGraph:
    """Creates a PlantUML graph from a node class graph using the logic
    held on each node and the connections between the nodes.

    :param node_class_graph: The node class graph.
    :type node_class_graph: :class:`DiGraph`
    :return: The PlantUML graph.
    :rtype: :class:`PUMLGraph`
    """
    head_node: Node = list(topological_sort(node_class_graph))[0]
    puml_graph = PUMLGraph()
    previous_puml_node = puml_graph.create_event_node(head_node.event_type)
    previous_node_class: Node = head_node
    logic_list: list[LogicBlockHolder] = []
    while True:
        # handle case in which the previous node is an event node that is
        # either a sequence or ends a sequence
        if (
            not previous_node_class.outgoing_logic
            and previous_node_class.event_type is not None
        ):
            # get the next node in the sequence if it exists
            if not previous_node_class.outgoing:
                next_node_class = None
            else:
                next_node_class = previous_node_class.outgoing[0]
            # break the loop if all logic blocks have been traversed and there
            # is no following node either
            if not logic_list and next_node_class is None:
                break
            if logic_list:
                # create a kill node if the next node is None and we are
                # within a logic block and then handle the merge point and
                # continue
                if next_node_class is None:
                    kill_node = puml_graph.create_kill_node()
                    puml_graph.add_edge(previous_puml_node, kill_node)
                    previous_puml_node, previous_node_class = (
                        handle_reach_logic_merge_point(
                            puml_graph,
                            logic_list,
                            kill_node,
                            previous_node_class,
                        )
                    )
                    continue
                # check if the next node has an alternative path back to the
                # logic node and then handle a merge into the end of the logic
                # block and continue
                elif check_is_merge_node_for_logic_block(
                    next_node_class, logic_list[-1], node_class_graph
                ):
                    previous_puml_node, previous_node_class = (
                        handle_reach_potential_merge_point(
                            puml_graph,
                            logic_list,
                            previous_puml_node,
                            previous_node_class,
                            next_node_class,
                        )
                    )
                    continue
                else:
                    pass
            # handle the next node if it there is just a straight line sequence
            previous_puml_node, previous_node_class = (
                update_puml_graph_with_event_node(
                    puml_graph, next_node_class, previous_puml_node
                )
            )
        else:
            # handle the case where there is an immediately following logic
            # node or a logic node as the previous node class
            previous_puml_node, previous_node_class = handle_logic_node_cases(
                puml_graph, logic_list, previous_puml_node, previous_node_class
            )
    return puml_graph


def handle_logic_node_cases(
    puml_graph: PUMLGraph,
    logic_list: list[LogicBlockHolder],
    previous_puml_node: PUMLNode,
    previous_node_class: Node,
) -> tuple[PUMLOperatorNode, Node]:
    """Handles the cases where there is an immediately following logic node or
    a logic node as the previous node class.

    :param puml_graph: The PlantUML graph to update.
    :type puml_graph: :class:`PUMLGraph`
    :param logic_list: The list of logic blocks.
    :type logic_list: `list`[:class:`LogicBlockHolder`]
    :param previous_puml_node: The previous PlantUML node.
    :type previous_puml_node: :class:`PUMLOperatorNode`
    :param previous_node_class: The previous node class.
    :type previous_node_class: :class:`Node`
    :return: A tuple containing the newly created PlantUML node and the event
    node.
    :rtype: `tuple`[:class:`PUMLOperatorNode`, :class:`Node`]
    """
    # sets the logic node to the previous node class if it is a logic node or
    # the first node in the logic list if it is not
    if previous_node_class.operator is None:
        logic_node = previous_node_class.outgoing_logic[0]
    else:
        logic_node = previous_node_class
    # create the PUMLOperator node pairs and add them to the graph
    start_operator, end_operator = puml_graph.create_operator_node_pair(
        logic_node.get_operator_type()
    )
    # create and add the logic block holder to the logic list
    logic_list.append(
        LogicBlockHolder(start_operator, end_operator, logic_node)
    )
    # add the edge between the previous PUMLNode and the start node
    # of the PUMLOperatorNode pair
    puml_graph.add_edge(previous_puml_node, start_operator)
    # handle the next path in the logic list and return updated previous puml
    # node and node class
    return handle_logic_list_next_path(
        puml_graph, logic_list, previous_node_class
    )


def handle_reach_potential_merge_point(
    puml_graph: PUMLGraph,
    logic_list: list[LogicBlockHolder],
    previous_puml_node: PUMLNode,
    previous_node_class: Node,
    next_node_class: Node,
) -> tuple[PUMLOperatorNode, Node]:
    """Handles reaching a potential merge point in the logic block.

    :param puml_graph: The PlantUML graph to update.
    :type puml_graph: :class:`PUMLGraph`
    :param logic_block: The logic block to handle.
    :type logic_block: :class:`LogicBlock
    :param previous_puml_node: The previous PlantUML node.
    :type previous_puml_node: :class:`PUMLOperatorNode`
    :param previous_node_class: The previous node class.
    :type previous_node_class: :class:`Node`
    :param next_node_class: The next node class.
    :type next_node_class: :class:`Node`
    :return: A tuple containing the newly created PlantUML node and the event
    node.
    :rtype: `tuple`[:class:`PUMLOperatorNode`, :class:`Node`]
    """
    logic_block = logic_list[-1]
    if logic_block.handle_path_merge(next_node_class):
        previous_puml_node, previous_node_class = (
            handle_reach_logic_merge_point(
                puml_graph, logic_list, previous_puml_node, previous_node_class
            )
        )
    else:
        # check if we are caught in an infinite loop when there are multiple
        # merge nodes
        if logic_block.merge_counter > len(logic_block.merge_nodes):
            logic_block.merge_counter = 0

            counter = Counter(logic_block.merge_nodes)
            most_common = counter.most_common(1)[0][0]
            indices = [
                i
                for i, x in enumerate(logic_block.merge_nodes)
                if x == most_common
            ]

            new_node = Node(
                operator=logic_block.logic_node.operator,
                outgoing_logic=[
                    logic_block.logic_node.outgoing_logic[index]
                    for index in indices
                ],
            )
            start_op, end_op = puml_graph.create_operator_node_pair(
                new_node.get_operator_type()
            )
            puml_graph.add_edge(logic_block.start_node, start_op)

            for out_node in [
                    logic_block.puml_nodes[index]
                    for index in indices
            ]:
                try:
                    puml_graph.remove_edge(
                        logic_block.start_node,
                        out_node
                    )
                except NetworkXError:
                    pass
                puml_graph.add_edge(start_op, out_node)

            new_logic_block = LogicBlockHolder(
                start_node=start_op,
                end_node=end_op,
                logic_node=new_node,
            )
            new_logic_block.puml_nodes = [
                logic_block.puml_nodes[index]
                for index in indices
            ]

            not_indices = [
                i
                for i, x in enumerate(logic_block.merge_nodes)
                if x != most_common
            ]
            logic_block.merge_nodes = [
                logic_block.merge_nodes[index] for index in not_indices
            ]
            logic_block.puml_nodes = [
                logic_block.puml_nodes[index] for index in not_indices
            ]
            logic_block.paths = [
                logic_block.paths[index] for index in not_indices
            ]

            logic_block.paths.append(new_node)
            logic_block.puml_nodes.append(start_op)
            logic_block.merge_nodes.append(None)

            logic_list.append(new_logic_block)

            return (
                new_logic_block.current_path_puml_node,
                new_logic_block.current_path
            )

        previous_puml_node, previous_node_class = handle_rotate_path(
            puml_graph, logic_list, previous_puml_node, previous_node_class
        )
    return previous_puml_node, previous_node_class


def handle_rotate_path(
    puml_graph: PUMLGraph,
    logic_list: list[LogicBlockHolder],
    previous_puml_node: PUMLOperatorNode,
    previous_node_class: Node,
) -> tuple[PUMLOperatorNode, Node]:
    """Handles rotating the path in the logic block. This switched to another
    path of the logic block and updates the previous puml node and node class
    to the new path that was saved in the logic block.

    :param puml_graph: The PlantUML graph to update.
    :type puml_graph: :class:`PUMLGraph`
    :param logic_block: The logic block to handle.
    :type logic_block: :class:`LogicBlock
    :param previous_puml_node: The previous PlantUML node.
    :type previous_puml_node: :class:`PUMLOperatorNode`
    :param previous_node_class: The previous node class.
    :type previous_node_class: :class:`Node`
    :return: A tuple containing the newly created PlantUML node and the event
    node.
    :rtype: `tuple`[:class:`PUMLOperatorNode`, :class:`Node`]
    """
    previous_puml_node, previous_node_class = logic_list[-1].rotate_path(
        previous_node_class, previous_puml_node
    )
    # if the next path is the start of a path then we must handle the start of
    # next path to ensure the start node is connected to the first node in the
    # path
    if previous_puml_node == logic_list[-1].start_node:
        previous_puml_node, previous_node_class = handle_logic_list_next_path(
            puml_graph, logic_list, previous_node_class
        )
        logic_list[-1].current_path_puml_node = previous_puml_node
    return previous_puml_node, previous_node_class


def handle_reach_logic_merge_point(
    puml_graph: PUMLGraph,
    logic_list: list[LogicBlockHolder],
    previous_puml_node: PUMLNode,
    previous_node_class: Node,
) -> tuple[PUMLOperatorNode | PUMLEventNode, Node]:
    """Handles reaching a merge point in the logic block. Adds an edge between
    the previous node and the end node of the logic block and then grabs the
    next node from the logic list having removed the path that has just ended.

    After the above handles gettting the previous puml node and previous node
    class from the next path in the logic list. Check to see if a logic block
    has ended.

    :param puml_graph: The PlantUML graph to update.
    :type puml_graph: :class:`PUMLGraph`
    :param logic_list: The list of logic blocks.
    :type logic_list: `list`[:class:`LogicBlockHolder`]
    :param previous_puml_node: The previous PlantUML node.
    :type previous_puml_node: :class:`PUMLOperatorNode`
    :param previous_node_class: The previous node class.
    :type previous_node_class: :class:`Node`
    :return: A tuple containing the newly created PlantUML node and the event
    node.
    :rtype: `tuple`[:class:`PUMLOperatorNode`, :class:`Node`]
    """
    # when there is a merge point we must add an edge from the previous node
    # to the end node of the logic block
    puml_graph.add_edge(
        previous_puml_node,
        logic_list[-1].end_node,
    )
    # handle the next path in the logic list and return updated previous puml
    # node and node class
    next_node_class = logic_list[-1].set_path_node(pop=True)
    # if there is no next path node then we must handle the end of the logic
    # block and return the updated previous puml node as the end node of the
    # logic block
    if next_node_class is None:
        previous_puml_node = logic_list.pop().end_node
    # if the next path node is a start node then we must handle the start of
    # the next path
    elif logic_list[-1].current_path_puml_node == logic_list[-1].start_node:
        previous_puml_node, previous_node_class = handle_logic_list_next_path(
            puml_graph, logic_list, previous_node_class
        )
        logic_list[-1].current_path_puml_node = previous_puml_node
    # Otherwise we grab the last puml node in the logic block and
    # set it as the previous puml node and the next node class as the previous
    # node class
    else:
        previous_puml_node = logic_list[-1].current_path_puml_node
        previous_node_class = next_node_class
    return previous_puml_node, previous_node_class


def handle_logic_list_next_path(
    puml_graph: PUMLGraph,
    logic_list: list[LogicBlockHolder],
    previous_node_class: Node,
) -> tuple[PUMLOperatorNode | PUMLEventNode, Node]:
    """Handles the next path in the logic list.

    :param puml_graph: The PlantUML graph to update.
    :type puml_graph: :class:`PUMLGraph`
    :param logic_list: The list of logic blocks.
    :type logic_list: `list`[:class:`LogicBlockHolder`]
    :param previous_node_class: The previous node class.
    :type previous_node_class: :class:`Node`
    :return: A tuple containing the newly created PlantUML node and the event
    node.
    :rtype: `tuple`[:class:`PUMLOperatorNode`, :class:`Node`]
    """
    # get the next path node in the logic block using the logic block holder
    next_node_class = logic_list[-1].set_path_node()
    # if there is no next path node then we must handle the end of the logic
    # block and return the updated previous puml node as the end node of the
    # logic block
    if next_node_class is None:
        previous_puml_node = logic_list.pop().end_node
    # the next blocks handle the case where there is a next path node
    # if the next node is an operator node then we must make the it the next
    # node class and reset the previous puml node to the start of the logic
    # block
    elif next_node_class.operator is not None:
        previous_node_class = next_node_class
        previous_puml_node = logic_list[-1].start_node
    # if the next node is an event node then we must create a PUML node for it
    # and create an edge between this node and the start PUML node of the logic
    # block. Then we must update the previous puml node to the newly created
    # node and the previous node class to the event node
    else:
        previous_puml_node, previous_node_class = (
            update_puml_graph_with_event_node(
                puml_graph, next_node_class, logic_list[-1].start_node
            )
        )
    return previous_puml_node, previous_node_class


def update_puml_graph_with_event_node(
    puml_graph: PUMLGraph,
    event_node: Node,
    previous_puml_node: PUMLNode,
) -> tuple[PUMLEventNode, Node]:
    """Updates the PlantUML graph with an event node connecting the previous
    PlantUML node to a newly created node and then returns the newly created
    node and the event node which will be set as the previous in the next
    iteration

    :param puml_graph: The PlantUML graph to update.
    :type puml_graph: :class:`PUMLGraph`
    :param event_node: The event node to add.
    :type event_node: :class:`Node`
    :param previous_puml_node: The previous PlantUML node.
    :type previous_puml_node: :class:`PUMLNode`
    :return: A tuple containing the newly created PlantUML node and the event
    node.
    :rtype: `tuple`[:class:`PUMLEventNode`, :class:`Node`]
    """
    if event_node.event_type is None:
        raise ValueError(
            f"Node event type is not set for node with uid {event_node.uid}"
        )
    next_puml_node = puml_graph.create_event_node(
        event_node.event_type, event_node.get_puml_event_types(),
        parent_graph_node=event_node.uid
    )
    puml_graph.add_edge(previous_puml_node, next_puml_node)
    return next_puml_node, event_node


def get_node_as_list(
    node: Node
) -> list[Node]:
    """Makes a list of nodes from a node using the following logic:
    * If the node is a logic node then traverse the logic list of the node and
    return the list of nodes
    * otherwise return the node itself.

    :param node: The node to get the list of nodes from.
    :type node: :class:`Node`
    :return: The list of nodes.
    :rtype: `list`[:class:`Node`]
    """
    return (
        node.traverse_logic("outgoing") if node.operator is not None
        else [node]
    )


def check_is_merge_node_for_logic_block(
    node: Node,
    logic_block_holder: LogicBlockHolder,
    node_class_graph: DiGraph,
) -> bool:
    """Checks if a node has a different path to the logic node other than the
    current path of the logic block. Subsequently checks that
    the penultimate node in the paths, i.e. the node immediately previous to
    the node to check, has out going logic or not and therefore can or cannot
    be, respectively, a merge point of the current path.

    :param node: The node to check.
    :type node: :class:`Node`
    :param logic_block_holder: The logic block holder.
    :type logic_block_holder: :class:`LogicBlockHolder`
    :param node_class_graph: The node class graph.
    :type node_class_graph: :class:`DiGraph`
    :return: `True` if the node has a different path to the logic node other
    than the current path of the logic block, `False` otherwise.
    :rtype: `bool`
    """
    if logic_block_holder.will_merge:
        return True
    # get all leaf nodes of the node classes of all the paths of the logic
    # block holder apart from the current path. Then check if there is a path
    # from the node to the node class that is not through the current path of
    # the logic block holder and does not have outgoing logic
    for path_node in chain(
        *[
            get_node_as_list(child)
            for child in logic_block_holder.paths[:-1]
        ]
    ):
        if path_node == node:
            continue
        if has_path(node_class_graph, path_node, node):
            # check if there is at least one incoming node that has a path to
            # the path_node and not through the current path of the logic block
            # holder and does not have outgoing logic
            in_nodes_with_path_and_no_logic = []
            # make sure we handle bunched logic within the current path
            nodes_to_avoid = get_node_as_list(
                logic_block_holder.current_path
            )
            for in_node, _ in node_class_graph.in_edges(node):
                if check_has_path_not_through_nodes(
                    node_class_graph,
                    path_node,
                    in_node,
                    nodes_to_avoid,
                ):
                    if not in_node.outgoing_logic:
                        in_nodes_with_path_and_no_logic.append(in_node)
            if len(in_nodes_with_path_and_no_logic) == 0:
                continue
            return True
    return False
