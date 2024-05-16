"""Tests for the tel2puml.events module."""
from tel2puml.events import (
    Event, EventSet, get_loop_events_to_remove_mapping,
    remove_detected_loop_data_from_events,
    remove_detected_loop_events
)
from tel2puml.detect_loops import Loop


class TestEventSet:
    """Tests for the EventSet class."""

    @staticmethod
    def test_init_single_entries() -> None:
        """Tests for the __init__ method."""
        event_set = EventSet(["A", "B", "C"])
        assert event_set["A"] == 1
        assert event_set["B"] == 1
        assert event_set["C"] == 1

    @staticmethod
    def test_init_repeated_entries() -> None:
        """Tests for the __init__ method for repeated entries."""
        event_set = EventSet(["A", "B", "A", "C", "B", "A"])
        assert event_set["A"] == 3
        assert event_set["B"] == 2
        assert event_set["C"] == 1

    @staticmethod
    def test_init_empty_entries() -> None:
        """Tests for the __init__ method for empty entries."""
        event_set = EventSet([])
        assert len(event_set) == 0

    @staticmethod
    def test_hash() -> None:
        """Tests for the __hash__ method."""
        event_set_1 = EventSet(["A", "B", "C"])
        assert hash(event_set_1) == hash((("A", 1), ("B", 1), ("C", 1)))
        event_set_2 = EventSet(["A", "B", "A", "C", "B", "A"])
        assert hash(event_set_2) == hash((("A", 3), ("B", 2), ("C", 1)))

    @staticmethod
    def test_eq() -> None:
        """Tests for the __eq__ method."""
        event_set_1 = EventSet(["A", "B", "C"])
        event_set_2 = EventSet(["B", "A", "C"])
        assert event_set_1 == event_set_2
        event_set_3 = EventSet(["A", "B", "A", "C", "B", "A"])
        assert event_set_1 != event_set_3

    @staticmethod
    def test_to_frozenset() -> None:
        """Tests for the to_list method."""
        event_set = EventSet(["A", "B", "C"])
        assert event_set.to_frozenset() == frozenset(["A", "B", "C"])
        event_set = EventSet(["B", "A", "C"])
        assert event_set.to_frozenset() == frozenset(["A", "B", "C"])
        event_set = EventSet(["A", "B", "A", "C", "B", "A"])
        assert event_set.to_frozenset() == frozenset(["A", "B", "C"])

    @staticmethod
    def test_get_branch_events() -> None:
        """Tests for the get_branch_counts method."""
        event_set = EventSet(["A", "B", "C"])
        assert event_set.get_repeated_events() == {}
        event_set = EventSet(["A", "A"])
        assert event_set.get_repeated_events() == {"A": 2}
        event_set = EventSet(["A", "B", "A", "C", "B", "A"])
        assert event_set.get_repeated_events() == {"A": 3, "B": 2}


class TestEvent:
    """Tests for the Event class."""
    @staticmethod
    def test_update_event_sets() -> None:
        """Tests for method update_event_sets"""
        event = Event("A")
        events = ["B", "C", "D"]
        # check that the event sets are updated
        event.update_event_sets(events)
        assert event.event_sets == {EventSet(events)}
        # check that the event sets are not updated
        event.update_event_sets(events)
        assert event.event_sets == {EventSet(events)}
        # check that the event sets are not updated if events are reversed
        event.update_event_sets(["D", "C", "B"])
        assert event.event_sets == {EventSet(events)}
        # check that the event sets are updated
        event.update_event_sets(["B", "C"])
        assert event.event_sets == {EventSet(events), EventSet(["B", "C"])}
        # check that the event sets are updated
        event.update_event_sets(["B", "B", "C"])
        assert event.event_sets == {
            EventSet(events),
            EventSet(["B", "C"]),
            EventSet(["B", "B", "C"]),
        }
        # check that the event sets are not updated
        event.update_event_sets(["B", "C", "B"])
        assert event.event_sets == {
            EventSet(events),
            EventSet(["B", "C"]),
            EventSet(["B", "B", "C"]),
        }
        # check that the event sets are updated
        event.update_event_sets(["C", "B", "C"])
        assert event.event_sets == {
            EventSet(events),
            EventSet(["B", "C"]),
            EventSet(["B", "B", "C"]),
            EventSet(["B", "C", "C"]),
        }

    def test_get_reduced_event_set(self) -> None:
        """Tests for method get_reduced_event_set"""
        event = Event("A")
        event.event_sets = {
            EventSet(["B", "C"]),
            EventSet(["B", "B", "C"]),
            EventSet(["B", "C", "C"]),
        }
        reduced_event_set = event.get_reduced_event_set()
        assert reduced_event_set == {frozenset(["B", "C"])}

        event.event_sets = {
            EventSet(["A"]),
            EventSet(["B"]),
            EventSet(["B", "C"]),
            EventSet(["B", "B", "C"]),
            EventSet(["B", "C", "C"]),
        }
        reduced_event_set = event.get_reduced_event_set()
        assert reduced_event_set == {
            frozenset(["B", "C"]),
            frozenset(["A"]),
            frozenset(["B"]),
            }

    def test_get_event_set_counts(self) -> None:
        """Tests for method get_event_set_counts"""
        event = Event("A")
        event.event_sets = {
            EventSet(["B"]),
        }
        event_set_counts = event.get_event_set_counts()
        assert event_set_counts == {'B': {1}}

        event.event_sets = {
            EventSet(["B", "C"]),
            EventSet(["B", "B", "C"]),
            EventSet(["B", "C", "C"]),
        }
        event_set_counts = event.get_event_set_counts()
        assert event_set_counts == {'B': {1, 2}, 'C': {1, 2}}

        event.event_sets = {
            EventSet(["B"]),
            EventSet(["B", "C"]),
            EventSet(["B", "C", "C"]),
        }
        event_set_counts = event.get_event_set_counts()
        assert event_set_counts == {'B': {1}, 'C': {1, 2}}

        event.event_sets = {
            EventSet(["B", "C"]),
            EventSet(["B", "B", "C"]),
            EventSet(["B", "C", "C", "D"]),
        }
        event_set_counts = event.get_event_set_counts()
        assert event_set_counts == {'B': {1, 2}, 'C': {1, 2}, 'D': {1}}

    def test_remove_event_type_from_event_sets(self) -> None:
        """Tests for method remove_event_type_from_event_sets"""
        event = Event("A")
        event.event_sets = {
            EventSet(["B"]),
        }
        event.remove_event_type_from_event_sets("B")
        assert event.event_sets == set()

        event.event_sets = {
            EventSet(["B", "C"]),
            EventSet(["B", "B", "C"]),
            EventSet(["C", "C"]),
        }
        event.remove_event_type_from_event_sets("B")
        assert event.event_sets == {
            EventSet(["C", "C"]),
        }


