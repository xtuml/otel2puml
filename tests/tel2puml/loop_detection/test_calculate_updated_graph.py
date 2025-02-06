"""Test for module loop_detection.calculate_updated_graph"""
import pytest
from networkx import DiGraph

from tel2puml.tel2puml_types import DUMMY_START_EVENT, DUMMY_END_EVENT
from tel2puml.events import Event, EventSet
from tel2puml.loop_detection.loop_types import LoopEvent, Loop, EventEdge
from tel2puml.loop_detection.calculate_updated_graph import (
    get_event_list_from_event_sets_intersecting_with_event_types_set,
    check_eventsets_indicate_branch_for_set_of_event_types,
    get_event_list_with_loop_event_from_event_list,
    get_event_lists_with_loop_events_from_event_lists,
    get_event_lists_with_loop_events,
    update_graph_for_loop_start_events,
    update_graph_for_loop_end_events,
    update_graph_for_break_events_with_path_to_root_event,
    calculate_updated_graph_with_loop_event,
    remove_event_sets_mirroring_removed_edges,
    remove_event_edges_and_event_sets
)


class TestsRemoveEdgesAndEventSets:
    """Group of tests for removal of edges and event sets:

    * remove_event_sets_mirroring_removed_edges
    * remove_event_edges_and_event_sets
    """
    @staticmethod
    def test_remove_event_sets_mirroring_removed_edges(
        graph_and_events: tuple["DiGraph[Event]", dict[str, Event]]
    ) -> None:
        """Test the removal of event sets that mirror the removal of edges."""
        _, events = graph_and_events
        # Test removing a single event edge from the graph
        assert events["A"].in_event_sets == {EventSet(["D"])}
        assert events["D"].event_sets == {EventSet(["E"]), EventSet(["A"])}
        remove_event_sets_mirroring_removed_edges(
            [EventEdge(events["D"], events["A"])]
        )
        assert events["A"].in_event_sets == set()
        assert events["D"].event_sets == {EventSet(["E"])}
        # test removing an event sets that are asynchronous events
        assert events["A"].event_sets == {EventSet(["B", "C"])}
        assert events["B"].in_event_sets == {EventSet(["A"])}
        assert events["C"].in_event_sets == {EventSet(["A"])}
        remove_event_sets_mirroring_removed_edges(
            [EventEdge(events["A"], events["B"])]
        )
        assert events["A"].event_sets == set()
        assert events["B"].in_event_sets == set()
        assert events["C"].in_event_sets == {EventSet(["A"])}

    @staticmethod
    def test_remove_event_edges_and_event_sets(
        graph_and_events: tuple["DiGraph[Event]", dict[str, Event]]
    ) -> None:
        """Test the removal of event edges and event sets."""
        graph, events = graph_and_events
        # Test removing a single event edge from the graph
        assert events["A"].in_event_sets == {EventSet(["D"])}
        assert events["D"].event_sets == {EventSet(["E"]), EventSet(["A"])}
        remove_event_edges_and_event_sets(
            [EventEdge(events["D"], events["A"])],
            graph,
        )
        assert events["A"].in_event_sets == set()
        assert events["D"].event_sets == {EventSet(["E"])}
        assert EventEdge(events["D"], events["A"]) not in graph.edges()
        # test removing an event sets that are asynchronous events
        assert events["A"].event_sets == {EventSet(["B", "C"])}
        assert events["B"].in_event_sets == {EventSet(["A"])}
        assert events["C"].in_event_sets == {EventSet(["A"])}
        remove_event_edges_and_event_sets(
            [EventEdge(events["A"], events["B"])],
            graph,
        )
        assert events["A"].event_sets == set()
        assert events["B"].in_event_sets == set()
        assert events["C"].in_event_sets == {EventSet(["A"])}
        assert EventEdge(events["A"], events["B"]) not in graph.edges()


