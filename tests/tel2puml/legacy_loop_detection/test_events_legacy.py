"""Tests for the tel2puml.events module."""

from tel2puml.legacy_loop_detection.events import (
    get_loop_events_to_remove_mapping,
    remove_detected_loop_data_from_events,
    remove_detected_loop_events,
)
from tel2puml.events import Event, EventSet
from tel2puml.legacy_loop_detection.detect_loops import Loop


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
        self,
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
            loops, events, node_event_name_reference
        )
        assert len(events["C"].event_sets) == 1
        assert len(events["E"].event_sets) == 0
        assert len(events["A"].event_sets) == 1
        assert len(events["B"].event_sets) == 1
        assert len(events["D"].event_sets) == 1
