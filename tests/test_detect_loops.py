"""Tests for the detect_loops module."""
from typing import Iterable, Any
import pytest

from networkx import DiGraph

from tel2puml.pipelines.data_ingestion import (
    update_all_connections_from_clustered_events,
)
from tel2puml.events import (
    events_to_markov_graph, get_event_reference_from_events
)
from tel2puml.detect_loops import (
    Loop,
    detect_loops,
    add_loop_edges_to_remove,
    update_subloops,
    merge_loops,
    update_break_points,
    merge_break_points,
    get_break_point_edges_to_remove_from_loop,
    update_break_point_edges_to_remove,
    get_all_break_points_from_loops,
    get_all_break_edges_from_loops,
    get_all_lonely_merge_killed_edges_from_loop_nodes_and_end_points,
    get_all_lonely_merge_killed_edges_from_loop,
    get_all_lonely_merge_killed_edges_from_loops,
    update_break_edges_and_exits
)
from tel2puml.pipelines.data_creation import (
    generate_test_data_event_sequences_from_puml,
)


class TestLoop():
    """Tests for the Loop class."""

    @staticmethod
    def test_init() -> None:
        """Test the __init__ method of the Loop class."""
        loop = Loop(["A"])
        assert isinstance(loop.sub_loops, list)
        assert loop.nodes == ["A"]
        assert loop.edges_to_remove == set()
        assert loop.break_edges == set()
        assert loop.break_points == set()
        assert loop.exit_points == set()
        assert not loop.merge_processed

    @staticmethod
    def test_get_edges() -> None:
        """Test the get_edges method of the Loop class."""
        loop = Loop(["A"])
        assert loop.get_edges() == {("A", "A")}

        loop = Loop(["A", "B"])
        assert loop.get_edges() == {("A", "B"), ("B", "A")}

        loop = Loop(["A", "B", "C"])
        assert loop.get_edges() == {("A", "B"), ("B", "C"), ("C", "A")}

        loop.set_merged()
        with pytest.raises(RuntimeError):
            loop.get_edges()

    @staticmethod
    def test_check_subloop() -> None:
        """Test the check_subloop method of the Loop class."""
        loop = Loop(["A", "B", "C", "D"])
        loop.add_edge_to_remove(("D", "A"))

        other = Loop(["A", "B", "C", "D"])
        assert not loop.check_subloop(other)

        other = Loop(["B"])
        other.add_edge_to_remove(("B", "B"))
        assert loop.check_subloop(other)

        other = Loop(["A", "B"])
        other.add_edge_to_remove(("B", "A"))
        assert loop.check_subloop(other)

        other = Loop(["C", "D"])
        other.add_edge_to_remove(("D", "C"))
        assert loop.check_subloop(other)

        other = Loop(["D", "A"])
        other.add_edge_to_remove(("D", "A"))
        assert not loop.check_subloop(other)

        other = Loop(["B", "D"])
        other.add_edge_to_remove(("D", "B"))
        assert not loop.check_subloop(other)

        other = Loop(["B", "D", "C"])
        other.add_edge_to_remove(("C", "B"))
        assert not loop.check_subloop(other)

        loop.set_merged()
        with pytest.raises(RuntimeError):
            loop.check_subloop(other)

    @staticmethod
    def test_add_edge_to_remove() -> None:
        """Test the add_edge_to_remove method of the Loop class."""
        loop = Loop(["A", "B", "C"])
        assert len(loop.edges_to_remove) == 0
        loop.add_edge_to_remove(("A", "B"))
        assert loop.edges_to_remove == {("A", "B")}

        loop.set_merged()
        with pytest.raises(RuntimeError):
            loop.add_edge_to_remove(("A", "B"))

    @staticmethod
    def test_add_break_edge() -> None:
        """Test the add_break_edge method of the Loop class."""
        loop = Loop(["A", "B", "C"])
        with pytest.raises(RuntimeError):
            loop.add_break_edge(("A", "B"))
        loop.set_merged()
        assert len(loop.break_edges) == 0
        loop.add_break_edge(("A", "B"))
        assert loop.break_edges == {("A", "B")}

    @staticmethod
    def test_add_break_point() -> None:
        """Test the add_break_point method of the Loop class."""
        loop = Loop(["A", "B", "C"])
        assert len(loop.break_points) == 0
        loop.add_break_point("A")
        assert loop.break_points == {"A"}

    @staticmethod
    def test_get_sublist_of_length() -> None:
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
    def test_add_subloop() -> None:
        """Test the add_subloop method of the Loop class."""
        loop = Loop(["A", "B", "C"])
        sub_loop = Loop(["B"])

        assert loop.sub_loops == []
        loop.add_subloop(sub_loop)
        assert loop.sub_loops == [sub_loop]

    @staticmethod
    def test_set_merge() -> None:
        """Test the set_merge method of the Loop class."""
        loop = Loop(["A", "B", "C"])
        assert not loop.merge_processed
        loop.set_merged()
        assert loop.merge_processed

    @staticmethod
    def test_set_exit_point() -> None:
        """Test the set_exit_point method of the Loop class."""
        loop = Loop(["A", "B", "C"])
        assert loop.exit_points == set()
        loop.set_exit_points({"A"})
        assert loop.exit_points == {"A"}

    @staticmethod
    def test_all_edges_to_remove() -> None:
        """Test the `all_edges_to_remove` property of the Loop class."""
        loop = Loop(["A", "B", "C", "D"])
        loop.add_edge_to_remove(("C", "A"))
        loop.break_point_edges_to_remove.add(("D", "E"))
        assert loop.all_edges_to_remove == {("C", "A"), ("D", "E")}

    @staticmethod
    def test_start_points() -> None:
        """Test the `start_points` property of the Loop class."""
        loop = Loop(["A", "B", "C", "D"])
        loop.add_edge_to_remove(("C", "A"))
        assert loop.start_points == {"A"}

    @staticmethod
    def test_end_points() -> None:
        """Test the `end_points` property of the Loop class."""
        loop = Loop(["A", "B", "C", "D"])
        loop.add_edge_to_remove(("C", "A"))
        loop.add_break_point("D")
        assert loop.end_points == {"D", "C"}

    @staticmethod
    def test_add_break_point_edges_to_remove() -> None:
        """Test the `add_break_point_edges_to_remove` method of the Loop class.
        """
        loop, graph = TestBreakPointFunctions.break_point_loop_and_graph()
        loop.add_break_point_edges_to_remove(graph)
        assert loop.break_point_edges_to_remove == {
            ("A", x) for x in "BCD"
        }


