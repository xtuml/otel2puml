"""Tests for the puml_graph.graph module.
"""

import pytest
from test_event_generator.io.parse_puml import parse_raw_job_def_lines

from tel2puml.tel2puml_types import (
    PUMLEvent, PUMLOperatorNodes, PUMLOperator, DUMMY_START_EVENT
)
from tel2puml.graph import (
    PUMLGraph,
    PUMLEventNode,
    PUMLOperatorNode,
    OPERATOR_NODE_PUML_MAP,
    update_graph_for_dummy_break_event_node,
)
from tel2puml.check_puml_equiv import (
    create_networkx_graph_from_parsed_puml,
    check_networkx_graph_equivalence
)
from tel2puml.loop_detection.loop_types import DUMMY_BREAK_EVENT_TYPE


class TestPUMLEventNode:
    """Tests for the PUMLEventNode class.
    """
    @staticmethod
    def test_init_normal() -> None:
        """Tests the __init__ method.
        """
        event = PUMLEventNode(
            "event", 0,
            (PUMLEvent.NORMAL,),
        )
        assert event.node_id == ("event", 0)
        assert event.node_type == "event"
        assert event.extra_info == {}

    @staticmethod
    def test_init_event_types() -> None:
        """Tests the __init__ method.
        """
        event = PUMLEventNode(
            "event", 0,
            (PUMLEvent.BRANCH, PUMLEvent.MERGE, PUMLEvent.BREAK),
        )
        assert event.node_id == ("event", 0)
        assert event.node_type == "event"
        assert event.extra_info == {
            "is_branch": True, "is_merge": True, "is_break": True
        }

    @staticmethod
    def test_write_uml_block_normal() -> None:
        """Tests the write_uml_block method.
        """
        event = PUMLEventNode("event", 0)
        for indent in [0, 4]:
            for tab_size in [0, 4]:
                assert event.write_uml_blocks(
                    indent=indent, tab_size=tab_size
                ) == ([" " * indent + ":event;"], 0)

    @staticmethod
    def test_write_uml_block_event_types() -> None:
        """Tests the write_uml_block method.
        """
        branch_event = PUMLEventNode(
            "event", 0,
            (PUMLEvent.BRANCH,),
            branch_number=1
        )
        assert branch_event.write_uml_blocks(
            indent=4,
            tab_size=4
        ) == (["    :event,BCNT,user=event,name=BC1;"], 0)
        branch_event_no_branch_number = PUMLEventNode(
            "event", 0,
            (PUMLEvent.BRANCH,)
        )
        with pytest.raises(RuntimeError):
            branch_event_no_branch_number.write_uml_blocks(
                indent=4, tab_size=4
            )

        break_event = PUMLEventNode("event", 0, (PUMLEvent.BREAK,))
        assert break_event.write_uml_blocks(indent=4, tab_size=4) == (
            ["    :event;", "    break"], 0
        )
        # check case where Break event type is added after init
        break_event = PUMLEventNode("event", 0)
        break_event.event_types = (PUMLEvent.BREAK,)
        assert break_event.write_uml_blocks(indent=4, tab_size=4) == (
            ["    :event;", "    break"], 0
        )

    @staticmethod
    def test_write_uml_block_sub_graph() -> None:
        """Tests the write_uml_block method.
        """
        sub_graph = PUMLGraph()
        event_node = sub_graph.create_event_node("event")
        start_loop_node, end_loop_node = sub_graph.create_operator_node_pair(
            PUMLOperator.LOOP
        )
        sub_graph.add_puml_edge(start_loop_node, event_node)
        sub_graph.add_puml_edge(event_node, end_loop_node)

        event = PUMLEventNode(
            "event", 0,
            sub_graph=sub_graph
        )
        for indent in [0, 4]:
            for tab_size in [0, 4]:
                assert event.write_uml_blocks(
                    indent=indent, tab_size=tab_size
                ) == ([
                    " " * indent + "repeat",
                    " " * (indent + tab_size) + ":event;",
                    " " * indent + "repeat while"
                ], 0)

    @staticmethod
    def test_write_uml_block_sub_graph_loop_event() -> None:
        """Tests the write_uml_block method for a loop event.
        """
        sub_graph = PUMLGraph()
        _ = sub_graph.create_event_node("event")
        loop_event = PUMLEventNode(
            "event", 0, (PUMLEvent.LOOP,), sub_graph=sub_graph
        )
        for indent in [0, 4]:
            for tab_size in [0, 4]:
                assert loop_event.write_uml_blocks(
                    indent=indent, tab_size=tab_size
                ) == ([
                    " " * indent + "repeat",
                    " " * (indent + tab_size) + ":event;",
                    " " * indent + "repeat while"
                ], 0)


