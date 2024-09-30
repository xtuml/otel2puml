"""End to end tests for nested constraint cases."""

from typing import Callable

import pytest


def test_kill_with_no_merge(end_to_end_test: Callable[..., None]) -> None:
    """Test kill with no merge."""
    end_to_end_test(
        "end-to-end-pumls/constraints/kill/kill_with_no_merge.puml",
    )


def test_kill_with_merge(end_to_end_test: Callable[..., None]) -> None:
    """Test kill with merge."""
    end_to_end_test(
        "end-to-end-pumls/constraints/kill/kill_with_merge.puml",
    )


@pytest.mark.xfail(
    reason="A kill XOR that merges on the parent will not work correctly"
    "currently",
    strict=True,
)
def test_kill_with_merge_on_parent(
    end_to_end_test: Callable[..., None],
) -> None:
    """Test kill with merge on parent."""
    end_to_end_test(
        "end-to-end-pumls/constraints/kill/kill_with_merge_on_parent.puml",
    )


def test_kill_in_loop(end_to_end_test: Callable[..., None]) -> None:
    """Test kill in loop."""
    end_to_end_test(
        "end-to-end-pumls/constraints/kill/kill_in_loop.puml",
    )
