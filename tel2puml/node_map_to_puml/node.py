"""This module holds the 'node' class"""

from typing import Literal, NamedTuple
from uuid import uuid4
import logging

from networkx import DiGraph

from pm4py import ProcessTree
from pm4py.objects.process_tree.obj import Operator

from tel2puml.events import Event
from tel2puml.logic_detection import Operator as Logic_operator

from tel2puml.tel2puml_types import PUMLEvent, PUMLOperator


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

        self.lonely_merge: "Node" | None = None
        self._event_incoming: Event | None = None
        self.is_loop_kill_path: list[bool] = []

    def __repr__(self) -> str:
        return self.uid + ":" + (self.event_type or self.operator or "None")

    def __hash__(self) -> int:
        return hash(self.uid)

    @property
    def event_incoming(self) -> Event:
        """Gets the event incoming.

        :return: The event incoming.
        :rtype: :class:`Event`
        """
        if self._event_incoming is None:
            raise ValueError("Event incoming is not set")
        return self._event_incoming

    @event_incoming.setter
    def event_incoming(self, value: Event) -> None:
        """Sets the event incoming.

        :param value: The value to set.
        :type value: :class:`Event`
        """
        if self.event_type is None:
            raise ValueError("Event type is not set")
        self._event_incoming = value

    def update_logic_list(
        self, node: "Node", direction: Literal["incoming", "outgoing"]
    ) -> None:
        """Updates the logic list.

        :param direction: The direction to update the logic list.
        :type direction: `Literal`[`"incoming"`, `"outgoing"`]
        """
        if direction not in ["incoming", "outgoing"]:
            raise ValueError(f"Invalid direction {direction}")
        if direction == "incoming":
            self.incoming_logic.append(node)
        else:
            self.outgoing_logic.append(node)
            self.is_loop_kill_path.append(False)

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
                root_node.update_event_types(PUMLEvent.BRANCH)
                for child in logic_tree.children:
                    self._load_logic_into_logic_list(
                        child, event_node_map, direction, root_node
                    )
                return

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
                self.update_logic_list(
                    event_node_map[logic_tree.label], direction
                )

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
            self.update_logic_list(logic_operator_node, direction)

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

    def update_event_types(self, event_type: PUMLEvent) -> None:
        """Updates the event types.

        :param event_type: The event type to update.
        :type event_type: :class:`PUMLEvent`
        """
        self.event_types.add(event_type)

    def get_puml_event_types(self) -> tuple[PUMLEvent]:
        """Gets the PUML event types for the node if it is an event node or
        `None` otherwise.

        :return: The PUML event types for the node.
        :rtype: `tuple`[:class:`PUMLEvent`] | `None`
        """
        if self.event_types:
            return tuple(self.event_types)
        return tuple()

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

    def get_outgoing_logic_by_indices(
        self, indices: list[int]
    ) -> list["Node"]:
        """Gets the outgoing logic by indices.

        :param indices: The indices to get the outgoing logic by.
        :type indices: `list`[`int`]
        :return: The outgoing logic by indices.
        :rtype: `list`[:class:`Node`]
        """
        return [self.outgoing_logic[index] for index in indices]

    def set_outgoing_logic(self, outgoing_logic: list["Node"]) -> None:
        """Sets the outgoing logic.

        :param outgoing_logic: The outgoing logic to set.
        :type outgoing_logic: `list`[:class:`Node`]
        """
        self.outgoing_logic = outgoing_logic

    def update_loop_kill_paths_from_given_leaf_nodes(
        self,
        leaf_nodes: set[str],
    ) -> None:
        """Updates the loop kill paths from given leaf nodes.

        :param leaf_nodes: The leaf nodes to update the loop kill paths from.
        :type leaf_nodes: `set`[`str`]
        """
        if self.operator is None:
            return
        for index, node in enumerate(self.outgoing_logic):
            if all(
                leaf_of_logic.uid in leaf_nodes
                for leaf_of_logic in get_node_as_list(node)
            ):
                self.is_loop_kill_path[index] = True
            else:
                node.update_loop_kill_paths_from_given_leaf_nodes(leaf_nodes)


