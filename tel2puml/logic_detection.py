"""Module to detect logic gates from EventSet's held in Event class and create
a logic gate process tree"""

from typing import Any, Generator, TypeVar, Iterable, TypedDict, Literal
from itertools import permutations
from datetime import datetime, timedelta
from uuid import uuid4
from enum import Enum

import pandas as pd
from pm4py import (  # type: ignore[import-untyped]
    discover_process_tree_inductive,
    ProcessTree,
    format_dataframe,
)
import numpy as np
from numpy.typing import NDArray
import networkx as nx

import tel2puml.events as ev
from tel2puml.utils import get_weighted_cover
from tel2puml.tel2puml_types import DUMMY_START_EVENT


T = TypeVar("T", bound=np.generic, covariant=True)


class Operator(Enum):
    """
    Enum to represent the operators in a process tree.
    """

    # sequence operator
    SEQUENCE = "->"
    # exclusive choice operator
    XOR = "X"
    # parallel operator
    PARALLEL = "+"
    # loop operator
    LOOP = "*"
    # or operator
    OR = "O"
    # interleaving operator
    INTERLEAVING = "<>"
    # partially-ordered operator
    PARTIALORDER = "PO"
    # branch operator
    BRANCH = "BR"
    AMBIGUOUS = "AMBIGUOUS"

    def __str__(self) -> str:
        """
        Provides a string representation of the current operator

        :return: String representation of the process tree.
        :rtype: `str`
        """
        return self.value

    def __repr__(self) -> str:
        """
        Provides a string representation of the current operator

        :return: String representation of the process tree.
        :rtype: `str`
        """
        return self.value


def get_non_operator_successor_labels(
    node: ProcessTree,
) -> Generator[str, Any, None]:
    """Recursive method to get the leaf label nodes of a process tree.

    :param node: The process tree node.
    :type node: :class:`pm4py.objects.process_tree.obj.ProcessTree`
    :return: The leaf label nodes.
    :rtype: `Generator`[`str`, `Any`, `None`]"""
    if node.operator is None:
        yield node.label
    for child in node.children:
        yield from get_non_operator_successor_labels(child)


def calculate_logic_gates(event_sets: set["ev.EventSet"]) -> ProcessTree:
    """This method calculates the logic gates from the event sets.

    :param event_sets: The event sets.
    :type event_sets: `set`[:class:`tel2puml.events.EventSet`]
    :return: The logic gate tree.
    :rtype: :class:`pm4py.objects.process_tree.obj.ProcessTree`
    """
    # check if we have no event sets then return None
    if len(event_sets) == 0:
        return None
    process_tree = calculate_process_tree_from_event_sets(event_sets)
    # process_tree = ProcessTree(
    #     Operator.SEQUENCE,
    #     children=[get_logic_tree_from_event_sets(event_sets)],
    # )
    # process_tree.children[0].parent = process_tree
    logic_gate_tree = reduce_process_tree_to_preferred_logic_gates(
        event_sets, process_tree
    )
    logic_gate_tree_with_repeats = calculate_repeats_in_tree(
        event_sets, logic_gate_tree 
    )
    ensure_or_replaced_with_and(logic_gate_tree_with_repeats, event_sets)
    return logic_gate_tree_with_repeats


def create_augmented_data_from_event_sets(
    event_sets: set["ev.EventSet"],
) -> Generator[dict[str, Any], Any, None]:
    """Method to create augmented data from the event sets and yields
    the data.

    :param event_sets: The event sets.
    :type event_sets: `set`[:class:`tel2puml.events.EventSet`]
    :return: The augmented data.
    :rtype: `Generator`[`dict`[`str`, `Any`], `Any`, `None`]"""
    for reduced_event_set in ev.get_reduced_event_set(event_sets):
        yield from create_augmented_data_from_reduced_event_set(
            reduced_event_set
        )


def create_augmented_data_from_reduced_event_set(
    reduced_event_set: frozenset[str],
) -> Generator[dict[str, Any], Any, None]:
    """Method to create augmented data from a single event set then
    yielding the augmented data.

    :param reduced_event_set: The reduced event set.
    :type reduced_event_set: `frozenset`[`str`]
    :return: The augmented data.
    :rtype: `Generator`[`dict`[`str`, `Any`], `Any`, `None`]
    """
    for permutation in permutations(reduced_event_set, len(reduced_event_set)):
        case_id = str(uuid4())
        yield from create_data_from_event_sequence(
            [DUMMY_START_EVENT, *permutation],
            case_id,
            start_time=datetime.now(),
        )


