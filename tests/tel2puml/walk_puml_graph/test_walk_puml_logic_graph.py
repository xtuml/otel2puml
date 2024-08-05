"""Tests for the LogicBlockHolder module."""

import networkx as nx

from tel2puml.walk_puml_graph.node import (
    Node,
    merge_markov_without_loops_and_logic_detection_analysis,
)
from tel2puml.walk_puml_graph.walk_puml_logic_graph import (
    create_puml_graph_from_node_class_graph,
    check_is_merge_node_for_logic_block,
    LogicBlockHolder,
    walk_nested_graph
)
from tel2puml.puml_graph.graph import (
    PUMLGraph,
    PUMLOperatorNode,
    PUMLOperatorNodes,
)
from tel2puml.data_pipelines.data_ingestion import (
    update_all_connections_from_clustered_events,
)
from tel2puml.events import events_to_markov_graph
from tel2puml.legacy_loop_detection.events import (
    get_event_reference_from_events,
)
from tel2puml.data_pipelines.data_creation import (
    generate_test_data_event_sequences_from_puml,
)
from tel2puml.check_puml_equiv import (
    check_puml_graph_equivalence_to_expected_graphs,
    gen_puml_graphs_from_files,
    check_puml_equivalence
)
from tel2puml.tel2puml_types import DUMMY_START_EVENT


class TestCreatePumlGraphFromNodeClassGraph:
    """Tests for the create_puml_graph_from_node_class_graph function."""

    @staticmethod
    def load(
        puml_file: str,
        remove_dummy_start_from_test_data: bool = False,
        add_dummy_start: bool = False,
    ) -> PUMLGraph:
        """Load the puml file, create puml graph and return the puml graph.

        :param puml_file: The puml file to load.
        :type puml_file: `str`
        :param remove_dummy_start_from_test_data: Whether to remove the dummy
        start event from the test data, defaults to False
        :type remove_dummy_start_from_test_data: `bool`, optional
        :param add_dummy_start: Whether to add a dummy start event to the
        sequences, defaults to False
        :type add_dummy_start: `bool`, optional
        :return: The puml graph.
        :rtype: :class:`PUMLGraph`"""
        # setup
        test_data_logic = generate_test_data_event_sequences_from_puml(
            puml_file,
            remove_dummy_start_event=remove_dummy_start_from_test_data,
        )
        forward, backward = update_all_connections_from_clustered_events(
            test_data_logic, add_dummy_start=add_dummy_start
        )
        markov_graph = events_to_markov_graph(forward.values())
        event_reference = get_event_reference_from_events(forward.values())
        node_class_graph, _ = (
            merge_markov_without_loops_and_logic_detection_analysis(
                (markov_graph, event_reference),
                backward,
                forward,
            )
        )
        # function call
        puml_graph = create_puml_graph_from_node_class_graph(node_class_graph)
        return puml_graph

    def load_and_check(
        self, puml_file: str, equivalent_pumls: list[str] | None = None
    ) -> None:
        """Load the puml file, create puml graph and check the graph
        equivalence.

        :param puml_file: The puml file to load.
        :type puml_file: `str`
        :param equivalent_pumls: The equivalent pumls to check against,
        defaults to `None`
        :type equivalent_pumls: `list`[`str`] | `None`, optional
        """
        expected_puml_files = set(
            [puml_file, *equivalent_pumls] if equivalent_pumls else [puml_file]
        )
        # setup
        puml_graph = self.load(puml_file)
        # test
        # load in the expected graphs
        expected_puml_graphs = gen_puml_graphs_from_files(expected_puml_files)
        # check graph equivalence
        try:
            assert check_puml_graph_equivalence_to_expected_graphs(
                puml_graph, expected_puml_graphs
            )
        except AssertionError as exc:
            print(puml_file)
            raise AssertionError(f"Graph not equivalent. {puml_file}") from exc

    def test_create_puml_graph_from_node_class_graph(self) -> None:
        """Test the create_puml_graph_from_node_class_graph function."""
        # cases to check in order of complexity
        # * nested and logic case
        # * nested deep xor logic case
        # * bunched logic case
        # * complicated merge case with same event that is not mergeable
        # * branched kill case
        # * merge with kills case
        cases = [
            # test nested logic case
            "puml_files/ANDFork_ANDFork_a.puml",
            # test a complicated nested xor logic case
            "puml_files/complicated_test.puml",
            # test a bunched logic case of different types
            "puml_files/bunched_XOR_AND.puml",
            # test a merge point that is not mergeable at events E or I as they
            # are in a sub logic path that is closed.
            "puml_files/complicated_merge_with_same_event.puml",
            # test a case with kill statements directly after a start node in a
            # branched logic case to confirm that start nodes are added
            "puml_files/branched_kill.puml",
            # test a case where a logic block merges for some paths but the
            # other paths have kill statements.
            "puml_files/merge_with_kills.puml",
        ]
        for puml_file in cases:
            self.load_and_check(puml_file)

    def test_create_puml_graph_from_node_class_graph_bunched_xor(self) -> None:
        """Test create_puml_graph_from_node_class_graph for several bunched XOR
        logic cases."""
        cases = [
            # test simple nested XOR
            "puml_files/bunched_XOR_simple.puml",
            # test medium difficulty nested XOR with AND
            "puml_files/bunched_XOR_medium_AND.puml",
            # test medium difficulty nested XOR
            "puml_files/bunched_XOR_medium.puml",
            # test a complex nested 3 layer XOR logic case
            "puml_files/bunched_XOR_complex.puml",
            # test a complex nested XOR logic case with AND
            "puml_files/bunched_XOR_complex_AND.puml",
            # test a complex nested XOR logic case with side XOR
            "puml_files/bunched_XOR_complex_XOR.puml",
            # test a very complicated nested XOR logic case switch
            "puml_files/bunched_XOR_switch_not_case.puml",
        ]
        for puml_file in cases:
            self.load_and_check(puml_file)

    def test_create_puml_graph_from_node_class_graph_bunched_xor_equiv(
        self,
    ) -> None:
        """Test create_puml_graph_from_node_class_graph for bunched XOR
        logic cases which are written equivalently (e.g. using switches)."""
        # test a very complicated (equivalent to above) nested XOR logic
        self.load_and_check(
            "puml_files/bunched_XOR_switch_case.puml",
            equivalent_pumls=["puml_files/bunched_XOR_switch_not_case.puml"],
        )

    def test_create_puml_graph_from_node_class_graph_with_dummy_start(
        self,
    ) -> None:
        """Tests the create_puml_graph_from_node_class_graph function with a
        dummy start event."""
        puml_graph = self.load(
            "puml_files/two_start_events.puml",
            remove_dummy_start_from_test_data=True,
            add_dummy_start=True,
        )
        dummy_start_events = [
            node
            for node in puml_graph.nodes
            if node.node_type == DUMMY_START_EVENT
        ]
        assert len(dummy_start_events) == 1
        puml_graph.remove_dummy_start_event_nodes()
        assert dummy_start_events[0] not in puml_graph.nodes
        head_node = list(nx.topological_sort(puml_graph))[0]
        assert isinstance(head_node, PUMLOperatorNode)
        assert head_node.operator_type == PUMLOperatorNodes.START_AND


