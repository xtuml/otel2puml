"""Test the logic detection pipeline.
"""
from datetime import datetime, timedelta

from tel2puml.pipelines.logic_detection_pipeline import (
    Event, update_all_connections_from_data
)
from tel2puml.pipelines.data_creation import generate_test_data


class TestEvent:
    @staticmethod
    def test_add_new_edge_to_conditional_count_matrix():
        """Tests for method add_new_edge_to_conditional_count_matrix"""
        event = Event("A")
        event.add_new_edge_to_conditional_count_matrix()
        assert event.conditional_count_matrix.tolist() == [[0]]
        event.add_new_edge_to_conditional_count_matrix()
        assert event.conditional_count_matrix.tolist() == [[0, 0], [0, 0]]
        event.add_new_edge_to_conditional_count_matrix()
        assert event.conditional_count_matrix.tolist() == [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]
        event.conditional_count_matrix[0, 0] = 1
        event.conditional_count_matrix[2, 2] = 1
        event.add_new_edge_to_conditional_count_matrix()
        assert event.conditional_count_matrix.tolist() == [
            [1, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 0],
        ]

    @staticmethod
    def test_add_new_edge_to_edge_counts_per_data_point():
        """Tests for method add_new_edge_to_edge_counts_per_data_point"""
        event = Event("A")
        for i, edge_tuple in enumerate(
            [("A", "B"), ("B", "C"), ("C", "D")]
        ):
            event.add_new_edge_to_edge_counts_per_data_point(edge_tuple)
            assert edge_tuple in event.edge_counts_per_data_point
            assert (
                event.edge_counts_per_data_point[edge_tuple]
            )["index"] == i

    @staticmethod
    def test_update_conditional_count_matrix():
        """Tests for method update_conditional_count_matrix"""
        event = Event("A")
        data_point_edges = {("A", "B"), ("B", "C"), ("C", "D")}
        for _ in range(len(data_point_edges)):
            event.add_new_edge_to_conditional_count_matrix()
        for edge_tuple in data_point_edges:
            event.add_new_edge_to_edge_counts_per_data_point(edge_tuple)
        event.update_conditional_count_matrix(data_point_edges)
        assert event.conditional_count_matrix.tolist() == [
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
        ]
        data_point_edges = {("A", "B"), ("B", "C")}
        event.update_conditional_count_matrix(data_point_edges)
        to_check_list = [
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
        ]
        index_ab = event.edge_counts_per_data_point[("A", "B")]["index"]
        index_bc = event.edge_counts_per_data_point[("B", "C")]["index"]
        for i in [index_ab, index_bc]:
            for j in [index_ab, index_bc]:
                to_check_list[i][j] += 1
        assert event.conditional_count_matrix.tolist() == to_check_list

    @staticmethod
    def test_update_with_edge_tuple_and_data_point_edges():
        """Tests for method update_with_edge_tuple_and_data_point_edges"""
        event = Event("A")
        edge_tuple = ("A", "B")
        data_point_edges = set()
        event.update_with_edge_tuple_and_data_point_edges(
            edge_tuple,
            data_point_edges,
        )
        assert edge_tuple in event.edge_counts_per_data_point
        assert event.edge_counts_per_data_point[edge_tuple]["index"] == 0
        assert event.conditional_count_matrix.tolist() == [[0]]
        assert data_point_edges == {edge_tuple}

    @staticmethod
    def test_update_with_data_point():
        """Tests for method update_with_data_point"""
        event = Event("A")
        assert event._update_since_conditional_probability_matrix is False
        edge_tuples = [("A", "B"), ("B", "C"), ("C", "D")]
        event.update_with_data_point(edge_tuples)
        assert event.conditional_count_matrix.tolist() == [
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
        ]
        for i, edge_tuple in enumerate(edge_tuples):
            assert edge_tuple in event.edge_counts_per_data_point
            assert event.edge_counts_per_data_point[edge_tuple]["index"] == i
        assert event._update_since_conditional_probability_matrix is True

    @staticmethod
    def test_conditional_probability_matrix():
        """Tests for property conditional_probability_matrix"""
        event = Event("A")
        assert event.conditional_probability_matrix is None
        edge_tuples = [("A", "B"), ("B", "C"), ("C", "D")]
        event.update_with_data_point(edge_tuples)
        assert event.conditional_probability_matrix.tolist() == [
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
        ]
        event.update_with_data_point(edge_tuples[:2])
        assert event.conditional_probability_matrix.tolist() == [
            [1, 1, 1],
            [1, 1, 1],
            [0.5, 0.5, 1],
        ]
        event.update_with_data_point(edge_tuples[:1])
        assert event.conditional_probability_matrix.tolist() == [
            [1, 1, 1],
            [2/3, 1, 1],
            [1/3, 0.5, 1],
        ]

    @staticmethod
    def test_update_event_sets():
        """Tests for method update_edge_sets"""
        event = Event("A")
        events = ["B", "C", "D"]
        # check that the event sets are updated
        event.update_event_sets(events)
        assert event.event_sets == {frozenset(events)}
        # check that the event sets are not updated
        event.update_event_sets(events)
        assert event.event_sets == {frozenset(events)}
        # check that the event sets are not updated if events are reversed
        event.update_event_sets(["D", "C", "B"])
        assert event.event_sets == {frozenset(events)}
        # check that the event sets are updated
        event.update_event_sets(["B", "C"])
        assert event.event_sets == {frozenset(events), frozenset(["B", "C"])}

    @staticmethod
    def test_create_data_from_event_sequence():
        event_sequence = ["A", "B", "C", "D"]
        case_id = "case_1"
        start_time = datetime(2021, 1, 1, 0, 0, 0)
        data = Event.create_data_from_event_sequence(
            event_sequence,
            case_id,
            start_time
        )
        for i, event_data in enumerate(data):
            assert event_data["case_id"] == case_id
            assert event_data["activity"] == event_sequence[i]
            assert event_data["timestamp"] == start_time + timedelta(seconds=i)

    @staticmethod
    def test_create_augmented_data_from_event_set():
        event = Event("A")
        event_set = frozenset(["B", "C"])
        data = list(event.created_augemented_data_from_event_set(
            event_set,
        ))
        assert len(data) == 6
        expected_sequences = [
            "ABC",
            "ACB",
        ]
        expected_sequences.remove("".join(
            [event_data["activity"] for event_data in data[:3]]
        ))
        expected_sequences.remove("".join(
            [event_data["activity"] for event_data in data[3:]]
        ))
        assert len(expected_sequences) == 0
        first_seq_case_ids = set(
            [event_data["case_id"] for event_data in data[:3]]
        )
        second_seq_case_ids = set(
            [event_data["case_id"] for event_data in data[3:]]
        )
        assert len(first_seq_case_ids) == 1
        assert len(second_seq_case_ids) == 1
        assert first_seq_case_ids != second_seq_case_ids

    @staticmethod
    def test_create_augmented_data_from_event_sets():
        event = Event("A")
        event.event_sets = {
            frozenset(["B", "C"]),
            frozenset(["D", "E"]),
        }
        data = list(event.create_augmented_data_from_event_sets())
        assert len(data) == 12
        expected_sequences = [
            "ABC",
            "ACB",
            "ADE",
            "AED",
        ]
        for i in range(4):
            expected_sequences.remove("".join(
                [event_data["activity"] for event_data in data[i*3:i*3+3]]
            ))
        assert len(expected_sequences) == 0

    @staticmethod
    def test_calculate_process_tree_from_event_sets_xor_ands():
        event = Event("A")
        event.event_sets = {
            frozenset(["B", "C"]),
            frozenset(["D", "E"]),
        }
        process_tree = event.calculate_process_tree_from_event_sets()
        first_children = process_tree.children
        assert len(first_children) == 2
        start_event = first_children[0]
        next_operator = first_children[1]
        assert start_event.label == "A"
        assert next_operator.operator.name == "XOR"
        second_children = next_operator.children
        assert len(second_children) == 2
        first_operator = second_children[0]
        second_operator = second_children[1]
        assert first_operator.operator.name == "PARALLEL"
        assert second_operator.operator.name == "PARALLEL"
        first_operator_children = first_operator.children
        assert len(first_operator_children) == 2
        second_operator_children = second_operator.children
        assert len(second_operator_children) == 2
        children_labels = []
        for operator_children in [
            first_operator_children, second_operator_children
        ]:
            operator_child_labels = []
            for child in operator_children:
                assert len(child.children) == 0
                operator_child_labels.append(child.label)
            children_labels.append(frozenset(sorted(operator_child_labels)))
        for to_remove in [
            frozenset(sorted(["B", "C"])),
            frozenset(sorted(["D", "E"]))
        ]:
            children_labels.remove(to_remove)
        assert len(children_labels) == 0

    @staticmethod
    def test_calculate_process_tree_from_event_sets_or():
        event = Event("A")
        event.event_sets = {
            frozenset(["B", "C"]),
            frozenset(["B"]),
            frozenset(["C"]),
        }
        process_tree = event.calculate_process_tree_from_event_sets()
        first_children = process_tree.children
        assert len(first_children) == 2
        start_event = first_children[0]
        next_operator = first_children[1]
        assert start_event.label == "A"
        assert next_operator.operator.name == "PARALLEL"
        second_children = next_operator.children
        assert len(second_children) == 2
        first_operator = second_children[0]
        second_operator = second_children[1]
        assert first_operator.operator.name == "XOR"
        assert second_operator.operator.name == "XOR"
        first_operator_children = first_operator.children
        assert len(first_operator_children) == 2
        second_operator_children = second_operator.children
        assert len(second_operator_children) == 2
        children_labels = []
        for operator_children in [
            first_operator_children, second_operator_children
        ]:
            operator_child_labels = []
            for child in operator_children:
                assert len(child.children) == 0
                operator_child_labels.append(str(child))
            children_labels.append(frozenset(sorted(operator_child_labels)))
        for to_remove in [
            frozenset(sorted(["B", "tau"])),
            frozenset(sorted(["C", "tau"])),
        ]:
            children_labels.remove(to_remove)
        assert len(children_labels) == 0

    @staticmethod
    def test_infer_or_gate_from_node():
        event = Event("A")
        event.event_sets = {
            frozenset(["B", "C"]),
            frozenset(["B"]),
            frozenset(["C"]),
        }
        process_tree = event.calculate_process_tree_from_event_sets()
        and_gate = process_tree.children[1]
        assert and_gate.operator.name == "PARALLEL"
        event.infer_or_gate_from_node(and_gate)
        assert and_gate.operator.name == "OR"
        and_gate_children = and_gate.children
        assert len(and_gate_children) == 2
        first_child = and_gate_children[0]
        assert len(first_child.children) == 0
        second_child = and_gate_children[1]
        assert second_child.operator.name == "PARALLEL"

    @staticmethod
    def test_get_extended_or_gates_from_process_tree():
        event = Event("A")
        event.event_sets = {
            frozenset(["B", "C"]),
            frozenset(["B"]),
            frozenset(["C"]),
        }
        process_tree = event.calculate_process_tree_from_event_sets()
        logic_gates_tree = process_tree.children[1]
        event.get_extended_or_gates_from_process_tree(logic_gates_tree)
        assert logic_gates_tree.operator.name == "OR"
        assert len(logic_gates_tree.children) == 2
        assert logic_gates_tree.children[1].operator.name == "OR"
        assert logic_gates_tree.children[0].label is not None
        assert len(logic_gates_tree.children[1].children) == 1
        assert logic_gates_tree.children[1].children[0].label is not None

    @staticmethod
    def test_filter_defunct_or_gates():
        event = Event("A")
        event.event_sets = {
            frozenset(["B", "C"]),
            frozenset(["B"]),
            frozenset(["C"]),
        }
        process_tree = event.calculate_process_tree_from_event_sets()
        logic_gates_tree = process_tree.children[1]
        event.get_extended_or_gates_from_process_tree(logic_gates_tree)
        event.filter_defunct_or_gates(logic_gates_tree)
        assert logic_gates_tree.operator.name == "OR"
        assert len(logic_gates_tree.children) == 2
        labels = ["B", "C"]
        for child in logic_gates_tree.children:
            assert child.label in labels
            labels.remove(child.label)
        assert len(labels) == 0

    @staticmethod
    def test_process_or_gates():
        event = Event("A")
        event.event_sets = {
            frozenset(["B", "C", "D"]),
            frozenset(["B", "C"]),
            frozenset(["C", "D"]),
            frozenset(["B", "D"]),
            frozenset(["B"]),
            frozenset(["C"]),
            frozenset(["D"]),
        }
        process_tree = event.calculate_process_tree_from_event_sets()
        logic_gates_tree = process_tree.children[1]
        event.process_or_gates(logic_gates_tree)
        assert logic_gates_tree.operator.name == "OR"
        assert len(logic_gates_tree.children) == 3
        labels = ["B", "C", "D"]
        for child in logic_gates_tree.children:
            assert child.label in labels
            labels.remove(child.label)
        assert len(labels) == 0

    @staticmethod
    def test_reduce_process_tree_to_preffered_logic_gates():
        event = Event("A")
        event.event_sets = {
            frozenset(["B", "C", "D"]),
            frozenset(["B", "C"]),
            frozenset(["C", "D"]),
            frozenset(["B", "D"]),
            frozenset(["B"]),
            frozenset(["C"]),
            frozenset(["D"]),
        }
        process_tree = event.calculate_process_tree_from_event_sets()
        logic_gates_tree = event.reduce_process_tree_to_preferred_logic_gates(
            process_tree
        )
        assert logic_gates_tree.operator.name == "OR"
        assert len(logic_gates_tree.children) == 3
        labels = ["B", "C", "D"]
        for child in logic_gates_tree.children:
            assert child.label in labels
            labels.remove(child.label)
        assert len(labels) == 0

    @staticmethod
    def test_calculate_logic_gates():
        event = Event("A")
        event.event_sets = {
            frozenset(["B", "C", "D"]),
            frozenset(["B", "C"]),
            frozenset(["C", "D"]),
            frozenset(["B", "D"]),
            frozenset(["B"]),
            frozenset(["C"]),
            frozenset(["D"]),
        }
        logic_gates_tree = event.calculate_logic_gates()
        assert logic_gates_tree.operator.name == "OR"
        assert len(logic_gates_tree.children) == 3
        labels = ["B", "C", "D"]
        for child in logic_gates_tree.children:
            assert child.label in labels
            labels.remove(child.label)
        assert len(labels) == 0


