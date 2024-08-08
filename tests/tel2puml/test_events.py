"""Tests for the tel2puml.events module."""

from tel2puml.events import (
    Event,
    EventSet,
    has_event_set_as_subset,
    get_reduced_event_set,
)


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

    @staticmethod
    def test_has_intersection_with_event_types() -> None:
        """Tests for the has_intersection_with_event_types method."""
        event_set = EventSet(["A", "B", "C"])
        assert event_set.has_intersection_with_event_types(["A", "B"])
        assert event_set.has_intersection_with_event_types(["A", "B", "C"])
        assert event_set.has_intersection_with_event_types(["A", "D"])
        assert not event_set.has_intersection_with_event_types(["D", "E"])
        assert not event_set.has_intersection_with_event_types([])

    @staticmethod
    def test_get_event_type_counts_for_given_event_types() -> None:
        """Tests for the get_event_type_counts_for_given_event_types method."""
        event_set = EventSet(["A", "A", "B", "C"])
        assert event_set.get_event_type_counts_for_given_event_types(
            ["A", "B"]
        ) == {"A": 2, "B": 1}
        assert event_set.get_event_type_counts_for_given_event_types(
            ["A", "B", "C"]
        ) == {"A": 2, "B": 1, "C": 1}
        assert event_set.get_event_type_counts_for_given_event_types(
            ["A", "D"]
        ) == {"A": 2, "D": 0}
        assert event_set.get_event_type_counts_for_given_event_types(
            ["D", "E"]
        ) == {"D": 0, "E": 0}
        assert event_set.get_event_type_counts_for_given_event_types([]) == {}


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

    def test_get_event_set_counts(self) -> None:
        """Tests for method get_event_set_counts"""
        event = Event("A")
        event.event_sets = {
            EventSet(["B"]),
        }
        event_set_counts = event.get_event_set_counts()
        assert event_set_counts == {"B": {1}}

        event.event_sets = {
            EventSet(["B", "C"]),
            EventSet(["B", "B", "C"]),
            EventSet(["B", "C", "C"]),
        }
        event_set_counts = event.get_event_set_counts()
        assert event_set_counts == {"B": {1, 2}, "C": {1, 2}}

        event.event_sets = {
            EventSet(["B"]),
            EventSet(["B", "C"]),
            EventSet(["B", "C", "C"]),
        }
        event_set_counts = event.get_event_set_counts()
        assert event_set_counts == {"B": {1}, "C": {1, 2}}

        event.event_sets = {
            EventSet(["B", "C"]),
            EventSet(["B", "B", "C"]),
            EventSet(["B", "C", "C", "D"]),
        }
        event_set_counts = event.get_event_set_counts()
        assert event_set_counts == {"B": {1, 2}, "C": {1, 2}, "D": {1}}

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


def test_has_event_set_as_subset() -> None:
    """Test function has_event_set_as_subset"""
    # Test case 1: Has subset
    event1 = Event("A")
    event1.update_event_sets(["a", "b"])
    event1.update_event_sets(["b", "b"])
    event_sets_to_check1 = ["a"]
    assert has_event_set_as_subset(event1.event_sets, event_sets_to_check1)

    # Test case 2: No subset
    event2 = Event("A")
    event2.update_event_sets(["a", "b"])
    event2.update_event_sets(["b", "b"])
    event_sets_to_check2 = ["c"]
    assert not (
        has_event_set_as_subset(event2.event_sets, event_sets_to_check2)
    )

    # Test case 3: Empty event sets
    event3 = Event("A")
    event_sets_to_check3 = ["a"]
    assert not (
        has_event_set_as_subset(event3.event_sets, event_sets_to_check3)
    )

    # Test case 4: Both empty
    event4 = Event("A")
    event_sets_to_check4: list[str] = []
    assert not (
        has_event_set_as_subset(event4.event_sets, event_sets_to_check4)
    )


def test_get_reduced_event_set() -> None:
    """Test for function get_reduced_event_set"""
    event_sets = {
        EventSet(["B", "C"]),
        EventSet(["B", "B", "C"]),
        EventSet(["B", "C", "C"]),
    }
    reduced_event_set = get_reduced_event_set(event_sets)
    assert reduced_event_set == {frozenset(["B", "C"])}

    event_sets = {
        EventSet(["A"]),
        EventSet(["B"]),
        EventSet(["B", "C"]),
        EventSet(["B", "B", "C"]),
        EventSet(["B", "C", "C"]),
    }
    reduced_event_set = get_reduced_event_set(event_sets)
    assert reduced_event_set == {
        frozenset(["B", "C"]),
        frozenset(["A"]),
        frozenset(["B"]),
    }
