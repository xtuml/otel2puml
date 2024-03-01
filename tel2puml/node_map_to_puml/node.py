"""This module holds the 'node' class"""
from typing import Literal

from pm4py import ProcessTree

from tel2puml.pipelines.logic_detection_pipeline import Event


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
    ) -> None:
        """Constructor method.
        """
        self.data = data if data is None else operator
        self.incoming = [] if incoming is None else incoming
        self.outgoing = [] if outgoing is None else outgoing
        self.incoming_logic = [] if incoming_logic is None else incoming_logic
        self.outgoing_logic = [] if outgoing_logic is None else outgoing_logic
        self.uid = uid if uid is not None else data
        self.operator = operator
        self.event_type = event_type

        self.branch_enum = ["AND", "OR", "XOR", "LOOP"]
    

    @property
    def event_node_map(self) -> dict[str, "Node"]:
        """Returns a map of event types to nodes.
        
        :return: A map of event types to nodes.
        :rtype: `dict`[`str`, `Node`]
        """
        event_node_map = {}
        for node in self.incoming:
            if node.event_type is None:
                raise ValueError(f"Node event type is not set for node with uid {self.uid}")
            event_node_map[node.event_type] = node
        return event_node_map

    def load_logic_into_list(
        self,
        logic_tree: ProcessTree,
        direction: Literal["incoming", "outgoing"]
    ) -> None:
        """Loads logic into the logic list.

        :param logic_tree: The logic tree to load.
        :type logic_tree: :class:`ProcessTree`
        :param direction: The direction to load the logic.
        :type direction: `Literal`[`"incoming"`, `"outgoing"`]
        """
        if direction not in ["incoming", "outgoing"]:
            raise ValueError(f"Invalid direction {direction}")
        event_node_map = self.event_node_map
        self._load_logic_into_logic_list(logic_tree, event_node_map, direction)
    
    def _load_logic_into_logic_list(
        self,
        logic_tree: ProcessTree,
        event_node_map: dict[str, "Node"],
        direction: Literal["incoming", "outgoing"]
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
        for child in logic_tree.children:
            if child.label is not None:
                logic_list.append(event_node_map[child.label])
            else:
                logic_operator_node = Node(
                    operator=child.operator.name,
                )
                logic_operator_node._load_logic_into_logic_list(
                    logic_operator_node,
                    event_node_map,
                    direction
                )
                logic_list.append(logic_operator_node)


def load_all_logic_trees_into_nodes(
    events: dict[str, Event],
    nodes: dict[str, list[Node]],
    direction: Literal["incoming", "outgoing"]
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
        for node in nodes[event_type]:
            node.load_logic_into_list(
                event.logic_gate_tree, direction
            )