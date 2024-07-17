"""This module contains classes to store incoming events and their outgoing
events. It also contains functions to convert these classes to a Markov graph.
"""

from typing import Iterable
from copy import deepcopy
from uuid import uuid4

from pm4py import (  # type: ignore[import-untyped]
    ProcessTree,
)
from networkx import DiGraph
from test_event_generator.solutions.graph_solution import (  # type: ignore[import-untyped] # noqa: E501
    GraphSolution,
)
from test_event_generator.solutions.event_solution import (  # type: ignore[import-untyped] # noqa: E501
    EventSolution,
)

from tel2puml.detect_loops import Loop
from tel2puml.logic_detection import calculate_logic_gates


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

    def __key(self) -> tuple[tuple[str, int], ...]:
        return tuple((k, self[k]) for k in sorted(self))

    def __hash__(self) -> int:
        return hash(self.__key())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EventSet):
            return NotImplemented
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

    def is_subset(self, other: "EventSet") -> bool:
        """Method to check if the event set is a subset of another event set.

        :param other: The other event set.
        :type other: :class:`EventSet`
        :return: Whether the event set is a subset.
        :rtype: `bool`
        """
        return all(
            count == other.get(event, -1) for event, count in self.items()
        )

    def to_list(self) -> list[str]:
        """Method to get the events as a list.

        :return: The events as a list.
        :rtype: `list`[`str`]
        """
        return list(
            event for event, count in self.items() for _ in range(count)
        )


class Event:
    """Class to detect the logic in a sequence of PV events.

    :param event_type: The type of event.
    :type event_type: `str`
    """

    def __init__(
        self,
        event_type: str,
        uid: str | None = None,
    ) -> None:
        """Constructor method."""
        self.event_type = event_type
        self.event_sets: set[EventSet] = set()
        self.in_event_sets: set[EventSet] = set()
        self._set_uid(uid)
        self._logic_gate_tree: ProcessTree | None = None
        self._update_since_logic_gate_tree = False

    @property
    def uid(self) -> str:
        """This property gets the unique identifier for the event.

        :return: The unique identifier.
        :rtype: `str`
        """
        if self._uid is None:
            raise ValueError("The event does not have a unique identifier.")
        return self._uid

    def _set_uid(self, uid: str | None) -> None:
        """This method sets the unique identifier for the event.

        :param uid: The unique identifier.
        :type uid: `str`
        """
        if uid is None:
            uid = str(uuid4())
        self._uid = uid

    def __repr__(self) -> str:
        return self.event_type

    def __hash__(self) -> int:
        """Method to hash the event type.

        :return: The hash of the event type.
        :rtype: `int`
        """
        return hash(self.uid)

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
            self._logic_gate_tree = calculate_logic_gates(self)
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

    def update_in_event_sets(
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

        self.in_event_sets.add(EventSet(events))

    def get_reduced_in_event_set(self) -> set[frozenset[str]]:
        """This method reduces the event set to a list of unique events.

        :return: The reduced event set.
        :rtype: `list`[`str`]
        """
        return {event_set.to_frozenset() for event_set in self.in_event_sets}

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

    def remove_event_type_from_in_event_sets(self, event_type: str) -> None:
        """Method to remove an event type from the in event sets.

        :param event_type: The event type.
        :type event_type: `str`
        """
        self.in_event_sets = {
            event_set
            for event_set in self.in_event_sets
            if event_type not in event_set
        }


def remove_detected_loop_events(
    mapping: dict[str, list[str]], events: dict[str, Event]
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
        for node_from, node_to in loop.all_edges_to_remove:
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
    for loop in loops:
        if loop.sub_loops:
            remove_detected_loop_data_from_events(
                loop.sub_loops, events, node_event_name_reference
            )


def events_to_markov_graph(
    events: Iterable[Event],
) -> "DiGraph[str]":
    """This function converts a sequence of events to a minimal Markov chain
    or what could be termed as a directly follows graph.

    :param events: A sequence of events.
    :type events: `Iterable`[:class:`Event`]
    :return: The Markov graph.
    :rtype: :class:`nx.DiGraph`
    """
    graph: "DiGraph[str]" = DiGraph()
    for event in events:
        out_events = set(
            event_type
            for event_set in event.event_sets
            for event_type in event_set.to_frozenset()
        )
        for out_event in out_events:
            graph.add_edge(event.event_type, out_event)
    return graph


def get_event_reference_from_events(
    events: Iterable[Event],
) -> dict[str, str]:
    """This function gets an event reference from a sequence of events.

    :param events: A sequence of events.
    :type events: `Iterable`[:class:`Event`]
    :return: The event reference.
    :rtype: `dict`[`str`, `str`]
    """
    return {event.event_type: event.event_type for event in events}


def create_graph_from_events(
    events: Iterable[Event],
) -> "DiGraph[Event]":
    """This function gets a graph of events by creating a reference dictionary
    locally and then creating a graph from the `events_sets` of the events as
    directed edges.

    :param events: A sequence of events.
    :type events: `Iterable`[:class:`Event`]
    :return: The graph of events.
    :rtype: :class:`nx.DiGraph`[:class:`Event`]
    """
    graph: "DiGraph[Event]" = DiGraph()
    event_ref = {event.event_type: event for event in events}
    for event in events:
        out_events = set(
            event_ref[event_type]
            for event_set in event.event_sets
            for event_type in event_set.to_frozenset()
        )
        for out_event in out_events:
            graph.add_edge(event, out_event)
    return graph


def has_event_set_as_subset(
    event_sets: set[EventSet], events: list[str]
) -> bool:
    """Function to check if the event set exists as a subset of any of the
    eventsets.

    :param event_sets: The event sets to check.
    :type event_sets: `set`[:class:`EventSet`]
    :param events: The list of events to check
    :type events: `list`[`str`]
    :return: Whether the event sets exist as a subset of events
    :rtype: `bool`
    """
    event_set_to_check = EventSet(events)
    return any(
        event_set_to_check.is_subset(event_set) for event_set in event_sets
    )


def get_reduced_event_set(event_sets: set[EventSet]) -> set[frozenset[str]]:
    """This function reduces a set of event sets to a set of unique events.

    :return: The reduced event set.
    :rtype: `set`[:class:`frozenset`[`str`]]
    """
    return {event_set.to_frozenset() for event_set in event_sets}