def _get_referenced_iterable(
    iterable: Iterable[Any],
    references: dict[str, str]
) -> Iterable[Any]:
    """Return referenced iterator.

    :param iterable: The iterable to get the references for.
    :type iterable: `Iterable`
    :param references: The references to use.
    :type references: `dict`[`str`, `str`]
    :return: The referenced iterable.
    :rtype: `Iterable`
    """
    if isinstance(iterable, list):
        return [references[item] for item in iterable]
    elif isinstance(iterable, tuple):
        return tuple(
            references[item] for item in iterable
            )
    elif isinstance(iterable, set):
        return {references[item] for item in iterable}
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
        assert loop.edges_to_remove == {("E", "B")}

    loops = [Loop(["B", "D"]), Loop(["C", "E"]), Loop(["B", "D", "C", "E"])]
    edges = [
        ("A", "B"), ("A", "C"), ("B", "D"), ("D", "B"), ("C", "E"),
        ("E", "C"), ("D", "C"), ("E", "B"), ("D", "F"), ("E", "F")
    ]
    loops = add_loop_edges_to_remove(loops, edges)
    assert len(loops) == 3
    for loop in loops:
        if {("B", "D"), ("D", "B")} == loop.get_edges():
            assert loop.edges_to_remove == {("D", "B")}
        elif {("C", "E"), ("E", "C")} == loop.get_edges():
            assert loop.edges_to_remove == {("E", "C")}
        else:
            assert loop.edges_to_remove == {
                ("E", "B"), ("D", "C")
            }

    loops = [Loop(["B", "D", "E"])]
    edges = [
        ('A', 'B'), ('B', 'D'), ('B', 'C'), ('C', 'F'),
        ('D', 'E'), ('E', 'B'), ('E', 'F')
    ]

    assert add_loop_edges_to_remove(loops, edges) == loops
    loop, = loops
    assert loop.edges_to_remove == {('E', 'B')}

    loops = [Loop(["B", "D", "E"])]
    edges = [
        ('A', 'B'), ('B', 'D'), ('B', 'C'), ('C', 'F'),
        ('D', 'E'), ('E', 'B'), ('E', 'F')
    ]

    assert add_loop_edges_to_remove(loops, edges) == loops
    loop, = loops
    assert loop.edges_to_remove == {('E', 'B')}