class TestGetEventListsWithLoopEvents:
    """Tests for the get event lists with loop events method."""
    def event_sets(self) -> set[EventSet]:
        """Return a set of event sets."""
        return {
            EventSet(["A", "B", "B"]),
            EventSet(["A", "B"]),
            EventSet(["C", "B", "B"]),
            EventSet(["D", "E"]),
            EventSet(["F", "B", "B", "B"]),
        }

    def test_get_event_list_from_event_sets_intersecting_with_event_types_set(
        self
    ) -> None:
        """Test for the
        `get_event_list_from_event_sets_intersecting_with_event_types_set`
        method."""
        event_sets = self.event_sets()
        assert {
            EventSet(event_list)
            for event_list in
            get_event_list_from_event_sets_intersecting_with_event_types_set(
                event_sets, {"A", "B"}
            )
        } == {
            EventSet(["A", "B"]),
            EventSet(["A", "B", "B"]),
            EventSet(["C", "B", "B"]),
            EventSet(["F", "B", "B", "B"]),
        }
        assert {
            EventSet(event_list)
            for event_list in
            get_event_list_from_event_sets_intersecting_with_event_types_set(
                event_sets, {"D"}
            )
        } == {
            EventSet(["D", "E"]),
        }

    def test_check_eventsets_indicate_branch_for_set_of_event_types(
        self
    ) -> None:
        """Test for the
        `check_eventsets_indicate_branch_for_set_of_event_types` method.
        """
        event_sets = self.event_sets()
        event_sets.remove(EventSet(["D", "E"]))
        assert check_eventsets_indicate_branch_for_set_of_event_types(
            event_sets, {"A", "B"}
        )
        assert not check_eventsets_indicate_branch_for_set_of_event_types(
            event_sets, {"A", "C", "F"}
        )
        with pytest.raises(ValueError):
            check_eventsets_indicate_branch_for_set_of_event_types(
                event_sets, {"D", "E"}
            )

    def test_get_event_list_with_loop_event_from_event_list(self) -> None:
        """Test for the `get_event_list_with_loop_event_from_event_list`
        method."""
        event_list = ["M", "A", "B", "B"]
        loop_event_type = "LOOP"
        event_types = {"A", "B"}
        # check if not a branch
        assert get_event_list_with_loop_event_from_event_list(
            event_list, loop_event_type, event_types
        ) == ["M", "LOOP"]
        # check if a branch
        assert get_event_list_with_loop_event_from_event_list(
            event_list, loop_event_type, event_types, is_branch=True
        ) == ["M", "LOOP", "LOOP", "LOOP"]
        with pytest.raises(ValueError):
            get_event_list_with_loop_event_from_event_list(
                event_list, loop_event_type, {"C", "D"}
            )

    def test_get_event_lists_with_loop_events_from_event_lists(self) -> None:
        """Test for the
        `get_event_lists_with_loop_events_from_event_lists` method."""
        event_lists = [
            event_set.to_list()
            for event_set in self.event_sets()
            if event_set != EventSet(["D", "E"])
        ]
        loop_event_type = "LOOP"
        event_types = {"A", "B"}
        # check if not a branch
        assert sorted(get_event_lists_with_loop_events_from_event_lists(
            event_lists, loop_event_type, event_types
        )) == sorted([
            ["LOOP"],
            ["LOOP"],
            ["C", "LOOP"],
            ["F", "LOOP"],
        ])
        # check if a branch
        assert sorted(get_event_lists_with_loop_events_from_event_lists(
            event_lists, loop_event_type, event_types, is_branch=True
        )) == sorted([
            ["LOOP", "LOOP"],
            ["LOOP", "LOOP", "LOOP"],
            ["C", "LOOP", "LOOP"],
            ["F", "LOOP", "LOOP", "LOOP"],
        ])

    def test_get_event_lists_with_loop_events(self) -> None:
        """Test for the `get_event_lists_with_loop_events` method."""
        event_sets = self.event_sets()
        event_types = {"A", "B"}
        loop_event_type = "LOOP"
        assert sorted(get_event_lists_with_loop_events(
            event_sets, event_types, loop_event_type
        )) == sorted([
            ["LOOP", "LOOP"],
            ["LOOP", "LOOP", "LOOP"],
            ["C", "LOOP", "LOOP"],
            ["F", "LOOP", "LOOP", "LOOP"],
        ])


def test_update_graph_for_loop_start_events(
    graph: "DiGraph[Event]", loop: Loop, events: dict[str, Event]
) -> None:
    """Test for the `update_graph_for_loop_start_events` method."""
    loop_event = LoopEvent("LOOP", graph)
    update_graph_for_loop_start_events(
        loop.start_events, loop.loop_events,
        loop_event, graph
    )
    assert all(
        edge not in graph.edges
        for edge in [
            (events["B"], events["D"]),
            (events["B"], events["E"]),
            (events["C"], events["F"]),
        ]
    )
    assert events["B"].event_sets == {
        EventSet(["LOOP"]),
        EventSet(["LOOP", "LOOP"]),
    }
    assert events["C"].event_sets == {
        EventSet(["LOOP"]),
    }


