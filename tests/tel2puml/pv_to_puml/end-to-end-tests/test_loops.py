"""End to end tests for loops."""
from typing import Callable


def test_self_loop(end_to_end_test: Callable[..., None]) -> None:
    """Test self loop."""
    end_to_end_test(
        "end-to-end-pumls/loops/self_loop.puml",
    )


class TestNestedLoops:
    """End to end tests for nested loops."""

    @staticmethod
    def test_nested_normal_loop(end_to_end_test: Callable[..., None]) -> None:
        """Test nested normal loops."""
        end_to_end_test(
            "end-to-end-pumls/loops/nested_loops/nested_normal_loops.puml",
        )

    @staticmethod
    def test_nested_self_loop(end_to_end_test: Callable[..., None]) -> None:
        """Test nested self loop."""
        end_to_end_test(
            "end-to-end-pumls/loops/nested_loops/nested_self_loop.puml",
        )


class TestNestedLogicBlocks:
    """End to end tests for nested logic blocks in loops."""

    @staticmethod
    def test_nested_and(end_to_end_test: Callable[..., None]) -> None:
        """Test nested AND in loop"""
        end_to_end_test(
            "end-to-end-pumls/loops/nested_logic_blocks/loop_nested_AND.puml",
        )

    @staticmethod
    def test_nested_or(end_to_end_test: Callable[..., None]) -> None:
        """Test nested OR in loop"""
        end_to_end_test(
            "end-to-end-pumls/loops/nested_logic_blocks/loop_nested_OR.puml",
        )

    @staticmethod
    def test_nested_xor(end_to_end_test: Callable[..., None]) -> None:
        """Test nested XOR in loop"""
        end_to_end_test(
            "end-to-end-pumls/loops/nested_logic_blocks/loop_nested_XOR.puml",
        )

    @staticmethod
    def test_logic_bunched(end_to_end_test: Callable[..., None]) -> None:
        """Test nested bunched logic in loop"""
        end_to_end_test(
            "end-to-end-pumls/loops/nested_logic_blocks/"
            "loop_nested_logic_bunched.puml",
        )


class TestNestedBranchCounts:
    """End to end tests for nested branch counts in loops."""

    @staticmethod
    def test_nested_branch_counts(
        end_to_end_test: Callable[..., None],
    ) -> None:
        """Test nested branch counts in loop."""
        end_to_end_test(
            "end-to-end-pumls/loops/nested_branch_counts/"
            "loop_nested_branch_counts.puml",
            is_branch_puml=True,
        )

    @staticmethod
    def test_loop_nested_branch_counts_event_at_end_of_loop(
        end_to_end_test: Callable[..., None],
    ) -> None:
        """Test loop with nested branch counts and event at end of loop."""
        end_to_end_test(
            "end-to-end-pumls/loops/nested_branch_counts/"
            "loop_nested_branch_counts_event_at_end_of_loop.puml",
            is_branch_puml=True,
            equivalent_pumls=[
                "end-to-end-pumls/loops/nested_branch_counts/"
                "loop_nested_branch_counts_event_at_end_of_loop_equiv.puml",
            ],
        )


class TestBreakPoints:
    """End to end tests for break points in loops."""

    @staticmethod
    def test_loop_break_point(end_to_end_test: Callable[..., None]) -> None:
        """Test loop with break point."""
        end_to_end_test(
            "end-to-end-pumls/loops/break_points/loop_break_point.puml",
            equivalent_pumls=[
                "end-to-end-pumls/loops/break_points/"
                "loop_break_point_equiv.puml",
            ],
        )

    @staticmethod
    def test_loop_two_break_points(
        end_to_end_test: Callable[..., None],
    ) -> None:
        """Test loop with 2 break points."""
        end_to_end_test(
            "end-to-end-pumls/loops/break_points/loop_with_2_breaks.puml",
            equivalent_pumls=[
                "end-to-end-pumls/loops/break_points/"
                "loop_with_2_breaks_equiv.puml",
            ],
        )

    @staticmethod
    def test_loop_nested_break_point(
        end_to_end_test: Callable[..., None],
    ) -> None:
        """Test loop with break point in a nested loop."""
        end_to_end_test(
            "end-to-end-pumls/loops/break_points/loop_nested_break_point.puml",
            equivalent_pumls=[
                "end-to-end-pumls/loops/break_points/"
                "loop_nested_break_point_equiv.puml",
            ],
        )
    
    @staticmethod
    def test_loop_with_2_breaks_one_leads_to_other(
        end_to_end_test: Callable[..., None],
    ) -> None:
        """Test loop with 2 breaks where one leads to the other."""
        end_to_end_test(
            "end-to-end-pumls/loops/break_points/"
            "loop_with_2_breaks_one_leads_to_other.puml",
            equivalent_pumls=[
                "end-to-end-pumls/loops/break_points/"
                "loop_with_2_breaks_one_leads_to_other_equiv.puml",
            ],
        )


class TestEdgeCases:
    """End to end tests for edge cases of loops."""

    @staticmethod
    def test_loop_break_split_exit(
        end_to_end_test: Callable[..., None],
    ) -> None:
        """Test loop with break, split and exit."""
        end_to_end_test(
            "end-to-end-pumls/loops/edge_cases/loop_break_split_exit.puml",
        )

    @staticmethod
    def test_paths_should_kill_in_loop(
        end_to_end_test: Callable[..., None],
    ) -> None:
        """Test paths that should kill in loop."""
        end_to_end_test(
            "end-to-end-pumls/loops/edge_cases/paths_should_kill_in_loop.puml",
        )

    @staticmethod
    def test_two_different_loops_follow_same_event(
        end_to_end_test: Callable[..., None],
    ) -> None:
        """Test two different loops following the same event."""
        end_to_end_test(
            "end-to-end-pumls/loops/edge_cases/"
            "two_different_loops_follow_same_event.puml",
        )