def test_update_break_edges_and_exits() -> None:
    """Test the update_break_edges_and_exits function."""
    def setup_and_check_case(
        loop: Loop,
        edges: list[tuple[str, str]],
        expected_break_edges: set[tuple[str, str]],
        expected_exit_points: set[str]
    ) -> None:
        loop.set_merged()
        loops = update_break_edges_and_exits([loop], edges)
        assert loops == [loop]
        assert loop.break_edges == expected_break_edges
        assert loop.exit_points == expected_exit_points
    # self loop
    loop = Loop(["B"])
    loop.add_edge_to_remove(("B", "B"))
    setup_and_check_case(
        loop, [("A", "B"), ("B", "C"), ("B", "B")], set(), {"C"}
    )
    # normal loop
    loop = Loop(["B", "C", "D"])
    loop.add_edge_to_remove(("D", "B"))
    setup_and_check_case(
        loop, [("A", "B"), ("B", "C"), ("C", "D"), ("D", "B"), ("D", "E")],
        set(), {"E"}
    )
    # dual exit point
    loop = Loop(["B", "C", "D"])
    loop.add_edge_to_remove(("D", "B"))
    setup_and_check_case(
        loop,
        [
            ("A", "B"), ("B", "C"), ("C", "D"), ("D", "B"), ("D", "E"),
            ("D", "F")
        ],
        set(), {"E", "F"}
    )
    # break point
    loop = Loop(["B", "C", "D"])
    loop.add_edge_to_remove(("D", "B"))
    setup_and_check_case(
        loop,
        [
            ("A", "B"), ("B", "C"), ("C", "D"), ("D", "B"), ("D", "E"),
            ("C", "F"), ("F", "E")
        ],
        {("C", "F")}, {"E"}
    )
    # break point with multiple break edges
    loop = Loop(["B", "C", "D"])
    loop.add_edge_to_remove(("D", "B"))
    setup_and_check_case(
        loop,
        [
            ("A", "B"), ("B", "C"), ("C", "D"), ("D", "B"), ("D", "E"),
            ("C", "F"), ("F", "E"), ("C", "G"), ("G", "E")
        ], {("C", "F"), ("C", "G")}, {"E"}
    )
    # break point in nested loop
    loop = Loop(["B", "C", "D", "E", "F"])
    loop.add_edge_to_remove(("E", "B"))
    sub_loop = Loop(["C", "D"])
    sub_loop.add_edge_to_remove(("D", "C"))
    loop.add_subloop(sub_loop)
    sub_loop.set_merged()
    setup_and_check_case(
        loop,
        [
            ("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"), ("E", "B"),
            ("C", "F"), ("F", "E"), ("D", "C"), ("E", "G")
        ], set(), {"G"}
    )
    assert sub_loop.break_edges == {("C", "F")}
    assert sub_loop.exit_points == {"E"}


