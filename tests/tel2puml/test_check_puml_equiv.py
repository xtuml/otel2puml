"""Tests for the check_puml_equiv module."""
from copy import deepcopy

import networkx as nx
from test_event_generator.io.parse_puml import EventData

from tel2puml.check_puml_equiv import (
    create_networkx_graph_from_parsed_puml,
    check_networkx_graph_equivalence,
    get_network_x_graph_from_puml_string,
    check_puml_equivalence,
    update_collected_attributes,
    NXNode
)


def test_update_collected_attributes() -> None:
    """Test the `update_collected_attributes` function updates the collected
    attributes correctly"""
    event_data = EventData()
    event_data.event_type = "A"
    event_data.occurence_id = 0
    event_data.is_break = True
    event_data.branch_counts = {
        **event_data.branch_counts,
        "BC1": {
            "user": ("A", 0),
        },
        "BC2": {
            "user": ("B", 0),
        }
    }
    collected_attributes = {}
    update_collected_attributes(
        collected_attributes=collected_attributes,
        event_data=event_data
    )
    expected_collected_attributes = {
        ("A", 0): {
            "is_break": True,
            "is_branch": True,
        },
        ("B", 0): {
            "is_branch": True
        }
    }
    assert collected_attributes == expected_collected_attributes


def test_create_networkx_graph_from_parsed_puml_break_and_branch() -> None:
    """Test the `create_networkx_graph_from_parsed_puml` function creates the
    correct networkx graph from the parsed puml with breaks and branches
    """
    events = {}
    for event_string in ["A", "B"]:
        event_data = EventData()
        event_data.event_type = event_string
        event_data.occurence_id = 0
        events[event_data.event_tuple] = event_data
    events[("A", 0)].is_break = True
    events[("A", 0)].branch_counts = {
        "BC1": {
            "user": ("A", 0),
        },
        "BC2": {
            "user": ("B", 0),
        }
    }
    parsed_puml = [
        events[("A", 0)], events[("B", 0)],
    ]
    graph = create_networkx_graph_from_parsed_puml(parsed_puml)
    expected_edges = [
        (('A', 0), ('B', 0)),
    ]
    for edge in graph.edges:
        edge_tuple = (edge[0].node_id, edge[1].node_id)
        assert edge_tuple in expected_edges
        expected_edges.remove(edge_tuple)
    assert len(expected_edges) == 0
    for node in graph.nodes:
        attributes = graph.nodes[node]
        if node.node_id == ("A", 0):
            assert attributes == {
                "extra_info": {
                    "is_break": True,
                    "is_branch": True,
                },
                "node_type": "A"
            }
        else:
            assert attributes == {
                "extra_info": {
                    "is_branch": True,
                },
                "node_type": "B"
            }


def test_create_networkx_graph_from_parsed_puml() -> None:
    """Test the `create_networkx_graph_from_parsed_puml` function creates the
    correct networkx graph from the parsed puml
    """
    def check_edges_in_graph(graph, expected_edges) -> None:
        for edge in graph.edges:
            edge_tuple = (edge[0].node_id, edge[1].node_id)
            assert edge_tuple in expected_edges
            expected_edges.remove(edge_tuple)
        assert len(expected_edges) == 0
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
    check_edges_in_graph(graph, expected_edges)
    # case with kill/detach event
    # setup
    kill_event = EventData()
    kill_event.event_type = "kill_event"
    kill_event.is_end = True
    kill_event.occurence_id = 0
    parsed_puml = [kill_event]
    # create graph
    graph = create_networkx_graph_from_parsed_puml(parsed_puml)
    expected_edges = [(("kill_event", 0), ("KILL", 0))]
    check_edges_in_graph(graph, expected_edges)
    # case with kill/detach event in logic block
    # setup
    parsed_puml = [
        events[("A", 0)],
        ("START", "XOR"), ("PATH", "XOR"), events[("B", 0)],
        ("PATH", "XOR"), kill_event, ("END", "XOR"), events[("C", 0)]
    ]
    graph = create_networkx_graph_from_parsed_puml(parsed_puml)
    expected_edges = [
        (('A', 0), ('START', 'XOR', 1)),
        (('START', 'XOR', 1), ('B', 0)),
        (('B', 0), ('END', 'XOR', 1)),
        (('END', 'XOR', 1), ('C', 0)),
        (('START', 'XOR', 1), ('kill_event', 0)),
        (('kill_event', 0), ("KILL", 0)),
        (("KILL", 0), ('END', 'XOR', 1))
    ]
    check_edges_in_graph(graph, expected_edges)


