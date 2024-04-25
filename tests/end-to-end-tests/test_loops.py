"""End to end tests for loops.
"""
import pytest

from tel2puml.utils_test import end_to_end_test


def test_self_loop() -> None:
    end_to_end_test(
        "end-to-end-pumls/loops/self_loop.puml",
    )


class TestNestedLoops:
    @staticmethod
    def test_nested_normal_loop() -> None:
        end_to_end_test(
            "end-to-end-pumls/loops/nested_loops/nested_normal_loops.puml",
        )

    @staticmethod
    def test_nested_self_loop() -> None:
        end_to_end_test(
            "end-to-end-pumls/loops/nested_loops/nested_self_loop.puml",
        )


class TestNestedLogicBlocks:
    @staticmethod
    def test_nested_and() -> None:
        end_to_end_test(
            "end-to-end-pumls/loops/nested_logic_blocks/loop_nested_AND.puml",
        )

    @staticmethod
    def test_nested_or() -> None:
        end_to_end_test(
            "end-to-end-pumls/loops/nested_logic_blocks/loop_nested_OR.puml",
        )

    @staticmethod
    def test_nested_xor() -> None:
        end_to_end_test(
            "end-to-end-pumls/loops/nested_logic_blocks/loop_nested_XOR.puml",
        )

    @staticmethod
    @pytest.mark.xfail(
        reason="Bunched logic not working at end of loop", strict=True
    )
    def test_logic_bunched() -> None:
        end_to_end_test(
            "end-to-end-pumls/loops/nested_logic_blocks/"
            "loop_nested_logic_bunched.puml",
        )


@pytest.mark.xfail(
    reason="Markov chain is providing a straight chain rather than loop",
    strict=True
)
def test_nested_branch_counts() -> None:
    end_to_end_test(
        "end-to-end-pumls/loops/nested_branch_counts/"
        "loop_nested_branch_counts.puml",
        is_branch_puml=True,
    )


class TestBreakPoints:
    @staticmethod
    @pytest.mark.xfail(
        reason="Break points not connected in full solution currently",
        strict=True
    )
    def test_loop_break_point() -> None:
        end_to_end_test(
            "end-to-end-pumls/loops/break_points/loop_break_point.puml",
        )

    @staticmethod
    @pytest.mark.xfail(
        reason="Break points not connected in full solution currently",
        strict=True
    )
    def test_loop_two_break_points() -> None:
        end_to_end_test(
            "end-to-end-pumls/loops/break_points/loop_with_2_breaks.puml",
        )

    @staticmethod
    @pytest.mark.xfail(
        reason="Break points not connected in full solution currently",
        strict=True
    )
    def test_loop_nested_break_point() -> None:
        end_to_end_test(
            "end-to-end-pumls/loops/break_points/loop_nested_break_point.puml",
        )


class TestEdgeCases:
    @staticmethod
    @pytest.mark.xfail(
        reason="Break points not connected in full solution currently",
        strict=True
    )
    def test_loop_break_split_exit() -> None:
        end_to_end_test(
            "end-to-end-pumls/loops/edge_cases/loop_break_split_exit.puml",
        )