def create_data_from_event_sequence(
    event_sequence: list[str],
    case_id: str,
    start_time: datetime = datetime.now(),
) -> Generator[dict[str, Any], Any, None]:
    """Method to create data from an event sequence given a case id and
    start time and yields the data.

    :param event_sequence: The event sequence.
    :type event_sequence: `list`[`str`]
    :param case_id: The case id.
    :type case_id: `str`
    :param start_time: The start time.
    :type start_time: `datetime.datetime`
    :return: The data.
    :rtype: `Generator`[`dict`[`str`, `Any`], `Any`, `None`]
    """
    for i, event in enumerate(event_sequence):
        yield {
            "case_id": case_id,
            "activity": event,
            "timestamp": start_time + timedelta(seconds=i),
        }


def calculate_process_tree_from_event_sets(
    event_sets: set["ev.EventSet"],
) -> ProcessTree:
    """This method calculates the pm4py process tree from the event sets.

    :param event_sets: The event sets.
    :type event_sets: `set`[:class:`tel2puml.events.EventSet`]
    :return: The process tree.
    :rtype: :class:`pm4py.objects.process_tree.obj.ProcessTree`
    """
    augmented_dataframe = pd.DataFrame(
        create_augmented_data_from_event_sets(event_sets)
    )
    event_log = format_dataframe(
        augmented_dataframe,
        case_id="case_id",
        activity_key="activity",
        timestamp_key="timestamp",
    )
    process_tree = discover_process_tree_inductive(
        event_log,
    )
    return process_tree


def reduce_process_tree_to_preferred_logic_gates(
    event_sets: set["ev.EventSet"],
    process_tree: ProcessTree,
) -> ProcessTree:
    """This method reduces a process tree to the preferred logic gates by
    removing the first event and getting the subsequent tree and then
    calculating the OR gates and adding missing AND gates.

    :param event_sets: The event sets.
    :type event_sets: `set`[:class:`tel2puml.events.EventSet`]
    :param process_tree: The process tree.
    :type process_tree: :class:`pm4py.objects.process_tree.obj.ProcessTree`
    :return: The logic gate tree.
    :rtype: :class:`pm4py.objects.process_tree.obj.ProcessTree`
    """
    # remove first event and get subsequent tree
    logic_gate_tree: ProcessTree = process_tree.children.pop()
    # calculate OR gates
    process_or_gates(event_sets, logic_gate_tree)
    # # process missing AND gates
    process_missing_and_gates(event_sets, logic_gate_tree)
    return logic_gate_tree


def process_or_gates(
    event_sets: set["ev.EventSet"],
    process_tree: ProcessTree,
) -> None:
    """Method to process the OR gates in a process tree by extending
    the OR gates and filtering the defunct OR gates.

    :param event_sets: The event sets.
    :type event_sets: `set`[:class:`tel2puml.events.EventSet`]
    :param process_tree: The process tree.
    :type process_tree: :class:`pm4py.objects.process_tree.obj.ProcessTree`
    """
    get_extended_or_gates_from_process_tree(event_sets, process_tree)
    filter_defunct_or_gates(process_tree)


def get_extended_or_gates_from_process_tree(
    event_sets: set["ev.EventSet"],
    process_tree: ProcessTree,
) -> None:
    """Static method to get the extended OR gates from a process tree by
    inferring the OR gates from a node.

    :param event_sets: The event sets.
    :type event_sets: `set`[:class:`tel2puml.events.EventSet`]
    :param process_tree: The process tree.
    :type process_tree: :class:`pm4py.objects.process_tree.obj.ProcessTree`
    """
    infer_or_gate_from_node(event_sets, process_tree)
    for node in process_tree.children:
        get_extended_or_gates_from_process_tree(event_sets, node)


