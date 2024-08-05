"""Configuration for the tests in the walk_puml_graph directory."""

from copy import deepcopy

import pytest
from pm4py import ProcessTree
from pm4py.objects.process_tree.obj import Operator
from networkx import DiGraph

from tel2puml.events import Event
from tel2puml.logic_detection import Operator as Logic_operator
from tel2puml.walk_puml_graph.node import Node, SubGraphNode
from tel2puml.tel2puml_types import (
    DUMMY_END_EVENT,
    DUMMY_START_EVENT,
    PUMLEvent,
    PUMLOperator,
)
from tel2puml.puml_graph.graph import PUMLGraph
from tel2puml.loop_detection.loop_types import LoopEvent, LOOP_EVENT_TYPE


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
        Node(uid=uid, event_type=event_type)
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
    return_node = Node(uid="test_data", event_type="test_event_type")
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
    return_node = Node(uid="test_data", event_type="test_event_type")
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
        node = Node(uid=event_type, event_type=event_type)
        node.update_node_list_with_nodes(nodes, "incoming")
        node.update_node_list_with_nodes(nodes, "outgoing")
        node_map[event_type] = [node]
    return node_map


@pytest.fixture
def process_tree_with_BRANCH() -> ProcessTree:
    """
    Creates a process tree with a BRANCH operator.

    :return: The process tree with a BRANCH operator.
    :rtype: :class:`ProcessTree`
    """

    process_tree = ProcessTree(
        operator=Logic_operator.BRANCH,
        children=[ProcessTree(label="A")],
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
        operator=Logic_operator.BRANCH,
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
            [Node(uid=uid, event_type=event_type, incoming=[node])],
            "outgoing",
        )
    return node


@pytest.fixture
def nested_sub_graph() -> "DiGraph[Node]":
    """Returns a nested sub graph with a self loop event."""
    start_node = Node(uid=DUMMY_START_EVENT, event_type=DUMMY_START_EVENT)
    end_node = Node(uid=DUMMY_END_EVENT, event_type=DUMMY_END_EVENT)
    nested_self_loop_event = Node(
        uid="nested_self_loop_event", event_type="nested_self_loop_event"
    )
    nested_sub_graph_graph: "DiGraph[Node]" = DiGraph()
    nested_sub_graph_graph.add_edge(start_node, nested_self_loop_event)
    nested_sub_graph_graph.add_edge(nested_self_loop_event, end_node)
    start_node.update_node_list_with_node(nested_self_loop_event, "outgoing")
    nested_self_loop_event.update_node_list_with_node(end_node, "outgoing")
    return nested_sub_graph_graph


@pytest.fixture
def sub_graph(nested_sub_graph: "DiGraph[Node]") -> "DiGraph[Node]":
    """Returns a sub graph with a nested sub graph node."""
    start_node = Node(uid=DUMMY_START_EVENT, event_type=DUMMY_START_EVENT)
    end_node = Node(uid=DUMMY_END_EVENT, event_type=DUMMY_END_EVENT)
    A = Node(uid="A", event_type="A")
    nested_sub_graph_node = SubGraphNode(
        uid="nested_sub_graph_node", event_type="nested_sub_graph_node"
    )
    nested_sub_graph_node.update_event_types(PUMLEvent.LOOP)
    nested_sub_graph_node.sub_graph = nested_sub_graph
    operator_node = Node(uid="operator_node", operator="XOR")
    operator_node.update_logic_list(A, "outgoing")
    operator_node.update_logic_list(nested_sub_graph_node, "outgoing")
    start_node.update_logic_list(operator_node, "outgoing")
    A.update_node_list_with_node(end_node, "outgoing")
    nested_sub_graph_node.update_node_list_with_node(end_node, "outgoing")
    sub_graph_graph: "DiGraph[Node]" = DiGraph()
    sub_graph_graph.add_edge(start_node, A)
    sub_graph_graph.add_edge(start_node, nested_sub_graph_node)
    sub_graph_graph.add_edge(A, end_node)
    sub_graph_graph.add_edge(nested_sub_graph_node, end_node)
    return sub_graph_graph


@pytest.fixture
def graph(sub_graph: "DiGraph[Node]") -> "DiGraph[Node]":
    """Returns a graph with a sub graph node inlcuding a
    nested sub graph node."""
    start_node = Node(uid=DUMMY_START_EVENT, event_type=DUMMY_START_EVENT)
    A = Node(uid="A", event_type="A")
    B = Node(uid="B", event_type="B")
    sub_graph_node = SubGraphNode(
        uid="sub_graph_node", event_type="sub_graph_node"
    )
    sub_graph_node.update_event_types(PUMLEvent.LOOP)
    sub_graph_node.sub_graph = sub_graph
    operator_node = Node(uid="operator_node", operator="XOR")
    operator_node.update_logic_list(A, "outgoing")
    operator_node.update_logic_list(sub_graph_node, "outgoing")
    start_node.update_logic_list(operator_node, "outgoing")
    A.update_node_list_with_node(sub_graph_node, "outgoing")
    sub_graph_node.update_node_list_with_node(B, "outgoing")
    graph_graph: "DiGraph[Node]" = DiGraph()
    graph_graph.add_edge(start_node, A)
    graph_graph.add_edge(A, sub_graph_node)
    graph_graph.add_edge(sub_graph_node, B)
    graph_graph.add_edge(start_node, sub_graph_node)
    return graph_graph


