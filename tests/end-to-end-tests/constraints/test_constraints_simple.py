"""End to end tests for simple single level constraint cases."""

from typing import Literal

import pytest

from tel2puml.utils_test import end_to_end_test


class TestConstraintAND:
    """End to end tests for simple single level AND constraint cases."""

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_simple_AND(version: Literal["v1", "v2"]) -> None:
        """Test simple AND."""
        end_to_end_test(
            "end-to-end-pumls/constraints/simple/AND/simple_AND.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_multiple_same_event_AND(version: Literal["v1", "v2"]) -> None:
        """Test multiple same event AND."""
        end_to_end_test(
            "end-to-end-pumls/constraints/simple/AND/"
            "multiple_same_event_AND.puml",
            version=version,
            equivalent_pumls=[
                "end-to-end-pumls/constraints/simple/AND/"
                "multiple_same_event_AND_equiv.puml"
            ]
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_multiple_same_event_AND_with_extra_branch(
        version: Literal["v1", "v2"],
    ) -> None:
        """Test multiple same event AND with extra branch"""
        end_to_end_test(
            "end-to-end-pumls/constraints/simple/AND/"
            "multiple_same_event_AND_with_extra_branch.puml",
            version=version,
            equivalent_pumls=[
                "end-to-end-pumls/constraints/simple/AND/"
                "multiple_same_event_AND_with_extra_branch_equiv.puml"
            ]
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_multiple_same_event_AND_with_self_loop(
        version: Literal["v1", "v2"],
    ) -> None:
        """Test multiple same event AND with self loop"""
        end_to_end_test(
            "end-to-end-pumls/constraints/simple/AND/"
            "multiple_same_event_AND_with_self_loop.puml",
            version=version,
            equivalent_pumls=[
                "end-to-end-pumls/constraints/simple/AND/"
                "multiple_same_event_AND_with_self_loop_equiv.puml"
            ]
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_merge_at_correct_event_AND(version: Literal["v1", "v2"]) -> None:
        """Test merge at correct event AND."""
        end_to_end_test(
            "end-to-end-pumls/constraints/simple/AND/"
            "merge_at_correct_event_AND.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_merge_at_correct_event_AND_with_kill(
        version: Literal["v1", "v2"],
    ) -> None:
        """Test merge at correct event AND with kill"""
        end_to_end_test(
            "end-to-end-pumls/constraints/simple/AND/"
            "merge_at_correct_event_AND_with_kill.puml",
            version=version,
        )


class TestConstraintOR:
    """End to end tests for simple single level OR constraint cases."""

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_simple_OR(version: Literal["v1", "v2"]) -> None:
        """Test simple OR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/simple/OR/simple_OR.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_merge_at_correct_event_OR(version: Literal["v1", "v2"]) -> None:
        """Test merge at correct event OR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/simple/OR/"
            "merge_at_correct_event_OR.puml",
            version=version,
        )


class TestConstraintXOR:
    """End to end tests for simple single level XOR constraint cases."""

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_simple_XOR(version: Literal["v1", "v2"]) -> None:
        """Test simple XOR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/simple/XOR/simple_XOR.puml",
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_merge_at_correct_event_XOR(version: Literal["v1", "v2"]) -> None:
        """Test merge at correct event XOR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/simple/XOR/"
            "merge_at_correct_event_XOR.puml",
            should_pass=False,
            version=version,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "version", ["v1", "v2"], ids=["version_1", "version_2"]
    )
    def test_merge_from_similar_paths(version: Literal["v1", "v2"]) -> None:
        """Test merge from similar paths."""
        end_to_end_test(
            "end-to-end-pumls/constraints/simple/XOR/"
            "merge_from_similar_paths.puml",
            version=version,
        )
