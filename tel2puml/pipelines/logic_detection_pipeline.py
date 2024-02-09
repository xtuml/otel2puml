"""Module to detect the logic in a sequence of PV events.
"""
from itertools import product

from numpy import ndarray
import numpy as np

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
        self.occured_edges: list[list[tuple[str, str]]] = []
        self.conditional_count_matrix: ndarray | None = None
        self._condtional_probability_matrix: ndarray | None = None
        self._update_since_conditional_probability_matrix = False

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