@pytest.fixture
def expected_nested_sub_graph_puml_graph() -> PUMLGraph:
    """Returns a PUMLGraph object representing the
    expected nested sub graph."""
    puml_graph = PUMLGraph()
    start_node = puml_graph.create_event_node(DUMMY_START_EVENT)
    end_node = puml_graph.create_event_node(DUMMY_END_EVENT)
    nested_self_loop = puml_graph.create_event_node("nested_self_loop_event")
    puml_graph.add_edge(start_node, nested_self_loop)
    puml_graph.add_edge(nested_self_loop, end_node)
    return puml_graph


@pytest.fixture
def expected_sub_graph_puml_graph(
    expected_nested_sub_graph_puml_graph: PUMLGraph,
    sub_graph: "DiGraph[Node]",
) -> PUMLGraph:
    """Returns a PUMLGraph object representing the expected sub graph."""
    puml_graph = PUMLGraph()
    start_node = puml_graph.create_event_node(DUMMY_START_EVENT)
    end_node = puml_graph.create_event_node(DUMMY_END_EVENT)
    A = puml_graph.create_event_node("A")
    nested_sub_graph_node_ref = [
        node
        for node in sub_graph.nodes
        if node.event_type == "nested_sub_graph_node"
    ][0]
    nested_sub_graph_node = puml_graph.create_event_node(
        "nested_sub_graph_node",
        PUMLEvent.LOOP,
        sub_graph=expected_nested_sub_graph_puml_graph,
        parent_graph_node=nested_sub_graph_node_ref,
    )
    start_xor, end_xor = puml_graph.create_operator_node_pair(PUMLOperator.XOR)
    puml_graph.add_edge(start_node, start_xor)
    puml_graph.add_edge(start_xor, A)
    puml_graph.add_edge(start_xor, nested_sub_graph_node)
    puml_graph.add_edge(A, end_xor)
    puml_graph.add_edge(nested_sub_graph_node, end_xor)
    puml_graph.add_edge(end_xor, end_node)
    return puml_graph


@pytest.fixture
def expected_graph_puml_graph(
    expected_sub_graph_puml_graph: PUMLGraph,
    graph: "DiGraph[Node]",
) -> PUMLGraph:
    """Returns a PUMLGraph object representing the expected graph."""
    puml_graph = PUMLGraph()
    start_node = puml_graph.create_event_node(DUMMY_START_EVENT)
    A = puml_graph.create_event_node("A")
    B = puml_graph.create_event_node("B")
    sub_graph_node_ref = [
        node for node in graph.nodes if node.event_type == "sub_graph_node"
    ][0]
    sub_graph_node_1 = puml_graph.create_event_node(
        "sub_graph_node",
        PUMLEvent.LOOP,
        sub_graph=expected_sub_graph_puml_graph,
        parent_graph_node=sub_graph_node_ref,
    )
    sub_graph_node_2 = puml_graph.create_event_node(
        "sub_graph_node",
        PUMLEvent.LOOP,
        sub_graph=expected_sub_graph_puml_graph,
        parent_graph_node=sub_graph_node_ref,
    )
    start_xor, end_xor = puml_graph.create_operator_node_pair(PUMLOperator.XOR)
    puml_graph.add_edge(start_node, start_xor)
    puml_graph.add_edge(start_xor, A)
    puml_graph.add_edge(start_xor, sub_graph_node_1)
    puml_graph.add_edge(A, sub_graph_node_2)
    puml_graph.add_edge(sub_graph_node_1, end_xor)
    puml_graph.add_edge(sub_graph_node_2, end_xor)
    puml_graph.add_edge(end_xor, B)
    return puml_graph


@pytest.fixture
def sub_node_sub_event_graph() -> "DiGraph[Event]":
    """Returns a sub graph with a self loop event."""
    start_node = Event(uid=DUMMY_START_EVENT, event_type=DUMMY_START_EVENT)
    end_node = Event(uid=DUMMY_END_EVENT, event_type=DUMMY_END_EVENT)
    nested_self_loop_event = Event(
        uid="nested_self_loop_event", event_type="nested_self_loop_event"
    )
    nested_sub_graph_graph: "DiGraph[Event]" = DiGraph()
    nested_sub_graph_graph.add_edge(start_node, nested_self_loop_event)
    nested_sub_graph_graph.add_edge(nested_self_loop_event, end_node)
    for edge in nested_sub_graph_graph.edges:
        edge[0].update_event_sets([edge[1].event_type])
        edge[1].update_in_event_sets([edge[0].event_type])
    return nested_sub_graph_graph