def check_is_or_operator(
    event_sets: set["ev.EventSet"],
    non_tau_children: list[ProcessTree],
    removed_tau_children: list[ProcessTree],
) -> bool:
    """Method to check if the operator is an OR operator from the non-tau
    children and removed tau children.

    :param event_sets: The event sets.
    :type event_sets: `set`[:class:`tel2puml.events.EventSet`]
    :param non_tau_children: The non-tau children.
    :type non_tau_children:
    `list`[:class:`pm4py.objects.process_tree.obj.ProcessTree`]
    :param removed_tau_children: The removed tau children.
    :type removed_tau_children:
    `list`[:class:`pm4py.objects.process_tree.obj.ProcessTree`]
    :return: Whether the operator is an OR operator.
    :rtype: `bool`
    """
    if len(non_tau_children) == 0:
        return True
    # get the leaf successors of the non-tau children
    # and get the leaf successors of the removed tau children
    # and see if there is a case where any of the removed tau children
    # don't appear with any of the non-tau children then we must have
    # an OR
    non_tau_successors_set = set(
        label
        for child in non_tau_children
        for label in get_non_operator_successor_labels(child)
    )
    removed_tau_children_set = set(
        label
        for child in removed_tau_children
        for label in get_non_operator_successor_labels(child)
    )
    for event_set in event_sets:
        frozen_set = event_set.to_frozenset()
        if non_tau_successors_set.intersection(
            frozen_set
        ) and not removed_tau_children_set.intersection(frozen_set):
            return True
    return False


def infer_or_gate_from_node(
    event_sets: set["ev.EventSet"],
    node: ProcessTree,
) -> None:
    """Method to infer the OR gates from a node.

    :param event_sets: The event sets.
    :type event_sets: `set`[:class:`tel2puml.events.EventSet`]
    :param node: The node.
    :type node: :class:`pm4py.objects.process_tree.obj.ProcessTree`
    """
    if node.operator is None:
        return
    if node.operator.value != Operator.PARALLEL.value:
        return

    tau_children = []
    non_tau_children = []
    for child in node.children:
        if child.operator is None:
            non_tau_children.append(child)
        elif child.operator.value == Operator.XOR.value:
            if any(str(grandchild) == "tau" for grandchild in child.children):
                tau_children.append(child)
            else:
                non_tau_children.append(child)

    if len(tau_children) > 0:
        removed_tau_children = []
        for child in tau_children:
            for grandchild in child.children:
                if str(grandchild) != "tau":
                    grandchild.parent = node
                    removed_tau_children.append(grandchild)
        if check_is_or_operator(
            event_sets, non_tau_children, removed_tau_children
        ):
            node.operator = Operator.OR
            if len(non_tau_children) > 1:
                node.children = [
                    *removed_tau_children,
                    ProcessTree(
                        Operator.PARALLEL,
                        node,
                        non_tau_children,
                    ),
                ]
            else:
                node.children = removed_tau_children + non_tau_children
            return
        # if not OR we must have an AND with a nested OR
        new_child_or = ProcessTree(
            Operator.OR,
            node,
            removed_tau_children,
        )

        node.children = non_tau_children + [new_child_or]


def filter_defunct_or_gates(
    process_tree: ProcessTree,
) -> None:
    """Method to filter the defunct OR gates from a process tree.

    :param process_tree: The process tree.
    :type process_tree: :class:`pm4py.objects.process_tree.obj.ProcessTree`
    """
    for node in process_tree.children:
        filter_defunct_or_gates(node)
        if node.operator is not None:
            if node.operator.value == Operator.OR.value:
                if node.parent.operator.value == Operator.OR.value:
                    node.parent.children.remove(node)
                    node.parent.children.extend(node.children)


def process_missing_and_gates(
    event_sets: set["ev.EventSet"],
    process_tree: ProcessTree,
) -> None:
    """Method to add missing AND gates to a process tree below OR gates.

    :param event_sets: The event sets.
    :type event_sets: `set`[:class:`tel2puml.events.EventSet`]
    :param process_tree: The process tree.
    :type process_tree: :class:`pm4py.objects.process_tree.obj.ProcessTree`
    """
    if (
        process_tree.operator is not None
        and process_tree.operator.value == Operator.OR.value
    ):
        universe_holder: set[str] = set()
        insoluble = False
        for child in process_tree.children:
            if child.operator is None:
                universe_holder.add(child.label)
            else:
                insoluble = True
                break
        universe = frozenset(universe_holder)

        if not insoluble:
            recursive_event_set = {
                event_set
                for event_set in ev.get_reduced_event_set(event_sets)
                if event_set.issubset(universe)
            }
            if universe in recursive_event_set:
                recursive_event_set.remove(universe)

            weighted_cover = get_weighted_cover(recursive_event_set, universe)

            if weighted_cover is not None:
                children = []
                for event_set in weighted_cover:
                    if len(event_set) > 1:
                        children.append(
                            ProcessTree(
                                Operator.PARALLEL,
                                process_tree,
                                [
                                    ProcessTree(
                                        label=event,
                                        parent=process_tree,
                                    )
                                    for event in event_set
                                ],
                            )
                        )
                    else:
                        (label,) = event_set
                        children.append(
                            ProcessTree(
                                label=label,
                                parent=process_tree,
                            )
                        )
                process_tree.children = children

    for child in process_tree.children:
        process_missing_and_gates(event_sets, child)