class TestPUMLOperatorNode:
    """Tests for the PUMLOperatorNode class."""
    @staticmethod
    def test_init() -> None:
        """Tests the __init__ method."""
        for operator_type in PUMLOperatorNodes:
            operator = PUMLOperatorNode(operator_type, 0)
            assert operator.node_id == (*operator_type.value, 0)
            assert operator.node_type == "_".join(operator_type.value)
            assert operator.extra_info == {}

    @staticmethod
    def test_write_uml_block() -> None:
        """Tests the write_uml_block method."""
        # test START_XOR
        operator = PUMLOperatorNode(
            PUMLOperatorNodes.START_XOR, 0
        )
        for indent in [0, 4]:
            for tab_size in [0, 4]:
                assert operator.write_uml_blocks(
                    indent=indent,
                    tab_size=tab_size
                ) == ([
                    " " * indent + "switch (XOR)",
                    " " * (indent + tab_size) + "case ()"
                ], 2)
        # test END_XOR
        for indent in [0, 4]:
            for tab_size in [0, 4]:
                operator = PUMLOperatorNode(
                    PUMLOperatorNodes.END_XOR, 0
                )
                assert operator.write_uml_blocks(
                    indent=indent,
                    tab_size=tab_size
                ) == ([" " * (indent - tab_size) + "endswitch"], -2)
        # test PATH
        for operator_type in PUMLOperatorNodes:
            if "PATH" in operator_type.value:
                operator = PUMLOperatorNode(
                    operator_type, 0
                )
                for indent in [0, 4]:
                    for tab_size in [0, 4]:
                        assert operator.write_uml_blocks(
                            indent=indent,
                            tab_size=tab_size
                        ) == ([
                            " " * (indent - tab_size)
                            + OPERATOR_NODE_PUML_MAP[
                                operator_type.value
                            ][0][0],
                        ], 0)
        # test START
        for operator_type in PUMLOperatorNodes:
            if (
                "START" in operator_type.value
                and "XOR" not in operator_type.value
            ):
                operator = PUMLOperatorNode(
                    operator_type, 0
                )
                for indent in [0, 4]:
                    for tab_size in [0, 4]:
                        assert operator.write_uml_blocks(
                            indent=indent,
                            tab_size=tab_size
                        ) == ([
                            " " * indent
                            + OPERATOR_NODE_PUML_MAP[
                                operator_type.value
                            ][0][0],
                        ], 1)
        # test END
        for operator_type in PUMLOperatorNodes:
            if (
                "END" in operator_type.value
                and "XOR" not in operator_type.value
            ):
                operator = PUMLOperatorNode(
                    operator_type, 0
                )
                for indent in [0, 4]:
                    for tab_size in [0, 4]:
                        assert operator.write_uml_blocks(
                            indent=indent, tab_size=tab_size
                        ) == ([
                            " " * (indent - tab_size)
                            + OPERATOR_NODE_PUML_MAP[
                                operator_type.value
                            ][0][0],
                        ], -1)


