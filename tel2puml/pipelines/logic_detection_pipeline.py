"""Module to detect the logic in a sequence of PV events.
"""
from itertools import product, permutations
from uuid import uuid4
from datetime import datetime, timedelta
from typing import Any, Generator

from numpy import ndarray
import numpy as np
import pandas as pd
from pm4py import (
    discover_process_tree_inductive, ProcessTree,
    format_dataframe
)
from pm4py.objects.process_tree.obj import Operator

from test_event_generator.solutions.graph_solution import GraphSolution


class Event:
    def __init__(
        self,
        event_type: str,
    ) -> None:
        self.event_type = event_type
        self.edge_counts_per_data_point: dict[
            tuple[str, str], dict[str, int]
        ] = {}
        self.event_sets: set[frozenset[str]] = set()
        self.occured_edges: list[list[tuple[str, str]]] = []
        self.conditional_count_matrix: ndarray | None = None
        self._condtional_probability_matrix: ndarray | None = None
        self._update_since_conditional_probability_matrix = False
        self._logic_gate_tree: ProcessTree | None = None
        self._update_since_logic_gate_tree = False

    @property
    def logic_gate_tree(self) -> ProcessTree:
        if self._update_since_logic_gate_tree:
            self._logic_gate_tree = self.calculate_logic_gates()
        return self._logic_gate_tree

    def calculate_logic_gates(
        self
    ) -> ProcessTree:
        process_tree = self.calculate_process_tree_from_event_sets()
        logic_gate_tree = self.reduce_process_tree_to_preferred_logic_gates(
            process_tree
        )
        return logic_gate_tree

    def update_event_sets(
        self,
        events: list[str],
    ) -> None:
        self.event_sets.add(frozenset(events))
        self._update_since_logic_gate_tree = True

    def create_augmented_data_from_event_sets(
        self,
    ) -> Generator[dict[str, Any], Any, None]:
        for event_set in self.event_sets:
            yield from self.created_augemented_data_from_event_set(
                event_set
            )

    def created_augemented_data_from_event_set(
        self,
        event_set: frozenset[str],
    ) -> Generator[dict[str, Any], Any, None]:
        for permutation in permutations(
            event_set, len(event_set)
        ):
            case_id = str(uuid4())
            yield from self.create_data_from_event_sequence(
                [self.event_type, *permutation],
                case_id,
                start_time=datetime.now(),
            )

    @staticmethod
    def create_data_from_event_sequence(
        event_sequence: list[str],
        case_id: str,
        start_time: datetime = datetime.now(),
    ) -> Generator[dict[str, Any], Any, None]:
        for i, event in enumerate(event_sequence):
            yield {
                "case_id": case_id,
                "activity": event,
                "timestamp": start_time + timedelta(seconds=i),
            }

    def calculate_process_tree_from_event_sets(
        self,
    ) -> ProcessTree:
        augmented_dataframe = pd.DataFrame(
            self.create_augmented_data_from_event_sets()
        )
        event_log = format_dataframe(
            augmented_dataframe, case_id='case_id', activity_key='activity',
            timestamp_key='timestamp'
        )
        process_tree = discover_process_tree_inductive(
            event_log
        )
        return process_tree

    @staticmethod
    def reduce_process_tree_to_preferred_logic_gates(
        process_tree: ProcessTree,
    ) -> ProcessTree:
        # remove first event and get subsequent tree
        logic_gate_tree: ProcessTree = process_tree.children[1]
        # calculate OR gates
        Event.process_or_gates(logic_gate_tree)
        return logic_gate_tree

    @staticmethod
    def process_or_gates(
        process_tree: ProcessTree,
    ):
        Event.get_extended_or_gates_from_process_tree(process_tree)
        Event.filter_defunct_or_gates(process_tree)

    @staticmethod
    def get_extended_or_gates_from_process_tree(
        process_tree: ProcessTree,
    ) -> None:
        Event.infer_or_gate_from_node(process_tree)
        for node in process_tree.children:
            Event.get_extended_or_gates_from_process_tree(node)

    @staticmethod
    def infer_or_gate_from_node(
        node: ProcessTree,
    ) -> None:
        if node.operator.name != "PARALLEL":
            return
        for counter, child in enumerate(node.children):
            if child.operator is None:
                continue
            if child.operator.name == "XOR":
                if any(
                    str(child_of_child) == "tau"
                    for child_of_child in child.children
                ):
                    node.operator == Operator.OR
                    node_new_children = []
                    for child_of_child in child.children:
                        if str(child_of_child) != "tau":
                            child_of_child.parent = node
                            node_new_children.append(child_of_child)
                    if len(node.children[counter + 1:]) > 1:
                        end_children = [
                            ProcessTree(
                                Operator.PARALLEL,
                                node,
                                node.children[counter + 1:]
                            )
                        ]
                    else:
                        end_children = node.children[counter + 1:]
                    node.children = [
                        *node.children[:counter],
                        *node_new_children,
                        *end_children
                    ]
                    break

    @staticmethod
    def filter_defunct_or_gates(
        process_tree: ProcessTree,
    ) -> None:
        for node in process_tree.children:
            Event.filter_defunct_or_gates(node)
            if node.operator is not None:
                if node.operator.name == "OR":
                    if node.parent.operator.name == "OR":
                        node.parent.children.remove(node)
                        node.parent.children.extend(node.children)

    def update_with_data_point(
        self,
        edge_tuples: list[tuple[str, str]],
    ) -> None:
        data_point_edges = set()
        for edge_tuple in edge_tuples:
            self.update_with_edge_tuple_and_data_point_edges(
                edge_tuple,
                data_point_edges
            )
        self.update_conditional_count_matrix(data_point_edges)
        self._update_since_conditional_probability_matrix = True

    def update_with_edge_tuple_and_data_point_edges(
        self,
        edge_tuple: tuple[str, str],
        data_point_edges: set[tuple[str, str]],
    ) -> None:
        if edge_tuple not in self.edge_counts_per_data_point:
            self.add_new_edge_to_edge_counts_per_data_point(edge_tuple)
            self.add_new_edge_to_conditional_count_matrix()
        self.update_edge_counts_with_edge_tuple(edge_tuple, data_point_edges)

    def add_new_edge_to_edge_counts_per_data_point(
        self,
        edge_tuple: tuple[str, str],
    ) -> None:
        self.edge_counts_per_data_point[edge_tuple] = {
            "data_count": 0,
            "total_count": 0,
            "index": len(self.edge_counts_per_data_point),
        }

    def add_new_edge_to_conditional_count_matrix(self) -> None:
        if self.conditional_count_matrix is None:
            self.conditional_count_matrix = np.array([[0]])
            return
        self.conditional_count_matrix = np.pad(
            self.conditional_count_matrix,
            ((0, 1), (0, 1)),
            mode="constant",
            constant_values=0,
        )

    def update_edge_counts_with_edge_tuple(
        self,
        edge_tuple: tuple[str, str],
        data_point_edges: set[tuple[str, str]],
    ):
        if edge_tuple not in data_point_edges:
            self.edge_counts_per_data_point[edge_tuple]["data_count"] += 1
            data_point_edges.add(edge_tuple)
        self.edge_counts_per_data_point[edge_tuple]["total_count"] += 1

    def update_conditional_count_matrix(
        self,
        data_point_edges: set[tuple[str, str]],
    ):
        indexes = [
            self.edge_counts_per_data_point[edge_tuple]["index"]
            for edge_tuple in data_point_edges
        ]
        self.conditional_count_matrix[
            tuple(zip(*product(indexes, repeat=2)))
        ] += 1

    @property
    def conditional_probability_matrix(self) -> ndarray | None:
        if self._update_since_conditional_probability_matrix:
            self._condtional_probability_matrix = (
                self._calculate_conditional_probability_matrix()
            )
            self._update_since_conditional_probability_matrix = False
        return self._condtional_probability_matrix

    def _calculate_conditional_probability_matrix(self) -> ndarray:
        return self.conditional_count_matrix / np.diag(
            self.conditional_count_matrix
        )


def detect_logic(events: list[dict]):
    """This function detects the logic in a sequence of PV events.

    :param events: A sequence of PV events.
    :type events: `list`[:class:`dict`]
    """
    pass


def get_graph_solutions_from_events(events: list[dict]) -> list[GraphSolution]:
    """This function gets the graph solutions from a sequence of PV events.

    :param events: A sequence of PV events.
    :type events: `list`[:class:`dict`]
    """
    clustered_events = cluster_events_by_job_id(events)
    graph_solutions = [
        GraphSolution.from_event_list(job_events)
        for job_events in clustered_events.values()
    ]
    return graph_solutions


def cluster_events_by_job_id(events: list[dict]) -> dict[str, list[dict]]:
    """This function clusters PV events into jobs.

    :param events: A sequence of PV events.
    :type events: `list`[:class:`dict`]
    """
    events_by_job_id: dict[str, list[dict]] = {}
    for event in events:
        job_id = event["jobId"]
        if job_id not in events_by_job_id:
            events_by_job_id[job_id] = []
        events_by_job_id[job_id].append(event)
    return events_by_job_id
