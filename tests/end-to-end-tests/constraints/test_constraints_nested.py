"""End to end tests for nested constraint cases.
"""
from typing import Literal

import pytest

from tel2puml.utils_test import end_to_end_test


class TestConstraintNestedAND:
    """End to end tests for nested AND constraint cases."""
    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_AND_AND(version: Literal['v1', 'v2']) -> None:
        """Test AND with nested AND."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/AND/ANDFork_ANDFork_a.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_AND_OR(version: Literal['v1', 'v2']) -> None:
        """Test AND with nested OR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/AND/ANDFork_ORFork_a.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_AND_XOR(version: Literal['v1', 'v2']) -> None:
        """Test AND with nested XOR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/AND/ANDFork_XORFork_a.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2",], ids=["version_1", "version_2"]
    )
    def test_AND_branch_count(version: Literal['v1', 'v2']) -> None:
        """Test AND with nested branch count."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/AND/"
            "ANDFork_branch_count.puml",
            is_branch_puml=True,
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_AND_loop(version: Literal['v1', 'v2']) -> None:
        """Test AND with nested loop."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/AND/ANDFork_loop_a.puml",
            version=version,
        )


class TestConstraintNestedOR:
    """End to end tests for nested OR constraint cases."""
    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_OR_AND(version: Literal['v1', 'v2']) -> None:
        """Test OR with nested AND."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/OR/ORFork_ANDFork_a.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_OR_OR(version: Literal['v1', 'v2']) -> None:
        """Test OR with nested OR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/OR/ORFork_ORFork_a.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_OR_XOR(version: Literal['v1', 'v2']) -> None:
        """Test OR with nested XOR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/OR/ORFork_XORFork_a.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2",], ids=["version_1", "version_2"]
    )
    def test_OR_branch_count(version: Literal['v1', 'v2']) -> None:
        """Test OR with nested branch count."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/OR/ORFork_branch_count.puml",
            is_branch_puml=True,
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_OR_loop(version: Literal['v1', 'v2']) -> None:
        """Test OR with nested loop."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/OR/ORFork_loop_a.puml",
            version=version,
        )


class TestConstraintNestedXOR:
    """End to end tests for nested XOR constraint cases."""
    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_XOR_AND(version: Literal['v1', 'v2']) -> None:
        """Test XOR with nested AND."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/XOR/XORFork_ANDFork_a.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_XOR_OR(version: Literal['v1', 'v2']) -> None:
        """Test XOR with nested OR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/XOR/XORFork_ORFork_a.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_XOR_XOR(version: Literal['v1', 'v2']) -> None:
        """Test XOR with nested XOR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/XOR/XORFork_XORFork_a.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_XOR_branch_count(version: Literal['v1', 'v2']) -> None:
        """Test XOR with nested branch count."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/XOR/"
            "XORFork_branch_count.puml",
            is_branch_puml=True,
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_XOR_loop(version: Literal['v1', 'v2']) -> None:
        """Test XOR with nested loop."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/XOR/XORFork_loop_a.puml",
            version=version,
        )