def get_process_tree_leaves(
    process_tree: ProcessTree,
) -> Generator[str, Any, None]:
    """Method to get the leaves of a process tree.

    :param process_tree: The process tree.
    :type process_tree: :class:`pm4py.objects.process_tree.obj.ProcessTree`
    :return: The leaves.
    :rtype: `Generator`[`str`, `Any`, `None`]
    """
    if process_tree.label is not None:
        if not isinstance(process_tree.label, str):
            raise ValueError("Label must be a string")
        yield process_tree.label
    else:
        for child in process_tree.children:
            yield from get_process_tree_leaves(child)


def get_matrix_of_event_counts_from_event_sets_and_leaves(
    event_sets: set["ev.EventSet"],
    leaves: Iterable[str],
) -> NDArray[np.int32]:
    """Method to get a matrix of event counts from event sets and leaves.

    :param event_sets: The event sets.
    :type event_sets: `set`[:class:`tel2puml.events.EventSet`]
    :param leaves: The leaves.
    :type leaves: `Iterable`[`str`]
    :return: The matrix of event counts.
    :rtype: :class:`numpy.ndarray`
    """
    records: list[list[int]] = []
    for event_set in event_sets:
        if event_set.has_intersection_with_event_types(
            leaves
        ):
            event_counts = (
                event_set.get_event_type_counts_for_given_event_types(
                        leaves
                )
            )
            records.append(
                [
                    event_counts.get(leaf, 0)
                    for leaf in leaves
                ]
            )
    return np.array(records, dtype=np.int32)


def order_matrix_of_event_counts(
    matrix: NDArray[np.int32]
) -> NDArray[np.int32]:
    """Method to order a matrix of event counts so that rows that have more of
    the same columns with non-zero values are grouped together.

    :param matrix: The matrix.
    :type matrix: :class:`numpy.ndarray`
    :return: The ordered matrix.
    :rtype: :class:`numpy.ndarray`
    """
    matrix_of_ones: NDArray[np.intp] = np.sign(matrix, dtype=np.intp)
    unique_rows, row_indices = np.unique(
        matrix_of_ones, return_inverse=True, axis=0
    )
    sorted_unique_indexes: NDArray[np.intp] = np.lexsort(
        unique_rows.T[::-1]
    )
    sorted_row_indices: list[int] = [
        int(index[0])
        for sorted_index in sorted_unique_indexes
        for index in np.argwhere(row_indices == sorted_index)
    ]
    return matrix[sorted_row_indices]


def check_is_ok_and_under_branch(
    event_sets: set["ev.EventSet"],
    leaves: Iterable[str],
) -> bool:
    """Method to check if the OR/AND operators are correct under a branch given
    the event sets and leaves. Checks to see if there is at least some positive
    evidence of OR/AND with no contradictions.

    :param event_sets: The event sets.
    :type event_sets: `set`[:class:`tel2puml.events.EventSet`]
    :param leaves: The leaves.
    :type leaves: `Iterable`[`str`]
    :return: Whether the OR/AND operators is correct.
    :rtype: `bool`
    """
    matrix = get_matrix_of_event_counts_from_event_sets_and_leaves(
        event_sets, leaves
    )
    if len(matrix) == 1:
        return True
    # order matrix of event counts so that rows that are similar in terms of
    # having non-zero columns are grouped together
    ordered_matrix = order_matrix_of_event_counts(matrix)
    # set any zeros to for division
    float_ordered_matrix = ordered_matrix.astype(float)
    float_ordered_matrix[ordered_matrix == 0] = np.nan
    # look for positive evidence of OR/AND. If there is any contradiction
    # or no evidence then return False
    evidence = False
    for i in range(1, len(float_ordered_matrix)):
        unique_vals = np.unique(
            float_ordered_matrix[i] / float_ordered_matrix[i - 1],
            equal_nan=True
        )
        if any(np.isnan(unique_vals)):
            if len(unique_vals) == 2:
                evidence = True
            elif len(unique_vals) > 2:
                return False
            else:
                continue
        else:
            if len(unique_vals) > 1:
                return False
            evidence = True
    return evidence