def test_update_all_connections_from_data():
    """Test for method detect_logic"""
    puml_file = "puml_files/sequence_xor_fork.puml"
    data = generate_test_data(puml_file)
    events_forward_logic, events_backward_logic = (
        update_all_connections_from_data(data)
    )
    assert len(events_forward_logic) == 6
    assert len(events_backward_logic) == 6
    assert all(
        event_type in events_forward_logic
        for event_type in ["A", "B", "C", "D", "E", "F"]
    )
    assert all(
        event_type in events_backward_logic
        for event_type in ["A", "B", "C", "D", "E", "F"]
    )
    # check A
    assert events_forward_logic["A"].event_sets == {
        frozenset(["B"]),
    }
    assert events_backward_logic["A"].event_sets == set()
    # check B
    assert events_forward_logic["B"].event_sets == {
        frozenset(["C"]),
        frozenset(["D"]),
        frozenset(["E"]),
    }
    assert events_backward_logic["B"].event_sets == {
        frozenset(["A"]),
    }
    # check C, D, E
    for event_type in ["C", "D", "E"]:
        assert events_forward_logic[event_type].event_sets == {
            frozenset(["F"]),
        }
        assert events_backward_logic[event_type].event_sets == {
            frozenset(["B"]),
        }
    # check F
    assert events_forward_logic["F"].event_sets == set()
    assert events_backward_logic["F"].event_sets == {
        frozenset(["C"]),
        frozenset(["D"]),
        frozenset(["E"]),
    }


