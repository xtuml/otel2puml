from tel2puml.detect_loops import Loop, detect_loops
from tel2puml.jAlergiaPipeline import audit_event_sequences_to_network_x
from tel2puml.pipelines.data_creation import (
    generate_test_data_event_sequences_from_puml,
)


class TestLoop():

    @staticmethod
    def test_init():
        loop = Loop(["A"])
        assert isinstance(loop.sub_loops, list)
        assert loop.nodes == ["A"]

    @staticmethod
    def test_get_node_cycles():
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

    @staticmethod
    def test_check_subloop():
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

    @staticmethod
    def test_get_sublist_of_length():
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
        loop = Loop(["A", "B", "C"])
        sub_loop = Loop(["B"])

        assert loop.sub_loops == []
        loop.add_subloop(sub_loop)
        assert loop.sub_loops == [sub_loop]


def test_detect_loops_from_puml():
    event_sequences = generate_test_data_event_sequences_from_puml(
        "puml_files/loop_loop_a.puml"
    )
    graph, references = audit_event_sequences_to_network_x(event_sequences)
    loops = detect_loops(graph, references)
    loop, = loops
    assert ["B", "C", "D"] in loop.get_node_cycles()
    assert len(loop.sub_loops) == 1
    sub_loop, = loop.sub_loops
    assert sub_loop.nodes == ["C"]