class SubGraphNode(Node):
    """Represents a sub graph of Node instances

    :param _sub_graph: The subgraph
    :type: :class: `DiGraph`
    :param uid: The unique identifier of the sub graph node, defaults to `None`
    :type uid: `str` | `None`, optional
    :param event_type: The event type of the sub graph node, defaults to `None`
    :type event_type: `str` | `None`, optional
    :param start_uid: The start uid of the sub graph node, defaults to `None`
    :type start_uid: `str` | `None`, optional
    :param end_uid: The end uid of the sub graph node, defaults to `None`
    :type end_uid: `str` | `None`, optional
    :param break_uids: The break uids of the sub graph node, defaults to `None`
    :type break_uids: `set`[`str`] | `None`, optional
    """

    def __init__(
        self,
        uid: str,
        event_type: str,
        start_uid: str | None = None,
        end_uid: str | None = None,
        break_uids: set[str] | None = None,
    ) -> None:
        """Constructor method"""
        super().__init__(uid=uid, event_type=event_type)
        self._sub_graph: "DiGraph[Node]" | None = None
        self._start_uid: str | None = start_uid
        self._end_uid: str | None = end_uid
        self._break_uids: set[str] | None = break_uids

    @property
    def start_uid(self) -> str:
        """Getter for start_uid."""
        if self._start_uid is None:
            raise AttributeError("start_uid is not set.")
        return self._start_uid

    @start_uid.setter
    def start_uid(self, start_uid: str) -> None:
        """Setter for start_uid."""
        if self._start_uid is None:
            self._start_uid = start_uid
        else:
            raise AttributeError("start_uid is already set.")

    @property
    def end_uid(self) -> str:
        """Getter for end_uid."""
        if self._end_uid is None:
            raise AttributeError("end_uid is not set.")
        return self._end_uid

    @end_uid.setter
    def end_uid(self, end_uid: str) -> None:
        """Setter for end_uid."""
        if self._end_uid is None:
            self._end_uid = end_uid
        else:
            raise AttributeError("end_uid is already set.")

    @property
    def break_uids(self) -> set[str]:
        """Getter for break_uids."""
        if self._break_uids is None:
            raise AttributeError("break_uids is not set.")
        return self._break_uids

    @break_uids.setter
    def break_uids(self, break_uids: set[str]) -> None:
        """Setter for break_uids."""
        if self._break_uids is None:
            self._break_uids = break_uids
        else:
            raise AttributeError("break_uids is already set.")

    @property
    def sub_graph(self) -> "DiGraph[Node]":
        """Gets the sub graph

        :return: The subgraoh
        :rtype: :class:`DiGraph`
        """
        if self._sub_graph is None:
            raise ValueError("Sub graph is not set")
        return self._sub_graph

    @sub_graph.setter
    def sub_graph(self, sub_graph: "DiGraph[Node]") -> None:
        """Sets the sub graph

        :param sub_graph: The sub graph to set
        :type sub_graph: :class: `DiGraph`
        """
        if self._sub_graph is not None:
            raise ValueError("Sub graph has already been set")
        self._sub_graph = sub_graph


class NodeTuple(NamedTuple):
    """Named tuple for node graph edge.

    :param out_node: Start node for the edge
    :type out_node: `Node`
    :param in_node: End node for the edge
    :type in_node: `Node`
    """

    out_node: Node
    in_node: Node


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
    markov_graph: "DiGraph[str]",
    node_event_references: dict[str, str],
) -> tuple["DiGraph[Node]", dict[str, list[Node]]]:
    """Creates a NetworkX graph of nodes from a Markov graph.

    :param markov_graph: The Markov graph to create the NetworkX graph from.
    :type markov_graph: :class:`DiGraph`[`str`]
    :param node_event_references: The node event references.
    :type node_event_references: `dict`[`str`, `str`]
    :return: A tuple containing the NetworkX graph and the event node
    reference.
    :rtype: `tuple`[:class:`DiGraph`[:class:`Node`], `dict`[`str`,
    `list`[:class:`Node`]]]
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
    node_class_network_x_graph: "DiGraph[Node]",
) -> dict[str, list[Node]]:
    """Creates an event node reference.

    :param node_class_network_x_graph: The node class NetworkX graph.
    :type node_class_network_x_graph: :class:`DiGraph`[:class:`Node`]
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


def load_all_incoming_events_into_nodes(
    events: dict[str, Event],
    nodes: dict[str, list[Node]],
) -> None:
    """Loads all incoming events into nodes.

    :param events: The events to load.
    :type events: `dict`[`str`, :class:`Event`]
    :param nodes: The nodes to load the events into.
    :type nodes: `dict`[`str`, `list`[:class:`Node`]]
    """
    for event_type, event in events.items():
        for node in nodes[event_type]:
            node.event_incoming = event
            if event.logic_gate_tree is not None:
                if event.logic_gate_tree.operator == Logic_operator.BRANCH:
                    node.update_event_types(PUMLEvent.MERGE)


def merge_markov_without_loops_and_logic_detection_analysis(
    markov_graph_ref_pair: tuple["DiGraph[str]", dict[str, str]],
    incoming_logic_events: dict[str, Event],
    outgoing_logic_events: dict[str, Event],
) -> tuple["DiGraph[Node]", dict[str, list[Node]]]:
    """Merges a Markov graph without loops and logic detection analysis.

    :param markov_graph_ref_pair: The Markov graph reference pair.
    :type markov_graph_ref_pair: `tuple`[:class:`DiGraph`[`str`],
    `dict`[`str`, `str`]]
    :param incoming_logic_events: The incoming logic events.
    :type incoming_logic_events: `dict`[`str`, :class:`Event`]
    :param outgoing_logic_events: The outgoing logic events.
    :type outgoing_logic_events: `dict`[`str`, :class:`Event`]
    :return: A tuple containing the NetworkX graph and the event node
    reference.
    :rtype: `tuple`[:class:`DiGraph`[:class:`Node`], `dict`[`str`,
    `list`[:class:`Node`]]]
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
    load_all_incoming_events_into_nodes(incoming_logic_events, event_node_map)
    return node_class_graph, event_node_map


def get_node_as_list(node: Node) -> list[Node]:
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
        node.traverse_logic("outgoing")
        if node.operator is not None
        else [node]
    )