def test_update_graph_for_loop_end_events(
    graph: "DiGraph[Event]", loop: Loop, events: dict[str, Event]
) -> None:
    """Test for the `update_graph_for_loop_end_events` method."""
    loop_event = LoopEvent("LOOP", graph)
    update_graph_for_loop_end_events(
        loop.end_events, loop.loop_events,
        loop_event, graph
    )
    assert all(
        edge not in graph.edges
        for edge in [
            (events["H"], events["J"]),
            (events["H"], events["K"]),
            (events["I"], events["L"]),
        ]
    )
    assert events["J"].in_event_sets == {
        EventSet(["LOOP"]),
        EventSet(["M"])
    }
    assert events["K"].in_event_sets == {
        EventSet(["LOOP"]),
    }
    assert events["L"].in_event_sets == {
        EventSet(["LOOP"]),
    }


def test_update_graph_for_break_events_with_path_to_root_event(
    graph: "DiGraph[Event]", loop: Loop, events: dict[str, Event]
) -> None:
    """Test for the `update_graph_for_break_events_with_path_to_root_event`"""
    loop_event = LoopEvent("LOOP", graph)
    update_graph_for_break_events_with_path_to_root_event(
        loop.break_events, loop.loop_events,
        loop_event, graph
    )
    assert (events["M"], events["J"]) in graph.edges
    assert events["M"].event_sets == {
        EventSet(["J"]),
    }
    assert events["J"].in_event_sets == {
        EventSet(["LOOP"]),
        EventSet(["M"]),
        EventSet(["H"])
    }


