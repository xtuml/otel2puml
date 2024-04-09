"""Configuration for the tests in the node_map_to_puml directory."""

from copy import deepcopy

import pytest
from pm4py import ProcessTree
from pm4py.objects.process_tree.obj import Operator

from tel2puml.pipelines.logic_detection_pipeline import Event
from tel2puml.node_map_to_puml.node import Node
from tel2puml.tel2puml_types import PUMLEvent


@pytest.fixture
def uids_and_event_types() -> list[tuple[str, str]]:
    """Returns a list of uids and event types.

    :return: The uids and event types.
    :rtype: `list`[`tuple`[`str`, `str`]]
    """
    return [
        ("uid1", "event1"),
        ("uid2", "event2"),
        ("uid3", "event3"),
    ]


@pytest.fixture
def nodes(uids_and_event_types: list[tuple[str, str]]) -> list[Node]:
    """Returns a list of nodes.

    :param uids_and_event_types: The uids and event types.
    :type uids_and_event_types: `list`[`tuple`[`str`, `str`]]
    :return: The nodes.
    :rtype: `list`[:class:`Node`]
    """
    return [
        Node(data=uid, event_type=event_type)
        for uid, event_type in uids_and_event_types
    ]


@pytest.fixture
def node(nodes: list[Node]) -> Node:
    """Returns a node.

    :param nodes: The nodes to use.
    :type nodes: `list`[:class:`Node`]
    :return: The node.
    :rtype: :class:`Node`
    """
    return_node = Node("test_data", "test_event_type")
    return_node.update_node_list_with_nodes(deepcopy(nodes), "incoming")
    return_node.update_node_list_with_nodes(deepcopy(nodes), "outgoing")
    return return_node


@pytest.fixture
def node_with_child_to_stub(nodes: list[Node]) -> Node:
    """Returns a node with a child missing from incoming and outgoing.

    :param nodes: The child nodes to use.
    :type nodes: `list`[:class:`Node`]
    :return: The node with a child missing.
    :rtype: :class:`Node`
    """
    return_node = Node("test_data", "test_event_type")
    return_node.update_node_list_with_nodes(deepcopy(nodes)[:-1], "incoming")
    return_node.update_node_list_with_nodes(deepcopy(nodes)[:-1], "outgoing")
    return return_node


@pytest.fixture
def process_tree_no_logic(
    uids_and_event_types: list[tuple[str, str]],
) -> ProcessTree:
    """Returns a process tree with no logic.

    :param uids_and_event_types: The uids and event types.
    :type: `list`[`tuple`[`str`, `str`]]
    :return: The process tree with no logic.
    :rtype: :class:`ProcessTree`
    """
    process_tree = ProcessTree(operator=Operator.SEQUENCE)
    children = []
    for _, event_type in uids_and_event_types:
        children.append(ProcessTree(label=event_type))
    process_tree.children = children
    return process_tree


@pytest.fixture
def process_tree_with_and_logic_gate(
    uids_and_event_types: list[tuple[str, str]],
) -> ProcessTree:
    """Returns a process tree with an AND logic gate.

    :param uids_and_event_types: The uids and event types.
    :type: `list`[`tuple`[`str`, `str`]]
    :return: The process tree with an AND logic gate.
    :rtype: :class:`ProcessTree`
    """
    process_tree = ProcessTree(operator=Operator.PARALLEL)
    children = []
    for _, event_type in uids_and_event_types:
        children.append(ProcessTree(label=event_type))
    process_tree.children = children
    return process_tree


@pytest.fixture
def process_tree_with_or_logic_gate(
    uids_and_event_types: list[tuple[str, str]],
) -> ProcessTree:
    """Returns a process tree with an OR logic gate.

    :param uids_and_event_types: The uids and event types.
    :type: `list`[`tuple`[`str`, `str`]]
    :return: The process tree with an OR logic gate.
    :rtype: :class:`ProcessTree`
    """
    process_tree = ProcessTree(operator=Operator.OR)
    children = []
    for _, event_type in uids_and_event_types:
        children.append(ProcessTree(label=event_type))
    process_tree.children = children
    return process_tree


@pytest.fixture
def process_tree_with_xor_logic_gate(
    uids_and_event_types: list[tuple[str, str]],
) -> ProcessTree:
    """Returns a process tree with an XOR logic gate.

    :param uids_and_event_types: The uids and event types.
    :type: `list`[`tuple`[`str`, `str`]]
    :return: The process tree with an XOR logic gate.
    :rtype: :class:`ProcessTree`
    """
    process_tree = ProcessTree(operator=Operator.XOR)
    children = []
    for _, event_type in uids_and_event_types:
        children.append(ProcessTree(label=event_type))
    process_tree.children = children
    return process_tree


