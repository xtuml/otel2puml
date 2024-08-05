"""This module contains functions to update the forward and backward
dictionaries holding the Event's and their EventSet's"""

from typing import Any, Generator, Iterable

from test_event_generator.solutions.event_solution import EventSolution
from test_event_generator.solutions.graph_solution import GraphSolution

from tel2puml.events import Event
from tel2puml.tel2puml_types import PVEvent, DUMMY_START_EVENT


def update_all_connections_from_data(
    events: Iterable[PVEvent],
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
    add_dummy_start: bool = False,
) -> tuple[dict[str, Event], dict[str, Event]]:
    """This function detects the logic in a sequence of PV events and updates
    the forward and backward logic dictionaries of events.

    :param clustered_events: A sequence of PV events.
    :type clustered_events: `Iterable`[`Iterable`[:class:`PVEvent`]]
    :param add_dummy_start: Whether to add a dummy start event.
    :type add_dummy_start: `bool`
    :return: A tuple of the forward and backward logic dictionaries of events.
    :rtype: `tuple`[`dict`[`str`, :class:`Event`],
    `dict`[`str`, :class:`Event`]]
    """
    graph_solutions = get_graph_solutions_from_clustered_events(
        clustered_events,
        add_dummy_start=add_dummy_start,
    )
    return update_all_connections_from_graph_solutions(graph_solutions)


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


def get_graph_solutions_from_events(
    events: Iterable[PVEvent],
) -> list[GraphSolution]:
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


def cluster_events_by_job_id(
    events: Iterable[PVEvent],
) -> dict[str, list[PVEvent]]:
    """This function clusters PV events into jobs.

    :param events: A sequence of PV events.
    :type events: `list`[:class:`dict`]
    """
    events_by_job_id: dict[str, list[PVEvent]] = {}
    for event in events:
        job_id = event["jobId"]
        if job_id not in events_by_job_id:
            events_by_job_id[job_id] = []
        events_by_job_id[job_id].append(event)
    return events_by_job_id


def get_graph_solutions_from_clustered_events(
    clustered_events: Iterable[Iterable[PVEvent]],
    add_dummy_start: bool = False,
) -> Generator[GraphSolution, Any, None]:
    """This function gets the graph solutions from a sequence of clustered PV
    events.

    :param clustered_events: A sequence of clustered PV events.
    :type clustered_events: `Iterable`[`Iterable`[:class:`PVEvent`]]
    :param add_dummy_start: Whether to add a dummy start event.
    :type add_dummy_start: `bool`
    :return: A generator that yields the graph solutions.
    :rtype: `Generator`[:class:`GraphSolution`, `Any`, `None`]
    """
    for job_events in clustered_events:
        graph_solution = GraphSolution.from_event_list(job_events)
        if add_dummy_start:
            update_graph_solution_with_dummy_start_event(graph_solution)
        yield graph_solution


def update_graph_solution_with_dummy_start_event(
    graph_solution: GraphSolution,
) -> None:
    """This function updates a graph solution with a dummy start event with
    event type as the constant `DUMMY_START_EVENT`. Removes all start events
    and adds the dummy start event as the start event.

    :param graph_solution: The graph solution.
    :type graph_solution: :class:`GraphSolution`
    """
    dummy_start_event = EventSolution(
        meta_data={"EventType": DUMMY_START_EVENT}
    )
    keys_to_remove = []
    for key, start_event in graph_solution.start_events.items():
        dummy_start_event.add_post_event(start_event)
        keys_to_remove.append(key)
    for key in keys_to_remove:
        del graph_solution.start_events[key]
    dummy_start_event.add_to_post_events()
    graph_solution.add_event(dummy_start_event)


def update_and_create_events_from_graph_solution(
    graph_solution: GraphSolution,
    events: dict[str, Event],
) -> None:
    """This function updates and creates events, in a dictionary, from a graph
    solution.

    :param graph_solution: The graph solution.
    :type graph_solution: :class:`GraphSolution`
    :param events: The dictionary of events.
    :type events: `dict`[`str`, :class:`Event`]
    """
    for event in graph_solution.events.values():
        event_type: str = event.meta_data["EventType"]
        if event_type not in events:
            events[event_type] = Event(event_type)
        events[event_type].update_event_sets(
            get_events_set_from_events_list(event.post_events)
        )
        events[event_type].update_in_event_sets(
            get_events_set_from_events_list(event.previous_events)
        )


def update_and_create_events_from_graph_solutions(
    graph_solutions: Iterable[GraphSolution],
) -> dict[str, Event]:
    """This function updates and creates events from an iterable of graph
    solutions.

    :param graph_solutions: An iterable of graph solutions.
    :type graph_solutions: `Iterable`[:class:`GraphSolution`]
    :return: A dictionary of events.
    :rtype: `dict`[`str`, :class:`Event`]
    """
    events: dict[str, Event] = {}
    for graph_solution in graph_solutions:
        update_and_create_events_from_graph_solution(graph_solution, events)
    return events


def update_and_create_events_from_clustered_pvevents(
    clustered_events: Iterable[Iterable[PVEvent]],
    add_dummy_start: bool = False,
) -> dict[str, Event]:
    """This function updates and creates events from a sequence of clustered PV
    events.

    :param clustered_events: A sequence of clustered PV events.
    :type clustered_events: `Iterable`[`Iterable`[:class:`PVEvent`]]
    :param add_dummy_start: Whether to add a dummy start event.
    :type add_dummy_start: `bool`
    :return: A dictionary of events.
    :rtype: `dict`[`str`, :class:`Event`]
    """
    graph_solutions = get_graph_solutions_from_clustered_events(
        clustered_events,
        add_dummy_start=add_dummy_start,
    )
    return update_and_create_events_from_graph_solutions(graph_solutions)
