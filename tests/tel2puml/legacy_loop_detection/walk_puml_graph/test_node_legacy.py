"""Tests for the node module."""

from copy import deepcopy
from typing import Literal

from pm4py import ProcessTree
import networkx as nx

from tel2puml.walk_puml_graph.node import Node
from tel2puml.legacy_loop_detection.walk_puml_graph.node import (
    load_logic_tree_into_nodes,
    load_all_logic_trees_into_nodes,
    create_event_node_ref,
    create_networkx_graph_of_nodes_from_markov_graph,
    merge_markov_without_loops_and_logic_detection_analysis,
)
from tel2puml.pv_to_puml.data_ingestion import (
    update_all_connections_from_clustered_events,
)
from tel2puml.events import (
    Event,
    events_to_markov_graph,
)
from tel2puml.legacy_loop_detection.events import (
    get_event_reference_from_events,
)
from tel2puml.pv_event_simulator import (
    generate_test_data_event_sequences_from_puml,
)


def test_load_logic_tree_into_nodes_incoming(
    node: Node,
    process_tree_with_and_logic_gate: ProcessTree,
) -> None:
    """Test the load_logic_tree_into_nodes function for both incoming and
    outgoing nodes.

    :param node: The node to test.
    :type node: :class:`Node`
    :param process_tree_with_and_logic_gate: The process tree with and logic.
    :type process_tree_with_and_logic_gate: :class:`ProcessTree`
    """
    directions: list[Literal['incoming', 'outgoing']] = [
        "incoming", "outgoing"
    ]
    for direction in directions:
        nodes_list = [deepcopy(node), deepcopy(node)]
        load_logic_tree_into_nodes(
            process_tree_with_and_logic_gate, nodes_list, direction
        )
        for parent_node in nodes_list:
            direction_node_list = getattr(parent_node, direction)
            direction_logic_list = getattr(parent_node, f"{direction}_logic")
            assert len(direction_logic_list) == 1
            operator_node = direction_logic_list[0]
            assert operator_node.operator == "AND"
            operator_node_direction_logic_list = getattr(
                operator_node, f"{direction}_logic"
            )
            for direction_node in direction_node_list:
                assert direction_node in operator_node_direction_logic_list


def test_load_all_logic_trees_into_nodes(
    events: dict[str, Event],
    node_map: dict[str, list[Node]],
) -> None:
    """Test the load_all_logic_trees_into_nodes function for both incoming and
    outgoing nodes.

    :param events: The events to test.
    :type events: `dict`[`str`, :class:`Event`]
    :param node_map: The node map to test.
    :type node_map: `dict`[`str`, `list`[:class:`Node`]]
    """
    directions: list[Literal['incoming', 'outgoing']] = [
        "incoming", "outgoing"
    ]
    for direction in directions:
        load_all_logic_trees_into_nodes(events, node_map, direction)
        for nodes in node_map.values():
            node = nodes[0]
            direction_node_list = getattr(node, direction)
            direction_logic_list = getattr(node, f"{direction}_logic")
            assert len(direction_logic_list) == 1
            operator_node = direction_logic_list[0]
            assert operator_node.operator == "AND"
            operator_node_direction_logic_list = getattr(
                operator_node, f"{direction}_logic"
            )
            for direction_node in direction_node_list:
                assert direction_node in operator_node_direction_logic_list


def test_create_event_node_ref() -> None:
    """Test the create_event_node_ref function."""
    graph: "nx.DiGraph[Node]" = nx.DiGraph()
    node_1 = Node(uid="1", event_type="Event1")
    node_2 = Node(uid="2", event_type="Event2")
    node_3 = Node(uid="3", event_type="Event1")
    nodes = [node_1, node_2, node_3]
    for node in nodes:
        graph.add_node(node)
    event_node_references = create_event_node_ref(graph)
    expected_event_node_references = {
        "Event1": [node_1, node_3],
        "Event2": [node_2],
    }
    assert event_node_references == expected_event_node_references