def test_update_subloops() -> None:
    """Test the update_subloops function."""
    loop1 = Loop(["A"])
    loop2 = Loop(["A", "B", "C"])
    loop1.add_edge_to_remove(("A", "A"))
    loop2.add_edge_to_remove(("C", "A"))

    loops = [loop1, loop2]
    loops = update_subloops(loops)
    loop, = loops
    assert loop == loop2
    subloop, = loop.sub_loops
    assert subloop == loop1

    loop1 = Loop(["A", "B", "C"])
    loop2 = Loop(["A"])
    loop1.add_edge_to_remove(("A", "A"))
    loop2.add_edge_to_remove(("C", "A"))

    loops = [loop1, loop2]
    loops = update_subloops(loops)
    loop, = loops
    assert loop == loop1
    subloop, = loop.sub_loops
    assert subloop == loop2

    loop1 = Loop(["A"])
    loop2 = Loop(["A", "B", "C"])
    loop3 = Loop(["A", "B", "C", "D"])
    loop1.add_edge_to_remove(("A", "A"))
    loop2.add_edge_to_remove(("C", "A"))
    loop3.add_edge_to_remove(("D", "A"))

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
    loop1.add_edge_to_remove(("A", "A"))
    loop2.add_edge_to_remove(("C", "B"))
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
        ("E", "B"), ("D", "C")
    }

    assert len(loop.sub_loops) == 2
    for subloop in loop.sub_loops:
        assert len(subloop.sub_loops) == 0
        if set(subloop.nodes) == {"B", "D"}:
            assert subloop.edges_to_remove == {("D", "B")}
        else:
            assert set(subloop.nodes) == {"C", "E"}
            assert subloop.edges_to_remove == {("E", "C")}


def test_update_break_points() -> None:
    """Test the update_break_points function."""
    graph = DiGraph(
        [
            ("A", "B"), ("B", "D"), ("B", "C"),
            ("C", "E"), ("D", "A"), ("D", "E")
        ]
    )

    loop = Loop(["A", "B", "D"])
    loop.set_merged()
    loop.add_break_edge(("B", "C"))
    loop.exit_points = {"E"}

    loops = [loop]
    loops = update_break_points(graph, loops)
    loop, = loops
    assert loop.break_edges == {("B", "C")}
    assert loop.break_points == {"C"}
    assert set(loop.nodes) == {"A", "B", "C", "D"}

    graph = DiGraph(
        [
            ("A", "B"), ("B", "D"), ("D", "B"),
            ("B", "B"), ("B", "C"), ("D", "E"),
            ("C", "E"),
        ]
    )
    loop = Loop(["B", "D"])
    sub_loop = Loop(["D"])
    sub_loop.exit_points = {"B"}
    loop.set_merged()
    loop.add_break_edge(("B", "C"))
    loop.sub_loops = [sub_loop]
    loop.exit_points = {"E"}

    loops = [loop]
    loops = update_break_points(graph, loops)
    loop, = loops
    assert set(loop.nodes) == {"B", "C", "D"}
    assert loop.break_edges == {("B", "C")}
    assert loop.break_points == {"C"}
    sub_loop, = loop.sub_loops
    assert set(sub_loop.nodes) == {"D"}
    assert sub_loop.break_edges == set()
    assert sub_loop.break_points == set()


def test_merge_break_points() -> None:
    """Test the merge_break_points function."""
    loop1 = Loop(["A", "B", "C", "D"])
    loop2 = Loop(["C"])

    loops = [loop1, loop2]
    loops = merge_break_points(loops)
    loop, = loops
    assert set(loop.nodes) == {"A", "B", "C", "D"}
    assert loop.sub_loops == [loop2]

    loop1 = Loop(["A", "B", "C", "D"])
    loop2 = Loop(["C", "D"])
    loop1.sub_loops = [loop2]
    loop3 = Loop(["C"])

    loops = [loop1, loop3]
    loops = merge_break_points(loops)
    loop, = loops
    assert set(loop.nodes) == {"A", "B", "C", "D"}
    sub_loop, = loop.sub_loops
    assert set(sub_loop.nodes) == {"C", "D"}
    sub_sub_loop, = sub_loop.sub_loops
    assert set(sub_sub_loop.nodes) == {"C"}


