"""Tests for the puml_graph.graph module.
"""

import pytest

from tel2puml.tel2puml_types import PUMLEvent, PUMLOperatorNodes
from tel2puml.puml_graph.graph import (
    PUMLEventNode,
    PUMLOperatorNode,
    operator_node_puml_map
)


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
        assert event.extra_info == {
            "is_branch": False,
            "is_merge": False,
            "is_break": False
        }

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
            "is_branch": True,
            "is_merge": True,
            "is_break": True
        }

    @staticmethod
    def test_write_uml_block_normal() -> None:
        """Tests the write_uml_block method.
        """
        event = PUMLEventNode(
            "event", 0
        )
        for indent in [0, 4]:
            for tab_size in [0, 4]:
                assert event.write_uml_blocks(
                    indent=indent,
                    tab_size=tab_size
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
        ) == (
            ["    :event,BCNT,user=event,name=BC1;"],
            0
        )
        branch_event_no_branch_number = PUMLEventNode(
            "event", 0,
            (PUMLEvent.BRANCH,)
        )
        with pytest.raises(RuntimeError):
            branch_event_no_branch_number.write_uml_blocks(
                indent=4,
                tab_size=4
            )

        break_event = PUMLEventNode(
            "event", 0,
            (PUMLEvent.BREAK,),
        )
        assert break_event.write_uml_blocks(
            indent=4,
            tab_size=4
        ) == (
            ["    :event;", "    break"],
            0
        )


class TestPUMLOperatorNode:
    """Tests for the PUMLOperatorNode class."""
    @staticmethod
    def test_init() -> None:
        """Tests the __init__ method."""
        for operator_type in PUMLOperatorNodes:
            operator = PUMLOperatorNode(
                operator_type, 0
            )
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
                    " " * (indent + tab_size) + "case"
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
                            + operator_node_puml_map[
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
                            + operator_node_puml_map[
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
                            indent=indent,
                            tab_size=tab_size
                        ) == ([
                            " " * (indent - tab_size)
                            + operator_node_puml_map[
                                operator_type.value
                            ][0][0],
                        ], -1)
