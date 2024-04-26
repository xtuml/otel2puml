"""Test the logic detection pipeline."""

from datetime import datetime, timedelta
from pm4py import ProcessTree


from tel2puml.pipelines.logic_detection_pipeline import (
    Event,
    EventSet,
    Operator,
    update_all_connections_from_data,
    remove_detected_loop_events,
    get_loop_events_to_remove_mapping,
    remove_detected_loop_data_from_events,
    get_graph_solutions_from_clustered_events
)
from tel2puml.pipelines.data_creation import (
    generate_test_data,
    generate_test_data_event_sequences_from_puml
)
from tel2puml.detect_loops import Loop
from tel2puml.tel2puml_types import DUMMY_START_EVENT


class TestOperator:
    """Tests for the Operator class."""

    def test_values(self):
        """Tests for the values of the Operator class."""
        assert Operator.SEQUENCE.value == "->"
        assert Operator.PARALLEL.value == "+"
        assert Operator.XOR.value == "X"
        assert Operator.OR.value == "O"
        assert Operator.LOOP.value == "*"
        assert Operator.INTERLEAVING.value == "<>"
        assert Operator.PARTIALORDER.value == "PO"
        assert Operator.BRANCH.value == "BR"


class TestEventSet:
    """Tests for the EventSet class."""

    @staticmethod
    def test_init_single_entries() -> None:
        """Tests for the __init__ method."""
        event_set = EventSet(["A", "B", "C"])
        assert event_set["A"] == 1
        assert event_set["B"] == 1
        assert event_set["C"] == 1

    @staticmethod
    def test_init_repeated_entries() -> None:
        """Tests for the __init__ method for repeated entries."""
        event_set = EventSet(["A", "B", "A", "C", "B", "A"])
        assert event_set["A"] == 3
        assert event_set["B"] == 2
        assert event_set["C"] == 1

    @staticmethod
    def test_init_empty_entries() -> None:
        """Tests for the __init__ method for empty entries."""
        event_set = EventSet([])
        assert len(event_set) == 0

    @staticmethod
    def test_hash() -> None:
        """Tests for the __hash__ method."""
        event_set_1 = EventSet(["A", "B", "C"])
        assert hash(event_set_1) == hash((("A", 1), ("B", 1), ("C", 1)))
        event_set_2 = EventSet(["A", "B", "A", "C", "B", "A"])
        assert hash(event_set_2) == hash((("A", 3), ("B", 2), ("C", 1)))

    @staticmethod
    def test_eq() -> None:
        """Tests for the __eq__ method."""
        event_set_1 = EventSet(["A", "B", "C"])
        event_set_2 = EventSet(["B", "A", "C"])
        assert event_set_1 == event_set_2
        event_set_3 = EventSet(["A", "B", "A", "C", "B", "A"])
        assert event_set_1 != event_set_3

    @staticmethod
    def test_to_frozenset() -> None:
        """Tests for the to_list method."""
        event_set = EventSet(["A", "B", "C"])
        assert event_set.to_frozenset() == frozenset(["A", "B", "C"])
        event_set = EventSet(["B", "A", "C"])
        assert event_set.to_frozenset() == frozenset(["A", "B", "C"])
        event_set = EventSet(["A", "B", "A", "C", "B", "A"])
        assert event_set.to_frozenset() == frozenset(["A", "B", "C"])

    @staticmethod
    def test_get_branch_events() -> None:
        """Tests for the get_branch_counts method."""
        event_set = EventSet(["A", "B", "C"])
        assert event_set.get_repeated_events() == {}
        event_set = EventSet(["A", "A"])
        assert event_set.get_repeated_events() == {"A": 2}
        event_set = EventSet(["A", "B", "A", "C", "B", "A"])
        assert event_set.get_repeated_events() == {"A": 3, "B": 2}