def test_detect_loops_from_simple_puml() -> None:
    """Test the detect_loops function with a simple puml file."""
    event_sequences = generate_test_data_event_sequences_from_puml(
        "puml_files/loop_loop_a.puml"
    )
    forward, _ = update_all_connections_from_clustered_events(
        event_sequences
    )
    graph = events_to_markov_graph(forward.values())
    references = get_event_reference_from_events(forward.values())
    loops = detect_loops(graph)
    loop, = loops
    loop.merge_processed = False
    assert loop.get_edges() == {
        _get_referenced_iterable(("B", "C"), references),
        _get_referenced_iterable(("C", "D"), references),
        _get_referenced_iterable(("D", "B"), references)
    }
    assert loop.edges_to_remove == {
        _get_referenced_iterable(("D", "B"), references)
    }
    assert loop.exit_points == _get_referenced_iterable({"E"}, references)
    sub_loop, = loop.sub_loops
    assert sub_loop.nodes == _get_referenced_iterable(["C"], references)
    assert sub_loop.edges_to_remove == {
        _get_referenced_iterable(("C", "C"), references)
    }
    assert sub_loop.exit_points == _get_referenced_iterable({"D"}, references)


def test_detect_loops_from_XOR_puml() -> None:
    """Test the detect_loops function with a XOR puml file."""
    event_sequences = generate_test_data_event_sequences_from_puml(
        "puml_files/loop_XORFork_a.puml"
    )
    forward, _ = update_all_connections_from_clustered_events(
        event_sequences
    )
    graph = events_to_markov_graph(forward.values())
    references = get_event_reference_from_events(forward.values())
    loops = detect_loops(graph)
    loop, = loops
    assert set(loop.nodes) == _get_referenced_iterable(
        {"B", "C", "D", "E", "F"}, references
    )
    assert loop.edges_to_remove == {
        _get_referenced_iterable(("F", "B"), references)
    }
    assert loop.break_edges == set()
    assert loop.exit_points == _get_referenced_iterable({"G"}, references)
    assert len(loop.sub_loops) == 0


def test_detect_loops_from_AND_puml() -> None:
    """Test the detect_loops function with a AND puml file."""
    event_sequences = generate_test_data_event_sequences_from_puml(
        "puml_files/loop_ANDFork_a.puml"
    )
    forward, _ = update_all_connections_from_clustered_events(
        event_sequences
    )
    graph = events_to_markov_graph(forward.values())
    references = get_event_reference_from_events(forward.values())
    loops = detect_loops(graph)
    loop, = loops
    assert set(loop.nodes) == _get_referenced_iterable(
        {"B", "C", "D", "E"}, references
    )
    assert loop.edges_to_remove == {
        _get_referenced_iterable(("E", "B"), references)
    }
    assert loop.break_edges == set()
    assert loop.exit_points == _get_referenced_iterable({"F"}, references)
    assert len(loop.sub_loops) == 0


def test_detect_loops_from_simple_break_puml() -> None:
    """Test the detect_loops function with a simple loop and break puml
    file."""
    event_sequences = generate_test_data_event_sequences_from_puml(
        "puml_files/simple_loop_with_break.puml"
    )
    forward, _ = update_all_connections_from_clustered_events(
        event_sequences
    )
    graph = events_to_markov_graph(forward.values())
    references = get_event_reference_from_events(forward.values())
    loops = detect_loops(graph)
    loop, = loops
    assert set(loop.nodes) == _get_referenced_iterable(
        {"B", "C", "D", "E", "F"}, references
    )
    assert loop.edges_to_remove == {
        _get_referenced_iterable(("F", "B"), references)
    }
    assert loop.break_edges == {
        _get_referenced_iterable(("B", "C"), references)
    }
    assert loop.break_points == _get_referenced_iterable({"D"}, references)
    assert loop.exit_points == _get_referenced_iterable({"G"}, references)
    assert len(loop.sub_loops) == 0