def test_get_logic_from_xor_puml_file():
    """Test for method detect_logic"""
    puml_file = "puml_files/sequence_xor_fork.puml"
    data = generate_test_data(puml_file)
    events_forward_logic, events_backward_logic = (
        update_all_connections_from_data(data)
    )
    # check A logic trees
    assert events_forward_logic["A"].logic_gate_tree.label == "B"
    assert events_backward_logic["A"].logic_gate_tree is None
    # check B logic trees
    assert events_forward_logic["B"].logic_gate_tree.operator.name == "XOR"
    following_b_events = ["C", "D", "E"]
    for child in events_forward_logic["B"].logic_gate_tree.children:
        assert child.label in following_b_events
        following_b_events.remove(child.label)
    assert len(following_b_events) == 0
    assert events_backward_logic["B"].logic_gate_tree.label == "A"
    # check C, D, E logic trees
    for event_type in ["C", "D", "E"]:
        assert events_forward_logic[event_type].logic_gate_tree.label == "F"
        assert events_backward_logic[event_type].logic_gate_tree.label == "B"
    # check F logic trees
    assert events_forward_logic["F"].logic_gate_tree is None
    assert events_backward_logic["F"].logic_gate_tree.operator.name == "XOR"
    preceding_f_events = ["C", "D", "E"]
    for child in events_backward_logic["F"].logic_gate_tree.children:
        assert child.label in preceding_f_events
        preceding_f_events.remove(child.label)
    assert len(preceding_f_events) == 0


