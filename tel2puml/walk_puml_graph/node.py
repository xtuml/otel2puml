"""This module holds the 'node' class"""

from typing import Literal, NamedTuple, Optional
from uuid import uuid4
import logging

from networkx import DiGraph

from pm4py import ProcessTree
from pm4py.objects.process_tree.obj import Operator

from tel2puml.events import EventSet
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
        self.incoming = [] if incoming is None else incoming
        self.outgoing = [] if outgoing is None else outgoing
        self.incoming_logic = [] if incoming_logic is None else incoming_logic
        self.outgoing_logic = [] if outgoing_logic is None else outgoing_logic
        self.uid = uid
        self.operator = operator
        self.event_type = event_type
        self.is_stub = is_stub

        self.event_types: set[PUMLEvent] = (
            set() if event_types is None else event_types
        )

        self._eventsets_incoming: set[EventSet] | None = None
        self.is_loop_kill_path: list[bool] = []

    def __repr__(self) -> str:
        return (self.uid if self.uid is not None else "None") + ":" + (
            self.event_type or self.operator or "None"
        )

    def __hash__(self) -> int:
        return hash(self.uid)

    @property
    def lonely_merge(self) -> Optional["Node"]:
        """Gets the lonley merge node.

        :return: The lonley merge node.
        :rtype: :class:`Node` | `None`
        """
        lonely_merge = None
        if len(self.is_loop_kill_path) <= 1:
            return None
        for index, path in enumerate(self.is_loop_kill_path):
            if not path:
                if lonely_merge is not None:
                    return None
                lonely_merge = self.outgoing_logic[index]
        return lonely_merge

    @property
    def eventsets_incoming(self) -> set[EventSet]:
        """Gets the incoming event sets.

        :return: The incoming event sets.
        :rtype: :class:`EventSet`
        """
        if self._eventsets_incoming is None:
            raise ValueError("Event sets incoming is not set")
        return self._eventsets_incoming

    @eventsets_incoming.setter
    def eventsets_incoming(self, value: set[EventSet]) -> None:
        """Sets the incoming event sets.

        :param value: The value to set.
        :type value: :class:`EventSet`
        """
        if self.event_type is None:
            raise ValueError("Event type is not set")
        self._eventsets_incoming = value

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
        direction: Literal["incoming"] | Literal["outgoing"],
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

    def get_puml_event_types(self) -> tuple[PUMLEvent, ...]:
        """Gets the PUML event types for the node if it is an event node or
        `None` otherwise.

        :return: The PUML event types for the node.
        :rtype: `tuple`[:class:`PUMLEvent`] | `None`
        """
        if self.event_types:
            return tuple(self.event_types)
        return tuple()

    def get_operator_type(self) -> PUMLOperator:
        """Gets the PUML operator type for the node if it is a logic node or
        raises an error otherwise.

        :return: The PUML operator type for the node.
        :rtype: :class:`PUMLOperator`
        """
        for operator in PUMLOperator:
            if self.operator == operator.name:
                return operator
        raise ValueError("Operator has not been set")

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
                self.is_loop_kill_path[index] = node.all_paths_are_loop_kill()

    def all_paths_are_loop_kill(self) -> bool:
        """Checks if all paths kill.

        :return: `True` if all paths kill, `False` otherwise.
        :rtype: `bool`
        """
        if len(self.is_loop_kill_path) == 0:
            return False
        return all(self.is_loop_kill_path)


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
