"""End to end tests for nested constraint cases.
"""
import pytest

from tel2puml.utils_test import end_to_end_test


def test_kill_with_no_merge() -> None:
    """Test kill with no merge."""
    end_to_end_test(
        "end-to-end-pumls/constraints/kill/kill_with_no_merge.puml",
    )


def test_kill_with_merge() -> None:
    """Test kill with merge."""
    end_to_end_test(
        "end-to-end-pumls/constraints/kill/kill_with_merge.puml",
    )


@pytest.mark.xfail(
    reason="A kill XOR that merges on the parent will not work correctly"
    "currently",
    strict=True
)
def test_kill_with_merge_on_parent() -> None:
    """Test kill with merge on parent."""
    end_to_end_test(
        "end-to-end-pumls/constraints/kill/kill_with_merge_on_parent.puml",
    )


@pytest.mark.xfail(
    reason="A kill XOR that has only a single branch that continues will not "
    "work correctly as the logic block will continue beyond the end of the "
    "loop",
    strict=True
)
def test_kill_in_loop() -> None:
    """Test kill in loop."""
    end_to_end_test(
        "end-to-end-pumls/constraints/kill/kill_in_loop.puml",
    )