def test_check_networkx_graph_equivalence_same_graph() -> None:
    """Test the `check_networkx_graph_equivalence` function returns True when
    the same graph is passed in"""
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
    """Test the `check_networkx_graph_equivalence` function returns False when
    different graphs are passed in"""
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


def test_check_networkx_graph_equivalence_graph_break_and_branch_true(
) -> None:
    """Test the `check_networkx_graph_equivalence` function returns True when
    the graphs are the same due to a break and branch attribute being the same
    """
    graph = nx.DiGraph()
    node_A = NXNode(("A", 0), "A")
    node_B = NXNode(("B", 0), "B")
    node_A.extra_info = {
        "is_break": True,
        "is_branch": True
    }
    node_B.extra_info = {
        "is_break": False,
        "is_branch": True
    }
    graph.add_edge(node_A, node_B)
    nx.set_node_attributes(
        graph,
        {
            node: {
                "extra_info": node.extra_info,
                "node_type": node.node_type
            }
            for node in graph.nodes
        }
    )
    nx.set_edge_attributes(
        graph,
        {
            (node_A, node_B): {
                "start_node_attr": graph.nodes[node_A],
                "end_node_attr": graph.nodes[node_B]
            }
        }
    )
    graph2 = deepcopy(graph)
    assert check_networkx_graph_equivalence(graph, graph2)


def test_check_networkx_graph_equivalence_graph_break_and_branch_false(
) -> None:
    """Test the `check_networkx_graph_equivalence` function returns False when
    the graphs are different due to a break and branch attribute being
    different"""
    graph = nx.DiGraph()
    node_A = NXNode(("A", 0), "A")
    node_B = NXNode(("B", 0), "B")
    node_A.extra_info = {
        "is_break": True,
        "is_branch": True
    }
    node_B.extra_info = {
        "is_break": False,
        "is_branch": True
    }
    graph.add_edge(node_A, node_B)
    nx.set_node_attributes(
        graph,
        {
            node: {
                "extra_info": node.extra_info,
                "node_type": node.node_type
            }
            for node in graph.nodes
        }
    )
    nx.set_edge_attributes(
        graph,
        {
            (node_A, node_B): {
                "start_node_attr": graph.nodes[node_A],
                "end_node_attr": graph.nodes[node_B]
            }
        }
    )
    graph2 = deepcopy(graph)
    node_B.extra_info["is_break"] = True
    node_B.extra_info["is_branch"] = False
    assert not check_networkx_graph_equivalence(graph, graph2)


def test_check_puml_equivalence_same_puml() -> None:
    """Test the `check_puml_equivalence` function returns True when the same
    puml is passed in"""
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
    """Test the `check_puml_equivalence` function returns False when different
    puml are passed in"""
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
    """Test the `check_puml_equivalence` function returns True when the same
    puml is passed in but with different ordering"""
    with open(
        "puml_files/bunched_XOR_switch.puml", "r", encoding="utf-8"
    ) as file:
        puml_string_1 = file.read()
    with open(
        "puml_files/bunched_XOR_switch_reordered.puml", "r", encoding="utf-8"
    ) as file:
        puml_string_2 = file.read()
    assert check_puml_equivalence(puml_string_1, puml_string_2)


def test_check_puml_equivalence_break_branch_true() -> None:
    """Test the `check_puml_equivalence` function returns True when the same
    puml is passed in with breaks and branches"""
    with open(
        "puml_files/sequence_branch_break_points.puml", "r", encoding="utf-8"
    ) as file:
        puml_string_1 = file.read()
    with open(
        "puml_files/sequence_branch_break_points.puml", "r",
        encoding="utf-8"
    ) as file:
        puml_string_2 = file.read()
    assert check_puml_equivalence(puml_string_1, puml_string_2)


def test_check_puml_equivalence_break_branch_false() -> None:
    """Test the `check_puml_equivalence` function returns False when different
    puml are passed in with breaks and branches i.e. one is missing a branch
    count indicator"""
    with open(
        "puml_files/sequence_break_points.puml", "r", encoding="utf-8"
    ) as file:
        puml_string_1 = file.read()
    with open(
        "puml_files/sequence_branch_break_points.puml", "r",
        encoding="utf-8"
    ) as file:
        puml_string_2 = file.read()
    assert not check_puml_equivalence(puml_string_1, puml_string_2)
