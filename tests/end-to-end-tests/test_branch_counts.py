"""End to end tests for branch counts.
"""
from tel2puml.utils_test import end_to_end_test


def test_simple_branch_count() -> None:
    """Test simple branch count."""
    end_to_end_test(
        "end-to-end-pumls/branch_counts/simple_branch_count.puml",
        is_branch_puml=True
    )


def test_double_branch_count() -> None:
    """Test double branch count."""
    end_to_end_test(
        "end-to-end-pumls/branch_counts/double_branch_count.puml",
        is_branch_puml=True
    )
