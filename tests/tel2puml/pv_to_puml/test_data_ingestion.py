"""Tests for data ingestion pipeline"""
from tel2puml.events import EventSet
from tel2puml.pv_event_simulator import (
    generate_test_data,
    generate_test_data_event_sequences_from_puml,
)
from tel2puml.pv_to_puml.data_ingestion import (
    update_all_connections_from_data,
    get_graph_solutions_from_clustered_events,
    update_and_create_events_from_clustered_pvevents,
    cluster_events_by_job_id
)
from tel2puml.tel2puml_types import DUMMY_START_EVENT


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


def test_update_and_create_events_from_clustered_pvevents() -> None:
    """Test for method update_and_create_events_from_clustered_pvevents"""
    puml_file = "puml_files/sequence_xor_fork.puml"
    data = list(cluster_events_by_job_id(
        generate_test_data(puml_file)
    ).values())
    events = (
        update_and_create_events_from_clustered_pvevents(data)
    )
    assert len(events) == 6
    assert all(
        event_type in events
        for event_type in ["A", "B", "C", "D", "E", "F"]
    )
    # check A
    assert events["A"].event_sets == {
        EventSet(["B"]),
    }
    assert events["A"].in_event_sets == set()
    # check B
    assert events["B"].event_sets == {
        EventSet(["C"]),
        EventSet(["D"]),
        EventSet(["E"]),
    }
    assert events["B"].in_event_sets == {
        EventSet(["A"]),
    }
    # check C, D, E
    for event_type in ["C", "D", "E"]:
        assert events[event_type].event_sets == {
            EventSet(["F"]),
        }
        assert events[event_type].in_event_sets == {
            EventSet(["B"]),
        }
    # check F
    assert events["F"].event_sets == set()
    assert events["F"].in_event_sets == {
        EventSet(["C"]),
        EventSet(["D"]),
        EventSet(["E"]),
    }