def test_detect_loops_from_complex_break_puml() -> None:
    """Test the detect_loops function with a complex loop and break puml
    file"""
    event_sequences = generate_test_data_event_sequences_from_puml(
        "puml_files/complex_loop_with_break.puml"
    )
    forward, _ = update_all_connections_from_clustered_events(
        event_sequences
    )
    graph = events_to_markov_graph(forward.values())
    references = get_event_reference_from_events(forward.values())
    loops = detect_loops(graph)
    loop, = loops
    assert set(loop.nodes) == _get_referenced_iterable(
        {"B", "C", "D", "E", "F"}, references
    )
    assert loop.edges_to_remove == {
        _get_referenced_iterable(("F", "B"), references)
    }
    assert loop.break_edges == {
        _get_referenced_iterable(("B", "C"), references),
    }
    assert loop.break_points == _get_referenced_iterable({"D"}, references)
    assert loop.exit_points == _get_referenced_iterable({"G"}, references)

    for sub_loop in loop.sub_loops:
        if set(sub_loop.nodes) == _get_referenced_iterable(
            {"C"}, references
        ):
            assert sub_loop.edges_to_remove == {
                _get_referenced_iterable(("C", "C"), references)
            }
            assert sub_loop.break_edges == set()
            assert sub_loop.break_points == set()
            assert sub_loop.exit_points == _get_referenced_iterable(
                {"D"}, references
            )
        else:
            assert set(sub_loop.nodes) == _get_referenced_iterable(
                {"F"}, references
            )
            assert sub_loop.edges_to_remove == {
                _get_referenced_iterable(("F", "F"), references)
            }
            assert sub_loop.break_edges == set()
            assert sub_loop.break_points == set()
            assert sub_loop.exit_points == _get_referenced_iterable(
                {"B", "G"}, references
            )


def test_detect_loops_from_2_break_puml() -> None:
    """Test the detect_loops function with a loop with 2 breaks puml
    file"""
    event_sequences = generate_test_data_event_sequences_from_puml(
        "puml_files/loop_with_2_breaks.puml"
    )
    forward, _ = update_all_connections_from_clustered_events(
        event_sequences
    )
    graph = events_to_markov_graph(forward.values())
    references = get_event_reference_from_events(forward.values())
    loops = detect_loops(graph)
    loop, = loops
    assert set(loop.nodes) == _get_referenced_iterable(
        {"B", "C", "D", "E", "F", "G", "H"}, references
    )
    assert loop.edges_to_remove == {
        _get_referenced_iterable(("H", "B"), references)
    }
    assert loop.break_edges == {
        _get_referenced_iterable(("B", "C"), references),
        _get_referenced_iterable(("D", "E"), references),
    }
    assert loop.break_points == _get_referenced_iterable(
        {"C", "G"}, references
    )
    assert loop.exit_points == _get_referenced_iterable({"I"}, references)

    assert len(loop.sub_loops) == 0


@pytest.mark.skip("audit_event_sequences_to_network_x fails for this puml")
def test_detect_loops_from_break_loop_in_break_loop_puml() -> None:
    """Test the detect_loops function with a break loop in break loop puml
    file"""
    event_sequences = generate_test_data_event_sequences_from_puml(
        "puml_files/break_loop_in_break_loop.puml"
    )
    event_sequences = generate_test_data_event_sequences_from_puml(
        "puml_files/loop_XORFork_a.puml"
    )
    forward, _ = update_all_connections_from_clustered_events(
        event_sequences
    )
    graph = events_to_markov_graph(forward.values())
    references = get_event_reference_from_events(forward.values())
    loops = detect_loops(graph)
    loop, = loops
    assert set(loop.nodes) == _get_referenced_iterable(
        {"B", "C", "D", "E", "F", "G", "H"}, references
    )
    assert loop.edges_to_remove == {
        _get_referenced_iterable(("H", "B"), references)
    }
    assert loop.break_edges == {
        _get_referenced_iterable(("B", "C"), references),
    }
    assert loop.break_points == _get_referenced_iterable({"F"}, references)
    assert loop.exit_points == _get_referenced_iterable({"I"}, references)

    sub_loop, = loop.sub_loops
    assert set(sub_loop.nodes) == _get_referenced_iterable(
        {"C", "D", "E"}, references
    )
    assert sub_loop.edges_to_remove == {
        _get_referenced_iterable(("E", "C"), references)
    }
    assert sub_loop.break_edges == {
        _get_referenced_iterable(("C", "D"), references),
    }
    assert sub_loop.break_points == _get_referenced_iterable({"D"}, references)
    assert sub_loop.exit_points == _get_referenced_iterable({"F"}, references)
    assert len(sub_loop.sub_loops) == 0