class TestCalculateUpdatedGraphWithLoopEvent:
    """Tests for the `calculate_updated_graph_with_loop_event` method."""
    @staticmethod
    def graph() -> "DiGraph[Event]":
        """Returns a graph with Events.

        The graph is as shown in the diagram at the following link:

        `tests/loop_detection/loop_test_graph.svg`

        """
        graph: "DiGraph[Event]" = DiGraph()
        start_event = Event(DUMMY_START_EVENT)
        A = Event("A")
        B = Event("B")
        C = Event("C")
        D = Event("D")
        E = Event("E")
        F = Event("F")
        G = Event("G")
        end_event = Event(DUMMY_END_EVENT)
        # add down stream edges
        graph.add_edge(start_event, A)
        graph.add_edge(A, B)
        graph.add_edge(B, C)
        graph.add_edge(C, D)
        graph.add_edge(C, B)
        graph.add_edge(B, E)
        graph.add_edge(E, F)
        graph.add_edge(F, G)
        graph.add_edge(D, end_event)
        graph.add_edge(G, end_event)
        # add loop back edges
        graph.add_edge(C, B)
        # add event sets to events
        for edge in graph.edges:
            edge[0].update_event_sets([edge[1].event_type])
            edge[1].update_in_event_sets([edge[0].event_type])
        return graph

    @staticmethod
    def events(graph: "DiGraph[Event]") -> dict[str, Event]:
        """Returns a dictionary of events relating to the graph"""
        return {
            event.event_type: event
            for event in graph.nodes
        }

    @staticmethod
    def loop(events: dict[str, "Event"]) -> Loop:
        """Returns a Loop object for the graph."""
        return Loop(
            loop_events={events["B"], events["C"]},
            start_events={events["B"]},
            end_events={events["C"]},
            break_events={events["E"], events["F"]},
            edges_to_remove={
                EventEdge(events["C"], events["B"]),
            },
        )

    @staticmethod
    def graph_with_path_back_to_root(
        graph: "DiGraph[Event]",
        events: dict[str, "Event"]
    ) -> "DiGraph[Event]":
        """Returns a graph with a path back to the root event."""
        graph.add_edge(events["A"], events["E"])
        return graph

    @staticmethod
    def test_calculate_updated_graph_with_loop_event_normal(
        graph: "DiGraph[Event]", loop: Loop, events: dict[str, Event]
    ) -> None:
        """Test for the `calculate_updated_graph_with_loop_event` method."""
        loop_event = LoopEvent("LOOP", graph)
        events_with_loop_event_replaced = (
            set(graph.nodes) - loop.loop_events | {loop_event}
        )
        graph = calculate_updated_graph_with_loop_event(
            loop=loop, loop_event=loop_event, graph=graph
        )
        assert loop.loop_events.intersection(graph.nodes) == set()
        assert events_with_loop_event_replaced == set(graph.nodes)
        # check edges to loop event are correct
        assert all(
            edge in graph.edges
            for edge in [
                (events["B"], loop_event),
                (events["C"], loop_event),
                (loop_event, events["J"]),
                (loop_event, events["K"]),
                (loop_event, events["L"]),
                (events["M"], events["J"]),
            ]
        )
        # check event sets are correct
        assert events["M"].event_sets == {
            EventSet(["J"]),
        }
        assert events["M"].in_event_sets == {
            EventSet(["A"])
        }
        assert events["J"].in_event_sets == {
            EventSet(["LOOP"]),
            EventSet(["M"]),
        }
        assert events["K"].in_event_sets == {
            EventSet(["LOOP"]),
        }
        assert events["L"].in_event_sets == {
            EventSet(["LOOP"]),
        }
        assert events["B"].event_sets == {
            EventSet(["LOOP"]),
            EventSet(["LOOP", "LOOP"]),
        }
        assert events["C"].event_sets == {
            EventSet(["LOOP"]),
        }
        assert events["N"].in_event_sets == {
            EventSet(["L"]),
        }

    def test_calculate_updated_graph_with_loop_event_without_path_back_to_root(
       self
    ) -> None:
        """Test for the `calculate_updated_graph_with_loop_event` method.
        The break events do not have a path back to the root event."""
        graph = self.graph()
        events = self.events(graph)
        loop = self.loop(events)
        loop_event = LoopEvent("LOOP", graph)
        events_with_loop_event_replaced = (
            set(graph.nodes) - loop.loop_events
            - set([events["E"]]) | {loop_event}
        )
        graph = calculate_updated_graph_with_loop_event(
            loop=loop, loop_event=loop_event, graph=graph
        )
        assert loop.loop_events.intersection(graph.nodes) == set()
        assert events_with_loop_event_replaced == set(graph.nodes)
        # check event sets of events included in output graph are correct
        assert events["A"].event_sets == {
            EventSet(["LOOP"]),
        }
        assert events["D"].in_event_sets == {
            EventSet(["LOOP"]),
        }
        assert events["F"].in_event_sets == {
            EventSet(["LOOP"]),
        }
        assert events["F"].event_sets == {
            EventSet(["G"]),
        }
        assert events["G"].in_event_sets == {
            EventSet(["LOOP"]), EventSet(["F"])
        }
        # check edges in the graph are correct
        assert set(graph.edges) == set([
            (events["A"], loop_event),
            (loop_event, events["D"]),
            (loop_event, events["F"]),
            (loop_event, events["G"]),
            (events["F"], events["G"]),
            (events["D"], events[DUMMY_END_EVENT]),
            (events["G"], events[DUMMY_END_EVENT]),
            (events[DUMMY_START_EVENT], events["A"]),
        ])

    def test_calculate_updated_graph_with_loop_event_with_path_back_to_root(
        self,
    ) -> None:
        """Test for the `calculate_updated_graph_with_loop_event` method.
        The break events have a path back to the root event."""
        graph = self.graph()
        events = self.events(graph)
        loop = self.loop(events)
        graph = self.graph_with_path_back_to_root(graph, events)
        loop_event = LoopEvent("LOOP", graph)
        events_with_loop_event_replaced = (
            set(graph.nodes) - loop.loop_events | {loop_event}
        )
        graph = calculate_updated_graph_with_loop_event(
            loop=loop, loop_event=loop_event, graph=graph
        )
        assert loop.loop_events.intersection(graph.nodes) == set()
        assert events_with_loop_event_replaced == set(graph.nodes)
        # check event sets of events included in output graph are correct
        assert events["A"].event_sets == {
            EventSet(["LOOP"]),
        }
        assert events["D"].in_event_sets == {
            EventSet(["LOOP"]),
        }
        assert events["F"].in_event_sets == {
            EventSet(["LOOP"]),
            EventSet(["E"]),
        }
        assert events["F"].event_sets == {
            EventSet(["G"]),
        }
        assert events["G"].in_event_sets == {
            EventSet(["LOOP"]), EventSet(["F"])
        }
        # check edges in the graph are correct
        assert set(graph.edges) == set([
            (events["A"], loop_event),
            (loop_event, events["D"]),
            (loop_event, events["F"]),
            (loop_event, events["G"]),
            (events["F"], events["G"]),
            (events["D"], events[DUMMY_END_EVENT]),
            (events["G"], events[DUMMY_END_EVENT]),
            (events[DUMMY_START_EVENT], events["A"]),
            (events["A"], events["E"]),
            (events["E"], events["F"]),
        ])
