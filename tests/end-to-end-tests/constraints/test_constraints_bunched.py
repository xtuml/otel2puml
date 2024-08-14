"""End to end tests for bunched constraint cases."""
from typing import Literal

import pytest

from tel2puml.utils_test import end_to_end_test


class TestConstraintBunchedAND:
    """End to end tests for bunched AND constraint cases."""
    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_bunched_AND_AND(version: Literal['v1', 'v2']) -> None:
        """Test bunched AND with AND."""
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/AND/"
            "bunched_ANDFork_ANDFork.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_bunched_AND_OR(version: Literal['v1', 'v2']) -> None:
        """Test bunched AND with OR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/AND/"
            "bunched_ANDFork_ORFork.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_bunched_AND_XOR(version: Literal['v1', 'v2']) -> None:
        """Test bunched AND with XOR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/AND/"
            "bunched_ANDFork_XORFork.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_bunched_merge_AND_AND(version: Literal['v1', 'v2']) -> None:
        """Test bunched merge AND with AND."""
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/AND/"
            "bunched_merge_ANDFork_ANDFork.puml",
            should_pass=False,
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_bunched_merge_AND_OR(version: Literal['v1', 'v2']) -> None:
        """Test bunched merge AND with OR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/AND/"
            "bunched_merge_ANDFork_ORFork.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_bunched_merge_AND_XOR(version: Literal['v1', 'v2']) -> None:
        """Test bunched merge AND with XOR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/AND/"
            "bunched_merge_ANDFork_XORFork.puml",
            version=version,
        )


class TestConstraintBunchedOR:
    """End to end tests for bunched OR constraint cases."""
    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_bunched_OR_AND(version: Literal['v1', 'v2']) -> None:
        """Test bunched OR with AND."""
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/OR/"
            "bunched_ORFork_ANDFork.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_bunched_OR_OR(version: Literal['v1', 'v2']) -> None:
        """Test bunched OR with OR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/OR/"
            "bunched_ORFork_ORFork.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_bunched_OR_XOR(version: Literal['v1', 'v2']) -> None:
        """Test bunched OR with XOR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/OR/"
            "bunched_ORFork_XORFork.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_bunched_merge_OR_AND(version: Literal['v1', 'v2']) -> None:
        """Test bunched merge OR with AND."""
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/OR/"
            "bunched_merge_ORFork_ANDFork.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_bunched_merge_OR_OR(version: Literal['v1', 'v2']) -> None:
        """Test bunched merge OR with OR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/OR/"
            "bunched_merge_ORFork_ORFork.puml",
            should_pass=False,
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_bunched_merge_OR_XOR(version: Literal['v1', 'v2']) -> None:
        """Test bunched merge OR with XOR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/OR/"
            "bunched_merge_ORFork_XORFork.puml",
        )


class TestConstraintBunchedXOR:
    """End to end tests for bunched XOR constraint cases."""
    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_bunched_XOR_AND(version: Literal['v1', 'v2']) -> None:
        """Test bunched XOR with AND."""
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/XOR/"
            "bunched_XORFork_ANDFork.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_bunched_XOR_OR(version: Literal['v1', 'v2']) -> None:
        """Test bunched XOR with OR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/XOR/"
            "bunched_XORFork_ORFork.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_bunched_XOR_XOR(version: Literal['v1', 'v2']) -> None:
        """Test bunched XOR with XOR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/XOR/"
            "bunched_XORFork_XORFork.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_bunched_merge_XOR_AND(version: Literal['v1', 'v2']) -> None:
        """Test bunched merge XOR with AND."""
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/XOR/"
            "bunched_merge_XORFork_ANDFork.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_bunched_merge_XOR_OR(version: Literal['v1', 'v2']) -> None:
        """Test bunched merge XOR with OR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/XOR/"
            "bunched_merge_XORFork_ORFork.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_bunched_merge_XOR_XOR(version: Literal['v1', 'v2']) -> None:
        """Test bunched merge XOR with XOR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/XOR/"
            "bunched_merge_XORFork_XORFork.puml",
            should_pass=False,
            version=version,
        )


class TestBunchedHard:
    """End to end tests for difficult bunched constraint cases."""
    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_bunched_three_levels_AND(version: Literal['v1', 'v2']) -> None:
        """Test bunched three levels of AND."""
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/"
            "bunched_3_levels_same_AND.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_bunched_three_levels_XOR(version: Literal['v1', 'v2']) -> None:
        """Test bunched three levels of XOR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/"
            "bunched_3_levels_same_XOR.puml",
            version=version,
        )
    
    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_bunched_AND_OR_AND(version: Literal['v1', 'v2']) -> None:
        """Test bunched three levels of XOR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/"
            "bunched_3_levels_AND_OR_AND.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_bunched_XOR_XOR_with_kill(version: Literal['v1', 'v2']) -> None:
        """Test bunched XOR with XOR with kill."""
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/"
            "bunched_XORFork_XORFork_with_kill.puml",
            version=version,
        )
