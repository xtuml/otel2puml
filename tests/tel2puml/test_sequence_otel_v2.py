"""Test the tel2puml.sequence_otel_v2 module."""

import pytest

from tel2puml.sequence_otel_v2 import (
    order_groups_by_start_timestamp,
    sequence_groups_of_otel_events_asynchronously,
)
from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    OTelEvent,
)


class TestSeqeunceOTelJobs:
    """Test the sequence_otel_v2 module."""
    @staticmethod
    def reverse_order_groups() -> list[list[OTelEvent]]:
        return [
            [
                OTelEvent(
                    job_name="job_name",
                    job_id="job_id",
                    event_type="event_type",
                    event_id="event_id",
                    start_timestamp=i * 2 + j,
                    end_timestamp=i * 2 + j + 1,
                    application_name="application_name",
                    parent_event_id=None,
                    child_event_ids=None,
                )
                for j in reversed(range(2))
            ]
            for i in reversed(range(3))
        ]

    @staticmethod
    def correct_order_groups() -> list[list[OTelEvent]]:
        return [
            [
                OTelEvent(
                    job_name="job_name",
                    job_id="job_id",
                    event_type="event_type",
                    event_id="event_id",
                    start_timestamp=i * 2 + j,
                    end_timestamp=i * 2 + j + 1,
                    application_name="application_name",
                    parent_event_id=None,
                    child_event_ids=None,
                )
                for j in range(2)
            ]
            for i in range(3)
        ]

    def test_order_groups_by_start_timestamp(self) -> None:
        """Test order_groups_by_start_timestamp."""
        groups = self.reverse_order_groups()
        ordered_groups = order_groups_by_start_timestamp(groups)
        expected_ordered_groups = self.correct_order_groups()
        assert ordered_groups == expected_ordered_groups
        # test case where one group is empty
        with pytest.raises(ValueError):
            order_groups_by_start_timestamp(
                [
                    [],
                    [
                        OTelEvent(
                            job_name="job_name",
                            job_id="job_id",
                            event_type="event_type",
                            event_id="event_id",
                            start_timestamp=0,
                            end_timestamp=1,
                            application_name="application_name",
                            parent_event_id=None,
                            child_event_ids=None,
                        )
                    ],
                ]
            )
        # test case where there are no groups
        assert order_groups_by_start_timestamp([]) == []

    def test_sequence_groups_of_otel_events_asynchronously(self) -> None:
        """Test sequence_groups_of_otel_events_asynchronously."""
        # test case with correctly ordered groups which each overlap the
        # previous group
        groups = self.correct_order_groups()
        ordered_groups_async = sequence_groups_of_otel_events_asynchronously(
            groups
        )
        expected_ordered_groups_async = [
            [event for group in groups for event in group]
        ]
        assert ordered_groups_async == expected_ordered_groups_async
        # test case with the reverse groups
        ordered_groups_async = sequence_groups_of_otel_events_asynchronously(
            self.reverse_order_groups()
        )
        assert ordered_groups_async == expected_ordered_groups_async
        # test case with one group
        ordered_groups_async = sequence_groups_of_otel_events_asynchronously(
            [groups[0]]
        )
        assert ordered_groups_async == [groups[0]]
        # test case with no groups
        assert sequence_groups_of_otel_events_asynchronously([]) == []