def assure_or_and_operators_are_correct_under_branch(
    process_tree: ProcessTree,
    event_sets: set["ev.EventSet"],
) -> None:
    """Method to assure that the OR and AND operators are correct under a
    branch operator.

    :param process_tree: The process tree.
    :type process_tree: :class:`pm4py.objects.process_tree.obj.ProcessTree`
    """
    if process_tree.operator is None:
        return
    if process_tree.operator.value == Operator.PARALLEL.value:
        leaves = set(get_process_tree_leaves(process_tree))
        if not check_is_ok_and_under_branch(event_sets, leaves):
            process_tree.operator = Operator.XOR
    if process_tree.operator.value == Operator.OR.value:
        process_tree.operator = Operator.XOR
    for child in process_tree.children:
        assure_or_and_operators_are_correct_under_branch(
            child, event_sets
        )


def flatten_nested_xor_operators(
    process_tree: ProcessTree,
) -> None:
    """Method to flatten nested XOR operators in a process tree.

    :param process_tree: The process tree.
    :type process_tree: :class:`pm4py.objects.process_tree.obj.ProcessTree`
    """
    if process_tree.operator is None:
        return
    for child in process_tree.children:
        flatten_nested_xor_operators(child)
    if process_tree.operator.value == Operator.XOR.value:
        new_children: list[ProcessTree] = []
        for child in process_tree.children:
            if child.operator is not None:
                if child.operator.value == Operator.XOR.value:
                    new_children.extend(child.children)
                    continue
            new_children.append(child)
        process_tree.children = new_children


def create_branch_tree_from_logic_gate_tree(
    logic_gate_tree: ProcessTree,
    event_sets: set["ev.EventSet"],
) -> ProcessTree:
    """Method to create a branch tree from a logic gate tree and check that the
    OR/AND operators are correct under the branch.

    :param logic_gate_tree: The logic gate tree.
    :type logic_gate_tree: :class:`pm4py.objects.process_tree.obj.ProcessTree`
    :param event_sets: The event sets.
    :type event_sets: `set`[:class:`tel2puml.events.EventSet`]
    :return: The logic gate tree with branch added.
    :rtype: :class:`pm4py.objects.process_tree.obj.ProcessTree`
    """
    old_tree = logic_gate_tree
    assure_or_and_operators_are_correct_under_branch(
        old_tree, event_sets
    )
    logic_gate_tree = ProcessTree(
        Operator.BRANCH,
        logic_gate_tree.parent,
        [old_tree],
    )
    old_tree.parent = logic_gate_tree
    flatten_nested_xor_operators(old_tree)
    return logic_gate_tree


def calculate_repeats_in_tree(
    event_sets: set["ev.EventSet"], logic_gate_tree: ProcessTree
) -> ProcessTree:
    """Method to find the repeats in a process tree.

    :param event_sets: The event sets.
    :type event_sets: `set`[:class:`tel2puml.events.EventSet`]
    :return: The process tree with repeats.
    :rtype: :class:`pm4py.objects.process_tree.obj.ProcessTree`
    """
    counts = ev.get_event_set_counts(event_sets)
    for count in counts.values():
        if len(count) > 1:
            logic_gate_tree = create_branch_tree_from_logic_gate_tree(
                logic_gate_tree, event_sets
            )
            break

    logic_gate_tree = update_tree_with_repeat_logic(
        event_sets, logic_gate_tree
    )
    logic_gate_tree = remove_defunct_sequence_logic(logic_gate_tree)

    return logic_gate_tree


def update_tree_with_repeat_logic(
    event_sets: set["ev.EventSet"], node: ProcessTree
) -> ProcessTree:
    """Method to update a tree with repeat logic.

    :param event_sets: The event sets.
    :type event_sets: `set`[:class:`tel2puml.events.EventSet`]
    :param node: The node.
    :type node: :class:`pm4py.objects.process_tree.obj.ProcessTree`
    """
    if node.operator is None:
        counts = ev.get_event_set_counts(event_sets).get(node.label, set())
        if len(counts) == 1 and (count := counts.pop()) > 1:
            return ProcessTree(Operator.PARALLEL, node.parent, [node] * count)
    else:
        node.children = [
            update_tree_with_repeat_logic(event_sets, child)
            for child in node.children
        ]

    return node


