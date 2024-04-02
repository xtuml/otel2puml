"""Tests for the detect_loops module."""
from typing import Iterable
import pytest

from tel2puml.detect_loops import (
    Loop,
    detect_loops,
    add_loop_edges_to_remove,
    update_subloops,
    merge_loops
)
from tel2puml.jAlergiaPipeline import audit_event_sequences_to_network_x
from tel2puml.pipelines.data_creation import (
    generate_test_data_event_sequences_from_puml,
)


class TestLoop():
    """Tests for the Loop class."""

    @staticmethod
    def test_init():
        """Test the __init__ method of the Loop class."""
        loop = Loop(["A"])
        assert isinstance(loop.sub_loops, list)
        assert loop.nodes == ["A"]
        assert loop.edges_to_remove == set()

    @staticmethod
    def test_get_node_cycles():
        """Test the get_node_cycles method of the Loop class."""
        loop = Loop(["A"])
        assert loop.get_node_cycles() == [["A"]]

        loop = Loop(["A", "B"])
        assert loop.get_node_cycles() == [
            ["A", "B"],
            ["B", "A"]
        ]

        loop = Loop(["A", "B", "C"])
        assert loop.get_node_cycles() == [
            ["A", "B", "C"],
            ["B", "C", "A"],
            ["C", "A", "B"]
        ]

        loop.set_merged()
        with pytest.raises(RuntimeError):
            loop.get_node_cycles()

    @staticmethod
    def test_check_subloop():
        """Test the check_subloop method of the Loop class."""
        loop = Loop(["A", "B", "C", "D"])

        other = Loop(["A", "B", "C", "D"])
        assert not loop.check_subloop(other)

        other = Loop(["B"])
        assert loop.check_subloop(other)

        other = Loop(["A", "B"])
        assert loop.check_subloop(other)

        other = Loop(["C", "D"])
        assert loop.check_subloop(other)

        other = Loop(["D", "A"])
        assert loop.check_subloop(other)

        other = Loop(["B", "D"])
        assert not loop.check_subloop(other)

        other = Loop(["B", "D", "C"])
        assert not loop.check_subloop(other)

        loop.set_merged()
        with pytest.raises(RuntimeError):
            loop.check_subloop(other)

    def test_add_edge_to_remove(self):
        """Test the add_edge_to_remove method of the Loop class."""
        loop = Loop(["A", "B", "C"])
        assert len(loop.edges_to_remove) == 0
        loop.add_edge_to_remove(("A", "B"))
        assert loop.edges_to_remove == {("A", "B")}

        loop.set_merged()
        with pytest.raises(RuntimeError):
            loop.add_edge_to_remove(("A", "B"))

    @staticmethod
    def test_get_sublist_of_length():
        """Test the get_sublist_of_length method of the Loop class."""
        loop = Loop(["A"])
        assert loop.get_sublist_of_length(["A"], 1) == [["A"]]

        loop = Loop(["A", "B"])
        assert loop.get_sublist_of_length(["A", "B"], 1) == [["A"], ["B"]]
        assert loop.get_sublist_of_length(["A", "B"], 2) == [
            ["A", "B"],
            ["B", "A"]
        ]

        loop = Loop(["A", "B", "C", "D"])
        assert loop.get_sublist_of_length(["A", "B", "C", "D"], 1) == [
            ["A"], ["B"], ["C"], ["D"]
        ]
        assert loop.get_sublist_of_length(["A", "B", "C", "D"], 2) == [
            ["A", "B"], ["B", "C"], ["C", "D"], ["D", "A"]
        ]
        assert loop.get_sublist_of_length(["A", "B", "C", "D"], 3) == [
            ["A", "B", "C"], ["B", "C", "D"], ["C", "D", "A"], ["D", "A", "B"]
        ]
        assert loop.get_sublist_of_length(["A", "B", "C", "D"], 4) == [
            ["A", "B", "C", "D"],
            ["B", "C", "D", "A"],
            ["C", "D", "A", "B"],
            ["D", "A", "B", "C"],
        ]

    @staticmethod
    def test_add_subloop():
        """Test the add_subloop method of the Loop class."""
        loop = Loop(["A", "B", "C"])
        sub_loop = Loop(["B"])

        assert loop.sub_loops == []
        loop.add_subloop(sub_loop)
        assert loop.sub_loops == [sub_loop]

        loop.set_merged()
        with pytest.raises(RuntimeError):
            loop.add_subloop(sub_loop)

    @staticmethod
    def test_set_merge():
        """Test the set_merge method of the Loop class."""
        loop = Loop(["A", "B", "C"])
        assert not loop.merge_processed
        loop.set_merged()
        assert loop.merge_processed


