"""This module contains classes to store incoming events and their outgoing
events. It also contains functions to convert these classes to a Markov graph.
"""

from typing import Iterable, Any
from copy import deepcopy
from uuid import uuid4
import os
import json

from pydantic import BaseModel, TypeAdapter, Field
from pm4py import (  # type: ignore[import-untyped]
    ProcessTree,
)
from networkx import DiGraph, Graph, connected_components
from test_event_generator.solutions.graph_solution import (  # type: ignore[import-untyped] # noqa: E501
    GraphSolution,
)
from test_event_generator.solutions.event_solution import (  # type: ignore[import-untyped] # noqa: E501
    EventSolution,
)

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

    def __hash__(self) -> int:  # type: ignore[override]
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

    def has_intersection_with_event_types(
        self, event_types: Iterable[str]
    ) -> bool:
        """Method to check if the event set has an intersection with the event
        types.

        :param event_types: The event types.
        :type event_types: `Iterable`[`str`]
        :return: Whether the event set has an intersection with the event
        types.
        :rtype: `bool`
        """
        return bool(self.to_frozenset().intersection(event_types))

    def get_event_type_counts_for_given_event_types(
        self,
        event_types: Iterable[str],
    ) -> dict[str, int]:
        """Method to get the event type counts from an event set.

        :param event_types: The event types.
        :type event_types: `Iterable`[`str`]
        :return: The event type counts.
        :rtype: `dict`[`str`, `int`]
        """
        return {
            event_type: (self[event_type] if event_type in self else 0)
            for event_type in event_types
        }

    def to_event_set_count_input_list(self) -> list["EventSetCountInput"]:
        """Method to convert the event set to a list of event set count inputs.

        :return: The event set count inputs.
        :rtype: `list`[:class:`EventSetCountInput`]
        """
        return [
            EventSetCountInput(eventType=event, count=count)
            for event, count in self.items()
        ]


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
            self._logic_gate_tree = calculate_logic_gates(self.event_sets)
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

    def to_event_input(self) -> "EventInput":
        """Method to convert the event to an event input.

        :return: The event input.
        :rtype: :class:`EventInput`
        """
        return EventInput(
            eventType=self.event_type,
            outgoingEventSets=[
                event_set.to_event_set_count_input_list()
                for event_set in self.event_sets
            ],
            incomingEventSets=[
                event_set.to_event_set_count_input_list()
                for event_set in self.in_event_sets
            ],
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
    :rtype: `set`[`frozenset`[`str`]]
    """
    return {event_set.to_frozenset() for event_set in event_sets}


def get_event_set_counts(event_sets: set[EventSet]) -> dict[str, set[int]]:
    """Method to get the event set counts.

    :return: The event set counts.
    :rtype: `dict`[`str`, `set`[`int`]]
    """
    event_set_counts: dict[str, set[int]] = {}
    for event_set in event_sets:
        for event, count in event_set.items():
            if event in event_set_counts:
                event_set_counts[event].add(count)
            else:
                event_set_counts[event] = {count}
    return event_set_counts


def get_overlapping_event_types(
    event_sets: set[EventSet],
) -> set[frozenset[str]]:
    """This function gets the overlapping events from a set of event sets.

    :param event_sets: The event sets.
    :type event_sets: `set`[:class:`EventSet`]
    :return: The overlapping events.
    :rtype: `set`[`frozenset`[`str`]]
    """
    graph: "Graph[str]" = Graph()
    for event_set in event_sets:
        if len(event_set) > 1:
            graph.add_edges_from(
                {
                    (event1, event2)
                    for event1 in event_set
                    for event2 in event_set
                }
            )
    return {frozenset(component) for component in connected_components(graph)}


def get_overlapping_events_from_event_sets_and_connected_events(
    event_sets: set[EventSet], connected_events: set[Event]
) -> list[set[Event]]:
    """This function gets the overlapping events from a set of event sets.

    :param event_sets: The event sets.
    :type event_sets: `set`[:class:`EventSet`]
    :param connected_events: The connected events.
    :type connected_events: `set`[:class:`Event`]
    :return: The overlapping events.
    :rtype: `set`[`frozenset`[:class:`str`]]
    """
    overlapping_event_types = get_overlapping_event_types(event_sets)
    return [
        {
            event
            for event in connected_events
            if event.event_type in over_lapping_event_types_set
        }
        for over_lapping_event_types_set in overlapping_event_types
    ]


def get_overlapping_events_from_event_and_graph(
    event: Event, graph: "DiGraph[Event]"
) -> list[set[Event]]:
    """This function gets the overlapping events from a set of event sets.

    :param event: The event.
    :type event: :class:`Event`
    :param graph: The graph.
    :type graph: :class:`DiGraph`[:class:`Event`]
    :return: The overlapping events.
    :rtype: `set`[`frozenset`[`str`]]
    """
    return get_overlapping_events_from_event_sets_and_connected_events(
        event.event_sets, set(edge[1] for edge in graph.out_edges(event))
    )


def get_event_to_over_lapping_events_map(
    graph: "DiGraph[Event]",
) -> dict[Event, list[set[Event]]]:
    """This function gets the event to overlapping events mapping from the
    graph.

    :param graph: The graph.
    :type graph: :class:`DiGraph`[:class:`Event`]
    :return: The event to overlapping events mapping.
    :rtype: `dict`[:class:`Event`, `list`[`set`[:class:`Event`]]]
    """
    event_to_overlapping_events_map: dict[Event, list[set[Event]]] = {}
    for event in graph.nodes:
        over_lapping_events = get_overlapping_events_from_event_and_graph(
            event, graph
        )
        if over_lapping_events:
            event_to_overlapping_events_map[event] = over_lapping_events
    return event_to_overlapping_events_map


class EventSetCountInput(BaseModel):
    """Class to store the count of an event.

    :param eventType: The type of event.
    :type eventType: `str`
    :param count: The count of the event.
    :type count: `int`
    """

    eventType: str
    count: int


class EventInput(BaseModel):
    """Class to store the input for an event.

    :param eventType: The type of event.
    :type eventType: `str`
    :param eventSets: The event sets.
    :type eventSets: `list`[:class:`EventSetCountInput`]
    """

    eventType: str
    outgoingEventSets: list[list[EventSetCountInput]] = Field(
        default_factory=list
    )
    incomingEventSets: list[list[EventSetCountInput]] = Field(
        default_factory=list
    )


class EventInputsFile(BaseModel):
    """Class to store the input for a file of events."""
    job_name: str
    events: list[EventInput]


def raw_event_input_to_event_input(raw_input_list: Any) -> list[EventInput]:
    """This function converts a raw input, validating it and then
    to a list of event inputs.

    :param raw_input_list: The raw input list.
    :type raw_input_list: `Any`
    :return: The event inputs.
    :rtype: `list`[:class:`EventInput`]"""
    return TypeAdapter(list[EventInput]).validate_python(raw_input_list)


def event_input_to_raw_event_input(event_input_list: list[EventInput]) -> Any:
    """This function converts a list of event inputs to a raw input that can be
    serialised to JSON

    :param event_input_list: The event input list.
    :type event_input_list: `list`[:class:`EventInput`]
    :return: The raw input.
    :rtype: `Any`
    """
    return TypeAdapter(list[EventInput]).dump_python(event_input_list)


def event_inputs_to_events(
    eventInputs: list[EventInput],
) -> dict[str, Event]:
    """This function converts a list of event inputs to a dictionary of events.

    :param eventInputs: The event inputs.
    :type eventInputs: `list`[:class:`EventInput`]
    :return: The events.
    :rtype: `dict`[`str`, :class:`Event`]
    """
    events: dict[str, Event] = {}
    for eventInput in eventInputs:
        if eventInput.eventType in events:
            raise ValueError(
                f"Event type {eventInput.eventType} already exists. "
                "Make sure the input array only contains unique event types."
            )
        event = Event(eventInput.eventType)
        for eventSetList in eventInput.outgoingEventSets:
            event.event_sets.add(
                EventSet(
                    [
                        eventSet.eventType
                        for eventSet in eventSetList
                        for _ in range(eventSet.count)
                    ]
                )
            )
        for eventSetList in eventInput.incomingEventSets:
            event.in_event_sets.add(
                EventSet(
                    [
                        eventSet.eventType
                        for eventSet in eventSetList
                        for _ in range(eventSet.count)
                    ]
                )
            )
        events[eventInput.eventType] = event
    return events


def events_to_event_inputs(
    events: dict[str, Event],
) -> list[EventInput]:
    """This function converts a dictionary of events to a list of event inputs.

    :param events: The events.
    :type events: `dict`[`str`, :class:`Event`]
    :return: The event inputs.
    :rtype: `list`[:class:`EventInput`]
    """
    eventInputs: list[EventInput] = []
    for event in events.values():
        eventInputs.append(event.to_event_input())
    return eventInputs


def raw_input_to_events(raw_input: Any) -> dict[str, Event]:
    """This function converts a raw input to a dictionary of events.

    :param raw_input: The raw input.
    :type raw_input: `Any`
    :return: The events.
    :rtype: `dict`[`str`, :class:`Event`]
    """
    return event_inputs_to_events(raw_event_input_to_event_input(raw_input))


def events_to_raw_input(events: dict[str, Event]) -> Any:
    """This function converts a dictionary of events to a raw input.

    :param events: The events.
    :type events: `dict`[`str`, :class:`Event`]
    :return: The raw input.
    :rtype: `Any`
    """
    return event_input_to_raw_event_input(events_to_event_inputs(events))


def load_events_from_file(file_path: str) -> tuple[str, dict[str, Event]]:
    """This function loads events from a file.

    :param file_path: The file path.
    :type file_path: `str`
    :return: The job name and the events.
    :rtype: `tuple`[`str`, `dict`[`str`, :class:`Event`]]
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Input events file not found: {file_path}")
    with open(file_path, "r") as file:
        raw_input = json.load(file)
        events_input_file_model = EventInputsFile.model_validate(raw_input)
        return events_input_file_model.job_name, event_inputs_to_events(
            events_input_file_model.events
        )


def save_events_to_file(
    job_name: str, events: dict[str, Event], file_path: str
) -> None:
    """This function saves events to a file.

    :param job_name: The job name.
    :type job_name: `str`
    :param events: The events.
    :type events: `dict`[`str`, :class:`Event`]
    :param file_path: The file path.
    :type file_path: `str`
    """
    events_input_file_model = EventInputsFile(
        job_name=job_name, events=events_to_event_inputs(events)
    )
    with open(file_path, "w") as file:
        json.dump(events_input_file_model.model_dump(), file, indent=4)
