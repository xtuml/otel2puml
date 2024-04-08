"""Tests for the node module."""

from copy import deepcopy, copy

from pm4py import ProcessTree
import networkx as nx
import pytest

from tel2puml.node_map_to_puml.node import (
    Node,
    load_logic_tree_into_nodes,
    load_all_logic_trees_into_nodes,
    create_event_node_ref,
    create_networkx_graph_of_nodes_from_markov_graph,
    merge_markov_without_loops_and_logic_detection_analysis,
    create_puml_graph_from_node_class_graph,
)
from tel2puml.pipelines.logic_detection_pipeline import (
    Event,
    update_all_connections_from_clustered_events,
)
from tel2puml.pipelines.data_creation import (
    generate_test_data_event_sequences_from_puml,
)
from tel2puml.jAlergiaPipeline import audit_event_sequences_to_network_x
from tel2puml.check_puml_equiv import (
    get_network_x_graph_from_puml_string,
    check_networkx_graph_equivalence,
)
from tel2puml.tel2puml_types import PUMLEvent, PUMLOperator


class TestNode:
    """Tests for the node class."""

    @staticmethod
    def test_event_node_map_incoming():
        """Test the event_node_map property for incoming nodes."""
        node = Node(data="test_data", event_type="test_event_type")
        assert len(node.event_node_map_incoming) == 0
        incoming_nodes = [
            Node(data=f"test_data_{i}", event_type=f"test_event_type_{i}")
            for i in range(3)
        ]
        node.update_node_list_with_nodes(incoming_nodes, "incoming")
        assert len(node.event_node_map_incoming) == 3
        for i in range(3):
            assert (
                node.event_node_map_incoming[f"test_event_type_{i}"]
                == incoming_nodes[i]
            )

    @staticmethod
    def test_event_node_map_outgoing() -> None:
        """Test the event_node_map property for outgoing nodes."""
        node = Node(data="test_data", event_type="test_event_type")
        assert len(node.event_node_map_outgoing) == 0
        outgoing_nodes = [
            Node(data=f"test_data_{i}", event_type=f"test_event_type_{i}")
            for i in range(3)
        ]
        node.update_node_list_with_nodes(outgoing_nodes, "outgoing")
        assert len(node.event_node_map_outgoing) == 3
        for i in range(3):
            assert (
                node.event_node_map_outgoing[f"test_event_type_{i}"]
                == outgoing_nodes[i]
            )

    @staticmethod
    def test_load_logic_into_list_no_logic(
        node: Node,
        process_tree_no_logic: ProcessTree,
    ) -> None:
        """Test the load_logic_into_list method with no logic.

        :param node: The node to test.
        :type node: :class:`Node`
        :param process_tree_no_logic: The process tree with no logic.
        :type process_tree_no_logic: :class:`ProcessTree`
        """
        for direction, direction_node_list, direction_logic_list in zip(
            ["incoming", "outgoing"],
            [node.incoming, node.outgoing],
            [node.incoming_logic, node.outgoing_logic],
        ):
            assert len(direction_logic_list) == 0
            assert len(direction_node_list) == 3
            node.load_logic_into_list(process_tree_no_logic, direction)
            assert len(direction_logic_list) == 0
            assert len(direction_node_list) == 3

    @staticmethod
    def test_load_logic_into_list_and_logic(
        node: Node,
        process_tree_with_and_logic_gate: ProcessTree,
    ) -> None:
        """Test the load_logic_into_list method and logic gate.

        :param node: The node to test.
        :type node: :class:`Node`
        :param process_tree_with_and_logic_gate: The process tree with an
        AND logic gate.
        :type process_tree_with_and_logic_gate: :class:`ProcessTree`
        """
        for direction, direction_node_list, direction_logic_list in zip(
            ["incoming", "outgoing"],
            [node.incoming, node.outgoing],
            [node.incoming_logic, node.outgoing_logic],
        ):
            assert len(direction_logic_list) == 0
            node.load_logic_into_list(
                process_tree_with_and_logic_gate, direction
            )
            assert len(direction_logic_list) == 1
            operator_node = direction_logic_list[0]
            assert operator_node.operator == "AND"
            operator_node_direction_logic_list = getattr(
                operator_node, f"{direction}_logic"
            )
            assert len(operator_node_direction_logic_list) == 3
            for incoming_node in direction_node_list:
                assert incoming_node in operator_node_direction_logic_list

    @staticmethod
    def test_load_logic_into_list_or_logic(
        node: Node,
        process_tree_with_or_logic_gate: ProcessTree,
    ) -> None:
        """Test the load_logic_into_list method or logic gate.

        :param node: The node to test.
        :type node: :class:`Node`
        :param process_tree_with_or_logic_gate: The process tree with an
        OR logic gate.
        :type process_tree_with_or_logic_gate: :class:`ProcessTree`
        """
        for direction, direction_node_list, direction_logic_list in zip(
            ["incoming", "outgoing"],
            [node.incoming, node.outgoing],
            [node.incoming_logic, node.outgoing_logic],
        ):
            assert len(direction_logic_list) == 0
            node.load_logic_into_list(
                process_tree_with_or_logic_gate, direction
            )
            assert len(direction_logic_list) == 1
            operator_node = direction_logic_list[0]
            assert operator_node.operator == "OR"
            operator_node_direction_logic_list = getattr(
                operator_node, f"{direction}_logic"
            )
            assert len(operator_node_direction_logic_list) == 3
            for incoming_node in direction_node_list:
                assert incoming_node in operator_node_direction_logic_list

    @staticmethod
    def test_load_logic_into_list_xor_logic(
        node: Node,
        process_tree_with_xor_logic_gate: ProcessTree,
    ) -> None:
        """Test the load_logic_into_list method xor logic gate.

        :param node: The node to test.
        :type node: :class:`Node`
        :param process_tree_with_xor_logic_gate: The process tree with an
            XOR logic gate.
        :type process_tree_with_xor_logic_gate: :class:`ProcessTree`
        """
        for direction, direction_node_list, direction_logic_list in zip(
            ["incoming", "outgoing"],
            [node.incoming, node.outgoing],
            [node.incoming_logic, node.outgoing_logic],
        ):
            assert len(direction_logic_list) == 0
            node.load_logic_into_list(
                process_tree_with_xor_logic_gate, direction
            )
            assert len(direction_logic_list) == 1
            operator_node = direction_logic_list[0]
            assert operator_node.operator == "XOR"
            operator_node_direction_logic_list = getattr(
                operator_node, f"{direction}_logic"
            )
            assert len(operator_node_direction_logic_list) == 3
            for incoming_node in direction_node_list:
                assert incoming_node in operator_node_direction_logic_list

    @staticmethod
    def test_load_logic_into_list_and_xor_logic(
        node: Node,
        process_tree_with_and_xor_logic_gate: ProcessTree,
    ) -> None:
        """Test the load_logic_into_list method and gate with xor gate nested
        underneath.

        :param node: The node to test.
        :type node: :class:`Node`
        :param process_tree_with_and_xor_logic_gate: The process tree with an
            AND logic gate and an XOR logic gate nested underneath.
        :type process_tree_with_and_xor_logic_gate: :class:`ProcessTree`
        """
        for direction, direction_node_list, direction_logic_list in zip(
            ["incoming", "outgoing"],
            [node.incoming, node.outgoing],
            [node.incoming_logic, node.outgoing_logic],
        ):
            assert len(direction_logic_list) == 0
            node.load_logic_into_list(
                process_tree_with_and_xor_logic_gate, direction
            )
            assert len(direction_logic_list) == 1
            and_node = direction_logic_list[0]
            assert and_node.operator == "AND"
            and_node_direction_logic_list = getattr(
                and_node, f"{direction}_logic"
            )
            assert len(and_node_direction_logic_list) == 2
            for child_node in and_node_direction_logic_list:
                if child_node.operator == "XOR":
                    xor_node = child_node
                else:
                    assert child_node == direction_node_list[0]
            xor_node_direction_logic_list = getattr(
                xor_node, f"{direction}_logic"
            )
            assert len(xor_node_direction_logic_list) == 2
            for incoming_node in direction_node_list[1:]:
                assert incoming_node in xor_node_direction_logic_list

    @staticmethod
    def test_load_logic_into_list_child_stub_node(
        node_with_child_to_stub: Node,
        process_tree_with_and_logic_gate: ProcessTree,
    ) -> None:
        """Test the load_logic_into_list method that should create a child stub
        node.

        :param node_with_child_to_stub: The node with a child missing.
        :type node_with_child_to_stub: :class:`Node`
        :param process_tree_no_logic: The process tree with no logic.
        :type process_tree_no_logic: :class:`ProcessTree`
        """
        for direction, direction_node_list, direction_logic_list in zip(
            ["incoming", "outgoing"],
            [
                node_with_child_to_stub.incoming,
                node_with_child_to_stub.outgoing,
            ],
            [
                node_with_child_to_stub.incoming_logic,
                node_with_child_to_stub.outgoing_logic,
            ],
        ):
            assert len(direction_node_list) == 2
            previous_direction_node_list = copy(direction_node_list)
            node_with_child_to_stub.load_logic_into_list(
                process_tree_with_and_logic_gate, direction
            )
            assert len(direction_node_list) == 3
            assert len(direction_logic_list) == 1
            operator_node = direction_logic_list[0]
            assert operator_node.operator == "AND"
            operator_node_direction_logic_list = getattr(
                operator_node, f"{direction}_logic"
            )
            assert len(operator_node_direction_logic_list) == 3
            copied_direction_node_list = copy(direction_node_list)
            for incoming_node in previous_direction_node_list:
                assert incoming_node in operator_node_direction_logic_list
                copied_direction_node_list.remove(incoming_node)
            assert len(copied_direction_node_list) == 1
            assert copied_direction_node_list[0].is_stub
            assert len(getattr(copied_direction_node_list[0], direction)) == 0
            assert (
                len(
                    getattr(
                        copied_direction_node_list[0], f"{direction}_logic"
                    )
                )
                == 0
            )

    @staticmethod
    def test_load_logic_into_list_parent_stub_node(
        process_tree_with_and_logic_gate: ProcessTree,
    ) -> None:
        """Test the load_logic_into_list method for a stub
        node. This should not update any of the lists on the stub node.
        """
        node = Node(uid="test_stub", event_type="test_stub", is_stub=True)
        for direction in ["incoming", "outgoing"]:
            assert len(getattr(node, direction)) == 0
            assert len(getattr(node, f"{direction}_logic")) == 0
            node.load_logic_into_list(
                process_tree_with_and_logic_gate, direction
            )
            assert len(getattr(node, direction)) == 0
            assert len(getattr(node, f"{direction}_logic")) == 0

    @staticmethod
    def test_traverse_logic():
        """Test the traverse_logic method."""
        # setup
        node = Node(uid="test_event", event_type="test_event")
        and_node = Node(uid="test_and", operator="AND")
        xor_node = Node(uid="test_xor", operator="XOR")
        or_node = Node(uid="test_or", operator="OR")
        extra_and_child = Node(
            uid="test_extra_and_child", event_type="test_extra_and_child"
        )
        and_node.outgoing_logic.extend([xor_node, or_node, extra_and_child])
        xor_nodes = [
            Node(uid=f"test_xor_{i}", event_type=f"XOR_{i}") for i in range(2)
        ]
        or_nodes = [
            Node(uid=f"test_or_{i}", event_type=f"OR_{i}") for i in range(2)
        ]
        xor_node.outgoing_logic.extend(xor_nodes)
        or_node.outgoing_logic.extend(or_nodes)
        node.update_node_list_with_nodes(
            [*xor_nodes, *or_nodes, extra_and_child], direction="outgoing"
        )
        node.outgoing_logic.append(and_node)
        # function call
        leaf_nodes = node.traverse_logic("outgoing")
        # test
        expected_leaf_nodes = [extra_and_child, *xor_nodes, *or_nodes]
        assert len(leaf_nodes) == 5
        for leaf_node in leaf_nodes:
            assert leaf_node in expected_leaf_nodes
            expected_leaf_nodes.remove(leaf_node)
        assert len(expected_leaf_nodes) == 0

    @staticmethod
    def test_get_operator_type():
        """Test the get_operator_type method."""
        for operator in PUMLOperator:
            node = Node(uid="test_operator", operator=operator.name)
            assert node.get_operator_type() == operator


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

    for direction in ["incoming", "outgoing"]:
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
    for direction in ["incoming", "outgoing"]:
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
    graph = nx.DiGraph()
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
    markov_graph, event_node_reference = audit_event_sequences_to_network_x(
        test_data
    )
    # function call
    node_class_graph, _ = create_networkx_graph_of_nodes_from_markov_graph(
        markov_graph, event_node_reference["event_reference"]
    )
    # test
    # check the graphs are mirrors of one another
    assert len(node_class_graph.nodes) == len(markov_graph.nodes)
    for node in node_class_graph.nodes:
        assert node.uid in markov_graph.nodes
        assert (
            node.event_type
            == event_node_reference["event_reference"][node.uid]
        )
    for edge in node_class_graph.edges:
        assert (edge[0].uid, edge[1].uid) in markov_graph.edges