@pytest.fixture
def process_tree_with_and_xor_logic_gate(
    uids_and_event_types: list[tuple[str, str]],
) -> ProcessTree:
    """Returns a process tree with an AND and XOR logic gate. The first event
    type is connected to an AND logic gate and the rest are connected to an XOR

    :param uids_and_event_types: The uids and event types.
    :type uids_and_event_types: `list`[`tuple`[`str`, `str`]]
    :return: The process tree with an AND and XOR logic gate.
    :rtype: :class:`ProcessTree`
    """
    process_tree = ProcessTree(operator=Operator.PARALLEL)
    children = []
    for _, event_type in uids_and_event_types[:1]:
        children.append(ProcessTree(label=event_type))
    xor_process_tree = ProcessTree(operator=Operator.XOR)
    xor_children = []
    for _, event_type in uids_and_event_types[1:]:
        xor_children.append(ProcessTree(label=event_type))
    xor_process_tree.children = xor_children
    children.append(xor_process_tree)
    process_tree.children = children
    return process_tree


@pytest.fixture
def events(
    process_tree_with_and_logic_gate: ProcessTree,
) -> dict[str, Event]:
    """Returns a dictionary of events.

    :param process_tree_with_and_logic_gate: The process tree with and logic.
    :type process_tree_with_and_logic_gate: :class:`ProcessTree`
    :return: The events as a dictionary of event types mapped to logic tree
    :rtype: `dict`[`str`, :class:`Event`]
    """
    process_trees_names_map = {
        "and_logic_1": process_tree_with_and_logic_gate,
        "and_logic_2": deepcopy(process_tree_with_and_logic_gate),
    }
    events_map = {}
    for event_type, process_tree in process_trees_names_map.items():
        event = Event(event_type=event_type)
        event.logic_gate_tree = process_tree
        events_map[event_type] = event
    return events_map


@pytest.fixture
def node_map(
    events: dict[str, Event],
    nodes: list[Node],
) -> dict[str, list[Node]]:
    """Returns a dictionary of event type mapped to nodes.

    :param events: The events to map.
    :type events: `dict`[`str`, :class:`Event`]
    :param nodes: The nodes to map.
    :type nodes: `list`[:class:`Node`]
    :return: The event types mapped to nodes.
    :rtype: `dict`[`str`, `list`[:class:`Node`]]"""
    node_map = {}
    for event_type in events.keys():
        node = Node(data=event_type, event_type=event_type)
        node.update_node_list_with_nodes(nodes, "incoming")
        node.update_node_list_with_nodes(nodes, "outgoing")
        node_map[event_type] = [node]
    return node_map


@pytest.fixture
def process_tree_with_BRANCH(
    uids_and_event_types: list[tuple[str, str]],
) -> ProcessTree:
    """
    Creates a process tree with a BRANCH operator.

    Args:
        uids_and_event_types (list[tuple[str, str]]): A list of tuples
            containing uids and event types.

    Returns:
        ProcessTree: The process tree with the BRANCH operator.

    """
    children = []
    for _, event_type in uids_and_event_types[1:]:
        children.append(ProcessTree(label=event_type))

    process_tree = ProcessTree(
        operator=PUMLEvent.BRANCH,
        children=[ProcessTree(label="A", children=children)],
    )
    return process_tree


@pytest.fixture
def process_tree_with_BRANCH_plus_XOR(
    uids_and_event_types: list[tuple[str, str]],
) -> ProcessTree:
    """
    Creates a ProcessTree node representing a branch in the logic tree.

    Args:
        event_node_map (dict[str, list[Node]]): A dictionary mapping event
            names to lists of nodes.

    Returns:
        ProcessTree: The ProcessTree node representing the branch.
    """

    xor_children = []
    for _, event_type in uids_and_event_types[1:]:
        xor_children.append(ProcessTree(label=event_type))

    process_tree = ProcessTree(
        operator=PUMLEvent.BRANCH,
        children=[
            ProcessTree(operator=Operator.XOR, children=xor_children),
        ],
    )
    return process_tree


@pytest.fixture
def node_for_BRANCH_plus_XOR(
    uids_and_event_types: list[tuple[str, str]],
) -> Node:
    """
    Creates a Node object representing a branch in the logic tree.

    Args:
        event_node_map (dict[str, list[Node]]): A dictionary mapping event
            names to lists of nodes.

    Returns:
        Node: The Node object representing the branch.
    """
    node = Node(
        uid=uids_and_event_types[0][0], event_type=uids_and_event_types[0][1]
    )
    for uid, event_type in uids_and_event_types[1:]:
        node.update_node_list_with_nodes(
            [Node(data=uid, event_type=event_type, incoming=[node])],
            "outgoing",
        )
    return node
