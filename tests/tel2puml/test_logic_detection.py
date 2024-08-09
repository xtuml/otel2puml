"""Tests for the logic_detection module."""
from datetime import datetime, timedelta
from pm4py import ProcessTree
import numpy as np
from numpy.typing import NDArray


from tel2puml.data_pipelines.data_creation import generate_test_data
from tel2puml.data_pipelines.data_ingestion import (
    update_all_connections_from_data
)
from tel2puml.events import EventSet
from tel2puml.logic_detection import (
    Operator,
    create_data_from_event_sequence,
    create_augmented_data_from_reduced_event_set,
    create_augmented_data_from_event_sets,
    calculate_process_tree_from_event_sets,
    infer_or_gate_from_node,
    get_extended_or_gates_from_process_tree,
    filter_defunct_or_gates,
    process_or_gates,
    process_missing_and_gates,
    reduce_process_tree_to_preferred_logic_gates,
    update_tree_with_repeat_logic,
    calculate_repeats_in_tree,
    remove_defunct_sequence_logic,
    calculate_logic_gates,
    get_process_tree_leaves,
    get_matrix_of_event_counts_from_event_sets_and_leaves,
    order_matrix_of_event_counts,
    check_is_ok_and_under_branch,
    assure_or_and_operators_are_correct_under_branch,
    flatten_nested_xor_operators,
    create_branch_tree_from_logic_gate_tree
)
from tel2puml.tel2puml_types import DUMMY_START_EVENT


class TestOperator:
    """Tests for the Operator class."""

    def test_values(self) -> None:
        """Tests for the values of the Operator class."""
        assert Operator.SEQUENCE.value == "->"
        assert Operator.PARALLEL.value == "+"
        assert Operator.XOR.value == "X"
        assert Operator.OR.value == "O"
        assert Operator.LOOP.value == "*"
        assert Operator.INTERLEAVING.value == "<>"
        assert Operator.PARTIALORDER.value == "PO"
        assert Operator.BRANCH.value == "BR"


def test_create_data_from_event_sequence() -> None:
    """Tests for method create_data_from_event_sequence"""
    event_sequence = ["A", "B", "C", "D"]
    case_id = "case_1"
    start_time = datetime(2021, 1, 1, 0, 0, 0)
    data = create_data_from_event_sequence(
        event_sequence, case_id, start_time
    )
    for i, event_data in enumerate(data):
        assert event_data["case_id"] == case_id
        assert event_data["activity"] == event_sequence[i]
        assert event_data["timestamp"] == start_time + timedelta(seconds=i)


