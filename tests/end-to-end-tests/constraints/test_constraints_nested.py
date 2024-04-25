"""End to end tests for nested constraint cases.
"""
from tel2puml.utils_test import end_to_end_test


class TestConstraintNestedAND:
    """End to end tests for nested AND constraint cases."""
    @staticmethod
    def test_AND_AND() -> None:
        """Test AND with nested AND."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/AND/ANDFork_ANDFork_a.puml",
        )

    @staticmethod
    def test_AND_OR() -> None:
        """Test AND with nested OR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/AND/ANDFork_ORFork_a.puml",
        )

    @staticmethod
    def test_AND_XOR() -> None:
        """Test AND with nested XOR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/AND/ANDFork_XORFork_a.puml",
        )

    @staticmethod
    def test_AND_branch_count() -> None:
        """Test AND with nested branch count."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/AND/"
            "ANDFork_branch_count.puml",
            is_branch_puml=True
        )

    @staticmethod
    def test_AND_loop() -> None:
        """Test AND with nested loop."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/AND/ANDFork_loop_a.puml",
        )


class TestConstraintNestedOR:
    """End to end tests for nested OR constraint cases."""
    @staticmethod
    def test_OR_AND() -> None:
        """Test OR with nested AND."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/OR/ORFork_ANDFork_a.puml",
        )

    @staticmethod
    def test_OR_OR() -> None:
        """Test OR with nested OR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/OR/ORFork_ORFork_a.puml",
        )

    @staticmethod
    def test_OR_XOR() -> None:
        """Test OR with nested XOR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/OR/ORFork_XORFork_a.puml",
        )

    @staticmethod
    def test_OR_branch_count() -> None:
        """Test OR with nested branch count."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/OR/ORFork_branch_count.puml",
            is_branch_puml=True
        )

    @staticmethod
    def test_OR_loop() -> None:
        """Test OR with nested loop."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/OR/ORFork_loop_a.puml",
        )


class TestConstraintNestedXOR:
    """End to end tests for nested XOR constraint cases."""
    @staticmethod
    def test_XOR_AND() -> None:
        """Test XOR with nested AND."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/XOR/XORFork_ANDFork_a.puml",
        )

    @staticmethod
    def test_XOR_OR() -> None:
        """Test XOR with nested OR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/XOR/XORFork_ORFork_a.puml",
        )

    @staticmethod
    def test_XOR_XOR() -> None:
        """Test XOR with nested XOR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/XOR/XORFork_XORFork_a.puml",
        )

    @staticmethod
    def test_XOR_branch_count() -> None:
        """Test XOR with nested branch count."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/XOR/"
            "XORFork_branch_count.puml",
            is_branch_puml=True
        )

    @staticmethod
    def test_XOR_loop() -> None:
        """Test XOR with nested loop."""
        end_to_end_test(
            "end-to-end-pumls/constraints/nested/XOR/XORFork_loop_a.puml",
        )