def test_detect_loops_from_loop_break_split_exit_puml() -> None:
    """Test the detect_loops function with a loop break split exit puml file"""
    event_sequences = generate_test_data_event_sequences_from_puml(
        "puml_files/loop_break_split_exit.puml"
    )
    forward, _ = update_all_connections_from_clustered_events(
        event_sequences
    )
    graph = events_to_markov_graph(forward.values())
    references = get_event_reference_from_events(forward.values())
    loops = detect_loops(graph)
    loop, = loops
    assert set(loop.nodes) == _get_referenced_iterable(
        {"B", "C", "D"}, references
    )
    assert loop.edges_to_remove == {
        _get_referenced_iterable(("D", "B"), references)
    }
    assert loop.break_edges == {
        _get_referenced_iterable(("B", "C"), references),
    }
    assert loop.break_points == _get_referenced_iterable(
        {"C"}, references
    )
    assert loop.exit_points == _get_referenced_iterable(
        {"E", "F"}, references
    )

    assert len(loop.sub_loops) == 0


class TestBreakPointFunctions:
    """Tests for the break point functions."""
    @staticmethod
    def break_point_loop_and_graph() -> tuple[Loop, DiGraph]:
        """Return a loop and graph with break points."""
        graph = DiGraph()
        graph.add_edge("A", "B")
        graph.add_edge("A", "C")
        graph.add_edge("A", "D")
        loop = Loop(["A"])
        loop.set_merged()
        loop.add_break_edge(("X", "A"))
        sub_loop = Loop(["E"])
        sub_loop.set_merged()
        sub_loop.add_break_edge(("Y", "E"))
        graph.add_edge("E", "F")
        sub_loop.add_break_point("E")
        loop.add_subloop(sub_loop)
        loop.add_break_point("A")
        return loop, graph

    def test_get_break_point_edges_to_remove_from_loop(self) -> None:
        """Test the `get_break_point_edges_to_remove_from_loop` function."""
        loop, graph = self.break_point_loop_and_graph()
        break_edges = get_break_point_edges_to_remove_from_loop(
            graph, loop
        )
        assert break_edges == [("A", "B"), ("A", "C"), ("A", "D")]

    def test_update_break_point_edges_to_remove(self) -> None:
        """Test the `update_break_point_edges_to_remove` function."""
        loop, graph = self.break_point_loop_and_graph()
        update_break_point_edges_to_remove(graph, [loop])
        assert loop.break_point_edges_to_remove == {
            ("A", "B"), ("A", "C"), ("A", "D")
        }
        assert loop.sub_loops[0].break_point_edges_to_remove == {("E", "F")}

    def test_get_all_break_points_from_loops(self) -> None:
        """Test the `get_all_break_points_from_loops` function."""
        loop, _ = self.break_point_loop_and_graph()
        break_points = get_all_break_points_from_loops([loop])
        assert break_points == {"A", "E"}

    def test_get_all_break_edges_from_loops(self) -> None:
        """Test the `get_all_break_edges_from_loops` function."""
        loop, _ = self.break_point_loop_and_graph()
        break_edges = get_all_break_edges_from_loops([loop])
        assert break_edges == {("X", "A"), ("Y", "E")}