def test_create_augmented_data_from_reduced_event_set() -> None:
    """Tests for method created_augemented_data_from_event_set"""
    event_set = EventSet(["B", "C"])
    data = list(
        create_augmented_data_from_reduced_event_set(
            event_set.to_frozenset(),
        )
    )
    assert len(data) == 6
    expected_sequences = [
        f"{DUMMY_START_EVENT}BC",
        f"{DUMMY_START_EVENT}CB",
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


def test_create_augmented_data_from_event_sets() -> None:
    """Tests for method created_augemented_data_from_event_sets"""
    event_sets = {
        EventSet(["B", "C"]),
        EventSet(["D", "E"]),
    }
    data = list(create_augmented_data_from_event_sets(event_sets))
    assert len(data) == 12
    expected_sequences = [
        f"{DUMMY_START_EVENT}BC",
        f"{DUMMY_START_EVENT}CB",
        f"{DUMMY_START_EVENT}DE",
        f"{DUMMY_START_EVENT}ED",
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


def test_calculate_process_tree_from_event_sets_xor_ands() -> None:
    """Tests for method calculate_process_tree_from_event_sets for XOR and
    AND gates
    """
    event_sets = {
        EventSet(["B", "C"]),
        EventSet(["D", "E"]),
    }
    process_tree = calculate_process_tree_from_event_sets(event_sets)
    first_children = process_tree.children
    assert len(first_children) == 2
    start_event = first_children[0]
    next_operator = first_children[1]
    assert start_event.label == DUMMY_START_EVENT
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


def test_calculate_process_tree_from_event_sets_or() -> None:
    """Tests for method calculate_process_tree_from_event_sets for OR
    gates"""
    event_sets = {
        EventSet(["B", "C"]),
        EventSet(["B"]),
        EventSet(["C"]),
    }
    process_tree = calculate_process_tree_from_event_sets(event_sets)
    first_children = process_tree.children
    assert len(first_children) == 2
    start_event = first_children[0]
    next_operator = first_children[1]
    assert start_event.label == DUMMY_START_EVENT
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


def test_infer_or_gate_from_node() -> None:
    """Tests for method infer_or_gate_from_node"""
    event_sets = {
        EventSet(["B", "C"]),
        EventSet(["B"]),
        EventSet(["C"]),
    }
    process_tree = calculate_process_tree_from_event_sets(event_sets)
    logic_gate = process_tree.children[1]
    assert logic_gate.operator.value == Operator.PARALLEL.value
    infer_or_gate_from_node(event_sets, logic_gate)
    assert logic_gate.operator.value == Operator.OR.value
    assert len(logic_gate.children) == 2
    labels = ["B", "C"]
    for child in logic_gate.children:
        labels.remove(child.label)
    assert len(labels) == 0

    def _check_or_and(tree: ProcessTree) -> None:
        logic_gate = tree.children[1]
        assert logic_gate.operator.value == Operator.PARALLEL.value
        infer_or_gate_from_node(event_sets, logic_gate)
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

    def _check_or(tree: ProcessTree) -> None:
        logic_gate = tree.children[1]
        assert logic_gate.operator.value == Operator.PARALLEL.value
        infer_or_gate_from_node(event_sets, logic_gate)
        assert logic_gate.operator.value == Operator.OR.value
        assert len(logic_gate.children) == 3
        labels = ["B", "C", "D"]
        for child in logic_gate.children:
            labels.remove(child.label)
        assert len(labels) == 0

    event_sets = {
        EventSet(["B", "C", "D"]),
        EventSet(["B"]),
    }
    process_tree = calculate_process_tree_from_event_sets(event_sets)
    _check_or(process_tree)

    event_sets = {
        EventSet(["B", "C", "D"]),
        EventSet(["C", "D"]),
    }
    process_tree = calculate_process_tree_from_event_sets(event_sets)
    _check_or_and(process_tree)


def test_get_extended_or_gates_from_process_tree() -> None:
    """Tests for method get_extended_or_gates_from_process_tree"""
    event_sets = {
        EventSet(["B", "C"]),
        EventSet(["B"]),
        EventSet(["C"]),
    }
    process_tree = calculate_process_tree_from_event_sets(event_sets)
    logic_gates_tree = process_tree.children[1]
    get_extended_or_gates_from_process_tree(event_sets, logic_gates_tree)
    assert logic_gates_tree.operator.value == Operator.OR.value
    assert len(logic_gates_tree.children) == 2
    labels = ["B", "C"]
    for child in logic_gates_tree.children:
        labels.remove(child.label)
    assert len(labels) == 0


def test_filter_defunct_or_gates() -> None:
    """Tests for method filter_defunct_or_gates"""
    event_sets = {
        EventSet(["B", "C"]),
        EventSet(["B"]),
        EventSet(["C"]),
    }
    process_tree = calculate_process_tree_from_event_sets(event_sets)
    logic_gates_tree = process_tree.children[1]
    get_extended_or_gates_from_process_tree(event_sets, logic_gates_tree)
    filter_defunct_or_gates(logic_gates_tree)
    assert logic_gates_tree.operator.value == Operator.OR.value
    assert len(logic_gates_tree.children) == 2
    labels = ["B", "C"]
    for child in logic_gates_tree.children:
        assert child.label in labels
        labels.remove(child.label)
    assert len(labels) == 0


def test_process_missing_and_gates() -> None:
    """Test for method process_missing_and_gates"""
    def _process(event_sets: set[EventSet]) -> ProcessTree:
        process_tree = calculate_process_tree_from_event_sets(event_sets)
        logic_gates_tree = process_tree.children[1]
        process_or_gates(event_sets, logic_gates_tree)
        process_missing_and_gates(event_sets, logic_gates_tree)
        return logic_gates_tree

    def _check_and_case(event_sets: set[EventSet]) -> None:
        logic_gates_tree = _process(event_sets)
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

    event_sets = {
        EventSet(["B", "C", "D"]),
        EventSet(["C", "D"]),
        EventSet(["B"]),

    }
    _check_and_case(event_sets)

    def _check_or_case(event_sets: set[EventSet]) -> None:
        logic_gates_tree = _process(event_sets)
        assert logic_gates_tree.operator.value == Operator.OR.value
        assert len(logic_gates_tree.children) == 3
        labels = ["B", "C", "D"]
        for child in logic_gates_tree.children:
            labels.remove(child.label)
        assert len(labels) == 0

    event_sets = {
        EventSet(["B", "C", "D"]),
        EventSet(["C", "D"]),
        EventSet(["B", "C"]),
        EventSet(["B"]),
        EventSet(["D"]),
    }
    _check_or_case(event_sets)

    event_sets = {
        EventSet(["B", "C", "D"]),
        EventSet(["C", "D"]),
        EventSet(["B", "C"]),
        EventSet(["B"]),
    }
    _check_or_case(event_sets)

    event_sets = {
        EventSet(["B", "C", "D"]),
        EventSet(["B", "C"]),
        EventSet(["B"]),
    }
    _check_or_case(event_sets)

    def _check_and_or_case(event_sets: set[EventSet]) -> None:
        logic_gates_tree = _process(event_sets)
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

    event_sets = {
        EventSet(["B", "C", "D"]),
        EventSet(["B", "C"]),
        EventSet(["B", "D"]),
    }
    _check_and_or_case(event_sets)

    def _check_recursive_case(event_sets: set[EventSet]) -> None:
        logic_gates_tree = _process(event_sets)
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

    event_sets = {
        EventSet(["B", "C"]),
        EventSet(["D", "E", "F"]),
        EventSet(["E", "F"]),
        EventSet(["D"]),

    }
    _check_recursive_case(event_sets)


def test_process_or_gates() -> None:
    """Tests for method process_or_gates"""
    event_sets = {
        EventSet(["B", "C", "D"]),
        EventSet(["B", "C"]),
        EventSet(["C", "D"]),
        EventSet(["B", "D"]),
        EventSet(["B"]),
        EventSet(["C"]),
        EventSet(["D"]),
    }
    process_tree = calculate_process_tree_from_event_sets(event_sets)
    logic_gates_tree = process_tree.children[1]
    process_or_gates(event_sets, logic_gates_tree)
    assert logic_gates_tree.operator.value == Operator.OR.value
    assert len(logic_gates_tree.children) == 3
    labels = ["B", "C", "D"]
    for child in logic_gates_tree.children:
        assert child.label in labels
        labels.remove(child.label)
    assert len(labels) == 0


def test_reduce_process_tree_to_preferred_logic_gates() -> None:
    """Tests for method reduce_process_tree_to_preffered_logic_gates"""
    def _test_logic_gate(process_tree: ProcessTree) -> None:
        logic_gates_tree = (
            reduce_process_tree_to_preferred_logic_gates(
                event_sets, process_tree
            )
        )
        assert logic_gates_tree.operator.value == Operator.OR.value
        assert len(logic_gates_tree.children) == 3
        labels = ["B", "C", "D"]
        for child in logic_gates_tree.children:
            assert child.label in labels
            labels.remove(child.label)
        assert len(labels) == 0

    event_sets = {
        EventSet(["B", "C", "D"]),
        EventSet(["B", "C"]),
        EventSet(["C", "D"]),
        EventSet(["B", "D"]),
        EventSet(["B"]),
        EventSet(["C"]),
        EventSet(["D"]),
    }
    process_tree = calculate_process_tree_from_event_sets(event_sets)
    _test_logic_gate(process_tree)

    event_sets = {
        EventSet(["B", "C", "D"]),
        EventSet(["C", "D"]),
        EventSet(["D"]),
        EventSet(["B"]),
    }
    process_tree = calculate_process_tree_from_event_sets(event_sets)
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


def test_update_tree_with_repeat_logic() -> None:
    """Tests for method update_tree_with_branch_logic"""
    event_sets = {
        EventSet(["B"]),
    }
    node_1 = ProcessTree(None, None, None, "B")
    updated_node_1 = update_tree_with_repeat_logic(event_sets, node_1)
    assert updated_node_1.label == "B"
    assert len(updated_node_1.children) == 0

    event_sets = {
        EventSet(["B", "B"]),
    }
    node_2 = ProcessTree(None, None, None, "B")
    updated_node_2 = update_tree_with_repeat_logic(event_sets, node_2)

    def _check_node_for_repeat_and(node: ProcessTree) -> None:
        assert node.operator.value == Operator.PARALLEL.value
        assert len(node.children) == 2
        labels = ["B", "B"]
        for child in node.children:
            assert child.label in labels
            labels.remove(child.label)
        assert len(labels) == 0

    _check_node_for_repeat_and(updated_node_2)

    event_sets = {
        EventSet(["B", "B", "C"]),
    }
    node_3 = ProcessTree(None, None, None, "C")
    node_4 = ProcessTree(
        Operator.PARALLEL,
        None,
        [node_2, node_3],
    )
    updated_node_4 = update_tree_with_repeat_logic(event_sets, node_4)
    assert updated_node_4.operator.value == Operator.PARALLEL.value
    assert len(updated_node_4.children) == 2

    labels = ["C"]
    for child in updated_node_4.children:
        if child.label == "C":
            labels.remove(child.label)
        else:
            _check_node_for_repeat_and(child)
    assert len(labels) == 0


def test_calculate_repeats_in_tree() -> None:
    """Tests for method find_branches_in_process_tree"""
    event_sets = {
        EventSet(["B", "B"]),
        EventSet(["C", "D"]),
    }
    process_tree = calculate_process_tree_from_event_sets(event_sets)
    logic_gates_tree = reduce_process_tree_to_preferred_logic_gates(
        event_sets, process_tree
    )
    logic_gate_tree_with_branches = calculate_repeats_in_tree(
        event_sets, logic_gates_tree
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

    event_sets = {
        EventSet(["B", "B"]),
        EventSet(["B"]),
    }

    process_tree = calculate_process_tree_from_event_sets(event_sets)
    logic_gates_tree = reduce_process_tree_to_preferred_logic_gates(
        event_sets, process_tree
    )
    logic_gate_tree_with_branches = calculate_repeats_in_tree(
        event_sets, logic_gates_tree
    )

    assert (
        logic_gate_tree_with_branches.operator.value
        == Operator.BRANCH.value
    )
    child, = logic_gate_tree_with_branches.children
    assert child.label == "B"

    event_sets = {
        EventSet(["B", "B", "B"]),
        EventSet(["B", "B"]),
        EventSet(["B"]),
    }

    process_tree = calculate_process_tree_from_event_sets(event_sets)
    logic_gates_tree = reduce_process_tree_to_preferred_logic_gates(
        event_sets, process_tree
    )
    logic_gate_tree_with_branches = calculate_repeats_in_tree(
        event_sets, logic_gates_tree
    )

    assert (
        logic_gate_tree_with_branches.operator.value
        == Operator.BRANCH.value
    )
    child, = logic_gate_tree_with_branches.children
    assert child.label == "B"

    event_sets = {
        EventSet(["C", "D"]),
        EventSet(["B", "B"]),
        EventSet(["B"]),
    }

    process_tree = calculate_process_tree_from_event_sets(event_sets)
    logic_gates_tree = reduce_process_tree_to_preferred_logic_gates(
        event_sets, process_tree
    )
    logic_gate_tree_with_branches = calculate_repeats_in_tree(
        event_sets, logic_gates_tree
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

    processed_tree = remove_defunct_sequence_logic(node_sequence)
    assert processed_tree.operator.value == Operator.PARALLEL.value


def test_calculate_logic_gates() -> None:
    """Tests for method calculate_logic_gates"""
    event_sets = {
        EventSet(["B", "C", "D"]),
        EventSet(["B", "C"]),
        EventSet(["C", "D"]),
        EventSet(["B", "D"]),
        EventSet(["B"]),
        EventSet(["C"]),
        EventSet(["D"]),
    }
    logic_gates_tree = calculate_logic_gates(event_sets)
    assert logic_gates_tree.operator.value == Operator.OR.value
    assert len(logic_gates_tree.children) == 3
    labels = ["B", "C", "D"]
    for child in logic_gates_tree.children:
        assert child.label in labels
        labels.remove(child.label)
    assert len(labels) == 0
    # test when there are no event sets
    event_sets = set()
    assert calculate_logic_gates(event_sets) is None


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


def test_get_process_tree_leaves() -> None:
    """Test method for getting leaves of a process tree"""
    process_tree = ProcessTree(
        operator=Operator.BRANCH,
        children=[
            ProcessTree(
                operator=Operator.PARALLEL,
                children=[
                    ProcessTree(
                        operator=Operator.XOR,
                        children=[
                            ProcessTree(label="A"),
                            ProcessTree(label="B"),
                        ],
                    ),
                    ProcessTree(label="C"),
                ],
            ),
        ],
    )
    leaves = list(get_process_tree_leaves(process_tree))
    assert len(leaves) == 3
    assert leaves == ["A", "B", "C"]
    # check process tree with no logic gate
    leaves = list(get_process_tree_leaves(ProcessTree(label="A")))
    assert len(leaves) == 1
    assert leaves == ["A"]


class TestCreateBranchTreeFromLogicGateTree:
    """Tests for method create_branch_tree_from_logic_gate_tree and sub methods
    """
    @staticmethod
    def event_sets() -> set[EventSet]:
        """Return a set of event sets"""
        return {
            EventSet(["B", "B", "C", "D"]),
            EventSet(["B", "C"]),
            EventSet(["C", "D"]),
            EventSet(["B", "D"]),
            EventSet(["B"]),
            EventSet(["C"]),
            EventSet(["D"]),
        }

    @staticmethod
    def expected_matrix() -> NDArray[np.int32]:
        """Return the expected matrix of event counts"""
        return np.array(
            [
                [0, 1, 1],
                [1, 1, 2],
                [0, 0, 1],
                [0, 1, 0],
                [1, 0, 0],
                [1, 0, 1],
                [1, 1, 0],
            ],
            dtype=np.int32,
        )

    @staticmethod
    def expected_ordered_matrix() -> NDArray[np.int32]:
        """Return the expected ordered matrix of event counts"""
        return np.array(
            [
                [0, 0, 1],
                [0, 1, 0],
                [0, 1, 1],
                [1, 0, 0],
                [1, 0, 1],
                [1, 1, 0],
                [1, 1, 2],
            ],
            dtype=np.int32,
        )

    def test_get_matrix_of_event_counts_from_event_sets_and_leaves(
        self
    ) -> None:
        """Test method for getting matrix of event counts from event sets and
        leaves"""
        event_sets = self.event_sets()
        matrix = get_matrix_of_event_counts_from_event_sets_and_leaves(
            event_sets, ["C", "D", "B"]
        )
        expected_matrix = np.sort(
            self.expected_matrix(), axis=0
        )
        assert np.array_equal(np.sort(matrix, axis=0), expected_matrix)

    def test_order_matrix_of_event_counts(self) -> None:
        """Test method for ordering matrix of event counts"""
        matrix = self.expected_matrix()
        ordered_matrix = order_matrix_of_event_counts(matrix)
        expected_ordered_matrix = self.expected_ordered_matrix()
        assert np.array_equal(ordered_matrix, expected_ordered_matrix)

    def test_check_is_ok_and_under_branch(self) -> None:
        """Test method for checking if event sets are OK and under a branch"""
        event_sets = self.event_sets()
        # check positive cases
        assert check_is_ok_and_under_branch(event_sets, ["C", "D", "B"])
        event_sets = {
            EventSet(["B", "C"]),
            EventSet(["B" "B", "C", "C"]),
        }
        assert check_is_ok_and_under_branch(event_sets, ["C", "B"])
        # check negative case
        event_sets = {
            EventSet(["B", "C"]),
            EventSet(["B", "B", "C"]),
        }
        assert not check_is_ok_and_under_branch(event_sets, ["C", "B"])

    def test_assure_or_and_operators_are_correct_under_branch(self) -> None:
        """Test method for assuring OR and AND operators are correct under a
        branch
        """
        event_sets = self.event_sets()
        # check OR case
        logic_gates_tree = ProcessTree(
            operator=Operator.OR,
            children=[
                ProcessTree(label="B"),
                ProcessTree(label="C"),
                ProcessTree(label="D"),
            ],
        )
        assure_or_and_operators_are_correct_under_branch(
            logic_gates_tree, event_sets
        )
        assert logic_gates_tree.operator.value == Operator.XOR.value
        # check single AND case that requires no changes
        logic_gates_tree = ProcessTree(
            operator=Operator.PARALLEL,
            children=[
                ProcessTree(label="B"),
                ProcessTree(label="C"),
                ProcessTree(label="D"),
            ],
        )
        event_sets = {
            EventSet(["B", "C", "D"]),
            EventSet(["B", "C", "D"] * 2),
        }
        assure_or_and_operators_are_correct_under_branch(
            logic_gates_tree, event_sets
        )
        assert logic_gates_tree.operator.value == Operator.PARALLEL.value
        # check single AND case that should be converted to an XOR
        event_sets.update({EventSet(["B", "B", "C", "D"])})
        assure_or_and_operators_are_correct_under_branch(
            logic_gates_tree, event_sets
        )
        assert logic_gates_tree.operator.value == Operator.XOR.value
        # check nested AND case that requires no change
        logic_gates_tree = ProcessTree(
            operator=Operator.XOR,
            children=[
                ProcessTree(
                    operator=Operator.PARALLEL,
                    children=[
                        ProcessTree(label="B"),
                        ProcessTree(label="C"),
                    ],
                ),
                ProcessTree(label="D"),
            ],
        )
        event_sets = {
            EventSet(["B", "C"]),
            EventSet(["B", "C"] * 2),
            EventSet(["D"]),
            EventSet(["D"] * 2),
        }
        assure_or_and_operators_are_correct_under_branch(
            logic_gates_tree, event_sets
        )
        assert (
            logic_gates_tree.children[0].operator.value
            == Operator.PARALLEL.value
        )
        # check nested AND case that should be converted to an XOR
        event_sets.update({EventSet(["B", "B", "C"])})
        assure_or_and_operators_are_correct_under_branch(
            logic_gates_tree, event_sets
        )
        assert (
            logic_gates_tree.children[0].operator.value
            == Operator.XOR.value
        )

    @staticmethod
    def test_flatten_nested_xor_operators() -> None:
        """Test method for flattening nested XOR operators"""
        children = [
            ProcessTree(label="A"), ProcessTree(label="B"),
            ProcessTree(label="C")
        ]
        process_tree = ProcessTree(
            operator=Operator.XOR,
            children=[
                ProcessTree(
                    operator=Operator.XOR,
                    children=children[:2],
                ),
                children[2],
            ],
        )
        flatten_nested_xor_operators(process_tree)
        assert process_tree.operator.value == Operator.XOR.value
        assert process_tree.children == children
        # test case with AND operator in between XOR operators
        children = [
            ProcessTree(
                operator=Operator.PARALLEL,
                children=[
                    ProcessTree(
                        operator=Operator.XOR,
                        children=children[:2],
                    ),
                    children[2],
                ],
            ),
            ProcessTree(label="D"),
        ]
        process_tree = ProcessTree(
            operator=Operator.XOR,
            children=children,
        )
        flatten_nested_xor_operators(process_tree)
        assert process_tree.operator.value == Operator.XOR.value
        assert process_tree.children == children

    def test_create_branch_tree_from_logic_gate_tree(self) -> None:
        """Test method for creating a branch tree from a logic gate tree"""
        def check_process_tree_correct(
            process_tree: ProcessTree, children: list[ProcessTree],
            expected_operator: Operator
        ) -> None:
            """Check if the process tree is correct"""
            assert process_tree.operator.value == Operator.BRANCH.value
            branch_children: list[ProcessTree] = list(process_tree.children)
            assert len(branch_children) == 1
            child = branch_children[0]
            assert child.operator.value == expected_operator.value
            assert child.children == children

        event_sets = self.event_sets()
        children = [
            ProcessTree(label="B"), ProcessTree(label="C"),
            ProcessTree(label="D")
        ]
        logic_gates_tree = ProcessTree(
            operator=Operator.OR,
            children=children,
        )
        branch_tree = create_branch_tree_from_logic_gate_tree(
            logic_gates_tree, event_sets
        )
        check_process_tree_correct(branch_tree, children, Operator.XOR)
        # test case with incorrect AND operators with nested XOR to be
        # flattened
        event_sets = {
            EventSet(["B", "D"]),
            EventSet(["C", "D"]),
            EventSet(["B", "D", "D"]),
        }
        logic_gates_tree = ProcessTree(
            operator=Operator.PARALLEL,
            children=[
                ProcessTree(
                    operator=Operator.XOR,
                    children=children[:2],
                ),
                children[2],
            ]
        )
        branch_tree = create_branch_tree_from_logic_gate_tree(
            logic_gates_tree, event_sets
        )
        check_process_tree_correct(branch_tree, children, Operator.XOR)
        # test case with correct AND
        event_sets = {
            EventSet(["B", "C", "D"]),
            EventSet(["B", "C", "D"] * 2),
        }
        logic_gates_tree = ProcessTree(
            operator=Operator.PARALLEL,
            children=children
        )
        branch_tree = create_branch_tree_from_logic_gate_tree(
            logic_gates_tree, event_sets
        )
        check_process_tree_correct(branch_tree, children, Operator.PARALLEL)
