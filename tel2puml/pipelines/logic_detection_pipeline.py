"""Module to detect the logic in a sequence of PV events.
"""

from itertools import product, permutations
from uuid import uuid4
from datetime import datetime, timedelta
from typing import Any, Generator, Iterable
from copy import deepcopy
from enum import Enum

from numpy import ndarray
import numpy as np
import pandas as pd
from pm4py import (
    discover_process_tree_inductive,
    ProcessTree,
    format_dataframe,
)

from test_event_generator.solutions.graph_solution import GraphSolution
from test_event_generator.solutions.event_solution import EventSolution

from tel2puml.utils import get_weighted_cover
from tel2puml.tel2puml_types import PVEvent
from tel2puml.detect_loops import Loop


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

    def __str__(self):
        """
        Provides a string representation of the current operator

        :return: String representation of the process tree.
        :rtype: `str`
        """
        return self.value

    def __repr__(self):
        """
        Provides a string representation of the current operator

        :return: String representation of the process tree.
        :rtype: `str`
        """
        return self.value


class EventSet(dict[str, int]):
    """Class to represent a set of unique events and their counts.

    :param events: The events.
    :type events: `list`[`str`]
    """

    def __init__(
        self,
        events: list[str],
    ) -> None:
        """Constructor method."""
        super().__init__()
        for event in events:
            self[event] = self.get(event, 0) + 1

    def __key(self):
        return tuple((k, self[k]) for k in sorted(self))

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return self.__key() == other.__key()

    def to_frozenset(self) -> frozenset[str]:
        """Method to get the events as a frozenset.

        :return: The events as a frozenset.
        :rtype: `frozenset`[`str`]
        """
        return frozenset(self.keys())

    def get_repeated_events(self) -> dict[str, int]:
        """Method to get the repeated events.

        :return: The repeated events.
        :rtype: `dict`[`str`, `int`]
        """
        return {event: count for event, count in self.items() if count > 1}