def _get_referenced_iterable(
        iterable: Iterable,
        references: dict[str, dict[str, str]]
) -> Iterable:
    """Return referenced iterator.

    :param iterable: The iterable to get the references for.
    :type iterable: `Iterable`
    :param references: The references to use.
    :type references: `dict`[`str`, `dict`[`str`, `str`]]
    :return: The referenced iterable.
    :rtype: `Iterable`
    """
    if isinstance(iterable, list):
        return [references["node_reference"][item][0] for item in iterable]
    elif isinstance(iterable, tuple):
        return tuple(
            references["node_reference"][item][0] for item in iterable
            )
    elif isinstance(iterable, set):
        return {references["node_reference"][item][0] for item in iterable}
    else:
        raise TypeError("Unsupported type")


def test_add_loop_edges_to_remove() -> None:
    """Test the add_loop_edges_to_remove function."""
    loops = [Loop(["B"])]
    edges = [("A", "B"), ("B", "C"), ("B", "B")]
    loops = add_loop_edges_to_remove(loops, edges)
    loop, = loops
    assert loop.edges_to_remove == {("B", "B")}

    loops = [Loop(["B", "C", "D"])]
    edges = [("A", "B"), ("B", "C"), ("C", "D"), ("D", "B"), ("D", "E")]
    loops = add_loop_edges_to_remove(loops, edges)
    loop, = loops
    assert loop.edges_to_remove == {("D", "B")}

    loops = [Loop(["B", "C", "D"])]
    edges = [("D", "B"), ("D", "E"), ("A", "B"), ("C", "D"), ("B", "C")]
    loops = add_loop_edges_to_remove(loops, edges)
    loop, = loops
    assert loop.edges_to_remove == {("D", "B")}

    loops = [Loop(["B", "C", "E"]), Loop(["B", "D", "E"])]
    edges = [
        ("A", "B"), ("B", "C"), ("C", "E"),
        ("D", "E"), ("B", "D"), ("E", "F"),
        ("E", "B")
    ]
    loops = add_loop_edges_to_remove(loops, edges)
    assert len(loops) == 2
    for loop in loops:
        loop.edges_to_remove == {("E", "B")}

    loops = [Loop(["B", "D"]), Loop(["C", "E"]), Loop(["B", "D", "C", "E"])]
    edges = [
        ("A", "B"), ("A", "C"), ("B", "D"), ("D", "B"), ("C", "E"),
        ("E", "C"), ("D", "C"), ("E", "B"), ("D", "F"), ("E", "F")
    ]
    loops = add_loop_edges_to_remove(loops, edges)
    assert len(loops) == 3
    for loop in loops:
        if ["B", "D"] in loop.get_node_cycles():
            assert loop.edges_to_remove == {("D", "B")}
        elif ["C", "E"] in loop.get_node_cycles():
            assert loop.edges_to_remove == {("E", "C")}
        else:
            assert loop.edges_to_remove == {
                ("E", "B"), ("D", "C"), ("D", "B"), ("E", "C")
            }


def test_update_subloops() -> None:
    """Test the update_subloops function."""
    loop1 = Loop(["A"])
    loop2 = Loop(["A", "B", "C"])

    loops = [loop1, loop2]
    loops = update_subloops(loops)
    loop, = loops
    assert loop == loop2
    subloop, = loop.sub_loops
    assert subloop == loop1

    loop1 = Loop(["A", "B", "C"])
    loop2 = Loop(["A"])

    loops = [loop1, loop2]
    loops = update_subloops(loops)
    loop, = loops
    assert loop == loop1
    subloop, = loop.sub_loops
    assert subloop == loop2

    loop1 = Loop(["A"])
    loop2 = Loop(["D", "A"])
    loop3 = Loop(["A", "B", "C", "D"])

    loops = [loop1, loop2, loop3]
    loops = update_subloops(loops)
    loop, = loops
    assert loop == loop3
    subloop, = loop.sub_loops
    assert subloop == loop2
    subsubloop, = subloop.sub_loops
    assert subsubloop == loop1

    loop1 = Loop(["A"])
    loop2 = Loop(["B", "C"])
    loops = [loop1, loop2]
    loops = update_subloops(loops)
    assert len(loops) == 2
    assert loops[0] == loop1
    assert loops[1] == loop2