def remove_defunct_sequence_logic(node: ProcessTree) -> Any | ProcessTree:
    """Method to remove defunct sequence logic from a tree.

    :param node: The node.
    :type node: :class:`pm4py.objects.process_tree.obj.ProcessTree`
    :return: The node.
    :rtype: :class:`pm4py.objects.process_tree.obj.ProcessTree`"""
    if node.operator is not None:
        if node.operator == Operator.SEQUENCE:
            return remove_defunct_sequence_logic(node.children[0])

        node.children = [
            remove_defunct_sequence_logic(child) for child in node.children
        ]

    return node



class LogicRelationships(TypedDict):
    """Typed dictionary to represent the logic relationships between the
    event sets."""
    OR: set[frozenset[T]]
    PARALLEL: set[frozenset[T]]
    XOR: set[frozenset[T]]
    AMBIGUOUS: set[frozenset[T]]
    

OPERATORS = {
    "OR": Operator.OR,
    "PARALLEL": Operator.PARALLEL,
    "XOR": Operator.XOR,
    "AMBIGUOUS": Operator.AMBIGUOUS,
}


def calculate_logic_gate_from_relationship_array(
    relationship_array: NDArray[np.int32],
) -> Literal["OR", "PARALLEL", "XOR"]:
    """Method to calculate the logic gate from a relationship array.

    :param relationship_array: The relationship array.
    :type relationship_array: :class:`numpy.ndarray`
    :return: The logic gate.
    :rtype: `Literal`["OR", "PARALLEL", "XOR"]
    """
    array_to_check = np.unique(relationship_array[np.sum(
        relationship_array, axis=1
    ) > 0], axis=0)
    if len(array_to_check) == 1:
        return "PARALLEL"
    if np.sum(array_to_check) == 2:
        return "XOR"
    if np.sum(array_to_check) == 3:
        return "AMBIGUOUS"
    return "OR"


def get_logic_relationships_from_event_sets(
    event_sets: set["ev.EventSet"],
) -> LogicRelationships:
    reduced_event_set_records = [
        {event: 1 for event in reduced_event_set}
        for reduced_event_set in
        {event_set.to_frozenset() for event_set in event_sets}
    ]
    relationship_df = pd.DataFrame.from_records(
        reduced_event_set_records
    ).fillna(0)
    num_cols = relationship_df.shape[1]
    logic_relationships: LogicRelationships = LogicRelationships(
        OR=set(),
        PARALLEL=set(),
        XOR=set(),
        AMBIGUOUS=set(),
    )
    for col_index_1 in range(num_cols - 1):
        for col_index_2 in range(col_index_1 + 1, num_cols):
            col_name_1 = relationship_df.columns[col_index_1]
            col_name_2 = relationship_df.columns[col_index_2]
            relationship_array = relationship_df[[col_name_1, col_name_2]].to_numpy()
            logic_gate = calculate_logic_gate_from_relationship_array(relationship_array)
            logic_relationships[logic_gate].add(
                frozenset([col_name_1, col_name_2])
            )
    return logic_relationships



def find_root_logic_operator(
    logic_relationships: LogicRelationships,
    all_members: set[T],
) -> Operator:
    for logic_gate, logic_sets in logic_relationships.items():
        case_intersection = all_members.intersection(
            {member for logic_set in logic_sets for member in logic_set}
        )
        if len(case_intersection) == len(all_members):
            return OPERATORS[logic_gate]
    to_remove: set[frozenset[T]] = set()
    for member in logic_relationships["OR"]:
        if any(member.intersection(logic_set) for logic_set in logic_relationships["AMBIGUOUS"]):
            logic_relationships["AMBIGUOUS"].add(member)
            to_remove.add(member)
    logic_relationships["OR"].difference_update(to_remove)
    if {member for logic_set in logic_relationships["AMBIGUOUS"] for member in logic_set} == all_members:
        return Operator.AMBIGUOUS
    raise RuntimeError("No root logic operator found")


