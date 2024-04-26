"""End to end tests for loops.
"""
import pytest

from tel2puml.utils_test import end_to_end_test


def test_self_loop() -> None:
    """Test self loop."""
    end_to_end_test(
        "end-to-end-pumls/loops/self_loop.puml",
    )


class TestNestedLoops:
    """End to end tests for nested loops."""
    @staticmethod
    def test_nested_normal_loop() -> None:
        """Test nested normal loops."""
        end_to_end_test(
            "end-to-end-pumls/loops/nested_loops/nested_normal_loops.puml",
        )

    @staticmethod
    def test_nested_self_loop() -> None:
        """Test nested self loop."""
        end_to_end_test(
            "end-to-end-pumls/loops/nested_loops/nested_self_loop.puml",
        )


class TestNestedLogicBlocks:
    """End to end tests for nested logic blocks in loops."""
    @staticmethod
    def test_nested_and() -> None:
        """Test nested AND in loop"""
        end_to_end_test(
            "end-to-end-pumls/loops/nested_logic_blocks/loop_nested_AND.puml",
        )

    @staticmethod
    def test_nested_or() -> None:
        """Test nested OR in loop"""
        end_to_end_test(
            "end-to-end-pumls/loops/nested_logic_blocks/loop_nested_OR.puml",
        )

    @staticmethod
    def test_nested_xor() -> None:
        """Test nested XOR in loop"""
        end_to_end_test(
            "end-to-end-pumls/loops/nested_logic_blocks/loop_nested_XOR.puml",
        )

    @staticmethod
    @pytest.mark.xfail(
        reason="Bunched logic not working at end of loop", strict=True
    )
    def test_logic_bunched() -> None:
        """Test nested bunched logic in loop"""
        end_to_end_test(
            "end-to-end-pumls/loops/nested_logic_blocks/"
            "loop_nested_logic_bunched.puml",
        )


def test_nested_branch_counts() -> None:
    """Test nested branch counts in loop."""
    end_to_end_test(
        "end-to-end-pumls/loops/nested_branch_counts/"
        "loop_nested_branch_counts.puml",
        is_branch_puml=True,
    )


class TestBreakPoints:
    """End to end tests for break points in loops."""
    @staticmethod
    @pytest.mark.xfail(
        reason="Break points not connected in full solution currently",
        strict=True
    )
    def test_loop_break_point() -> None:
        """Test loop with break point."""
        end_to_end_test(
            "end-to-end-pumls/loops/break_points/loop_break_point.puml",
        )

    @staticmethod
    @pytest.mark.xfail(
        reason="Break points not connected in full solution currently",
        strict=True
    )
    def test_loop_two_break_points() -> None:
        """Test loop with 2 break points."""
        end_to_end_test(
            "end-to-end-pumls/loops/break_points/loop_with_2_breaks.puml",
        )

    @staticmethod
    @pytest.mark.xfail(
        reason="Break points not connected in full solution currently",
        strict=True
    )
    def test_loop_nested_break_point() -> None:
        """Test loop with break point in a nested loop."""
        end_to_end_test(
            "end-to-end-pumls/loops/break_points/loop_nested_break_point.puml",
        )


class TestEdgeCases:
    """End to end tests for edge cases of loops."""
    @staticmethod
    @pytest.mark.xfail(
        reason="Break points not connected in full solution currently",
        strict=True
    )
    def test_loop_break_split_exit() -> None:
        """Test loop with break, split and exit."""
        end_to_end_test(
            "end-to-end-pumls/loops/edge_cases/loop_break_split_exit.puml",
        )
