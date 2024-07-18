"""End to end tests for branch counts.
"""
from typing import Literal

import pytest

from tel2puml.utils_test import end_to_end_test


@pytest.mark.parametrize(
    "version", ["v1", "v2"], ids=["version_1", "version_2"]
)
def test_simple_branch_count(version: Literal['v1', 'v2']) -> None:
    """Test simple branch count."""
    end_to_end_test(
        "end-to-end-pumls/branch_counts/simple_branch_count.puml",
        is_branch_puml=True,
        version=version,
    )


@pytest.mark.parametrize(
    "version", ["v1", "v2"], ids=["version_1", "version_2"]
)
def test_double_branch_count(version: Literal['v1', 'v2']) -> None:
    """Test double branch count."""
    end_to_end_test(
        "end-to-end-pumls/branch_counts/double_branch_count.puml",
        is_branch_puml=True,
        version=version,
    )