class Event:
    """Class to detect the logic in a sequence of PV events.

    :param event_type: The type of event.
    :type event_type: `str`
    """

    def __init__(
        self,
        event_type: str,
    ) -> None:
        """Constructor method."""
        self.event_type = event_type
        self.edge_counts_per_data_point: dict[
            tuple[str, str], dict[str, int]
        ] = {}
        self.event_sets: set[EventSet] = set()
        self.occured_edges: list[list[tuple[str, str]]] = []
        self.conditional_count_matrix: ndarray | None = None
        self._condtional_probability_matrix: ndarray | None = None
        self._update_since_conditional_probability_matrix = False
        self._logic_gate_tree: ProcessTree | None = None
        self._update_since_logic_gate_tree = False

    def save_vis_logic_gate_tree(
        self,
        output_file_path: str,
    ) -> None:
        """This method saves the logic gate tree as a visualisation.

        :param output_file_path: The path to save the visualisation.
        :type output_file_path: `str`
        """
        if self.logic_gate_tree is None:
            raise ValueError(
                "There has been no data to calculate logic gates."
            )
        logic_gate_tree = deepcopy(self.logic_gate_tree)
        start_event = ProcessTree(
            label=self.event_type,
        )
        start_event.children = [logic_gate_tree]
        logic_gate_tree.parent = start_event
        graph_solution = GraphSolution()
        Event.update_graph_solution_with_event_solution_from_process_node(
            start_event,
            graph_solution,
        )
        network_x_graph = GraphSolution.create_networkx_graph_from_nodes(
            list(graph_solution.events.values()),
            link_func=lambda x: x.get_post_event_edge_tuples(),
        )
        GraphSolution.get_graphviz_plot(network_x_graph).savefig(
            output_file_path
        )

    @staticmethod
    def update_graph_solution_with_event_solution_from_process_node(
        node: ProcessTree,
        graph_solution: GraphSolution,
    ) -> EventSolution:
        """Recursive method to create an event solution and update a graph
        solution with the tree of event solutions from a process node.

        :param node: The process node.
        :type node: :class:`pm4py.objects.process_tree.obj.ProcessTree`
        :param graph_solution: The graph solution.
        :type graph_solution:
        :class:`test_event_generator.solutions.graph_solution.GraphSolution`
        """
        event_solution = EventSolution(
            meta_data={
                "EventType": (
                    node.label
                    if node.label is not None
                    else node.operator.value
                )
            },
        )
        for child in node.children:
            event_solution.add_post_event(
                Event.update_graph_solution_with_event_solution_from_process_node(  # noqa: E501
                    child, graph_solution
                )
            )
        graph_solution.add_event(event_solution)
        return event_solution

    @property
    def logic_gate_tree(self) -> ProcessTree:
        """This property gets the logic gate tree. If the logic gate tree has
        not been calculated, it calculates it.

        :return: The logic gate tree.
        :rtype: :class:`pm4py.objects.process_tree.obj.ProcessTree`"""
        if self._update_since_logic_gate_tree:
            self._logic_gate_tree = self.calculate_logic_gates()
            self._update_since_logic_gate_tree = False
        return self._logic_gate_tree

    @logic_gate_tree.setter
    def logic_gate_tree(self, value: ProcessTree) -> None:
        """This property sets the logic gate tree.

        :param value: The logic gate tree.
        :type value: :class:`pm4py.objects.process_tree.obj.ProcessTree`
        """
        self._logic_gate_tree = value
        self._update_since_logic_gate_tree = False

    def calculate_logic_gates(self) -> ProcessTree:
        """This method calculates the logic gates from the event sets.

        :return: The logic gate tree.
        :rtype: :class:`pm4py.objects.process_tree.obj.ProcessTree`
        """
        process_tree = self.calculate_process_tree_from_event_sets()
        logic_gate_tree = self.reduce_process_tree_to_preferred_logic_gates(
            process_tree
        )
        logic_gate_tree_with_repeats = self.calculate_repeats_in_tree(
            logic_gate_tree
        )

        return logic_gate_tree_with_repeats

    def update_event_sets(
        self,
        events: list[str],
    ) -> None:
        """This method updates the event sets for a given list of events as
        strings.

        :param events: A list of events as strings.
        :type events: `list`[`str`]
        """
        if len(events) == 0:
            return

        self.event_sets.add(EventSet(events))

        self._update_since_logic_gate_tree = True

    def get_reduced_event_set(self) -> set[frozenset[str]]:
        """This method reduces the event set to a list of unique events.

        :return: The reduced event set.
        :rtype: `list`[`str`]
        """
        return {event_set.to_frozenset() for event_set in self.event_sets}

    def get_event_set_counts(self) -> dict[str, set[int]]:
        """Method to get the event set counts.

        :return: The event set counts.
        :rtype: `dict`[`str`, `set`[`int`]]
        """
        event_set_counts: dict[str, set[int]] = {}
        for event_set in self.event_sets:
            for event, count in event_set.items():
                if event in event_set_counts:
                    event_set_counts[event].add(count)
                else:
                    event_set_counts[event] = {count}
        return event_set_counts

    def remove_event_type_from_event_sets(self, event_type: str) -> None:
        """Method to remove an event type from the event sets.

        :param event_type: The event type.
        :type event_type: `str`
        """
        self.event_sets = {
            event_set
            for event_set in self.event_sets
            if event_type not in event_set
        }

        self._update_since_logic_gate_tree = True

    def create_augmented_data_from_event_sets(
        self,
    ) -> Generator[dict[str, Any], Any, None]:
        """Method to create augmented data from the event sets and yields
        the data.

        :return: The augmented data.
        :rtype: `Generator`[`dict`[`str`, `Any`], `Any`, `None`]"""
        for reduced_event_set in self.get_reduced_event_set():
            yield from self.create_augmented_data_from_reduced_event_set(
                reduced_event_set
            )

    def create_augmented_data_from_reduced_event_set(
        self,
        reduced_event_set: frozenset[str],
    ) -> Generator[dict[str, Any], Any, None]:
        """Method to create augmented data from a single event set then
        yielding the augmented data.

        :param reduced_event_set: The reduced event set.
        :type reduced_event_set: `frozenset`[`str`]
        :return: The augmented data.
        :rtype: `Generator`[`dict`[`str`, `Any`], `Any`, `None`]
        """
        for permutation in permutations(
            reduced_event_set, len(reduced_event_set)
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
        self,
    ) -> ProcessTree:
        """This method calculates the pm4py process tree from the event sets.

        :return: The process tree.
        :rtype: :class:`pm4py.objects.process_tree.obj.ProcessTree`
        """
        augmented_dataframe = pd.DataFrame(
            self.create_augmented_data_from_event_sets()
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
        self,
        process_tree: ProcessTree,
    ) -> ProcessTree:
        """This method reduces a process tree to the preferred logic gates by
        removing the first event and getting the subsequent tree and then
        calculating the OR gates and adding missing AND gates.

        :param process_tree: The process tree.
        :type process_tree: :class:`pm4py.objects.process_tree.obj.ProcessTree`
        :return: The logic gate tree.
        :rtype: :class:`pm4py.objects.process_tree.obj.ProcessTree`
        """
        # remove first event and get subsequent tree
        logic_gate_tree: ProcessTree = process_tree.children[1]
        # calculate OR gates
        Event.process_or_gates(logic_gate_tree)
        # process missing AND gates
        try:
            tree_copy = deepcopy(logic_gate_tree)
            self.process_missing_and_gates(tree_copy)
            return tree_copy
        except Exception:
            return logic_gate_tree

    @staticmethod
    def process_or_gates(
        process_tree: ProcessTree,
    ) -> None:
        """Static method to process the OR gates in a process tree by extending
        the OR gates and filtering the defunct OR gates.
        """
        Event.get_extended_or_gates_from_process_tree(process_tree)
        Event.filter_defunct_or_gates(process_tree)

    @staticmethod
    def get_extended_or_gates_from_process_tree(
        process_tree: ProcessTree,
    ) -> None:
        """Static method to get the extended OR gates from a process tree by
        inferring the OR gates from a node.

        :param process_tree: The process tree.
        :type process_tree: :class:`pm4py.objects.process_tree.obj.ProcessTree`
        """
        Event.infer_or_gate_from_node(process_tree)
        for node in process_tree.children:
            Event.get_extended_or_gates_from_process_tree(node)

    @staticmethod
    def infer_or_gate_from_node(
        node: ProcessTree,
    ) -> None:
        """Static method to infer the OR gates from a node.

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
                if any(
                    str(grandchild) == "tau"
                    for grandchild in child.children
                ):
                    tau_children.append(child)
                else:
                    non_tau_children.append(child)

        if len(tau_children) > 0:
            node.operator = Operator.OR
            removed_tau_children = []
            for child in tau_children:
                for grandchild in child.children:
                    if str(grandchild) != "tau":
                        grandchild.parent = node
                        removed_tau_children.append(grandchild)

            if len(non_tau_children) == 0:
                node.children = removed_tau_children
                return

            updated_children = []

            updated_children.extend(removed_tau_children)

            if len(non_tau_children) == 1:
                updated_children.append(non_tau_children[0])
            else:
                updated_children.append(
                    ProcessTree(
                        Operator.PARALLEL,
                        node,
                        non_tau_children,
                    )
                )

            node.children = updated_children

    @staticmethod
    def filter_defunct_or_gates(
        process_tree: ProcessTree,
    ) -> None:
        """Static method to filter the defunct OR gates from a process tree.

        :param process_tree: The process tree.
        :type process_tree: :class:`pm4py.objects.process_tree.obj.ProcessTree`
        """
        for node in process_tree.children:
            Event.filter_defunct_or_gates(node)
            if node.operator is not None:
                if node.operator.value == Operator.OR.value:
                    if node.parent.operator.value == Operator.OR.value:
                        node.parent.children.remove(node)
                        node.parent.children.extend(node.children)

    def process_missing_and_gates(
        self,
        process_tree: ProcessTree,
    ) -> None:
        """Method to add missing AND gates to a process tree below OR gates.

        :param process_tree: The process tree.
        :type process_tree: :class:`pm4py.objects.process_tree.obj.ProcessTree`
        """
        if (
                process_tree.operator is not None
                and process_tree.operator.value == Operator.OR.value
        ):
            labels = []
            insoluble = False
            for child in process_tree.children:
                if child.operator is None:
                    labels.append(child.label)
                else:
                    insoluble = True
                    break

            if not insoluble:
                universe = set(labels)
                reduced_event_set = self.get_reduced_event_set()
                reduced_event_set.remove(universe)

                weighted_cover = get_weighted_cover(
                    reduced_event_set,
                    universe
                )

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
                            label, = event_set
                            children.append(
                                ProcessTree(
                                    label=label,
                                    parent=process_tree,
                                )
                            )
                    process_tree.children = children

        for child in process_tree.children:
            self.process_missing_and_gates(child)

    def calculate_repeats_in_tree(
        self, logic_gate_tree: ProcessTree
    ) -> ProcessTree:
        """Method to find the repeats in a process tree.

        :return: The process tree with repeats.
        :rtype: :class:`pm4py.objects.process_tree.obj.ProcessTree`
        """
        counts = self.get_event_set_counts()
        for count in counts.values():
            if len(count) > 1:
                logic_gate_tree = ProcessTree(
                    Operator.BRANCH,
                    logic_gate_tree.parent,
                    [logic_gate_tree],
                )
                break

        logic_gate_tree = self.update_tree_with_repeat_logic(logic_gate_tree)
        logic_gate_tree = Event.remove_defunct_sequence_logic(logic_gate_tree)

        return logic_gate_tree

    def update_tree_with_repeat_logic(self, node: ProcessTree):
        """Method to update a tree with repeat logic.

        :param node: The node.
        :type node: :class:`pm4py.objects.process_tree.obj.ProcessTree`
        """
        if node.operator is None:
            counts = self.get_event_set_counts().get(node.label, set())
            if len(counts) == 1 and (count := counts.pop()) > 1:
                return ProcessTree(
                    Operator.PARALLEL, node.parent, [node] * count
                )
        else:
            node.children = [
                self.update_tree_with_repeat_logic(child)
                for child in node.children
            ]

        return node

    @staticmethod
    def remove_defunct_sequence_logic(node: ProcessTree):
        """Method to remove defunct sequence logic from a tree."""
        if node.operator is not None:
            if node.operator == Operator.SEQUENCE:
                return Event.remove_defunct_sequence_logic(node.children[0])

            node.children = [
                Event.remove_defunct_sequence_logic(child)
                for child in node.children
            ]

        return node

    # -----------------Conditional methods-----------------
    """
    NOTE: The following methods are for the conditional probability matrix and
    are not used currently and may be removed but are kept for now for
    potential future use.
    """

    def update_with_data_point(
        self,
        edge_tuples: list[tuple[str, str]],
    ) -> None:
        """Method to update the event with a data point.

        :param edge_tuples: The edge tuples.
        :type edge_tuples: `list`[`tuple`[`str`, `str`]]
        """
        data_point_edges = set()
        for edge_tuple in edge_tuples:
            self.update_with_edge_tuple_and_data_point_edges(
                edge_tuple, data_point_edges
            )
        self.update_conditional_count_matrix(data_point_edges)
        self._update_since_conditional_probability_matrix = True

    def update_with_edge_tuple_and_data_point_edges(
        self,
        edge_tuple: tuple[str, str],
        data_point_edges: set[tuple[str, str]],
    ) -> None:
        """Method to update the event with an edge tuple and data point edges.
        This method adds a new edge to the edge counts per data point
        dictionary and a new edge to the conditional count matrix if it does
        not exist and then updates the edge counts with the edge tuple and
        data point edges and adds a new edge to the conditional count matrix.

        :param edge_tuple: The edge tuple.
        :type edge_tuple: `tuple`[`str`, `str`]
        :param data_point_edges: The data point edges.
        :type data_point_edges: `set`[`tuple`[`str`, `str`]]
        """
        if edge_tuple not in self.edge_counts_per_data_point:
            self.add_new_edge_to_edge_counts_per_data_point(edge_tuple)
            self.add_new_edge_to_conditional_count_matrix()
        self.update_edge_counts_with_edge_tuple(edge_tuple, data_point_edges)

    def add_new_edge_to_edge_counts_per_data_point(
        self,
        edge_tuple: tuple[str, str],
    ) -> None:
        """Method to add a new edge to the edge counts per data point
        dictionary.

        :param edge_tuple: The edge tuple.
        :type edge_tuple: `tuple`[`str`, `str`]
        """
        self.edge_counts_per_data_point[edge_tuple] = {
            "data_count": 0,
            "total_count": 0,
            "index": len(self.edge_counts_per_data_point),
        }

    def add_new_edge_to_conditional_count_matrix(self) -> None:
        """Method to add a new edge to the conditional count matrix. This
        method pads the conditional count matrix with a new row and column of
        zeros. If the conditional count matrix is None, it creates a new
        conditional count matrix with a single zero.
        """
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
    ) -> None:
        """Method to update the edge counts with an edge tuple and data point
        edges.

        :param edge_tuple: The edge tuple.
        :type edge_tuple: `tuple`[`str`, `str`]
        :param data_point_edges: The data point edges.
        :type data_point_edges: `set`[`tuple`[`str`, `str`]]
        """
        if edge_tuple not in data_point_edges:
            self.edge_counts_per_data_point[edge_tuple]["data_count"] += 1
            data_point_edges.add(edge_tuple)
        self.edge_counts_per_data_point[edge_tuple]["total_count"] += 1

    def update_conditional_count_matrix(
        self,
        data_point_edges: set[tuple[str, str]],
    ) -> None:
        """Method to update the conditional count matrix with a set of data
        point edges.

        :param data_point_edges: The data point edges.
        :type data_point_edges: `set`[`tuple`[`str`, `str`]]
        """
        indexes = [
            self.edge_counts_per_data_point[edge_tuple]["index"]
            for edge_tuple in data_point_edges
        ]
        self.conditional_count_matrix[
            tuple(zip(*product(indexes, repeat=2)))
        ] += 1

    @property
    def conditional_probability_matrix(self) -> ndarray | None:
        """This property gets the conditional probability matrix. If the
        conditional probability matrix has not been calculated, it calculates
        it.

        :return: The conditional probability matrix.
        :rtype: `ndarray` | `None`
        """
        if self._update_since_conditional_probability_matrix:
            self._condtional_probability_matrix = (
                self._calculate_conditional_probability_matrix()
            )
            self._update_since_conditional_probability_matrix = False
        return self._condtional_probability_matrix

    def _calculate_conditional_probability_matrix(self) -> ndarray:
        """This method calculates the conditional probability matrix.

        :return: The conditional probability matrix.
        :rtype: `ndarray`
        """
        return self.conditional_count_matrix / np.diag(
            self.conditional_count_matrix
        )

    # -----------------End of conditional methods-----------------


def update_all_connections_from_data(
    events: list[dict],
) -> tuple[dict[str, Event], dict[str, Event]]:
    """This function detects the logic in a stream of PV events and updates
    the forward and backward logic dictionaries of events.

    :param events: A stream of PV events.
    :type events: `list`[:class:`dict`]
    :return: A tuple of the forward and backward logic dictionaries of events.
    :rtype: `tuple`[`dict`[`str`, :class:`Event`],
    `dict`[`str`, :class:`Event`]]
    """
    jobs = cluster_events_by_job_id(events)
    return update_all_connections_from_clustered_events(jobs.values())


def update_all_connections_from_clustered_events(
    clustered_events: Iterable[Iterable[PVEvent]],
) -> tuple[dict[str, Event], dict[str, Event]]:
    """This function detects the logic in a sequence of PV events and updates
    the forward and backward logic dictionaries of events.

    :param clustered_events: A sequence of PV events.
    :type clustered_events: `Iterable`[`Iterable`[:class:`PVEvent`]]
    :return: A tuple of the forward and backward logic dictionaries of events.
    :rtype: `tuple`[`dict`[`str`, :class:`Event`],
    `dict`[`str`, :class:`Event`]]
    """
    graph_solutions = get_graph_solutions_from_clustered_events(
        clustered_events
    )
    return update_all_connections_from_graph_solutions(
        graph_solutions
    )


def update_all_connections_from_graph_solutions(
    graph_solutions: Iterable[GraphSolution],
) -> tuple[dict[str, Event], dict[str, Event]]:
    """This function detects the logic in a sequence of graph solutions and
    updates the forward and backward logic dictionaries of events.

    :param graph_solutions: A sequence of graph solutions.
    :type graph_solutions: `Iterable`[:class:`GraphSolution`]
    :return: A tuple of the forward and backward logic dictionaries of events.
    :rtype: `tuple`[`dict`[`str`, :class:`Event`],
    `dict`[`str`, :class:`Event`]]
    """
    events_forward_logic: dict[str, Event] = {}
    events_backward_logic: dict[str, Event] = {}
    for graph_solution in graph_solutions:
        update_events_from_graph_solution(
            graph_solution, events_forward_logic, events_backward_logic
        )
    return events_forward_logic, events_backward_logic


def update_events_from_graph_solution(
    graph_solution: GraphSolution,
    events_forward_logic: dict[str, Event],
    events_backward_logic: dict[str, Event],
) -> None:
    """This function updates the forward and backward logic dictionaries of
    events from a graph solution.

    :param graph_solution: The graph solution.
    :type graph_solution: :class:`GraphSolution`
    :param events_forward_logic: The forward logic dictionary of events.
    :type events_forward_logic: `dict`[`str`, :class:`Event`]
    :param events_backward_logic: The backward logic dictionary of events.
    :type events_backward_logic: `dict`[`str`, :class:`Event`]
    """
    for event in graph_solution.events.values():
        event_type: str = event.meta_data["EventType"]
        if event_type not in events_forward_logic:
            events_forward_logic[event_type] = Event(event_type)
        if event_type not in events_backward_logic:
            events_backward_logic[event_type] = Event(event_type)
        events_forward_logic[event_type].update_event_sets(
            get_events_set_from_events_list(event.post_events)
        )
        events_backward_logic[event_type].update_event_sets(
            get_events_set_from_events_list(event.previous_events)
        )


def get_events_set_from_events_list(events: list[EventSolution]) -> list[str]:
    """This function gets the events set as a list of event types from a list
    of event solutions.

    :param events: A list of event solutions.
    :type events:
    `list`[:class:`test_event_generator.solutions.event_solution.EventSolution`
    ]
    :return: The events set as a list of event types.
    :rtype: `list`[`str`]
    """

    events_set = []
    for event in events:
        events_set.append(event.meta_data["EventType"])
    return events_set


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


def get_graph_solutions_from_clustered_events(
    clustered_events: Iterable[Iterable[PVEvent]],
) -> Generator[GraphSolution, Any, None]:
    """This function gets the graph solutions from a sequence of clustered PV
    events.

    :param clustered_events: A sequence of clustered PV events.
    :type clustered_events: `Iterable`[`Iterable`[:class:`PVEvent`]]
    :return: A generator that yields the graph solutions.
    :rtype: `Generator`[:class:`GraphSolution`, `Any`, `None`]
    """
    for job_events in clustered_events:
        yield GraphSolution.from_event_list(job_events)


def remove_detected_loop_events(
    mapping: dict[str, list[str]],
    events: dict[str, Event]
) -> None:
    """This function removes the detected loop events from the events.

    :param mapping: The mapping of event types to loop events.
    :type mapping: `dict`[`str`, `list`[`str`]]
    :param events: The events.
    :type events: `dict`[`str`, :class:`Event`]
    """
    for event_type, loop_events in mapping.items():
        for loop_event in loop_events:
            events[event_type].remove_event_type_from_event_sets(loop_event)


def get_loop_events_to_remove_mapping(
    loops: list[Loop],
    node_event_name_reference: dict[str, str],
) -> dict[str, list[str]]:
    """This function gets the mapping of event types to loop events to remove.

    :param loops: The loops.
    :type loops: `list`[:class:`Loop`]
    :param node_event_name_reference: The node event name reference.
    :type node_event_name_reference: `dict`[`str`, `str`]
    :return: The mapping of event types to loop events to remove.
    :rtype: `dict`[`str`, `list`[`str`]]
    """
    mapping: dict[str, list[str]] = {}
    for loop in loops:
        for node_from, node_to in loop.edges_to_remove:
            event_from = node_event_name_reference[node_from]
            event_to = node_event_name_reference[node_to]
            if event_from not in mapping:
                mapping[event_from] = []
            mapping[event_from].append(event_to)
    return mapping


def remove_detected_loop_data_from_events(
    loops: list[Loop],
    events: dict[str, Event],
    node_event_name_reference: dict[str, str],
) -> None:
    """This function removes the detected loop data from the events.

    :param loops: The loops.
    :type loops: `list`[:class:`Loop`]
    :param events: The events.
    :type events: `dict`[`str`, :class:`Event`]
    :param node_event_name_reference: The node event name reference.
    :type node_event_name_reference: `dict`[`str`, `str`]
    """
    loop_events_to_remove = get_loop_events_to_remove_mapping(
        loops, node_event_name_reference
    )
    remove_detected_loop_events(loop_events_to_remove, events)