def get_logic_tree_from_relationships(
    logic_relationships: LogicRelationships,
    all_members: set[T],
    operator: Operator,
) -> ProcessTree:
    """Method to get the logic tree from event sets.

    :param event_sets: The event sets.
    :type event_sets: `set`[:class:`tel2puml.events.EventSet`]
    :return: The logic tree.
    :rtype: :class:`pm4py.objects.process_tree.obj.ProcessTree`
    """
    logic_gate_intersections: dict[str, set[T]] = {}
    for logic_gate, logic_sets in logic_relationships.items():
        if OPERATORS[logic_gate] != operator:
            logic_gate_intersections[logic_gate] = all_members.intersection(
                {member for logic_set in logic_sets for member in logic_set}
            )
    parent = ProcessTree(
        operator=operator,
    )
    children: list[ProcessTree] = []
    for member in all_members.difference(
        {
            member
            for logic_gate_intersection in logic_gate_intersections.values()
            for member in logic_gate_intersection
        }
    ):
        children.append(ProcessTree(
            parent=parent,
            label=member,
        ))
    for logic_gate, logic_gate_intersection in logic_gate_intersections.items():
        # get clustered members of intersection
        graph = nx.Graph()
        graph.add_edges_from(
            [
                member
                for member in logic_relationships[logic_gate]
                if member.intersection(logic_gate_intersection)
            ]
        )
        for member_set in nx.connected_components(graph):
            input_logic_relationships = LogicRelationships(
                OR={logic_set for logic_set in logic_relationships["OR"] if logic_set.issubset(member_set)},
                PARALLEL={logic_set for logic_set in logic_relationships["PARALLEL"] if logic_set.issubset(member_set)},
                XOR={logic_set for logic_set in logic_relationships["XOR"] if logic_set.issubset(member_set)},
            )
            children.append(get_logic_tree_from_relationships(
                logic_relationships=input_logic_relationships,
                all_members=set(member_set),
                operator=OPERATORS[logic_gate],
            ))
    for child in children:
        child.parent = parent
    parent.children = children
    return parent
    

def get_logic_tree_from_event_sets(
    event_sets: set["ev.EventSet"],
) -> ProcessTree:
    """Method to get the logic tree from event sets.

    :param event_sets: The event sets.
    :type event_sets: `set`[:class:`tel2puml.events.EventSet`]
    :return: The logic tree.
    :rtype: :class:`pm4py.objects.process_tree.obj.ProcessTree`
    """
    all_members = {member for event_set in event_sets for member in event_set.to_frozenset()}
    if len(all_members) == 1:
        return ProcessTree(
            label=all_members.pop(),
        )
    logic_relationships = get_logic_relationships_from_event_sets(event_sets)
    root_operator = find_root_logic_operator(logic_relationships, all_members)
    logic_tree = get_logic_tree_from_relationships(
        logic_relationships=logic_relationships,
        all_members=all_members,
        operator=root_operator,
    )
    ensure_or_replaced_with_and(logic_tree, event_sets)
    return logic_tree
    

def ensure_or_replaced_with_and(
    process_tree: ProcessTree,
    event_sets: set["ev.EventSet"],
) -> None:
    """Method to ensure that OR operators are replaced with AND operators.

    :param process_tree: The process tree.
    :type process_tree: :class:`pm4py.objects.process_tree.obj.ProcessTree`
    """
    if process_tree.operator is not None:
        # if process_tree.operator.value == Operator.AMBIGUOUS.value:
        if process_tree.operator.value == Operator.OR.value:
            children_leaves = [
                set(get_non_operator_successor_labels(child))
                for child in process_tree.children
            ]
            all_leaves = set(leaf for leaves in children_leaves for leaf in leaves)
            event_sets_with_intersection_with_leaves = {
                event_set
                for event_set in event_sets
                if event_set.has_intersection_with_event_types(all_leaves)
            }
            has_intersection_all = [False] * len(children_leaves)
            for i, leaves in enumerate(children_leaves):
                if not all(leaves.intersection(event_set.to_frozenset()) for event_set in event_sets_with_intersection_with_leaves):
                    break
                has_intersection_all[i] = True
            if all(has_intersection_all):
                process_tree.operator = Operator.PARALLEL
            else:
                process_tree.operator = Operator.OR
    for child in process_tree.children:
        ensure_or_replaced_with_and(child, event_sets)