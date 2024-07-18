"""End to end tests for loops.
"""
from typing import Literal

import pytest

from tel2puml.utils_test import end_to_end_test


@pytest.mark.parametrize(
    "version", ["v1", "v2"], ids=["version_1", "version_2"]
)
def test_self_loop(version: Literal['v1', 'v2']) -> None:
    """Test self loop."""
    end_to_end_test(
        "end-to-end-pumls/loops/self_loop.puml",
        version=version,
    )


class TestNestedLoops:
    """End to end tests for nested loops."""
    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_nested_normal_loop(version: Literal['v1', 'v2']) -> None:
        """Test nested normal loops."""
        end_to_end_test(
            "end-to-end-pumls/loops/nested_loops/nested_normal_loops.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_nested_self_loop(version: Literal['v1', 'v2']) -> None:
        """Test nested self loop."""
        end_to_end_test(
            "end-to-end-pumls/loops/nested_loops/nested_self_loop.puml",
            version=version,
        )


class TestNestedLogicBlocks:
    """End to end tests for nested logic blocks in loops."""
    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_nested_and(version: Literal['v1', 'v2']) -> None:
        """Test nested AND in loop"""
        end_to_end_test(
            "end-to-end-pumls/loops/nested_logic_blocks/loop_nested_AND.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_nested_or(version: Literal['v1', 'v2']) -> None:
        """Test nested OR in loop"""
        end_to_end_test(
            "end-to-end-pumls/loops/nested_logic_blocks/loop_nested_OR.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_nested_xor(version: Literal['v1', 'v2']) -> None:
        """Test nested XOR in loop"""
        end_to_end_test(
            "end-to-end-pumls/loops/nested_logic_blocks/loop_nested_XOR.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_logic_bunched(version: Literal['v1', 'v2']) -> None:
        """Test nested bunched logic in loop"""
        end_to_end_test(
            "end-to-end-pumls/loops/nested_logic_blocks/"
            "loop_nested_logic_bunched.puml",
            version=version,
        )


@pytest.mark.parametrize(
    "version", ["v1", "v2"], ids=["version_1", "version_2"]
)
def test_nested_branch_counts(version: Literal['v1', 'v2']) -> None:
    """Test nested branch counts in loop."""
    end_to_end_test(
        "end-to-end-pumls/loops/nested_branch_counts/"
        "loop_nested_branch_counts.puml",
        is_branch_puml=True,
        version=version,
    )


class TestBreakPoints:
    """End to end tests for break points in loops."""
    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_loop_break_point(version: Literal['v1', 'v2']) -> None:
        """Test loop with break point."""
        end_to_end_test(
            "end-to-end-pumls/loops/break_points/loop_break_point.puml",
            equivalent_pumls=[
                "end-to-end-pumls/loops/break_points/"
                "loop_break_point_equiv.puml",
            ],
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_loop_two_break_points(version: Literal['v1', 'v2']) -> None:
        """Test loop with 2 break points."""
        end_to_end_test(
            "end-to-end-pumls/loops/break_points/loop_with_2_breaks.puml",
            equivalent_pumls=[
                "end-to-end-pumls/loops/break_points/"
                "loop_with_2_breaks_equiv.puml",
            ],
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_loop_nested_break_point(version: Literal['v1', 'v2']) -> None:
        """Test loop with break point in a nested loop."""
        end_to_end_test(
            "end-to-end-pumls/loops/break_points/loop_nested_break_point.puml",
            equivalent_pumls=[
                "end-to-end-pumls/loops/break_points/"
                "loop_nested_break_point_equiv.puml",
            ],
            version=version,
        )


class TestEdgeCases:
    """End to end tests for edge cases of loops."""
    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_loop_break_split_exit(version: Literal['v1', 'v2']) -> None:
        """Test loop with break, split and exit."""
        end_to_end_test(
            "end-to-end-pumls/loops/edge_cases/loop_break_split_exit.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_paths_should_kill_in_loop(version: Literal['v1', 'v2']) -> None:
        """Test paths that should kill in loop."""
        end_to_end_test(
            "end-to-end-pumls/loops/edge_cases/paths_should_kill_in_loop.puml",
            version=version,
        )
