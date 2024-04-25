"""End to end tests for simple single level constraint cases.
"""
import pytest

from tel2puml.utils_test import end_to_end_test


class TestConstraintAND:
    """End to end tests for simple single level AND constraint cases."""
    @staticmethod
    def test_simple_AND() -> None:
        """Test simple AND."""
        end_to_end_test(
            "end-to-end-pumls/constraints/simple/AND/simple_AND.puml",
        )

    @staticmethod
    @pytest.mark.xfail(
        reason="Multiple AND events does not merge correctly",
        strict=True
    )
    def test_multiple_same_event_AND() -> None:
        """Test multiple same event AND."""
        end_to_end_test(
            "end-to-end-pumls/constraints/simple/AND/"
            "multiple_same_event_AND.puml",
        )

    @staticmethod
    @pytest.mark.xfail(
        reason="AND does not merge at the correct event and will merge too "
        "early",
        strict=True
    )
    def test_merge_at_correct_event_AND() -> None:
        """Test merge at correct event AND."""
        end_to_end_test(
            "end-to-end-pumls/constraints/simple/AND/"
            "merge_at_correct_event_AND.puml",
        )


class TestConstraintOR:
    """End to end tests for simple single level OR constraint cases."""
    @staticmethod
    def test_simple_OR() -> None:
        """Test simple OR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/simple/OR/simple_OR.puml",
        )

    @staticmethod
    @pytest.mark.xfail(
        reason="Currently OR will not merge at the correct event. Likely not "
        "possible to implement",
        strict=True
    )
    def test_merge_at_correct_event_OR() -> None:
        """Test merge at correct event OR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/simple/OR/"
            "merge_at_correct_event_OR.puml",
        )


class TestConstraintXOR:
    """End to end tests for simple single level XOR constraint cases."""
    @staticmethod
    def test_simple_XOR() -> None:
        """Test simple XOR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/simple/XOR/simple_XOR.puml",
        )

    @staticmethod
    @pytest.mark.xfail(
        reason="No need for XOR to merge further down so this will fail but "
        "the PUML's are equivalent",
        strict=True
    )
    def test_merge_at_correct_event_XOR() -> None:
        """Test merge at correct event XOR."""
        end_to_end_test(
            "end-to-end-pumls/constraints/simple/XOR/"
            "merge_at_correct_event_XOR.puml",
        )
