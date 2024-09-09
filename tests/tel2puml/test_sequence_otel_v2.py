"""Test the tel2puml.sequence_otel_v2 module."""

import pytest

from tel2puml.sequence_otel_v2 import (
    order_groups_by_start_timestamp,
    sequence_groups_of_otel_events_asynchronously,
    group_events_using_async_information,
    sequence_otel_event_ancestors
)
from tel2puml.find_unique_graphs.otel_ingestion.otel_data_model import (
    OTelEvent
)
from tel2puml.tel2puml_types import PVEvent


class TestSeqeunceOTelJobs:
    """Test the sequence_otel_v2 module."""
    @staticmethod
    def events() -> dict[str, OTelEvent]:
        """Return a dictionary of OTelEvents."""
        return {
            f"{i}{j}": OTelEvent(
                job_name="job_name",
                job_id="job_id",
                event_type=f"event_type_{i}{j}",
                event_id=f"{i}{j}",
                start_timestamp=i * 2 + j,
                end_timestamp=i * 2 + j + 1,
                application_name="application_name",
                parent_event_id=None,
                child_event_ids=[] if i == 2 or j == 1 else [
                    f"{i + 1}0", f"{i + 1}1"
                ],
            )
            for i in range(3)
            for j in range(2)
        }

    def root_event(self) -> OTelEvent:
        """Return the root OTelEvent."""
        return OTelEvent(
            job_name="job_name",
            job_id="job_id",
            event_type="root_event",
            event_id="root",
            start_timestamp=0,
            end_timestamp=1,
            application_name="application_name",
            parent_event_id=None,
            child_event_ids=["00", "01"],
        )

    def events_with_root(self) -> dict[str, OTelEvent]:
        """Return a dictionary of OTelEvents with a root event."""
        return {
            "root": self.root_event(),
            **self.events(),
        }

    def reverse_order_groups(self) -> list[list[OTelEvent]]:
        """Return groups of OTelEvents in reverse order."""
        events = self.events()
        return [
            [
                events[f"{i}{j}"]
                for j in reversed(range(2))
            ]
            for i in reversed(range(3))
        ]

    def correct_order_groups(self) -> list[list[OTelEvent]]:
        """Return a list of groups of OTelEvents in the correct order."""
        events = self.events()
        return [
            [
                events[f"{i}{j}"]
                for j in range(2)
            ]
            for i in range(3)
        ]

    def synchronous_previous_event_ids(self) -> dict[str, list[str]]:
        """Return a dictionary mapping event ids to a list of previous event
        ids."""
        return {
            "root": ["01"],
            "00": ["11"],
            "01": ["00"],
            "10": ["21"],
            "11": ["10"],
            "20": [],
            "21": ["20"],
        }

    def async_previous_event_ids(self) -> dict[str, list[str]]:
        """Return a dictionary mapping event ids to a list of previous event
        ids."""
        return {
            "root": ["00", "01"],
            "00": ["10", "11"],
            "01": [],
            "10": ["20", "21"],
            "11": [],
            "20": [],
            "21": [],
        }

    def prior_async_information_event_ids(self) -> dict[str, list[str]]:
        """Return a dictionary mapping event ids to a list of previous event
        ids."""
        return {
            "root": ["00", "01"],
            "00": ["11"],
            "01": [],
            "10": ["20", "21"],
            "11": ["10"],
            "20": [],
            "21": [],
        }

    def event_to_async_group_map(self) -> dict[str, dict[str, str]]:
        """Return a dictionary mapping event types to async groups.
        """
        return {
            "root": {
                "event_type_00": "group_0",
                "event_type_01": "group_0",
            },
            "event_type_10": {
                "event_type_20": "group_0",
                "event_type_21": "group_0",
            },
        }

    def pv_events(
        self,
        previous_event_ids: dict[str, list[str]],
        events: dict[str, OTelEvent],
    ) -> dict[str, PVEvent]:
        """Return a list of PVEvents.

        :param previous_event_ids: A dictionary mapping event ids to a list of
        previous event ids.
        :type previous_event_ids: `dict`[`str`, `list`[`str`]]
        :param events: A dictionary mapping event ids to OTelEvents.
        :type events: `dict`[`str`, :class:`OTelEvent`]
        :return: A list of PVEvents.
        :rtype: `list`[:class:`PVEvent`]
        """
        return sorted([
            PVEvent(
                eventId=event.event_id,
                jobId=event.job_id,
                timestamp=event.end_timestamp,
                previousEventIds=previous_event_ids.get(event.event_id, []),
                eventType=event.event_type,
                applicationName=event.application_name,
                jobName=event.job_name,
            )
            for event in events.values()
        ])

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

    def test_group_events_using_async_information(self) -> None:
        """Test group_events_using_async_information."""
        events = self.events()
        async_event_types = {
            "event_type_00": "group_0",
            "event_type_11": "group_0",
            "event_type_20": "group_1",
            "event_type_21": "group_1",
        }
        groups = group_events_using_async_information(
            list(events.values()), async_event_types
        )
        expected_groups = [
            [
                events["00"],
                events["11"],
            ],
            [
                events["20"],
                events["21"],
            ],
            [events["01"]],
            [events["10"]],
        ]
        assert groups == expected_groups
        # test case where there are no events
        assert (
            group_events_using_async_information([], async_event_types) == []
        )
        # test case where there are no async event types
        assert group_events_using_async_information(
            list(events.values()), {}
        ) == [[event] for event in events.values()]

    def test_sequence_otel_event_ancestors(self) -> None:
        """Test sequence_otel_event_ancestors."""
        # test case where the event has no ancestors
        events = self.events_with_root()
        event = events["01"]
        assert sequence_otel_event_ancestors(event, {}) == {"01": []}
        # synchronous sequencing
        assert (
            sequence_otel_event_ancestors(events["root"], events)
            == self.synchronous_previous_event_ids()
        )
        # async flag set to True
        assert sequence_otel_event_ancestors(
            events["root"], events, async_flag=True
        ) == self.async_previous_event_ids()
        # async information is provided
        event_to_async_group_map = self.event_to_async_group_map()
        assert sequence_otel_event_ancestors(
            events["root"],
            events,
            event_to_async_group_map=event_to_async_group_map,
        ) == self.prior_async_information_event_ids()
        # async information is provided and async flag is set to True
        assert sequence_otel_event_ancestors(
            events["root"],
            events,
            event_to_async_group_map=event_to_async_group_map,
            async_flag=True,
        ) == self.async_previous_event_ids()
        # raise error if child event ids has not been set
        with pytest.raises(ValueError):
            sequence_otel_event_ancestors(
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
                ),
                {},
            )

    def test_sequence_otel_event_job(self) -> None:
        """Test sequence_otel_event_job."""
        events = self.events_with_root()
        assert sorted(sequence_otel_event_job(events)) == self.pv_events(
            self.synchronous_previous_event_ids(), events
        )
        assert sorted(
            sequence_otel_event_job(events, async_flag=True)
        ) == self.pv_events(self.async_previous_event_ids(), events)
        event_to_async_group_map = self.event_to_async_group_map()
        assert sorted(
            sequence_otel_event_job(
                events, event_to_async_group_map=event_to_async_group_map
            )
        ) == self.pv_events(self.prior_async_information_event_ids(), events)
        assert sorted(
            sequence_otel_event_job(
                events,
                event_to_async_group_map=event_to_async_group_map,
                async_flag=True,
            )
        ) == self.pv_events(self.async_previous_event_ids(), events)
        # test case where there are no events
        assert sequence_otel_event_job({}) == []
