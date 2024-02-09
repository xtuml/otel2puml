"""Module to detect the logic in a sequence of PV events.
"""
from test_event_generator.solutions.graph_solution import GraphSolution


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
