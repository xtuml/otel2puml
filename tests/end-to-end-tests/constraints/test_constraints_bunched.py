"""End to end tests for nested constraint cases."""

import pytest

from tel2puml.utils_test import end_to_end_test


class TestConstraintBunchedAND:
    @staticmethod
    @pytest.mark.xfail(
        reason="Bunched logic of same type currently unsupported", strict=True
    )
    def test_bunched_AND_AND() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/AND/"
            "bunched_ANDFork_ANDFork.puml",
        )

    @staticmethod
    @pytest.mark.xfail(
        reason="Currently a failing case needing fixing", strict=True
    )
    def test_bunched_AND_OR() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/AND/"
            "bunched_ANDFork_ORFork.puml",
        )

    @staticmethod
    def test_bunched_AND_XOR() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/AND/"
            "bunched_ANDFork_XORFork.puml",
        )

    @staticmethod
    @pytest.mark.xfail(reason="Indistinguishable from simple AND", strict=True)
    def test_bunched_merge_AND_AND() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/AND/"
            "bunched_merge_ANDFork_ANDFork.puml",
        )

    @staticmethod
    @pytest.mark.xfail(
        reason="Currently a failing case needing fixing", strict=True
    )
    def test_bunched_merge_AND_OR() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/AND/"
            "bunched_merge_ANDFork_ORFork.puml",
        )

    @staticmethod
    def test_bunched_merge_AND_XOR() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/AND/"
            "bunched_merge_ANDFork_XORFork.puml",
        )


class TestConstraintBunchedOR:
    @staticmethod
    def test_bunched_OR_AND() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/OR/"
            "bunched_ORFork_ANDFork.puml",
        )

    @staticmethod
    @pytest.mark.xfail(
        reason="Bunched logic of same type currently unsupported", strict=True
    )
    def test_bunched_OR_OR() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/OR/"
            "bunched_ORFork_ORFork.puml",
        )

    @staticmethod
    def test_bunched_OR_XOR() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/OR/"
            "bunched_ORFork_XORFork.puml",
        )

    @staticmethod
    def test_bunched_merge_OR_AND() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/OR/"
            "bunched_merge_ORFork_ANDFork.puml",
        )

    @staticmethod
    @pytest.mark.xfail(reason="Indistinguishable from simple OR", strict=True)
    def test_bunched_merge_OR_OR() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/OR/"
            "bunched_merge_ORFork_ORFork.puml",
        )

    @staticmethod
    def test_bunched_merge_OR_XOR() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/OR/"
            "bunched_merge_ORFork_XORFork.puml",
        )


class TestConstraintBunchedXOR:
    @staticmethod
    def test_bunched_XOR_AND() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/XOR/"
            "bunched_XORFork_ANDFork.puml",
        )

    @staticmethod
    def test_bunched_XOR_OR() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/XOR/"
            "bunched_XORFork_ORFork.puml",
        )

    @staticmethod
    @pytest.mark.xfail(
        reason="Bunched logic of same type currently unsupported", strict=True
    )
    def test_bunched_XOR_XOR() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/XOR/"
            "bunched_XORFork_XORFork.puml",
        )

    @staticmethod
    def test_bunched_merge_XOR_AND() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/XOR/"
            "bunched_merge_XORFork_ANDFork.puml",
        )

    @staticmethod
    def test_bunched_merge_XOR_OR() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/XOR/"
            "bunched_merge_XORFork_ORFork.puml",
        )

    @staticmethod
    @pytest.mark.xfail(reason="Indistinguishable from simple XOR", strict=True)
    def test_bunched_merge_XOR_XOR() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/XOR/"
            "bunched_merge_XORFork_XORFork.puml",
        )


class TestBunchedHard:
    @staticmethod
    @pytest.mark.xfail(
        reason="Bunched logic of same type currently unsupported", strict=True
    )
    def test_bunched_three_levels_AND() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/"
            "bunched_3_levels_same_AND.puml",
        )

    @staticmethod
    @pytest.mark.xfail(
        reason="Bunched logic of same type currently unsupported", strict=True
    )
    def test_bunched_three_levels_XOR() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/bunched/"
            "bunched_3_levels_same_XOR.puml",
        )