class TestPUMLGraph:
    """Tests for the PUMLGraph class."""
    @staticmethod
    def test_add_puml_node() -> None:
        """Tests the add_puml_node method."""
        # test puml event node
        graph = PUMLGraph()
        event_node = PUMLEventNode(
            "event", 0
        )
        graph.add_puml_node(event_node)
        assert len(graph.nodes) == 1
        assert graph.nodes[event_node] == {
            "node_type": "event",
            "extra_info": {}
        }
        operator_node = PUMLOperatorNode(
            PUMLOperatorNodes.START_XOR, 0
        )
        graph.add_puml_node(operator_node)
        assert len(graph.nodes) == 2
        assert graph.nodes[operator_node] == {
            "node_type": "START_XOR", "extra_info": {}
        }

    @staticmethod
    def test_add_edge() -> None:
        """Tests the add_edge method."""
        graph = PUMLGraph()
        event_node_1 = PUMLEventNode("event", 0)
        event_node_2 = PUMLEventNode("event", 1)
        graph.add_puml_node(event_node_1)
        graph.add_puml_node(event_node_2)
        graph.add_puml_edge(event_node_1, event_node_2)
        assert len(graph.edges) == 1
        assert graph.edges[event_node_1, event_node_2] == {
            "start_node_attr": {
                "node_type": "event",
                "extra_info": {}
            },
            "end_node_attr": {
                "node_type": "event",
                "extra_info": {}
            }
        }

    @staticmethod
    def test_increment_occurrence_count() -> None:
        """Tests the increment_occurrence_count method."""
        graph = PUMLGraph()
        assert len(graph.node_counts) == 0
        graph.increment_occurrence_count("event")
        assert len(graph.node_counts) == 1
        assert graph.node_counts["event"] == 1
        graph.increment_occurrence_count("event")
        assert graph.node_counts["event"] == 2

    @staticmethod
    def test_get_occurrence_count() -> None:
        """Tests the get_occurrence_count method."""
        graph = PUMLGraph()
        assert graph.get_occurrence_count("event") == 0
        graph.increment_occurrence_count("event")
        assert graph.get_occurrence_count("event") == 1

    @staticmethod
    def test_create_event_node() -> None:
        """Tests the create_event_node method for current cases."""
        # test normal event
        graph = PUMLGraph()
        event_node = graph.create_event_node("event")
        assert event_node.node_id == ("event", 0)
        assert event_node.node_type == "event"
        assert event_node.extra_info == {}
        graph.get_occurrence_count("event") == 1
        # test branch event
        event_node = graph.create_event_node(
            "branch_event", PUMLEvent.BRANCH
        )
        assert event_node.node_id == ("branch_event", 0)
        assert event_node.node_type == "branch_event"
        assert event_node.extra_info == {"is_branch": True}
        assert event_node.branch_number == 0
        assert graph.branch_counts == 1
        # test merge + break event
        event_node = graph.create_event_node(
            "merge_break_event", (PUMLEvent.MERGE, PUMLEvent.BREAK)
        )
        assert event_node.node_id == ("merge_break_event", 0)
        assert event_node.node_type == "merge_break_event"
        assert event_node.extra_info == {"is_merge": True, "is_break": True}

    @staticmethod
    def test_create_operator_node_pair() -> None:
        """Tests the create_operator_node_pair method for current cases."""
        for operator in PUMLOperator:
            graph = PUMLGraph()
            start_node, end_node = graph.create_operator_node_pair(operator)
            assert start_node.node_id == ("START", operator.name, 0)
            assert start_node.node_type == f"START_{operator.name}"
            assert start_node.extra_info == {}
            assert graph.get_occurrence_count(("START", operator.name)) == 1
            assert end_node.node_id == ("END", operator.name, 0)
            assert end_node.node_type == f"END_{operator.name}"
            assert end_node.extra_info == {}
            assert graph.get_occurrence_count(("END", operator.name)) == 1
            assert len(graph.nodes) == 2
            assert start_node in graph.nodes and end_node in graph.nodes

    @staticmethod
    def test_create_operator_path_node() -> None:
        """Tests the create_operator_path_node method for various cases."""
        for operator in PUMLOperator:
            if len(operator.value) == 3:
                graph = PUMLGraph()
                path_node = graph.create_operator_path_node(operator)
                assert path_node.node_id == ("PATH", operator.name, 0)
                assert path_node.node_type == f"PATH_{operator.name}"
                assert path_node.extra_info == {}
                assert graph.get_occurrence_count(("PATH", operator.name)) == 1
                assert path_node in graph.nodes
                assert len(graph.nodes) == 1

    @staticmethod
    def test_write_uml_blocks() -> None:
        """Tests the write_uml_blocks method for current cases."""
        # test simple event sequence block
        graph = PUMLGraph()
        event_node_1 = graph.create_event_node("event")
        event_node_2 = graph.create_event_node("event")
        graph.add_puml_edge(event_node_1, event_node_2)
        assert graph.write_uml_blocks() == [":event;", ":event;"]

        # test loop block
        graph = PUMLGraph()
        event_node = graph.create_event_node("event")
        start_loop_node, end_loop_node = graph.create_operator_node_pair(
            PUMLOperator.LOOP
        )
        graph.add_puml_edge(start_loop_node, event_node)
        graph.add_puml_edge(event_node, end_loop_node)
        assert graph.write_uml_blocks() == [
            "repeat",
            "    :event;",
            "repeat while"
        ]

        # test nested XOR block
        graph = PUMLGraph()
        event_node_1 = graph.create_event_node("event")
        event_node_2 = graph.create_event_node("event")
        event_node_3 = graph.create_event_node("event")
        start_xor_node_1, end_xor_node_1 = graph.create_operator_node_pair(
            PUMLOperator.XOR
        )
        start_xor_node_2, end_xor_node_2 = graph.create_operator_node_pair(
            PUMLOperator.XOR
        )
        graph.add_puml_edge(start_xor_node_1, start_xor_node_2)
        graph.add_puml_edge(start_xor_node_2, event_node_1)
        graph.add_puml_edge(event_node_1, end_xor_node_2)
        graph.add_puml_edge(start_xor_node_2, event_node_3)
        graph.add_puml_edge(event_node_3, end_xor_node_2)
        graph.add_puml_edge(start_xor_node_1, event_node_2)
        graph.add_puml_edge(event_node_2, end_xor_node_1)
        graph.add_puml_edge(end_xor_node_2, end_xor_node_1)
        block = graph.write_uml_blocks()
        expected_block = [
            "switch (XOR)",
            "    case ()",
            "        switch (XOR)",
            "            case ()",
            "                :event;",
            "            case ()",
            "                :event;",
            "        endswitch",
            "    case ()",
            "        :event;",
            "endswitch"
        ]
        # check equivalence of expected and actual blocks
        actual_graph = create_networkx_graph_from_parsed_puml(
            parse_raw_job_def_lines(block)
        )
        expected_graph = create_networkx_graph_from_parsed_puml(
            parse_raw_job_def_lines(expected_block)
        )
        assert check_networkx_graph_equivalence(
            actual_graph, expected_graph
        )

        # test other operators nested
        for operator in PUMLOperator:
            if operator == PUMLOperator.XOR or operator == PUMLOperator.LOOP:
                continue
            graph = PUMLGraph()
            event_node_1 = graph.create_event_node("event")
            event_node_2 = graph.create_event_node("event")
            event_node_3 = graph.create_event_node("event")
            start_xor_node_1, end_xor_node_1 = graph.create_operator_node_pair(
                operator=operator
            )
            start_xor_node_2, end_xor_node_2 = graph.create_operator_node_pair(
                operator=operator
            )
            graph.add_puml_edge(start_xor_node_1, start_xor_node_2)
            graph.add_puml_edge(start_xor_node_2, event_node_1)
            graph.add_puml_edge(event_node_1, end_xor_node_2)
            graph.add_puml_edge(start_xor_node_2, event_node_3)
            graph.add_puml_edge(event_node_3, end_xor_node_2)
            graph.add_puml_edge(start_xor_node_1, event_node_2)
            graph.add_puml_edge(event_node_2, end_xor_node_1)
            graph.add_puml_edge(end_xor_node_2, end_xor_node_1)
            block = graph.write_uml_blocks()
            expected_block = [
                OPERATOR_NODE_PUML_MAP[operator.value[0].value][0][0],
                "    " + OPERATOR_NODE_PUML_MAP[operator.value[0].value][0][0],
                "        :event;",
                "    " + OPERATOR_NODE_PUML_MAP[operator.value[2].value][0][0],
                "        :event;",
                "    " + OPERATOR_NODE_PUML_MAP[operator.value[1].value][0][0],
                OPERATOR_NODE_PUML_MAP[operator.value[2].value][0][0],
                "    :event;",
                OPERATOR_NODE_PUML_MAP[operator.value[1].value][0][0]
            ]
            # check equivalence of expected and actual blocks
            actual_graph = create_networkx_graph_from_parsed_puml(
                parse_raw_job_def_lines(block)
            )
            expected_graph = create_networkx_graph_from_parsed_puml(
                parse_raw_job_def_lines(expected_block)
            )
            assert check_networkx_graph_equivalence(
                actual_graph, expected_graph
            )

        # check case with event with subgraph
        graph = PUMLGraph()
        # create subgraph
        sub_graph = PUMLGraph()
        sub_graph_event_node = sub_graph.create_event_node("event")
        start_loop_node, end_loop_node = sub_graph.create_operator_node_pair(
            PUMLOperator.LOOP
        )
        sub_graph.add_puml_edge(start_loop_node, sub_graph_event_node)
        sub_graph.add_puml_edge(sub_graph_event_node, end_loop_node)
        # create event node with subgraph
        event_node_1 = graph.create_event_node("event", sub_graph=sub_graph)
        event_node_2 = graph.create_event_node("event")
        start_xor_node, end_xor_node = graph.create_operator_node_pair(
            PUMLOperator.XOR
        )
        graph.add_puml_edge(start_xor_node, event_node_1)
        graph.add_puml_edge(event_node_1, end_xor_node)
        graph.add_puml_edge(start_xor_node, event_node_2)
        graph.add_puml_edge(event_node_2, end_xor_node)
        block = graph.write_uml_blocks()
        expected_block = [
            "switch (XOR)",
            "    case ()",
            "        repeat",
            "            :event;",
            "        repeat while",
            "    case ()",
            "        :event;",
            "endswitch"
        ]
        # check equivalence of expected and actual blocks
        actual_graph = create_networkx_graph_from_parsed_puml(
            parse_raw_job_def_lines(block)
        )
        expected_graph = create_networkx_graph_from_parsed_puml(
            parse_raw_job_def_lines(expected_block)
        )
        assert check_networkx_graph_equivalence(
            actual_graph, expected_graph
        )

    @staticmethod
    def test_write_puml_string() -> None:
        """Tests the write_uml_string method."""
        graph = PUMLGraph()
        event_node_1 = graph.create_event_node("event")
        event_node_2 = graph.create_event_node("event")
        graph.add_puml_edge(event_node_1, event_node_2)
        for tab_size in range(5):
            assert graph.write_puml_string(tab_size=tab_size) == (
                "@startuml\n" +
                tab_size * " " + 'partition "default_name" ' + "{\n" +
                2 * tab_size * " " + "group " + '"default_name"\n' +
                3 * tab_size * " " + ":event;\n" +
                3 * tab_size * " " + ":event;\n" +
                2 * tab_size * " " + "end group\n"
                + tab_size * " " + "}\n"
                "@enduml"
            )

    @staticmethod
    def test_add_graph_node_to_set_from_reference(
        puml_graph: tuple[PUMLGraph, dict[tuple[str, int], PUMLEventNode]],
    ) -> None:
        """Tests the add_graph_node_to_set_from_reference method."""
        graph, event_nodes = puml_graph
        node_set: set[PUMLEventNode] = set()
        # test case where node_ref is in event_nodes
        graph.add_graph_node_to_set_from_reference(
            node_set=node_set, node_ref="q0"
        )
        assert len(node_set) == 1
        assert event_nodes[("A", 0)] in node_set
        # test case where two nodes have same node ref
        graph.add_graph_node_to_set_from_reference(
            node_set=node_set, node_ref="q1"
        )
        assert len(node_set) == 3
        for i in range(2):
            assert event_nodes[("B", i)] in node_set
        # test case where node_ref is not in event_nodes
        with pytest.raises(KeyError):
            graph.add_graph_node_to_set_from_reference(
                node_set=node_set, node_ref="q9"
            )

    @staticmethod
    def test_replace_subgraph_node_from_start_and_end_nodes() -> None:
        """Tests the replace_subgraph_node_from_start_and_end_nodes method."""
        # test case where start and end nodes are the same
        graph = PUMLGraph()
        A = graph.create_event_node("A")
        B = graph.create_event_node("B")
        C = graph.create_event_node("C")
        graph.add_puml_edge(A, B)
        graph.add_puml_edge(B, C)
        # test case where start and end nodes are the same
        sub_graph_node = graph.replace_subgraph_node_from_start_and_end_nodes(
            B, B, "sub_graph_node"
        )
        expected_graph_nodes = [A, sub_graph_node, C]
        expected_graph_edges = [(A, sub_graph_node), (sub_graph_node, C)]
        assert len(graph.nodes) == 3
        assert len(graph.edges) == 2
        for node in graph.nodes:
            assert node in expected_graph_nodes
            expected_graph_nodes.remove(node)
        assert len(expected_graph_nodes) == 0
        for edge in graph.edges:
            assert edge in expected_graph_edges
            expected_graph_edges.remove(edge)
        assert len(expected_graph_edges) == 0
        assert sub_graph_node.sub_graph is not None
        assert len(sub_graph_node.sub_graph.nodes) == 1
        assert B in sub_graph_node.sub_graph.nodes
        assert len(sub_graph_node.sub_graph.edges) == 0
        # test case where start node has no incoming edges
        graph = PUMLGraph()
        A = graph.create_event_node("A")
        B = graph.create_event_node("B")
        C = graph.create_event_node("C")
        graph.add_puml_edge(A, B)
        graph.add_puml_edge(B, C)
        sub_graph_node = (
            graph.replace_subgraph_node_from_start_and_end_nodes(
                A, B, "sub_graph_node"
            )
        )
        expected_graph_nodes = [sub_graph_node, C]
        expected_graph_edges = [(sub_graph_node, C)]
        assert len(graph.nodes) == 2
        assert len(graph.edges) == 1
        for node in graph.nodes:
            assert node in expected_graph_nodes
            expected_graph_nodes.remove(node)
        assert len(expected_graph_nodes) == 0
        for edge in graph.edges:
            assert edge in expected_graph_edges
            expected_graph_edges.remove(edge)
        assert len(expected_graph_edges) == 0
        assert sub_graph_node.sub_graph is not None
        assert len(sub_graph_node.sub_graph.nodes) == 2
        assert (
            A in sub_graph_node.sub_graph.nodes
            and B in sub_graph_node.sub_graph.nodes
        )
        assert len(sub_graph_node.sub_graph.edges) == 1
        assert (
            (A, B) in sub_graph_node.sub_graph.edges
        )
        # test case where end node has no outgoing edges
        graph = PUMLGraph()
        A = graph.create_event_node("A")
        B = graph.create_event_node("B")
        C = graph.create_event_node("C")
        graph.add_puml_edge(A, B)
        graph.add_puml_edge(B, C)
        sub_graph_node = (
            graph.replace_subgraph_node_from_start_and_end_nodes(
                B, C, "sub_graph_node"
            )
        )
        expected_graph_nodes = [sub_graph_node, A]
        expected_graph_edges = [(A, sub_graph_node)]
        assert len(graph.nodes) == 2
        assert len(graph.edges) == 1
        for node in graph.nodes:
            assert node in expected_graph_nodes
            expected_graph_nodes.remove(node)
        assert len(expected_graph_nodes) == 0
        for edge in graph.edges:
            assert edge in expected_graph_edges
            expected_graph_edges.remove(edge)
        assert len(expected_graph_edges) == 0
        assert sub_graph_node.sub_graph is not None
        assert len(sub_graph_node.sub_graph.nodes) == 2
        assert (
            B in sub_graph_node.sub_graph.nodes
            and C in sub_graph_node.sub_graph.nodes
        )
        assert len(sub_graph_node.sub_graph.edges) == 1
        assert (
            (B, C) in sub_graph_node.sub_graph.edges
        )
        # setup for next tests
        graph = PUMLGraph()
        A = graph.create_event_node("A")
        B = graph.create_event_node("B")
        C = graph.create_event_node("C")
        D = graph.create_event_node("D")
        E = graph.create_event_node("E")
        F = graph.create_event_node("F")
        graph.add_puml_edge(A, C)
        graph.add_puml_edge(B, C)
        graph.add_puml_edge(C, D)
        graph.add_puml_edge(D, E)
        graph.add_puml_edge(D, F)
        # test raises error when there is more than one incoming edge to start
        # node
        with pytest.raises(RuntimeError) as exc_info:
            graph.replace_subgraph_node_from_start_and_end_nodes(
                C, C, "sub_graph_node"
            )
        assert str(exc_info.value) == (
            "Start node has more than one incoming edge"
        )
        # test raises and error when more than one outgoing edge from end node
        with pytest.raises(RuntimeError) as exc_info:
            graph.replace_subgraph_node_from_start_and_end_nodes(
                D, D, "sub_graph_node"
            )
        assert str(exc_info.value) == (
            "End node has more than one outgoing edge"
        )
        # test case where start node has no incoming edges and end node has no
        # outgoing edges
        with pytest.raises(RuntimeError) as exc_info:
            graph.replace_subgraph_node_from_start_and_end_nodes(
                A, F, "sub_graph_node"
            )
        assert str(exc_info.value) == (
            "Start and end nodes have no incoming or outgoing edges and "
            "there will be no subgraph to create"
        )
        # test case in which start and end nodes do not disconnect the graph
        graph = PUMLGraph()
        A = graph.create_event_node("A")
        B = graph.create_event_node("B")
        C = graph.create_event_node("C")
        D = graph.create_event_node("D")
        E = graph.create_event_node("E")
        graph.add_puml_edge(A, B)
        graph.add_puml_edge(B, C)
        graph.add_puml_edge(C, D)
        graph.add_puml_edge(D, E)
        graph.add_puml_edge(A, C)
        graph.add_puml_edge(C, E)
        with pytest.raises(RuntimeError) as exc_info:
            graph.replace_subgraph_node_from_start_and_end_nodes(
                B, D, "sub_graph_node"
            )
        assert str(exc_info.value) == (
            "Graph is not disconnected after removing start node in edges "
            "and end node out edges so there is no subgraph to create"
        )

    @staticmethod
    def test_remove_dummy_start_event_nodes() -> None:
        """Tests the remove_dummy_start_event_nodes method."""
        # setup
        graph = PUMLGraph()
        dummy_start = graph.create_event_node(DUMMY_START_EVENT)
        A = graph.create_event_node("A")
        B = graph.create_event_node("B")
        C = graph.create_event_node("C")
        graph.add_puml_edge(dummy_start, A)
        graph.add_puml_edge(dummy_start, B)
        graph.add_puml_edge(A, C)
        graph.add_puml_edge(B, C)
        assert (
            (dummy_start, A) in graph.edges and (dummy_start, B) in graph.edges
        )
        assert dummy_start in graph.nodes
        # test
        graph.remove_dummy_start_event_nodes()
        assert (dummy_start, A) not in graph.edges
        assert (dummy_start, B) not in graph.edges
        assert dummy_start not in graph.nodes

    @staticmethod
    def test_add_sub_graph_to_puml_nodes_with_ref() -> None:
        """Tests the add_sub_graph_to_puml_nodes_with_ref method."""
        # setup
        graph = PUMLGraph()
        A1 = graph.create_event_node("A1", parent_graph_node="A")
        A2 = graph.create_event_node("A2", parent_graph_node="A")
        B = graph.create_event_node("B", parent_graph_node="B")
        # test addition of subgraph to single node
        sub_graph_b = PUMLGraph()
        graph.add_sub_graph_to_puml_nodes_with_ref(
            sub_graph=sub_graph_b, ref="B"
        )
        assert B.sub_graph == sub_graph_b
        assert A1.sub_graph is None
        assert A2.sub_graph is None
        # test addition of subgraph to multiple nodes
        sub_graph_a = PUMLGraph()
        graph.add_sub_graph_to_puml_nodes_with_ref(
            sub_graph=sub_graph_a, ref="A"
        )
        assert A1.sub_graph == sub_graph_a
        assert A2.sub_graph == sub_graph_a
        assert B.sub_graph == sub_graph_b
        # test raises error when node_ref not in graph
        with pytest.raises(KeyError):
            graph.add_sub_graph_to_puml_nodes_with_ref(
                sub_graph=sub_graph_a, ref="C"
            )