class TestLoopLonelyMerges:
    """Tests for the lonely merge detection functions."""
    def lonely_merge_graph(self) -> DiGraph:
        """Return a graph with lonely merges."""
        graph = DiGraph()
        graph.add_edge("A", "B")
        graph.add_edge("B", "C")
        graph.add_edge("B", "D")
        graph.add_edge("B", "E")
        graph.add_edge("C", "F")
        graph.add_edge("F", "G")
        graph.add_edge("D", "H")
        graph.add_edge("D", "I")
        graph.add_edge("H", "J")
        graph.add_edge("H", "K")
        graph.add_edge("J", "L")
        graph.add_edge("K", "L")
        graph.add_edge("L", "M")
        return graph

    def lonely_merge_loop(self) -> Loop:
        """Return a loop with lonely merges."""
        loop = Loop(
            ["B", "C", "D", "E", "F", "H", "I", "J", "K", "L", "M"]
        )
        loop.add_edge_to_remove(("F", "B"))
        sub_loop = Loop(["D", "H", "I", "J", "K"])
        sub_loop.add_edge_to_remove(("K", "D"))
        sub_loop.add_edge_to_remove(("J", "D"))
        loop.add_subloop(sub_loop)
        return loop

    def lonely_merge_negative_test_graph(self) -> DiGraph:
        """Return a graph with no lonely merges."""
        graph = DiGraph()
        graph.add_edge("A", "B")
        graph.add_edge("B", "C")
        graph.add_edge("C", "D")
        graph.add_edge("C", "E")
        graph.add_edge("B", "F")
        graph.add_edge("F", "G")
        return graph

    @staticmethod
    def get_and_check_lonely_merge_killed_edges(
        graph: DiGraph,
        loop_nodes: set[str],
        end_points: set[str],
        expected_lonely_merge_killed_edges: set[tuple[str, str]]
    ) -> None:
        """Get and check lonely merge killed edges."""
        lonely_merge_killed_edges = {
            edge
            for edge in
            get_all_lonely_merge_killed_edges_from_loop_nodes_and_end_points(
                graph, loop_nodes, end_points
            )
        }
        assert lonely_merge_killed_edges == expected_lonely_merge_killed_edges

    def test_get_all_lonely_merge_killed_edges_from_loop_nodes_and_end_points(
        self
    ) -> None:
        """Test the
        `get_all_lonely_merge_killed_edges_from_loop_nodes_and_end_points`
        function.
        """
        graph = self.lonely_merge_graph()
        # test parent loop containing sub loop that occurs on a kill path
        # for correct detection of lonely merge
        loop_nodes = {"B", "C", "D", "E", "F", "H", "I", "J", "K"}
        end_points = {"G"}
        self.get_and_check_lonely_merge_killed_edges(
            graph, loop_nodes, end_points,
            {("B", "D"), ("B", "E")}
        )
        # test sub loop with multiple loop end points
        loop_nodes = {"D", "H", "I", "J", "K", "L"}
        end_points = {"K", "L"}
        self.get_and_check_lonely_merge_killed_edges(
            graph, loop_nodes, end_points, {("D", "I")}
        )
        # negative tests
        graph = self.lonely_merge_negative_test_graph()
        # test all nodes killed on node
        loop_nodes = {"C"}
        end_points = {"F"}
        self.get_and_check_lonely_merge_killed_edges(
            graph, loop_nodes, end_points, set()
        )
        # test single out edge
        loop_nodes = {"F"}
        end_points = {"G"}
        self.get_and_check_lonely_merge_killed_edges(
            graph, loop_nodes, end_points, set()
        )
        # test node is end point node
        loop_nodes = {"C"}
        end_points = {"C"}
        self.get_and_check_lonely_merge_killed_edges(
            graph, loop_nodes, end_points, set()
        )

    def test_get_all_lonely_merge_killed_edges_from_loop(self) -> None:
        """Test the `get_all_lonely_merge_killed_edges_from_loop` function."""
        killed_edges = {
            edge
            for edge in
            get_all_lonely_merge_killed_edges_from_loop(
                self.lonely_merge_graph(), self.lonely_merge_loop()
            )
        }
        assert killed_edges == {("B", "D"), ("B", "E"), ("D", "I")}

    def test_get_all_lonely_merge_killed_edges_from_loops(self) -> None:
        """Test the `get_all_lonely_merge_killed_edges_from_loops` function."""
        loop = self.lonely_merge_loop()
        killed_edges = get_all_lonely_merge_killed_edges_from_loops(
            self.lonely_merge_graph(), [loop]
        )
        assert killed_edges == {("B", "D"), ("B", "E"), ("D", "I")}
