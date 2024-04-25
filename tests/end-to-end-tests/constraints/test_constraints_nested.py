"""End to end tests for nested constraint cases.
"""
from tel2puml.utils_test import end_to_end_test


class TestConstraintNestedAND:
    @staticmethod
    def test_AND_AND() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/AND/ANDFork_ANDFork_a.puml",
        )

    @staticmethod
    def test_AND_OR() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/AND/ANDFork_ORFork_a.puml",
        )

    @staticmethod
    def test_AND_XOR() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/AND/ANDFork_XORFork_a.puml",
        )

    @staticmethod
    def test_AND_branch_count() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/AND/"
            "ANDFork_branch_count.puml",
            is_branch_puml=True
        )

    @staticmethod
    def test_AND_loop() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/AND/ANDFork_loop_a.puml",
        )


class TestConstraintNestedOR:
    @staticmethod
    def test_OR_AND() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/OR/ORFork_ANDFork_a.puml",
        )

    @staticmethod
    def test_OR_OR() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/OR/ORFork_ORFork_a.puml",
        )

    @staticmethod
    def test_OR_XOR() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/OR/ORFork_XORFork_a.puml",
        )

    @staticmethod
    def test_OR_branch_count() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/OR/ORFork_branch_count.puml",
            is_branch_puml=True
        )

    @staticmethod
    def test_OR_loop() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/OR/ORFork_loop_a.puml",
        )


class TestConstraintNestedXOR:
    @staticmethod
    def test_XOR_AND() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/XOR/XORFork_ANDFork_a.puml",
        )

    @staticmethod
    def test_XOR_OR() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/XOR/XORFork_ORFork_a.puml",
        )

    @staticmethod
    def test_XOR_XOR() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/XOR/XORFork_XORFork_a.puml",
        )

    @staticmethod
    def test_XOR_branch_count() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/XOR/"
            "XORFork_branch_count.puml",
            is_branch_puml=True
        )

    @staticmethod
    def test_XOR_loop() -> None:
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/XOR/XORFork_loop_a.puml",
        )
