"""Tests for the check_puml_equiv module."""

from test_event_generator.io.parse_puml import EventData

from tel2puml.check_puml_equiv import (
    create_networkx_graph_from_parsed_puml,
    check_networkx_graph_equivalence,
    get_network_x_graph_from_puml_string,
    check_puml_equivalence
)


def test_create_networkx_graph_from_parsed_puml() -> None:
    # setup events
    events = {}
    for event_string in ["A", "B", "C", "D", "E", "F", "G"]:
        event_data = EventData()
        event_data.event_type = event_string
        event_data.occurence_id = 0
        events[event_data.event_tuple] = event_data
    # setup parsed puml
    parsed_puml = [
        events[("A", 0)], ("START", "LOOP"), events[("B", 0)],
        ("START", "XOR"), ("PATH", "XOR"), events[("C", 0)],
        ("PATH", "XOR"), ("START", "AND"), ("PATH", "AND"),
        events[("D", 0)], ("PATH", "AND"), events[("E", 0)],
        ("END", "AND"), ("END", "XOR"), events[("F", 0)],
        ("END", "LOOP"), events[("G", 0)]
    ]
    # create graph
    graph = create_networkx_graph_from_parsed_puml(parsed_puml)
    expected_edges = [
        (('A', 0), ('START', 'LOOP', 1)),
        (('START', 'LOOP', 1), ('B', 0)),
        (('B', 0), ('START', 'XOR', 1)),
        (('START', 'XOR', 1), ('C', 0)),
        (('START', 'XOR', 1), ('START', 'AND', 1)),
        (('C', 0), ('END', 'XOR', 1)),
        (('END', 'XOR', 1), ('F', 0)),
        (('START', 'AND', 1), ('D', 0)),
        (('START', 'AND', 1), ('E', 0)),
        (('D', 0), ('END', 'AND', 1)),
        (('END', 'AND', 1), ('END', 'XOR', 1)),
        (('E', 0), ('END', 'AND', 1)),
        (('F', 0), ('END', 'LOOP', 1)),
        (('END', 'LOOP', 1), ('G', 0))
    ]
    for edge in graph.edges:
        edge_tuple = (edge[0].node_id, edge[1].node_id)
        assert edge_tuple in expected_edges
        expected_edges.remove(edge_tuple)
    assert len(expected_edges) == 0


def test_check_networkx_graph_equivalence_same_graph() -> None:
    with open(
        "puml_files/bunched_XOR_switch.puml", "r", encoding="utf-8"
    ) as file:
        puml_string = file.read()
    graph = next(get_network_x_graph_from_puml_string(puml_string))
    with open(
        "puml_files/bunched_XOR_switch.puml", "r", encoding="utf-8"
    ) as file:
        puml_string = file.read()
    graph2 = next(get_network_x_graph_from_puml_string(puml_string))
    assert check_networkx_graph_equivalence(graph, graph2)


def test_check_networkx_graph_equivalence_different_graph() -> None:
    with open(
        "puml_files/bunched_XOR_switch.puml", "r", encoding="utf-8"
    ) as file:
        puml_string = file.read()
    graph = next(get_network_x_graph_from_puml_string(puml_string))
    with open(
        "puml_files/complicated_test.puml", "r", encoding="utf-8"
    ) as file:
        puml_string = file.read()
    graph2 = next(get_network_x_graph_from_puml_string(puml_string))
    assert not check_networkx_graph_equivalence(graph, graph2)


def test_check_puml_equivalence_same_puml() -> None:
    with open(
        "puml_files/bunched_XOR_switch.puml", "r", encoding="utf-8"
    ) as file:
        puml_string_1 = file.read()
    with open(
        "puml_files/bunched_XOR_switch.puml", "r", encoding="utf-8"
    ) as file:
        puml_string_2 = file.read()
    assert check_puml_equivalence(puml_string_1, puml_string_2)


def test_check_puml_equivalence_different_puml() -> None:
    with open(
        "puml_files/bunched_XOR_switch.puml", "r", encoding="utf-8"
    ) as file:
        puml_string_1 = file.read()
    with open(
        "puml_files/complicated_test.puml", "r", encoding="utf-8"
    ) as file:
        puml_string_2 = file.read()
    assert not check_puml_equivalence(puml_string_1, puml_string_2)


def test_check_puml_equivalence_same_puml_reordered() -> None:
    with open(
        "puml_files/bunched_XOR_switch.puml", "r", encoding="utf-8"
    ) as file:
        puml_string_1 = file.read()
    with open(
        "puml_files/bunched_XOR_switch_reordered.puml", "r", encoding="utf-8"
    ) as file:
        puml_string_2 = file.read()
    assert check_puml_equivalence(puml_string_1, puml_string_2)
