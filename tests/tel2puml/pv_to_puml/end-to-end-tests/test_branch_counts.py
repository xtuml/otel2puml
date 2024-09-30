"""End to end tests for branch counts."""

from typing import Callable


def test_simple_branch_count(end_to_end_test: Callable[..., None]) -> None:
    """Test simple branch count."""
    end_to_end_test(
        "end-to-end-pumls/branch_counts/simple_branch_count.puml",
        is_branch_puml=True,
    )


def test_double_branch_count(end_to_end_test: Callable[..., None]) -> None:
    """Test double branch count."""
    end_to_end_test(
        "end-to-end-pumls/branch_counts/double_branch_count.puml",
        is_branch_puml=True,
    )


def test_branch_with_bunched_OR(end_to_end_test: Callable[..., None]) -> None:
    """Test double branch count."""
    end_to_end_test(
        "end-to-end-pumls/branch_counts/branch_with_bunched_OR.puml",
        is_branch_puml=True,
        dummy_start_event=True,
        equivalent_pumls=[
            "end-to-end-pumls/branch_counts/branch_with_bunched_OR_equiv.puml",
        ],
    )


def test_branch_with_bunched_AND(end_to_end_test: Callable[..., None]) -> None:
    """Test double branch count."""
    end_to_end_test(
        "end-to-end-pumls/branch_counts/branch_with_bunched_AND.puml",
        is_branch_puml=True,
        dummy_start_event=True,
        equivalent_pumls=[
            "end-to-end-pumls/branch_counts/branch_with_bunched_AND_equiv.puml"
        ],
    )