def test_check_is_merge_node_for_logic_block() -> None:
    """Test the check_is_merge_node_for_current_path function."""
    # setup
    # get the node class graph for the given puml
    test_data_logic = generate_test_data_event_sequences_from_puml(
        "puml_files/complicated_merge_with_same_event.puml"
    )
    forward, backward = update_all_connections_from_clustered_events(
        test_data_logic
    )
    markov_graph = events_to_markov_graph(forward.values())
    event_reference = get_event_reference_from_events(forward.values())
    node_class_graph, _ = (
        merge_markov_without_loops_and_logic_detection_analysis(
            (markov_graph, event_reference),
            backward,
            forward,
        )
    )
    # setup the test logic holder
    A = [node for node in node_class_graph.nodes if node.event_type == "A"][0]
    logic_holder = LogicBlockHolder(
        PUMLOperatorNode(PUMLOperatorNodes.START_AND, 1),
        PUMLOperatorNode(PUMLOperatorNodes.END_AND, 1),
        logic_node=A.outgoing_logic[0],
    )
    logic_holder.set_path_node()
    B = [node for node in node_class_graph.nodes if node.event_type == "B"][0]
    # make sure current path is B
    while logic_holder.current_path != B:
        logic_holder.rotate_path(
            logic_holder.current_path, logic_holder.start_node
        )

    # tests
    # check when the selected node has a different path to the logic node and
    # can therefore be a merge point
    H = [node for node in node_class_graph.nodes if node.event_type == "H"][0]
    assert check_is_merge_node_for_logic_block(
        H,
        logic_holder,
        node_class_graph,
    )
    # check when the selected node has no different path to the logic node
    # and therefore can't be a merge point
    assert not check_is_merge_node_for_logic_block(
        A,
        logic_holder,
        node_class_graph,
    )
    # check when the selected node has is a different path to the logic node
    # than the current path of the logic node but the penultimate node in that
    # path has outgoing logic and therefore the selected node can't be a merge
    # point for that path
    E = [node for node in node_class_graph.nodes if node.event_type == "E"][0]
    assert not check_is_merge_node_for_logic_block(
        E,
        logic_holder,
        node_class_graph,
    )
    # check the case when the selected node has been traversed on one of the
    # paths and cannot be a merge point when the path node is the same as the
    # selected node
    C = [node for node in node_class_graph.nodes if node.event_type == "C"][0]
    I_ = [node for node in node_class_graph.nodes if node.event_type == "I"][0]
    index = logic_holder.paths.index(C)
    logic_holder.paths[index] = I_
    assert not check_is_merge_node_for_logic_block(
        I_,
        logic_holder,
        node_class_graph,
    )
    # check above case when selected node is different to the path node
    F = [node for node in node_class_graph.nodes if node.event_type == "F"][0]
    logic_holder.paths[index] = F
    assert not check_is_merge_node_for_logic_block(
        I_,
        logic_holder,
        node_class_graph,
    )


def test_walk_nested_graph(
    graph: "nx.DiGraph[Node]",
    expected_graph_puml_graph: PUMLGraph,
) -> None:
    """Test the walk_nested_graph function."""
    puml_graph = walk_nested_graph(graph)
    assert check_puml_equivalence(
        puml_graph.write_puml_string(),
        expected_graph_puml_graph.write_puml_string(),
    )
