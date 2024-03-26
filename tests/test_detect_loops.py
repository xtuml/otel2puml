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


def test_detect_loops_from_puml():
    event_sequences = generate_test_data_event_sequences_from_puml(
            "puml_files/loop_loop_a.puml"
        )
    graph, references = audit_event_sequences_to_network_x(event_sequences)
    loops = detect_loops(graph, references)