def test_merge_markov_without_loops_and_logic_detection_analysis() -> None:
    """Test the merge_markov_without_loops_and_logic_detection_analysis
    function.

    The function should merge the markov graph with the logic detection
    analysis and return a graph with the expected connections and logic.
    """
    # setup
    test_data_markov = generate_test_data_event_sequences_from_puml(
        "puml_files/simple_test.puml"
    )
    markov_graph, node_event_reference = audit_event_sequences_to_network_x(
        test_data_markov
    )
    test_data_logic = generate_test_data_event_sequences_from_puml(
        "puml_files/simple_test.puml"
    )
    forward, backward = update_all_connections_from_clustered_events(
        test_data_logic
    )
    # function call
    node_class_graph = merge_markov_without_loops_and_logic_detection_analysis(
        (markov_graph, node_event_reference["event_reference"]),
        backward,
        forward,
    )
    # test
    expected_outgoing_event_type_logic = {
        "A": {"XOR": ["B", "D"]},
        "B": {},
        "C": {},
        "D": {},
    }
    expected_incoming_event_type_logic = {"A": {}, "B": {}, "C": {}, "D": {}}
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
        for outgoing_logic_node in node.outgoing_logic:
            assert outgoing_logic_node.operator in (
                expected_outgoing_event_type_logic[node.event_type]
            )
            assert sorted(
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
            assert incoming_logic_node.operator in (
                expected_incoming_event_type_logic[node.event_type]
            )
            assert sorted(
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
            sorted(
                [direction_node.event_type for direction_node in node.outgoing]
            )
            == expected_outgoing_event_type[node.event_type]
        )
        assert (
            sorted(
                [direction_node.event_type for direction_node in node.incoming]
            )
            == expected_incoming_event_type[node.event_type]
        )


class TestCreatePumlGraphFromNodeClassGraph:
    """Tests for the create_puml_graph_from_node_class_graph function."""

    @staticmethod
    def load_and_check(puml_file: str) -> None:
        """Load the puml file, create puml graph and check the graph
        equivalence.

        :param puml_file: The puml file to load.
        :type puml_file: `str`"""
        # setup
        test_data_markov = generate_test_data_event_sequences_from_puml(
            puml_file
        )
        markov_graph, node_event_reference = (
            audit_event_sequences_to_network_x(test_data_markov)
        )
        test_data_logic = generate_test_data_event_sequences_from_puml(
            puml_file
        )
        forward, backward = update_all_connections_from_clustered_events(
            test_data_logic
        )
        node_class_graph = (
            merge_markov_without_loops_and_logic_detection_analysis(
                (markov_graph, node_event_reference["event_reference"]),
                backward,
                forward,
            )
        )
        # function call
        puml_graph = create_puml_graph_from_node_class_graph(node_class_graph)
        # test
        # load in the expected graph
        with open(puml_file, "r", encoding="utf-8") as file:
            expected_puml_string = file.read()
        expected_puml_graph = next(
            get_network_x_graph_from_puml_string(expected_puml_string)
        )
        # check graph equivalence
        assert check_networkx_graph_equivalence(
            puml_graph, expected_puml_graph
        )

    def test_create_puml_graph_from_node_class_graph(self) -> None:
        """Test the create_puml_graph_from_node_class_graph function."""
        # cases to check in order of complexity
        # * nested and logic case
        # * nested deep xor logic case
        # * bunched logic case
        cases = [
            "puml_files/ANDFork_ANDFork_a.puml",
            "puml_files/complicated_test.puml",
            "puml_files/bunched_XOR_AND.puml",
        ]
        for puml_file in cases:
            self.load_and_check(puml_file)

    @pytest.mark.xfail(
        reason=(
            "Functionality to handle bunched logic of same type not"
            "implemented yet"
        ),
        strict=True,
    )
    def test_create_puml_graph_from_node_class_graph_bunched_xor(self) -> None:
        """Tests a bunched XOR logic case with and event ending one of the
        branches"""
        self.load_and_check(
            "puml_files/bunched_XOR_with_event_ending_logic.puml"
        )


class Test_load_logic_into_logic_list:
    """
    Test class for the _load_logic_into_logic_list method of a node.
    """

    def test_load_logic_into_logic_list_incoming(
        self, event_node_map, logic_tree_XOR
    ):
        """
        Test loading logic into the incoming logic list of a node.
        """

        # Set a node instance for testing
        node_to_test = event_node_map["B"]
        node_to_test._load_logic_into_logic_list(
            logic_tree=logic_tree_XOR,
            event_node_map=event_node_map,
            direction="incoming",
            root_node=node_to_test,
        )

        # Check if the logic is loaded correctly
        assert len(node_to_test.incoming_logic) == 1
        assert node_to_test.incoming_logic[0].data == "XOR"

    def test_load_logic_into_logic_list_outgoing(
        self, event_node_map, logic_tree_XOR
    ):
        """
        Test loading logic into the outgoing logic list of a node.
        """

        # Select a node instance for testing
        node_to_test = event_node_map["A"]
        node_to_test._load_logic_into_logic_list(
            logic_tree_XOR, event_node_map, "outgoing", node_to_test
        )

        # Check if the logic is loaded correctly
        assert len(node_to_test.outgoing_logic) == 1
        assert node_to_test.outgoing_logic[0].data == "XOR"

    def test_load_logic_into_logic_list_branch(
        self, event_node_map, logic_tree_BRANCH
    ):
        """
        Test loading logic into the incoming logic list of a node with branch
            event type.
        """

        # Set a node instance for testing
        node_to_test = event_node_map["B"]
        node_to_test._load_logic_into_logic_list(
            logic_tree_BRANCH, event_node_map, "incoming", node_to_test
        )

        assert len(node_to_test.event_types) > 0
        assert PUMLEvent.BRANCH in node_to_test.event_types