def test_remove_detected_loop_events() -> None:
    """Test for method remove_detected_loop_events"""
    event_a = Event("A")
    event_a.event_sets = {
        EventSet(["B"]),
    }
    event_b = Event("B")
    event_b.event_sets = {
        EventSet(["A"]),
        EventSet(["C"]),
    }
    event_c = Event("C")

    mapping = {"B": ["A"]}
    events = {"A": event_a, "B": event_b, "C": event_c}
    remove_detected_loop_events(mapping, events)
    for event_set in event_b.event_sets:
        assert "A" not in event_set


class TestLoopEdgeRemoval:
    """Tests functionality for loop edge removal from Event class"""
    def get_loop_ref_and_events(
        self
    ) -> tuple[list[Loop], dict[str, str], dict[str, Event]]:
        """Helper method to get loop reference and events for testing"""
        # setup loops
        loop_1 = Loop(["q1", "q2", "q3"])
        loop_1.add_edge_to_remove(("q3", "q1"))
        loop_2 = Loop(["q4", "q5"])
        loop_2.add_edge_to_remove(("q5", "q5"))
        loops = [loop_1, loop_2]
        # setup node events reference
        node_event_name_reference = {
            "q1": "A",
            "q2": "B",
            "q3": "C",
            "q4": "D",
            "q5": "E",
        }
        # setup events
        A = Event("A")
        B = Event("B")
        C = Event("C")
        D = Event("D")
        E = Event("E")
        A.update_event_sets(["B"])
        B.update_event_sets(["C"])
        C.update_event_sets(["A"])
        C.update_event_sets(["D"])
        D.update_event_sets(["E"])
        E.update_event_sets(["E"])
        events = {"A": A, "B": B, "C": C, "D": D, "E": E}
        return loops, node_event_name_reference, events

    def test_get_loop_events_to_remove_mapping(self) -> None:
        """Test for method get_loop_events_to_remove_mapping"""
        loops, node_event_name_reference, events = (
            self.get_loop_ref_and_events()
        )
        loop_events_to_remove = get_loop_events_to_remove_mapping(
            loops, node_event_name_reference
        )
        assert len(loop_events_to_remove) == 2
        assert "C" in loop_events_to_remove and "E" in loop_events_to_remove
        assert loop_events_to_remove["C"] == ["A"]
        assert loop_events_to_remove["E"] == ["E"]
        # test for loop with break edges to remove
        loops[0].break_point_edges_to_remove.add(("q6", "q4"))
        node_event_name_reference["q6"] = "F"
        F = Event("F")
        F.update_event_sets(["D"])
        events["A"].update_event_sets(["F"])
        loop_events_to_remove = get_loop_events_to_remove_mapping(
            loops, node_event_name_reference
        )
        assert len(loop_events_to_remove) == 3
        assert set(loop_events_to_remove.keys()) == {"C", "E", "F"}
        assert loop_events_to_remove["F"] == ["D"]

    def test_remove_detected_loop_data_from_events(self) -> None:
        """Test for method remove_detected_loop_data_from_events"""
        loops, node_event_name_reference, events = (
            self.get_loop_ref_and_events()
        )
        remove_detected_loop_data_from_events(
            loops,
            events,
            node_event_name_reference
        )
        assert len(events["C"].event_sets) == 1
        assert len(events["E"].event_sets) == 0
        assert len(events["A"].event_sets) == 1
        assert len(events["B"].event_sets) == 1
        assert len(events["D"].event_sets) == 1