def test_get_logic_from_nested_and_puml_file():
    """Test for method detect_logic"""
    puml_file = "puml_files/ANDFork_ANDFork_a.puml"
    data = generate_test_data(puml_file)
    events_forward_logic, events_backward_logic = (
        update_all_connections_from_data(data)
    )
    # check A logic trees
    assert events_forward_logic["A"].logic_gate_tree.operator.name == "PARALLEL"
    following_a_events = ["B", "C"]
    for child in events_forward_logic["A"].logic_gate_tree.children:
        assert child.label in following_a_events
        following_a_events.remove(child.label)
    assert len(following_a_events) == 0
    assert events_backward_logic["A"].logic_gate_tree is None
    # check B logic trees
    assert events_forward_logic["B"].logic_gate_tree.operator.name == "PARALLEL"
    following_b_events = ["D", "E"]
    for child in events_forward_logic["B"].logic_gate_tree.children:
        assert child.label in following_b_events
        following_b_events.remove(child.label)
    assert len(following_b_events) == 0
    assert events_backward_logic["B"].logic_gate_tree.label == "A"
    # check C logic trees
    assert events_forward_logic["C"].logic_gate_tree.label == "F"
    assert events_backward_logic["C"].logic_gate_tree.label == "A"
    # check D, E logic trees
    for event_type in ["D", "E"]:
        assert events_forward_logic[event_type].logic_gate_tree.label == "F"
        assert events_backward_logic[event_type].logic_gate_tree.label == "B"
    # check F logic trees
    assert events_forward_logic["F"].logic_gate_tree is None
    assert events_backward_logic["F"].logic_gate_tree.operator.name == "PARALLEL"
    preceding_f_events = ["C", "D", "E"]
    for child in events_backward_logic["F"].logic_gate_tree.children:
        assert child.label in preceding_f_events
        preceding_f_events.remove(child.label)
    assert len(preceding_f_events) == 0 