class TestEvent:
    """Tests for the Event class."""

    @staticmethod
    def test_add_new_edge_to_conditional_count_matrix() -> None:
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
    def test_add_new_edge_to_edge_counts_per_data_point() -> None:
        """Tests for method add_new_edge_to_edge_counts_per_data_point"""
        event = Event("A")
        for i, edge_tuple in enumerate([("A", "B"), ("B", "C"), ("C", "D")]):
            event.add_new_edge_to_edge_counts_per_data_point(edge_tuple)
            assert edge_tuple in event.edge_counts_per_data_point
            assert (event.edge_counts_per_data_point[edge_tuple])["index"] == i

    @staticmethod
    def test_update_conditional_count_matrix() -> None:
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
    def test_update_with_edge_tuple_and_data_point_edges() -> None:
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
    def test_update_with_data_point() -> None:
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
    def test_conditional_probability_matrix() -> None:
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
            [2 / 3, 1, 1],
            [1 / 3, 0.5, 1],
        ]

    @staticmethod
    def test_update_event_sets() -> None:
        """Tests for method update_event_sets"""
        event = Event("A")
        events = ["B", "C", "D"]
        # check that the event sets are updated
        event.update_event_sets(events)
        assert event.event_sets == {EventSet(events)}
        # check that the event sets are not updated
        event.update_event_sets(events)
        assert event.event_sets == {EventSet(events)}
        # check that the event sets are not updated if events are reversed
        event.update_event_sets(["D", "C", "B"])
        assert event.event_sets == {EventSet(events)}
        # check that the event sets are updated
        event.update_event_sets(["B", "C"])
        assert event.event_sets == {EventSet(events), EventSet(["B", "C"])}
        # check that the event sets are updated
        event.update_event_sets(["B", "B", "C"])
        assert event.event_sets == {
            EventSet(events),
            EventSet(["B", "C"]),
            EventSet(["B", "B", "C"]),
        }
        # check that the event sets are not updated
        event.update_event_sets(["B", "C", "B"])
        assert event.event_sets == {
            EventSet(events),
            EventSet(["B", "C"]),
            EventSet(["B", "B", "C"]),
        }
        # check that the event sets are updated
        event.update_event_sets(["C", "B", "C"])
        assert event.event_sets == {
            EventSet(events),
            EventSet(["B", "C"]),
            EventSet(["B", "B", "C"]),
            EventSet(["B", "C", "C"]),
        }

    def test_get_reduced_event_set(self) -> None:
        """Tests for method get_reduced_event_set"""
        event = Event("A")
        event.event_sets = {
            EventSet(["B", "C"]),
            EventSet(["B", "B", "C"]),
            EventSet(["B", "C", "C"]),
        }
        reduced_event_set = event.get_reduced_event_set()
        assert reduced_event_set == {frozenset(["B", "C"])}

        event.event_sets = {
            EventSet(["A"]),
            EventSet(["B"]),
            EventSet(["B", "C"]),
            EventSet(["B", "B", "C"]),
            EventSet(["B", "C", "C"]),
        }
        reduced_event_set = event.get_reduced_event_set()
        assert reduced_event_set == {
            frozenset(["B", "C"]),
            frozenset(["A"]),
            frozenset(["B"]),
            }

    def test_get_event_set_counts(self) -> None:
        """Tests for method get_event_set_counts"""
        event = Event("A")
        event.event_sets = {
            EventSet(["B"]),
        }
        event_set_counts = event.get_event_set_counts()
        assert event_set_counts == {'B': {1}}

        event.event_sets = {
            EventSet(["B", "C"]),
            EventSet(["B", "B", "C"]),
            EventSet(["B", "C", "C"]),
        }
        event_set_counts = event.get_event_set_counts()
        assert event_set_counts == {'B': {1, 2}, 'C': {1, 2}}

        event.event_sets = {
            EventSet(["B"]),
            EventSet(["B", "C"]),
            EventSet(["B", "C", "C"]),
        }
        event_set_counts = event.get_event_set_counts()
        assert event_set_counts == {'B': {1}, 'C': {1, 2}}

        event.event_sets = {
            EventSet(["B", "C"]),
            EventSet(["B", "B", "C"]),
            EventSet(["B", "C", "C", "D"]),
        }
        event_set_counts = event.get_event_set_counts()
        assert event_set_counts == {'B': {1, 2}, 'C': {1, 2}, 'D': {1}}

    def test_remove_event_type_from_event_sets(self) -> None:
        """Tests for method remove_event_type_from_event_sets"""
        event = Event("A")
        event.event_sets = {
            EventSet(["B"]),
        }
        event.remove_event_type_from_event_sets("B")
        assert event.event_sets == set()

        event.event_sets = {
            EventSet(["B", "C"]),
            EventSet(["B", "B", "C"]),
            EventSet(["C", "C"]),
        }
        event.remove_event_type_from_event_sets("B")
        assert event.event_sets == {
            EventSet(["C", "C"]),
        }

    @staticmethod
    def test_create_data_from_event_sequence() -> None:
        """Tests for method create_data_from_event_sequence"""
        event_sequence = ["A", "B", "C", "D"]
        case_id = "case_1"
        start_time = datetime(2021, 1, 1, 0, 0, 0)
        data = Event.create_data_from_event_sequence(
            event_sequence, case_id, start_time
        )
        for i, event_data in enumerate(data):
            assert event_data["case_id"] == case_id
            assert event_data["activity"] == event_sequence[i]
            assert event_data["timestamp"] == start_time + timedelta(seconds=i)

    @staticmethod
    def test_create_augmented_data_from_reduced_event_set() -> None:
        """Tests for method created_augemented_data_from_event_set"""
        event = Event("A")
        event_set = EventSet(["B", "C"])
        data = list(
            event.create_augmented_data_from_reduced_event_set(
                event_set,
            )
        )
        assert len(data) == 6
        expected_sequences = [
            "ABC",
            "ACB",
        ]
        expected_sequences.remove(
            "".join([event_data["activity"] for event_data in data[:3]])
        )
        expected_sequences.remove(
            "".join([event_data["activity"] for event_data in data[3:]])
        )
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
    def test_create_augmented_data_from_event_sets() -> None:
        """Tests for method created_augemented_data_from_event_sets"""
        event = Event("A")
        event.event_sets = {
            EventSet(["B", "C"]),
            EventSet(["D", "E"]),
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
            expected_sequences.remove(
                "".join(
                    [
                        event_data["activity"]
                        for event_data in data[i * 3:i * 3 + 3]
                    ]
                )
            )
        assert len(expected_sequences) == 0

    @staticmethod
    def test_calculate_process_tree_from_event_sets_xor_ands() -> None:
        """Tests for method calculate_process_tree_from_event_sets for XOR and
        AND gates
        """
        event = Event("A")
        event.event_sets = {
            EventSet(["B", "C"]),
            EventSet(["D", "E"]),
        }
        process_tree = event.calculate_process_tree_from_event_sets()
        first_children = process_tree.children
        assert len(first_children) == 2
        start_event = first_children[0]
        next_operator = first_children[1]
        assert start_event.label == "A"
        assert next_operator.operator.value == Operator.XOR.value
        second_children = next_operator.children
        assert len(second_children) == 2
        first_operator = second_children[0]
        second_operator = second_children[1]
        assert first_operator.operator.value == Operator.PARALLEL.value
        assert second_operator.operator.value == Operator.PARALLEL.value
        first_operator_children = first_operator.children
        assert len(first_operator_children) == 2
        second_operator_children = second_operator.children
        assert len(second_operator_children) == 2
        children_labels = []
        for operator_children in [
            first_operator_children,
            second_operator_children,
        ]:
            operator_child_labels = []
            for child in operator_children:
                assert len(child.children) == 0
                operator_child_labels.append(child.label)
            children_labels.append(frozenset(sorted(operator_child_labels)))
        for to_remove in [
            frozenset(sorted(["B", "C"])),
            frozenset(sorted(["D", "E"])),
        ]:
            children_labels.remove(to_remove)
        assert len(children_labels) == 0

    @staticmethod
    def test_calculate_process_tree_from_event_sets_or() -> None:
        """Tests for method calculate_process_tree_from_event_sets for OR
        gates"""
        event = Event("A")
        event.event_sets = {
            EventSet(["B", "C"]),
            EventSet(["B"]),
            EventSet(["C"]),
        }
        process_tree = event.calculate_process_tree_from_event_sets()
        first_children = process_tree.children
        assert len(first_children) == 2
        start_event = first_children[0]
        next_operator = first_children[1]
        assert start_event.label == "A"
        assert next_operator.operator.value == Operator.PARALLEL.value
        second_children = next_operator.children
        assert len(second_children) == 2
        first_operator = second_children[0]
        second_operator = second_children[1]
        assert first_operator.operator.value == Operator.XOR.value
        assert second_operator.operator.value == Operator.XOR.value
        first_operator_children = first_operator.children
        assert len(first_operator_children) == 2
        second_operator_children = second_operator.children
        assert len(second_operator_children) == 2
        children_labels = []
        for operator_children in [
            first_operator_children,
            second_operator_children,
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
    def test_infer_or_gate_from_node() -> None:
        """Tests for method infer_or_gate_from_node"""
        event = Event("A")
        event.event_sets = {
            EventSet(["B", "C"]),
            EventSet(["B"]),
            EventSet(["C"]),
        }
        process_tree = event.calculate_process_tree_from_event_sets()
        logic_gate = process_tree.children[1]
        assert logic_gate.operator.value == Operator.PARALLEL.value
        event.infer_or_gate_from_node(logic_gate)
        assert logic_gate.operator.value == Operator.OR.value
        assert len(logic_gate.children) == 2
        labels = ["B", "C"]
        for child in logic_gate.children:
            labels.remove(child.label)
        assert len(labels) == 0

        def _check_or_and(tree):
            logic_gate = tree.children[1]
            assert logic_gate.operator.value == Operator.PARALLEL.value
            event.infer_or_gate_from_node(logic_gate)
            assert logic_gate.operator.value == Operator.OR.value
            assert len(logic_gate.children) == 2
            labels_b = ["B"]
            labels_cd = ["C", "D"]
            for child in logic_gate.children:
                if child.label == "B":
                    labels_b.remove(child.label)
                else:
                    assert child.operator.value == Operator.PARALLEL.value
                    assert len(child.children) == 2
                    for grandchild in child.children:
                        labels_cd.remove(grandchild.label)
            assert len(labels_b) == 0
            assert len(labels_cd) == 0

        def _check_or(tree):
            logic_gate = tree.children[1]
            assert logic_gate.operator.value == Operator.PARALLEL.value
            event.infer_or_gate_from_node(logic_gate)
            assert logic_gate.operator.value == Operator.OR.value
            assert len(logic_gate.children) == 3
            labels = ["B", "C", "D"]
            for child in logic_gate.children:
                labels.remove(child.label)
            assert len(labels) == 0

        event.event_sets = {
            EventSet(["B", "C", "D"]),
            EventSet(["B"]),
        }
        process_tree = event.calculate_process_tree_from_event_sets()
        _check_or(process_tree)

        event.event_sets = {
            EventSet(["B", "C", "D"]),
            EventSet(["C", "D"]),
        }
        process_tree = event.calculate_process_tree_from_event_sets()
        _check_or_and(process_tree)

    @staticmethod
    def test_get_extended_or_gates_from_process_tree() -> None:
        """Tests for method get_extended_or_gates_from_process_tree"""
        event = Event("A")
        event.event_sets = {
            EventSet(["B", "C"]),
            EventSet(["B"]),
            EventSet(["C"]),
        }
        process_tree = event.calculate_process_tree_from_event_sets()
        logic_gates_tree = process_tree.children[1]
        event.get_extended_or_gates_from_process_tree(logic_gates_tree)
        assert logic_gates_tree.operator.value == Operator.OR.value
        assert len(logic_gates_tree.children) == 2
        labels = ["B", "C"]
        for child in logic_gates_tree.children:
            labels.remove(child.label)
        assert len(labels) == 0

    @staticmethod
    def test_filter_defunct_or_gates() -> None:
        """Tests for method filter_defunct_or_gates"""
        event = Event("A")
        event.event_sets = {
            EventSet(["B", "C"]),
            EventSet(["B"]),
            EventSet(["C"]),
        }
        process_tree = event.calculate_process_tree_from_event_sets()
        logic_gates_tree = process_tree.children[1]
        event.get_extended_or_gates_from_process_tree(logic_gates_tree)
        event.filter_defunct_or_gates(logic_gates_tree)
        assert logic_gates_tree.operator.value == Operator.OR.value
        assert len(logic_gates_tree.children) == 2
        labels = ["B", "C"]
        for child in logic_gates_tree.children:
            assert child.label in labels
            labels.remove(child.label)
        assert len(labels) == 0

    @staticmethod
    def test_process_missing_and_gates() -> None:
        """Test for method process_missing_and_gates"""
        def _process(event: Event) -> ProcessTree:
            process_tree = event.calculate_process_tree_from_event_sets()
            logic_gates_tree = process_tree.children[1]
            event.process_or_gates(logic_gates_tree)
            event.process_missing_and_gates(logic_gates_tree)
            return logic_gates_tree

        def _check_and_case(event: Event) -> None:
            logic_gates_tree = _process(event)
            assert logic_gates_tree.operator.value == Operator.OR.value
            assert len(logic_gates_tree.children) == 2
            labels = ["B", "C", "D"]
            for child in logic_gates_tree.children:
                if child.label == "B":
                    labels.remove(child.label)
                else:
                    assert child.operator.value == Operator.PARALLEL.value
                    assert len(child.children) == 2
                    for grandchild in child.children:
                        labels.remove(grandchild.label)
            assert len(labels) == 0

        event = Event("A")
        event.event_sets = {
            EventSet(["B", "C", "D"]),
            EventSet(["C", "D"]),
            EventSet(["B"]),

        }
        _check_and_case(event)

        def _check_or_case(event: Event) -> None:
            logic_gates_tree = _process(event)
            assert logic_gates_tree.operator.value == Operator.OR.value
            assert len(logic_gates_tree.children) == 3
            labels = ["B", "C", "D"]
            for child in logic_gates_tree.children:
                labels.remove(child.label)
            assert len(labels) == 0

        event.event_sets = {
            EventSet(["B", "C", "D"]),
            EventSet(["C", "D"]),
            EventSet(["B", "C"]),
            EventSet(["B"]),
            EventSet(["D"]),
        }
        _check_or_case(event)

        event.event_sets = {
            EventSet(["B", "C", "D"]),
            EventSet(["C", "D"]),
            EventSet(["B", "C"]),
            EventSet(["B"]),
        }
        _check_or_case(event)

        event.event_sets = {
            EventSet(["B", "C", "D"]),
            EventSet(["B", "C"]),
            EventSet(["B"]),
        }
        _check_or_case(event)

        def _check_and_or_case(event: Event) -> None:
            logic_gates_tree = _process(event)
            assert logic_gates_tree.operator.value == Operator.PARALLEL.value
            assert len(logic_gates_tree.children) == 2
            labels = ["B", "C", "D"]
            for child in logic_gates_tree.children:
                if child.label == "B":
                    labels.remove(child.label)
                else:
                    assert child.operator.value == Operator.OR.value
                    assert len(child.children) == 2
                    for grandchild in child.children:
                        labels.remove(grandchild.label)
            assert len(labels) == 0

        event.event_sets = {
            EventSet(["B", "C", "D"]),
            EventSet(["B", "C"]),
            EventSet(["B", "D"]),
        }
        _check_and_or_case(event)

        def _check_recursive_case(event: Event) -> None:
            logic_gates_tree = _process(event)
            assert logic_gates_tree.operator.value == Operator.XOR.value
            assert len(logic_gates_tree.children) == 2
            for operator_child in logic_gates_tree.children:
                if operator_child.operator.value == Operator.PARALLEL.value:
                    assert len(operator_child.children) == 2
                    labels_bc = ["B", "C"]
                    for child in operator_child.children:
                        labels_bc.remove(child.label)
                    assert len(labels_bc) == 0
                else:
                    assert operator_child.operator.value == Operator.OR.value
                    assert len(operator_child.children) == 2
                    labels = ["D", "E", "F"]
                    for child in operator_child.children:
                        if child.label == "D":
                            labels.remove(child.label)
                        else:
                            assert (
                                child.operator.value == Operator.PARALLEL.value
                            )
                            assert len(child.children) == 2
                            for grandchild in child.children:
                                labels.remove(grandchild.label)
                    assert len(labels) == 0

        event.event_sets = {
            EventSet(["B", "C"]),
            EventSet(["D", "E", "F"]),
            EventSet(["E", "F"]),
            EventSet(["D"]),

        }
        _check_recursive_case(event)

    @staticmethod
    def test_process_or_gates() -> None:
        """Tests for method process_or_gates"""
        event = Event("A")
        event.event_sets = {
            EventSet(["B", "C", "D"]),
            EventSet(["B", "C"]),
            EventSet(["C", "D"]),
            EventSet(["B", "D"]),
            EventSet(["B"]),
            EventSet(["C"]),
            EventSet(["D"]),
        }
        process_tree = event.calculate_process_tree_from_event_sets()
        logic_gates_tree = process_tree.children[1]
        event.process_or_gates(logic_gates_tree)
        assert logic_gates_tree.operator.value == Operator.OR.value
        assert len(logic_gates_tree.children) == 3
        labels = ["B", "C", "D"]
        for child in logic_gates_tree.children:
            assert child.label in labels
            labels.remove(child.label)
        assert len(labels) == 0

    @staticmethod
    def test_reduce_process_tree_to_preferred_logic_gates() -> None:
        """Tests for method reduce_process_tree_to_preffered_logic_gates"""
        def _test_logic_gate(process_tree: ProcessTree):
            logic_gates_tree = (
                event.reduce_process_tree_to_preferred_logic_gates(
                    process_tree
                )
            )
            assert logic_gates_tree.operator.value == Operator.OR.value
            assert len(logic_gates_tree.children) == 3
            labels = ["B", "C", "D"]
            for child in logic_gates_tree.children:
                assert child.label in labels
                labels.remove(child.label)
            assert len(labels) == 0

        event = Event("A")
        event.event_sets = {
            EventSet(["B", "C", "D"]),
            EventSet(["B", "C"]),
            EventSet(["C", "D"]),
            EventSet(["B", "D"]),
            EventSet(["B"]),
            EventSet(["C"]),
            EventSet(["D"]),
        }
        process_tree = event.calculate_process_tree_from_event_sets()
        _test_logic_gate(process_tree)

        event.event_sets = {
            EventSet(["B", "C", "D"]),
            EventSet(["C", "D"]),
            EventSet(["D"]),
            EventSet(["B"]),
        }
        process_tree = event.calculate_process_tree_from_event_sets()
        _test_logic_gate(process_tree)

        main_tree = ProcessTree(
            operator=Operator.PARALLEL,
            children=[
                ProcessTree(
                    operator=Operator.XOR,
                    children=[
                        ProcessTree(label="tau"),
                        ProcessTree(label="B")],
                ),
                ProcessTree(
                    operator=Operator.XOR,
                    children=[
                        ProcessTree(label="tau"),
                        ProcessTree(
                            operator=Operator.PARALLEL,
                            children=[
                                ProcessTree(
                                    operator=Operator.XOR,
                                    children=[
                                        ProcessTree(label="tau"),
                                        ProcessTree(label="C")],
                                ),
                                ProcessTree(label="D"),
                            ],
                        ),
                    ],
                ),
            ],
        )
        process_tree = ProcessTree(
            label=Operator.SEQUENCE,
            children=[
                ProcessTree(label="A"),
                main_tree,
            ]
        )
        _test_logic_gate(process_tree)

    @staticmethod
    def test_update_tree_with_repeat_logic() -> None:
        """Tests for method update_tree_with_branch_logic"""
        event = Event("A")
        event.event_sets = {
            EventSet(["B"]),
        }
        node_1 = ProcessTree(None, None, None, "B")
        updated_node_1 = event.update_tree_with_repeat_logic(node_1)
        assert updated_node_1.label == "B"
        assert len(updated_node_1.children) == 0

        event.event_sets = {
            EventSet(["B", "B"]),
        }
        node_2 = ProcessTree(None, None, None, "B")
        updated_node_2 = event.update_tree_with_repeat_logic(node_2)

        def _check_node_for_repeat_and(node):
            assert node.operator.value == Operator.PARALLEL.value
            assert len(node.children) == 2
            labels = ["B", "B"]
            for child in node.children:
                assert child.label in labels
                labels.remove(child.label)
            assert len(labels) == 0

        _check_node_for_repeat_and(updated_node_2)

        event.event_sets = {
            EventSet(["B", "B", "C"]),
        }
        node_3 = ProcessTree(None, None, None, "C")
        node_4 = ProcessTree(
            Operator.PARALLEL,
            None,
            [node_2, node_3],
        )
        updated_node_4 = event.update_tree_with_repeat_logic(node_4)
        assert updated_node_4.operator.value == Operator.PARALLEL.value
        assert len(updated_node_4.children) == 2

        labels = ["C"]
        for child in updated_node_4.children:
            if child.label == "C":
                labels.remove(child.label)
            else:
                _check_node_for_repeat_and(child)
        assert len(labels) == 0

    @staticmethod
    def test_calculate_repeats_in_tree() -> None:
        """Tests for method find_branches_in_process_tree"""
        event = Event("A")
        event.event_sets = {
            EventSet(["B", "B"]),
            EventSet(["C", "D"]),
        }
        process_tree = event.calculate_process_tree_from_event_sets()
        logic_gates_tree = event.reduce_process_tree_to_preferred_logic_gates(
            process_tree
        )
        logic_gate_tree_with_branches = event.calculate_repeats_in_tree(
            logic_gates_tree
        )

        assert (
            logic_gate_tree_with_branches.operator.value
            == Operator.XOR.value
        )
        labels_b = ["B", "B"]
        labels_cd = ["D", "C"]
        for child_and in logic_gate_tree_with_branches.children:
            assert child_and.operator.value == Operator.PARALLEL.value
            for child in child_and.children:
                if child.label == "B":
                    labels_b.remove(child.label)
                else:
                    labels_cd.remove(child.label)
        assert len(labels_b) == 0
        assert len(labels_cd) == 0

        event.event_sets = {
            EventSet(["B", "B"]),
            EventSet(["B"]),
        }

        process_tree = event.calculate_process_tree_from_event_sets()
        logic_gates_tree = event.reduce_process_tree_to_preferred_logic_gates(
            process_tree
        )
        logic_gate_tree_with_branches = event.calculate_repeats_in_tree(
            logic_gates_tree
        )

        assert (
            logic_gate_tree_with_branches.operator.value
            == Operator.BRANCH.value
        )
        child, = logic_gate_tree_with_branches.children
        assert child.label == "B"

        event.event_sets = {
            EventSet(["B", "B", "B"]),
            EventSet(["B", "B"]),
            EventSet(["B"]),
        }

        process_tree = event.calculate_process_tree_from_event_sets()
        logic_gates_tree = event.reduce_process_tree_to_preferred_logic_gates(
            process_tree
        )
        logic_gate_tree_with_branches = event.calculate_repeats_in_tree(
            logic_gates_tree
        )

        assert (
            logic_gate_tree_with_branches.operator.value
            == Operator.BRANCH.value
        )
        child, = logic_gate_tree_with_branches.children
        assert child.label == "B"

        event.event_sets = {
            EventSet(["C", "D"]),
            EventSet(["B", "B"]),
            EventSet(["B"]),
        }

        process_tree = event.calculate_process_tree_from_event_sets()
        logic_gates_tree = event.reduce_process_tree_to_preferred_logic_gates(
            process_tree
        )
        logic_gate_tree_with_branches = event.calculate_repeats_in_tree(
            logic_gates_tree
        )

        assert (
            logic_gate_tree_with_branches.operator.value
            == Operator.BRANCH.value
        )
        child_xor, = logic_gate_tree_with_branches.children
        assert child_xor.operator.value == Operator.XOR.value
        labels_b = ["B"]
        labels_cd = ["D", "C"]
        for grandchild in child_xor.children:
            if grandchild.label == "B":
                labels_b.remove(grandchild.label)
            else:
                assert grandchild.operator.value == Operator.PARALLEL.value
                for great_grandchild in grandchild.children:
                    labels_cd.remove(great_grandchild.label)
        assert len(labels_b) == 0
        assert len(labels_cd) == 0

    @staticmethod
    def test_remove_defunct_sequence_logic() -> None:
        """Tests for method remove_defunct_sequence_logic"""

        node_b1 = ProcessTree(None, None, None, "B")
        node_b2 = ProcessTree(None, None, None, "B")
        node_parallel = ProcessTree(
            Operator.PARALLEL,
            None,
            [node_b1, node_b2],
        )
        node_sequence = ProcessTree(
            Operator.SEQUENCE,
            None,
            [node_parallel],
        )

        processed_tree = Event.remove_defunct_sequence_logic(node_sequence)
        assert processed_tree.operator.value == Operator.PARALLEL.value

    @staticmethod
    def test_calculate_logic_gates() -> None:
        """Tests for method calculate_logic_gates"""
        event = Event("A")
        event.event_sets = {
            EventSet(["B", "C", "D"]),
            EventSet(["B", "C"]),
            EventSet(["C", "D"]),
            EventSet(["B", "D"]),
            EventSet(["B"]),
            EventSet(["C"]),
            EventSet(["D"]),
        }
        logic_gates_tree = event.calculate_logic_gates()
        assert logic_gates_tree.operator.value == Operator.OR.value
        assert len(logic_gates_tree.children) == 3
        labels = ["B", "C", "D"]
        for child in logic_gates_tree.children:
            assert child.label in labels
            labels.remove(child.label)
        assert len(labels) == 0


def test_update_all_connections_from_data() -> None:
    """Test for method update_all_connections_from_data"""
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
        EventSet(["B"]),
    }
    assert events_backward_logic["A"].event_sets == set()
    # check B
    assert events_forward_logic["B"].event_sets == {
        EventSet(["C"]),
        EventSet(["D"]),
        EventSet(["E"]),
    }
    assert events_backward_logic["B"].event_sets == {
        EventSet(["A"]),
    }
    # check C, D, E
    for event_type in ["C", "D", "E"]:
        assert events_forward_logic[event_type].event_sets == {
            EventSet(["F"]),
        }
        assert events_backward_logic[event_type].event_sets == {
            EventSet(["B"]),
        }
    # check F
    assert events_forward_logic["F"].event_sets == set()
    assert events_backward_logic["F"].event_sets == {
        EventSet(["C"]),
        EventSet(["D"]),
        EventSet(["E"]),
    }


def test_remove_detected_loop_events() -> None:
    """Test for method remove_detected_loop_events"""
    event_a = Event("A")
    event_a.event_sets = {
        EventSet(["B"]),
    }
    event_b = Event("B")
    event_b.event_sets = {
        EventSet(["A"]),
        EventSet(["C"]),
    }
    event_c = Event("C")

    mapping = {"B": ["A"]}
    events = {"A": event_a, "B": event_b, "C": event_c}
    remove_detected_loop_events(mapping, events)
    for event_set in event_b.event_sets:
        assert "A" not in event_set


def test_get_logic_from_xor_puml_file() -> None:
    """Test method for getting logic gates for a puml file with XOR gate"""
    puml_file = "puml_files/sequence_xor_fork.puml"
    data = generate_test_data(puml_file)
    events_forward_logic, events_backward_logic = (
        update_all_connections_from_data(data)
    )
    # check A logic trees
    assert events_forward_logic["A"].logic_gate_tree.label == "B"
    assert events_backward_logic["A"].logic_gate_tree is None
    # check B logic trees
    assert (
        events_forward_logic["B"].logic_gate_tree.operator.value
        == Operator.XOR.value
        )
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
    assert (
        events_backward_logic["F"].logic_gate_tree.operator.value
        == Operator.XOR.value
    )
    preceding_f_events = ["C", "D", "E"]
    for child in events_backward_logic["F"].logic_gate_tree.children:
        assert child.label in preceding_f_events
        preceding_f_events.remove(child.label)
    assert len(preceding_f_events) == 0


def test_get_logic_from_nested_and_puml_file() -> None:
    """Test method for getting logic gates for a puml file with nested AND
    gate"""
    puml_file = "puml_files/ANDFork_ANDFork_a.puml"
    data = generate_test_data(puml_file)
    events_forward_logic, events_backward_logic = (
        update_all_connections_from_data(data)
    )
    # check A logic trees
    assert (
        events_forward_logic["A"].logic_gate_tree.operator.value
        == Operator.PARALLEL.value
    )
    following_a_events = ["B", "C"]
    for child in events_forward_logic["A"].logic_gate_tree.children:
        assert child.label in following_a_events
        following_a_events.remove(child.label)
    assert len(following_a_events) == 0
    assert events_backward_logic["A"].logic_gate_tree is None
    # check B logic trees
    assert (
        events_forward_logic["B"].logic_gate_tree.operator.value
        == Operator.PARALLEL.value
    )
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
    assert (
        events_backward_logic["F"].logic_gate_tree.operator.value
        == Operator.PARALLEL.value
    )
    preceding_f_events = ["C", "D", "E"]
    for child in events_backward_logic["F"].logic_gate_tree.children:
        assert child.label in preceding_f_events
        preceding_f_events.remove(child.label)
    assert len(preceding_f_events) == 0


def test_get_logic_from_nested_or_puml_file() -> None:
    """Test method for getting logic gates for a puml file with nested OR
    gate"""
    puml_file = "puml_files/ORFork_ORFork_a.puml"
    data = generate_test_data(puml_file)
    events_forward_logic, events_backward_logic = (
        update_all_connections_from_data(data)
    )
    # check A logic trees
    assert (
        events_forward_logic["A"].logic_gate_tree.operator.value
        == Operator.OR.value
    )
    following_a_events = ["B", "C"]
    for child in events_forward_logic["A"].logic_gate_tree.children:
        assert child.label in following_a_events
        following_a_events.remove(child.label)
    # check B logic trees
    assert (
        events_forward_logic["B"].logic_gate_tree.operator.value
        == Operator.OR.value
    )
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
    assert (
        events_backward_logic["F"].logic_gate_tree.operator.value
        == Operator.OR.value
    )
    preceding_f_events = ["C", "D", "E"]
    for child in events_backward_logic["F"].logic_gate_tree.children:
        assert child.label in preceding_f_events
        preceding_f_events.remove(child.label)
    assert len(preceding_f_events) == 0


def test_get_logic_from_nested_xor_puml_file() -> None:
    """Test method for getting logic gates for a puml file with nested XOR
    gate"""
    puml_file = "puml_files/XORFork_XORFork_a.puml"
    data = generate_test_data(puml_file)
    events_forward_logic, events_backward_logic = (
        update_all_connections_from_data(data)
    )
    # check A logic trees
    assert (
        events_forward_logic["A"].logic_gate_tree.operator.value
        == Operator.XOR.value
    )
    following_a_events = ["B", "C"]
    for child in events_forward_logic["A"].logic_gate_tree.children:
        assert child.label in following_a_events
        following_a_events.remove(child.label)
    assert len(following_a_events) == 0
    assert events_backward_logic["A"].logic_gate_tree is None
    # check B logic trees
    assert (
        events_forward_logic["B"].logic_gate_tree.operator.value
        == Operator.XOR.value
    )
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
    assert (
        events_backward_logic["F"].logic_gate_tree.operator.value
        == Operator.XOR.value
    )
    preceding_f_events = ["C", "D", "E"]
    for child in events_backward_logic["F"].logic_gate_tree.children:
        assert child.label in preceding_f_events
        preceding_f_events.remove(child.label)
    assert len(preceding_f_events) == 0


def test_get_logic_from_repeated_event_puml_file() -> None:
    """Test method for getting logic gates for a puml file with repeated
    event"""
    puml_file = "puml_files/repeated_same_event.puml"
    data = generate_test_data(puml_file)
    events_forward_logic, events_backward_logic = (
        update_all_connections_from_data(data)
    )
    # check A logic trees
    assert (
        events_forward_logic["A"].logic_gate_tree.operator.value
        == Operator.XOR.value
    )
    following_a_events = ["B", "C"]
    for child in events_forward_logic["A"].logic_gate_tree.children:
        assert child.label in following_a_events
        following_a_events.remove(child.label)
    assert len(following_a_events) == 0
    assert events_backward_logic["A"].logic_gate_tree is None
    # check B logic trees
    assert (
        events_forward_logic["B"].logic_gate_tree.operator.value
        == Operator.PARALLEL.value
    )
    following_b_events = ["D", "D", "D"]
    for child in events_forward_logic["B"].logic_gate_tree.children:
        assert child.label in following_b_events
        following_b_events.remove(child.label)
    assert len(following_b_events) == 0
    assert events_backward_logic["B"].logic_gate_tree.label == "A"
    # check C logic trees
    assert events_forward_logic["C"].logic_gate_tree.label == "E"
    assert events_backward_logic["C"].logic_gate_tree.label == "A"
    # check D logic trees
    assert events_forward_logic["D"].logic_gate_tree.label == "E"
    assert events_backward_logic["D"].logic_gate_tree.label == "B"
    # check E logic trees
    assert events_forward_logic["E"].logic_gate_tree is None
    assert (
        events_backward_logic["E"].logic_gate_tree.operator.value
        == Operator.XOR.value
    )
    preceding_e_events = ["C", "D", "D", "D"]
    for child in events_backward_logic["E"].logic_gate_tree.children:
        if child.label == "C":
            preceding_e_events.remove(child.label)
        else:
            assert child.operator.value == Operator.PARALLEL.value
            for grandchild in child.children:
                assert grandchild.label in preceding_e_events
                preceding_e_events.remove(grandchild.label)
    assert len(preceding_e_events) == 0


def test_get_logic_from_and_under_or_puml_file() -> None:
    """Test method for getting logic gates for a puml file with AND gate below
    OR gate"""
    puml_file = "puml_files/AND_under_OR_test.puml"
    data = generate_test_data(puml_file)
    events_forward_logic, events_backward_logic = (
        update_all_connections_from_data(data)
    )
    # check A, E logic trees
    for events_logic in [
            events_forward_logic["A"],
            events_backward_logic["H"]
    ]:
        assert (
            events_logic.logic_gate_tree.operator.value
            == Operator.OR.value
        )

        events_after_cd = ["C", "D"]
        events_after_efg = ["E", "F", "G"]
        for child in events_logic.logic_gate_tree.children:
            if child.label is not None:
                assert child.label == "B"
            else:
                assert child.operator.value == Operator.PARALLEL.value
                if child.children[0].label in events_after_cd:
                    for grandchild in child.children:
                        events_after_cd.remove(grandchild.label)
                else:
                    for grandchild in child.children:
                        events_after_efg.remove(grandchild.label)
        assert len(events_after_cd) == 0
        assert len(events_after_efg) == 0

    for events_logic in [
            events_forward_logic["H"],
            events_backward_logic["A"]
    ]:
        assert events_logic.logic_gate_tree is None
    # check B logic trees
    assert events_forward_logic["B"].logic_gate_tree.label == "H"
    assert events_backward_logic["B"].logic_gate_tree.label == "A"
    # check C, D logic trees
    for event in ["C", "D", "E", "F", "G"]:
        assert events_forward_logic[event].logic_gate_tree.label == "H"
        assert events_backward_logic[event].logic_gate_tree.label == "A"


class TestLoopEdgeRemoval:
    """Tests functionality for loop edge removal from Event class"""
    def get_loop_ref_and_events(
        self
    ) -> tuple[list[Loop], dict[str, str], dict[str, Event]]:
        """Helper method to get loop reference and events for testing"""
        # setup loops
        loop_1 = Loop(["q1", "q2", "q3"])
        loop_1.add_edge_to_remove(("q3", "q1"))
        loop_2 = Loop(["q4", "q5"])
        loop_2.add_edge_to_remove(("q5", "q5"))
        loops = [loop_1, loop_2]
        # setup node events reference
        node_event_name_reference = {
            "q1": "A",
            "q2": "B",
            "q3": "C",
            "q4": "D",
            "q5": "E",
        }
        # setup events
        A = Event("A")
        B = Event("B")
        C = Event("C")
        D = Event("D")
        E = Event("E")
        A.update_event_sets(["B"])
        B.update_event_sets(["C"])
        C.update_event_sets(["A"])
        C.update_event_sets(["D"])
        D.update_event_sets(["E"])
        E.update_event_sets(["E"])
        events = {"A": A, "B": B, "C": C, "D": D, "E": E}
        return loops, node_event_name_reference, events

    def test_get_loop_events_to_remove_mapping(self) -> None:
        """Test for method get_loop_events_to_remove_mapping"""
        loops, node_event_name_reference, _ = self.get_loop_ref_and_events()
        loop_events_to_remove = get_loop_events_to_remove_mapping(
            loops, node_event_name_reference
        )
        assert len(loop_events_to_remove) == 2
        assert "C" in loop_events_to_remove and "E" in loop_events_to_remove
        assert loop_events_to_remove["C"] == ["A"]
        assert loop_events_to_remove["E"] == ["E"]

    def test_remove_detected_loop_data_from_events(self) -> None:
        """Test for method remove_detected_loop_data_from_events"""
        loops, node_event_name_reference, events = (
            self.get_loop_ref_and_events()
        )
        remove_detected_loop_data_from_events(
            loops,
            events,
            node_event_name_reference
        )
        assert len(events["C"].event_sets) == 1
        assert len(events["E"].event_sets) == 0
        assert len(events["A"].event_sets) == 1
        assert len(events["B"].event_sets) == 1
        assert len(events["D"].event_sets) == 1


def test_get_graph_solutions_from_clustered_events() -> None:
    """Test for method get_graph_solutions_from_clustered_events specifically
    for dual start events
    """
    # test for dual start event and add dummy start event
    event_sequences = generate_test_data_event_sequences_from_puml(
        "puml_files/two_start_events.puml",
        remove_dummy_start_event=True
    )
    graph_solutions = get_graph_solutions_from_clustered_events(
        event_sequences,
        add_dummy_start=True
    )
    graph_solution = next(graph_solutions)
    events = {
        event.meta_data["EventType"]: event
        for event in graph_solution.events.values()
    }
    assert len(events) == 4
    assert DUMMY_START_EVENT in events
    assert events[DUMMY_START_EVENT].post_events == [
        events["A"], events["B"]
    ]
    assert events["A"].previous_events == [events[DUMMY_START_EVENT]]
    assert events["B"].previous_events == [events[DUMMY_START_EVENT]]
