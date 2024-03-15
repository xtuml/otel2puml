"""This module holds the 'node' class"""

from typing import Literal
from uuid import uuid4
import logging

from pm4py import ProcessTree
from pm4py.objects.process_tree.obj import Operator

from tel2puml.pipelines.logic_detection_pipeline import Event


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
    ) -> None:
        """Constructor method."""
        self.data = data if data is None else operator
        self.incoming = [] if incoming is None else incoming
        self.outgoing = [] if outgoing is None else outgoing
        self.incoming_logic = [] if incoming_logic is None else incoming_logic
        self.outgoing_logic = [] if outgoing_logic is None else outgoing_logic
        self.uid = uid if uid is not None else data
        self.operator = operator
        self.event_type = event_type
        self.is_stub = is_stub

        self.branch_enum = ["AND", "OR", "XOR", "LOOP", "BRANCH"]

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
        if direction == "incoming":
            logic_list = self.incoming_logic
        else:
            logic_list = self.outgoing_logic
        if logic_tree.label is not None:
            if logic_tree.label not in event_node_map:
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
