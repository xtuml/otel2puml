"""End to end tests for nested constraint cases.
"""
from typing import Literal

import pytest

from tel2puml.utils_test import end_to_end_test


@pytest.mark.parametrize(
    "version", ["v1", "v2"], ids=["version_1", "version_2"]
)
def test_kill_with_no_merge(version: Literal['v1', 'v2']) -> None:
    """Test kill with no merge."""
    end_to_end_test(
        "end-to-end-pumls/constraints/kill/kill_with_no_merge.puml",
        version=version,
    )


@pytest.mark.parametrize(
    "version", ["v1", "v2"], ids=["version_1", "version_2"]
)
def test_kill_with_merge(version: Literal['v1', 'v2']) -> None:
    """Test kill with merge."""
    end_to_end_test(
        "end-to-end-pumls/constraints/kill/kill_with_merge.puml",
        version=version,
    )


@pytest.mark.xfail(
    reason="A kill XOR that merges on the parent will not work correctly"
    "currently",
    strict=True
)
@pytest.mark.parametrize(
    "version", ["v1", "v2"], ids=["version_1", "version_2"]
)
def test_kill_with_merge_on_parent(version: Literal['v1', 'v2']) -> None:
    """Test kill with merge on parent."""
    end_to_end_test(
        "end-to-end-pumls/constraints/kill/kill_with_merge_on_parent.puml",
        version=version,
    )


@pytest.mark.parametrize(
    "version", ["v1", "v2"], ids=["version_1", "version_2"]
)
def test_kill_in_loop(version: Literal['v1', 'v2']) -> None:
    """Test kill in loop."""
    end_to_end_test(
        "end-to-end-pumls/constraints/kill/kill_in_loop.puml",
        version=version,
    )