def test_merge_loops() -> None:
    """Test the merge_loops function."""
    loop1 = Loop(["A", "B", "D"])
    loop1.add_edge_to_remove(("D", "A"))
    loop2 = Loop(["A", "C", "D"])
    loop2.add_edge_to_remove(("D", "A"))

    loops = [loop1, loop2]
    loops = update_subloops(loops)
    loops = merge_loops(loops)

    loop, = loops
    assert set(loop.nodes) == {"A", "B", "C", "D"}
    assert loop.edges_to_remove == {("D", "A")}

    loop1 = Loop(["B", "D"])
    loop1.add_edge_to_remove(("D", "B"))
    loop2 = Loop(["C", "E"])
    loop2.add_edge_to_remove(("E", "C"))
    loop3 = Loop(["B", "D", "C", "E"])
    loop3.add_edge_to_remove(("D", "C"))
    loop3.add_edge_to_remove(("D", "B"))
    loop3.add_edge_to_remove(("E", "C"))
    loop3.add_edge_to_remove(("E", "B"))

    loops = [loop1, loop2, loop3]
    loops = update_subloops(loops)
    loops = merge_loops(loops)

    loop, = loops
    assert set(loop.nodes) == {"B", "C", "D", "E"}
    assert loop.edges_to_remove == {
        ("D", "B"), ("E", "C"), ("E", "B"), ("D", "C")
    }

    assert len(loop.sub_loops) == 2
    for subloop in loop.sub_loops:
        assert len(subloop.sub_loops) == 0
        if set(subloop.nodes) == {"B", "D"}:
            assert subloop.edges_to_remove == {("D", "B")}
        else:
            assert set(subloop.nodes) == {"C", "E"}
            assert subloop.edges_to_remove == {("E", "C")}


def test_detect_loops_from_simple_puml():
    """Test the detect_loops function with a simple puml file."""
    event_sequences = generate_test_data_event_sequences_from_puml(
        "puml_files/loop_loop_a.puml"
    )
    graph, references = audit_event_sequences_to_network_x(event_sequences)
    loops = detect_loops(graph, references)
    loop, = loops
    loop.merge_processed = False
    assert _get_referenced_iterable(
        ["B", "C", "D"], references
        ) in loop.get_node_cycles()
    assert loop.edges_to_remove == {
        _get_referenced_iterable(("D", "B"), references)
    }
    sub_loop, = loop.sub_loops
    assert sub_loop.nodes == _get_referenced_iterable(["C"], references)
    assert sub_loop.edges_to_remove == {
        _get_referenced_iterable(("C", "C"), references)
    }


def test_detect_loops_from_XOR_puml():
    """Test the detect_loops function with a XOR puml file."""
    event_sequences = generate_test_data_event_sequences_from_puml(
        "puml_files/loop_XORFork_a.puml"
    )
    graph, references = audit_event_sequences_to_network_x(event_sequences)
    loops = detect_loops(graph, references)
    loop, = loops
    assert set(loop.nodes) == _get_referenced_iterable(
        {"B", "C", "D", "E", "F"}, references
    )
    assert loop.edges_to_remove == {
        _get_referenced_iterable(("F", "B"), references)
    }
    assert len(loop.sub_loops) == 0


def test_detect_loops_from_AND_puml():
    """Test the detect_loops function with a AND puml file."""
    event_sequences = generate_test_data_event_sequences_from_puml(
        "puml_files/loop_ANDFork_a.puml"
    )
    graph, references = audit_event_sequences_to_network_x(event_sequences)
    loops = detect_loops(graph, references)
    loop, = loops
    assert set(loop.nodes) == _get_referenced_iterable(
        {"B", "C", "D", "E"}, references
    )
    assert loop.edges_to_remove == {
        _get_referenced_iterable(("E", "B"), references)
    }
    assert len(loop.sub_loops) == 0