def test_create_networkx_graph_of_nodes_from_markov_graph() -> None:
    """Test the create_networkx_graph_of_nodes_from_markov_graph function.

    The newly created graph should share the same nodes and edges as the but
    with nodes as :class:`Node` instances.
    """
    # setup
    test_data = generate_test_data_event_sequences_from_puml(
        "puml_files/simple_test.puml"
    )
    forward, _ = update_all_connections_from_clustered_events(test_data)
    markov_graph = events_to_markov_graph(forward.values())
    event_reference = get_event_reference_from_events(forward.values())
    # function call
    node_class_graph, _ = create_networkx_graph_of_nodes_from_markov_graph(
        markov_graph, event_reference
    )
    # test
    # check the graphs are mirrors of one another
    assert len(node_class_graph.nodes) == len(markov_graph.nodes)
    for node in node_class_graph.nodes:
        assert isinstance(node.uid, str)
        assert node.uid in markov_graph.nodes
        assert node.event_type == event_reference[node.uid]
    for edge in node_class_graph.edges:
        assert isinstance(edge[0].uid, str)
        assert isinstance(edge[1].uid, str)
        assert (edge[0].uid, edge[1].uid) in markov_graph.edges


def test_merge_markov_without_loops_and_logic_detection_analysis() -> None:
    """Test the merge_markov_without_loops_and_logic_detection_analysis
    function.

    The function should merge the markov graph with the logic detection
    analysis and return a graph with the expected connections and logic.
    """
    # setup
    test_data_logic = generate_test_data_event_sequences_from_puml(
        "puml_files/simple_test.puml"
    )
    forward, backward = update_all_connections_from_clustered_events(
        test_data_logic
    )
    markov_graph = events_to_markov_graph(forward.values())
    event_reference = get_event_reference_from_events(forward.values())
    # function call
    node_class_graph, _ = (
        merge_markov_without_loops_and_logic_detection_analysis(
            (markov_graph, event_reference),
            backward,
            forward,
        )
    )
    # test
    expected_outgoing_event_type_logic: dict[str, dict[str, list[str]]] = {
        "A": {"XOR": ["B", "D"]},
        "B": {},
        "C": {},
        "D": {},
    }
    expected_incoming_event_type_logic: dict[str, dict[str, list[str]]] = {
        "A": {}, "B": {}, "C": {}, "D": {}
    }
    expected_outgoing_event_type = {
        "A": ["B", "D"],
        "B": ["C"],
        "C": [],
        "D": [],
    }
    expected_incoming_event_type = {
        "A": [],
        "B": ["A"],
        "C": ["B"],
        "D": ["A"],
    }
    # test that every node has the expected connections and logic inserted
    for node in node_class_graph.nodes:
        assert isinstance(node.event_type, str)
        for outgoing_logic_node in node.outgoing_logic:
            assert outgoing_logic_node.operator in (
                expected_outgoing_event_type_logic[node.event_type]
            )
            assert sorted(  # type: ignore[type-var]
                [
                    logic_node.event_type
                    for logic_node in outgoing_logic_node.outgoing_logic
                ]
            ) == sorted(
                expected_outgoing_event_type_logic[node.event_type][
                    outgoing_logic_node.operator
                ]
            )
        for incoming_logic_node in node.incoming_logic:
            assert isinstance(incoming_logic_node.operator, str)
            assert all(
                isinstance(logic_node.event_type, str)
                for logic_node in incoming_logic_node.incoming_logic
            )
            assert incoming_logic_node.operator in (
                expected_incoming_event_type_logic[node.event_type]
            )
            assert sorted(  # type: ignore[type-var]
                [
                    logic_node.event_type
                    for logic_node in incoming_logic_node.incoming_logic
                ]
            ) == sorted(
                expected_incoming_event_type_logic[node.event_type][
                    incoming_logic_node.operator
                ]
            )
        assert (
            sorted(  # type: ignore[type-var]
                [direction_node.event_type for direction_node in node.outgoing]
            )
            == expected_outgoing_event_type[node.event_type]
        )
        assert (
            sorted(  # type: ignore[type-var]
                [direction_node.event_type for direction_node in node.incoming]
            )
            == expected_incoming_event_type[node.event_type]
        )