@pytest.fixture
def event_graph_nested_loop_event_and_events(
    sub_node_sub_event_graph: "DiGraph[Event]",
) -> tuple["DiGraph[Event]", list[Event]]:
    """Returns a Loop Event with a sub graph"""
    event1 = Event(event_type="A", uid="A")
    event2 = Event(event_type="B", uid="B")
    loop_event = LoopEvent(
        event_type=LOOP_EVENT_TYPE,
        subgraph=sub_node_sub_event_graph,
        start_uid="start_uid",
        end_uid="end_uid",
        break_uids=set(["break_uid1", "break_uid2"]),
    )
    event_graph: "DiGraph[Event]" = DiGraph()

    event_graph.add_node(event1)
    event_graph.add_node(event2)
    event_graph.add_node(loop_event)

    event_graph.add_edge(event1, loop_event)
    event_graph.add_edge(loop_event, event2)
    for edge in event_graph.edges:
        edge[0].update_event_sets([edge[1].event_type])
        edge[1].update_in_event_sets([edge[0].event_type])

    events = [event1, event2, loop_event]
    return (event_graph, events)


@pytest.fixture
def nested_sub_graph_node_with_kill_paths() -> SubGraphNode:
    """Returns a nested sub graph with a self loop event."""
    start_node = Node(uid=DUMMY_START_EVENT, event_type=DUMMY_START_EVENT)
    end_node = Node(uid=DUMMY_END_EVENT, event_type=DUMMY_END_EVENT)
    nested_self_loop_event = Node(
        uid="nested_self_loop_event", event_type="nested_self_loop_event"
    )
    nested_kill_path_node = Node(
        uid="nested_kill_path_node", event_type="nested_kill_path_node"
    )
    operator_node = Node(uid="operator_node", operator="XOR")
    operator_node.update_logic_list(nested_self_loop_event, "outgoing")
    operator_node.update_logic_list(nested_kill_path_node, "outgoing")
    start_node.update_logic_list(operator_node, "outgoing")
    nested_sub_graph_graph: "DiGraph[Node]" = DiGraph()
    nested_sub_graph_graph.add_edge(start_node, nested_self_loop_event)
    nested_sub_graph_graph.add_edge(nested_self_loop_event, end_node)
    nested_sub_graph_graph.add_edge(start_node, nested_kill_path_node)
    start_node.update_node_list_with_node(nested_self_loop_event, "outgoing")
    start_node.update_node_list_with_node(nested_kill_path_node, "outgoing")
    nested_self_loop_event.update_node_list_with_node(end_node, "outgoing")
    sub_graph_node = SubGraphNode(
        uid="sub_graph_node", event_type="sub_graph_node",
        start_uid=start_node.uid, end_uid=end_node.uid, break_uids=set()
    )
    sub_graph_node.sub_graph = nested_sub_graph_graph
    return sub_graph_node


@pytest.fixture
def sub_graph_node_with_kill_paths(
    nested_sub_graph_node_with_kill_paths: SubGraphNode,
) -> SubGraphNode:
    """Returns a sub graph with a nested sub graph node."""
    start_node = Node(uid=DUMMY_START_EVENT, event_type=DUMMY_START_EVENT)
    end_node = Node(uid=DUMMY_END_EVENT, event_type=DUMMY_END_EVENT)
    loop_event = nested_sub_graph_node_with_kill_paths
    kill_path_node = Node(
        uid="kill_path_node", event_type="kill_path_node"
    )
    operator_node = Node(uid="operator_node", operator="XOR")
    operator_node.update_logic_list(loop_event, "outgoing")
    operator_node.update_logic_list(kill_path_node, "outgoing")
    start_node.update_logic_list(operator_node, "outgoing")
    nested_sub_graph_graph: "DiGraph[Node]" = DiGraph()
    nested_sub_graph_graph.add_edge(start_node, loop_event)
    nested_sub_graph_graph.add_edge(loop_event, end_node)
    nested_sub_graph_graph.add_edge(start_node, kill_path_node)
    start_node.update_node_list_with_node(loop_event, "outgoing")
    start_node.update_node_list_with_node(kill_path_node, "outgoing")
    loop_event.update_node_list_with_node(end_node, "outgoing")
    sub_graph_node = SubGraphNode(
        uid="sub_graph_node", event_type="sub_graph_node",
        start_uid=start_node.uid, end_uid=end_node.uid, break_uids=set()
    )
    sub_graph_node.sub_graph = nested_sub_graph_graph
    return sub_graph_node


@pytest.fixture
def graph_with_nested_kill_paths(
    sub_graph_node_with_kill_paths: SubGraphNode,
) -> "DiGraph[Node]":
    """Returns a graph with a sub graph node inlcuding a nested sub graph node.
    """
    start_node = Node(uid=DUMMY_START_EVENT, event_type=DUMMY_START_EVENT)
    A = Node(uid="A", event_type="A")
    graph: "DiGraph[Node]" = DiGraph()
    graph.add_edge(start_node, A)
    graph.add_edge(A, sub_graph_node_with_kill_paths)
    start_node.update_node_list_with_node(A, "outgoing")
    A.update_node_list_with_node(sub_graph_node_with_kill_paths, "outgoing")
    return graph