def test_update_graph_for_dummy_break_event_node(
    graph_with_dummy_break_event: tuple[
        PUMLGraph, dict[str, PUMLOperatorNode | PUMLEventNode]
    ]
) -> None:
    """Tests the update_graph_for_dummy_break_event_node function."""
    # test case with two nested XOR above the dummy break event node
    graph, nodes = graph_with_dummy_break_event
    DUMMY_BREAK = nodes[DUMMY_BREAK_EVENT_TYPE]
    assert isinstance(DUMMY_BREAK, PUMLEventNode)
    update_graph_for_dummy_break_event_node(
        DUMMY_BREAK, graph
    )
    # check that the dummy break event node has been removed
    assert DUMMY_BREAK_EVENT_TYPE not in graph.nodes
    # check that the A node has been taken out and the start node is now
    # connected to the first XOR
    assert (nodes["START"], nodes["A"]) not in graph.edges
    assert (nodes["A"], nodes["XOR_START_1"]) not in graph.edges
    assert (nodes["START"], nodes["XOR_START_1"]) in graph.edges
    # check that the first XOR now has an outgoing edge to a new replica of A
    # in between the XOR and the B node
    assert (nodes["XOR_START_1"], nodes["B"]) not in graph.edges
    xor_start_out_edges = list(graph.out_edges(nodes["XOR_START_1"]))
    assert len(xor_start_out_edges) == 2
    xor_start_out_edges.remove((nodes["XOR_START_1"], nodes["XOR_START_2"]))
    new_a_event_node = xor_start_out_edges[0][1]
    assert isinstance(new_a_event_node, PUMLEventNode)
    assert new_a_event_node.node_type == "A"
    assert (new_a_event_node, nodes["B"]) in graph.edges
    # check that the second XOR now has two outgoing edges both of which are
    # of event type A. However one will be a break node and the other will be
    # connected to the C node
    xor_start_2_out_nodes: list[PUMLEventNode] = list(
        edge[1]
        for edge in graph.out_edges(nodes["XOR_START_2"])
    )
    assert len(xor_start_2_out_nodes) == 2
    breaks = 0
    for node in xor_start_2_out_nodes:
        assert node.node_type == "A"
        if PUMLEvent.BREAK in node.event_types:
            assert (node, nodes["XOR_END_2"]) in graph.edges
            breaks += 1
        else:
            assert (node, nodes["C"]) in graph.edges
    assert breaks == 1
    # test case with an event node above the dummy break event node and
    # nothing below
    graph = PUMLGraph()
    A = graph.create_event_node("A")
    DUMMY_BREAK = graph.create_event_node(
        DUMMY_BREAK_EVENT_TYPE,
        event_types=(PUMLEvent.BREAK,)
    )
    graph.add_puml_edge(A, DUMMY_BREAK)
    update_graph_for_dummy_break_event_node(DUMMY_BREAK, graph)
    assert DUMMY_BREAK not in graph.nodes
    assert PUMLEvent.BREAK in A.event_types
    # test case with an event node above the dummy break event node and
    # another node below
    A = graph.create_event_node("A")
    DUMMY_BREAK = graph.create_event_node(
        DUMMY_BREAK_EVENT_TYPE,
        event_types=(PUMLEvent.BREAK,)
    )
    B = graph.create_event_node("B")
    graph.add_puml_edge(A, DUMMY_BREAK)
    graph.add_puml_edge(DUMMY_BREAK, B)
    update_graph_for_dummy_break_event_node(DUMMY_BREAK, graph)
    assert DUMMY_BREAK not in graph.nodes
    assert PUMLEvent.BREAK in A.event_types
    assert (A, B) in graph.edges
    # test case with incorrect operators in the ancestry above break node
    for operator_type in [
        PUMLOperatorNodes.START_AND,
        PUMLOperatorNodes.END_AND,
        PUMLOperatorNodes.START_OR,
        PUMLOperatorNodes.END_OR,
        PUMLOperatorNodes.END_XOR,
    ]:
        puml_graph = PUMLGraph()
        A = puml_graph.create_event_node("A")
        DUMMY_BREAK = puml_graph.create_event_node(
            DUMMY_BREAK_EVENT_TYPE,
            event_types=(PUMLEvent.BREAK,)
        )
        operator_node = PUMLOperatorNode(operator_type, 0)
        puml_graph.add_puml_node(operator_node)
        puml_graph.increment_occurrence_count(operator_type.value)
        puml_graph.add_puml_edge(A, operator_node)
        puml_graph.add_puml_edge(operator_node, DUMMY_BREAK)
        with pytest.raises(NotImplementedError):
            update_graph_for_dummy_break_event_node(DUMMY_BREAK, puml_graph)
