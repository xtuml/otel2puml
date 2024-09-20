"""Test the tel2puml.sequence_otel_v2 module."""

from typing import Iterable, Generator, Any

import pytest
import yaml
from pytest import MonkeyPatch
from pathlib import Path

from tel2puml.otel_to_pv.sequence_otel_v2 import (
    order_groups_by_start_timestamp,
    sequence_groups_of_otel_events_asynchronously,
    group_events_using_async_information,
    sequence_otel_event_ancestors,
    get_root_event_from_event_id_to_event_map,
    sequence_otel_event_job,
    sequence_otel_jobs,
    sequence_otel_job_id_streams,
    job_ids_to_eventid_to_otelevent_map,
    config_to_otel_job_name_group_streams,
    otel_to_pv,
)
from tel2puml.otel_to_pv.otel_to_pv_types import OTelEvent
from tel2puml.tel2puml_types import PVEvent
from tel2puml.utils import unix_nano_to_pv_string
from tel2puml.otel_to_pv.data_holders.sql_data_holder.sql_dataholder import (
    SQLDataHolder,
)
from tel2puml.otel_to_pv.config import IngestDataConfig, IngestTypes


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
                parent_event_id="root" if i == 0 else f"{i - 1}{0}",
                child_event_ids=(
                    [] if i == 2 or j == 1 else [f"{i + 1}0", f"{i + 1}1"]
                ),
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
            [events[f"{i}{j}"] for j in reversed(range(2))]
            for i in reversed(range(3))
        ]

    def correct_order_groups(self) -> list[list[OTelEvent]]:
        """Return a list of groups of OTelEvents in the correct order."""
        events = self.events()
        return [[events[f"{i}{j}"] for j in range(2)] for i in range(3)]

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
        """Return a dictionary mapping event types to async groups."""
        return {
            "root_event": {
                "event_type_00": "group_0",
                "event_type_01": "group_0",
            },
            "event_type_10": {
                "event_type_20": "group_0",
                "event_type_21": "group_0",
            },
        }

    def sort_pv_events(
        self, unsorted_pv_events: Iterable[PVEvent]
    ) -> list[PVEvent]:
        """Return a sorted list of PVEvents."""
        return sorted(
            unsorted_pv_events,
            key=lambda pv_event: pv_event["eventId"],
        )

    def pv_events(
        self,
        previous_event_ids: dict[str, list[str]],
        events: dict[str, OTelEvent],
    ) -> list[PVEvent]:
        """Return a list of PVEvents."""
        return self.sort_pv_events(
            [
                PVEvent(
                    eventId=event.event_id,
                    jobId=event.job_id,
                    timestamp=unix_nano_to_pv_string(event.end_timestamp),
                    previousEventIds=previous_event_ids.get(
                        event.event_id, []
                    ),
                    eventType=event.event_type,
                    applicationName=event.application_name,
                    jobName=event.job_name,
                )
                for event in events.values()
            ]
        )

    def get_ingest_config(
        self, config_yaml: str, new_dirpath: Path
    ) -> IngestDataConfig:
        """Updates the dirpath in the config yaml string."""
        update_config_yaml_string = config_yaml.replace(
            "dirpath: /path/to/json/directory", f"dirpath: {new_dirpath}"
        ).replace("filepath: /path/to/json/file.json", "filepath: null")
        config_dict: dict[str, Any] = yaml.safe_load(update_config_yaml_string)
        config = IngestDataConfig(
            data_sources=config_dict["data_sources"],
            data_holders=config_dict["data_holders"],
            ingest_data=IngestTypes(**config_dict["ingest_data"]),
        )
        return config

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
        assert (
            sequence_otel_event_ancestors(
                events["root"], events, async_flag=True
            )
            == self.async_previous_event_ids()
        )
        # async information is provided
        event_to_async_group_map = self.event_to_async_group_map()
        assert (
            sequence_otel_event_ancestors(
                events["root"],
                events,
                event_to_async_group_map=event_to_async_group_map,
            )
            == self.prior_async_information_event_ids()
        )
        # async information is provided and async flag is set to True
        assert (
            sequence_otel_event_ancestors(
                events["root"],
                events,
                event_to_async_group_map=event_to_async_group_map,
                async_flag=True,
            )
            == self.async_previous_event_ids()
        )
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

    def test_get_root_event_from_event_id_to_event_map(self) -> None:
        """Test get_root_event_from_event_id_to_event_map."""
        events = self.events_with_root()
        assert (
            get_root_event_from_event_id_to_event_map(events)
            == self.root_event()
        )
        # test case where there are no events
        with pytest.raises(ValueError):
            get_root_event_from_event_id_to_event_map({})
        # test case where there are multiple root events
        with pytest.raises(ValueError):
            get_root_event_from_event_id_to_event_map(
                {f"{i}": self.root_event() for i in range(2)}
            )
        # test the case where there is no root event
        del events["root"]
        with pytest.raises(ValueError):
            get_root_event_from_event_id_to_event_map(events)

    def test_sequence_otel_event_job(self) -> None:
        """Test sequence_otel_event_job."""
        events = self.events_with_root()
        assert self.sort_pv_events(
            sequence_otel_event_job(events)
        ) == self.pv_events(self.synchronous_previous_event_ids(), events)
        assert self.sort_pv_events(
            sequence_otel_event_job(events, async_flag=True)
        ) == self.pv_events(self.async_previous_event_ids(), events)
        event_to_async_group_map = self.event_to_async_group_map()
        assert self.sort_pv_events(
            sequence_otel_event_job(
                events, event_to_async_group_map=event_to_async_group_map
            )
        ) == self.pv_events(self.prior_async_information_event_ids(), events)
        assert self.sort_pv_events(
            sequence_otel_event_job(
                events,
                event_to_async_group_map=event_to_async_group_map,
                async_flag=True,
            )
        ) == self.pv_events(self.async_previous_event_ids(), events)
        # test case where there are no events, should raise an error due to
        # the lack of a root event
        with pytest.raises(ValueError):
            list(sequence_otel_event_job({}))

    def test_sequence_otel_jobs(self) -> None:
        """Test sequence_otel_jobs."""
        events = self.events_with_root()
        for pv_events in sequence_otel_jobs([events] * 2):
            assert self.sort_pv_events(pv_events) == self.pv_events(
                self.synchronous_previous_event_ids(), events
            )
        for pv_events in sequence_otel_jobs([events] * 2, async_flag=True):
            assert self.sort_pv_events(pv_events) == self.pv_events(
                self.async_previous_event_ids(), events
            )
        for pv_events in sequence_otel_jobs(
            [events] * 2,
            event_to_async_group_map=self.event_to_async_group_map(),
        ):
            assert self.sort_pv_events(pv_events) == self.pv_events(
                self.prior_async_information_event_ids(), events
            )
        for pv_events in sequence_otel_jobs(
            [events] * 2,
            event_to_async_group_map=self.event_to_async_group_map(),
            async_flag=True,
        ):
            assert self.sort_pv_events(pv_events) == self.pv_events(
                self.async_previous_event_ids(), events
            )

    def test_sequence_otel_job_id_streams(self) -> None:
        """Tests for the function sequence_otel_job_id_streams"""

        # Test 1: Default parameters
        def job_id_streams() -> (
            Generator[Generator[OTelEvent, None, None], None, None]
        ):
            """Create a generator of generators of OTelEvents"""
            event_group = [event for event in events.values()]
            yield (event for event in event_group)

        events = self.events_with_root()

        expected_pv_events = self.pv_events(
            self.synchronous_previous_event_ids(), events
        )

        pv_event_generators = sequence_otel_job_id_streams(job_id_streams())

        actual_pv_events = []
        for pv_event_gen in pv_event_generators:
            actual_pv_events.extend(list(pv_event_gen))

        assert self.sort_pv_events(actual_pv_events) == self.sort_pv_events(
            expected_pv_events
        )

        # Test 2: async_flag = True
        expected_pv_events = []
        expected_pv_events.extend(
            self.pv_events(self.async_previous_event_ids(), events)
        )

        pv_event_generators = sequence_otel_job_id_streams(
            job_id_streams(), async_flag=True
        )
        actual_pv_events = []
        for pv_event_gen in pv_event_generators:
            actual_pv_events.extend(list(pv_event_gen))

        assert self.sort_pv_events(actual_pv_events) == self.sort_pv_events(
            expected_pv_events
        )

        # Test 3: event_to_async_group_map provided
        expected_pv_events = []
        expected_pv_events.extend(
            self.pv_events(self.prior_async_information_event_ids(), events)
        )

        event_to_async_group_map = self.event_to_async_group_map()
        pv_event_generators = sequence_otel_job_id_streams(
            job_id_streams(), event_to_async_group_map=event_to_async_group_map
        )

        actual_pv_events = []
        for pv_event_gen in pv_event_generators:
            actual_pv_events.extend(list(pv_event_gen))

        assert self.sort_pv_events(actual_pv_events) == self.sort_pv_events(
            expected_pv_events
        )

    def test_job_ids_to_eventid_to_otelevent_map(self) -> None:
        """Tests for the function job_ids_to_eventid_to_otelevent_map"""

        def job_id_streams() -> (
            Generator[Generator[OTelEvent, None, None], None, None]
        ):
            """Create a generator of generators of OTelEvents"""
            event_group = [event for event in events.values()]
            yield (event for event in event_group)

        events = self.events_with_root()

        expected_mappings = []
        expected_mappings.append(
            {event.event_id: event for event in events.values()}
        )

        event_dict_gen = job_ids_to_eventid_to_otelevent_map(job_id_streams())
        actual_mappings = list(event_dict_gen)

        assert len(actual_mappings) == len(expected_mappings)
        assert actual_mappings == expected_mappings

    def test_config_to_otel_job_name_group_streams(
        self,
        monkeypatch: MonkeyPatch,
        mock_yaml_config_dict: dict[str, Any],
        sql_data_holder_with_otel_jobs: SQLDataHolder,
        mock_yaml_config_string: str,
        mock_temp_dir_with_json_files: Path,
    ) -> None:
        """Tests for the function config_to_otel_job_name_group_streams"""

        # Test 1: Default parameters
        def mock_fetch_data_holder(config: IngestDataConfig) -> SQLDataHolder:
            return sql_data_holder_with_otel_jobs

        ingest_data_config = IngestDataConfig(
            data_sources=mock_yaml_config_dict["data_sources"],
            data_holders=mock_yaml_config_dict["data_holders"],
            ingest_data=IngestTypes(**mock_yaml_config_dict["ingest_data"]),
        )
        monkeypatch.setattr(
            "tel2puml.otel_to_pv.sequence_otel_v2.fetch_data_holder",
            mock_fetch_data_holder,
        )
        result = config_to_otel_job_name_group_streams(ingest_data_config)

        assert result
        events = []
        valid_job_names = {"test_name"}
        valid_event_ids = [f"{i}_{j}" for i in range(5) for j in range(2)]
        valid_job_ids = {f"test_id_{i}" for i in range(5)}
        job_id_count: dict[str, int] = {}
        for job_name, job_generator in result:
            assert job_name in valid_job_names
            for otel_event_generator in job_generator:
                for otel_event in otel_event_generator:
                    job_id_count.setdefault(otel_event.job_id, 0)
                    job_id_count[otel_event.job_id] += 1
                    events.append(otel_event)
                    assert isinstance(otel_event, OTelEvent)
                    assert otel_event.event_id in valid_event_ids
                    assert otel_event.job_id in valid_job_ids
                    valid_event_ids.remove(otel_event.event_id)

        assert len(events) == 10
        assert all(isinstance(event, OTelEvent) for event in events)
        assert all(count == 2 for count in job_id_count.values())
        assert len(valid_event_ids) == 0

        # Test 2: ingest_data = True
        config = self.get_ingest_config(
            mock_yaml_config_string, mock_temp_dir_with_json_files
        )
        result = config_to_otel_job_name_group_streams(
            config, ingest_data=True
        )
        events = []
        valid_job_names = {"Backend TestJob", "Frontend TestJob"}
        valid_job_ids = {
            "0_trace_id_1 4.8",
            "1_trace_id_1 4.8",
            "0_trace_id_0 4.8",
            "1_trace_id_0 4.8",
        }
        valid_event_ids = [
            f"{i}_span_{j}_{k}"
            for i in range(2)
            for j in range(2)
            for k in range(2)
        ]
        job_id_count = {}
        for job_name, job_generator in result:
            for otel_event_generator in job_generator:
                for otel_event in otel_event_generator:
                    job_id_count.setdefault(otel_event.job_id, 0)
                    job_id_count[otel_event.job_id] += 1
                    events.append(otel_event)
                    assert isinstance(otel_event, OTelEvent)
                    assert otel_event.event_id in valid_event_ids
                    assert otel_event.job_id in valid_job_ids
                    valid_event_ids.remove(otel_event.event_id)
        assert len(events) == 8
        assert all(isinstance(event, OTelEvent) for event in events)
        assert all(count == 2 for count in job_id_count.values())
        assert len(valid_event_ids) == 0

        # Test 3: find_unique_graphs = True
        result = config_to_otel_job_name_group_streams(
            ingest_data_config, find_unique_graphs=True
        )

        assert result
        events = []
        valid_job_names = {"test_name"}
        # job id test_id_0 is outside the config time buffer window, therefore
        # it is not included, reducing total events streamed to 8
        valid_event_ids = [f"{i}_{j}" for i in range(1, 5) for j in range(2)]
        valid_job_ids = {f"test_id_{i}" for i in range(1, 5)}
        job_id_count = {}
        for job_name, job_generator in result:
            assert job_name in valid_job_names
            for otel_event_generator in job_generator:
                for otel_event in otel_event_generator:
                    job_id_count.setdefault(otel_event.job_id, 0)
                    job_id_count[otel_event.job_id] += 1
                    events.append(otel_event)
                    assert isinstance(otel_event, OTelEvent)
                    assert otel_event.event_id in valid_event_ids
                    assert otel_event.job_id in valid_job_ids
                    valid_event_ids.remove(otel_event.event_id)

        assert len(events) == 8
        assert all(isinstance(event, OTelEvent) for event in events)
        assert all(count == 2 for count in job_id_count.values())
        assert len(valid_event_ids) == 0

    def test_otel_to_pv(
        self,
        monkeypatch: MonkeyPatch,
        mock_yaml_config_dict: dict[str, Any],
        sql_data_holder_with_otel_jobs: SQLDataHolder,
        mock_yaml_config_string: str,
        mock_temp_dir_with_json_files: Path,
    ) -> None:
        """Tests for the function otel_to_pv."""

        # Test 1: Default parameters
        def mock_fetch_data_holder(config: IngestDataConfig) -> SQLDataHolder:
            return sql_data_holder_with_otel_jobs

        ingest_data_config = IngestDataConfig(
            data_sources=mock_yaml_config_dict["data_sources"],
            data_holders=mock_yaml_config_dict["data_holders"],
            ingest_data=IngestTypes(**mock_yaml_config_dict["ingest_data"]),
        )
        monkeypatch.setattr(
            "tel2puml.otel_to_pv.sequence_otel_v2.fetch_data_holder",
            mock_fetch_data_holder,
        )

        result = otel_to_pv(ingest_data_config)

        events = []
        valid_job_names = {"test_name"}
        valid_event_ids = [f"{i}_{j}" for i in range(5) for j in range(2)]
        valid_job_ids = {f"test_id_{i}" for i in range(5)}
        job_id_count: dict[str, int] = {}
        for job_name, pv_event_streams in result:
            assert job_name in valid_job_names
            for pv_event_gen in pv_event_streams:
                for pv_event in pv_event_gen:
                    job_id_count.setdefault(pv_event["jobId"], 0)
                    job_id_count[pv_event["jobId"]] += 1
                    events.append(pv_event)
                    assert pv_event["eventId"] in valid_event_ids
                    assert pv_event["jobId"] in valid_job_ids
                    valid_event_ids.remove(pv_event["eventId"])

        assert len(events) == 10
        assert all(count == 2 for count in job_id_count.values())
        assert len(valid_event_ids) == 0

        # Test 2: ingest_data = True
        config = self.get_ingest_config(
            mock_yaml_config_string, mock_temp_dir_with_json_files
        )
        result = otel_to_pv(config, ingest_data=True)

        events = []
        valid_job_names = {"Backend TestJob", "Frontend TestJob"}
        valid_job_ids = {
            "0_trace_id_1 4.8",
            "1_trace_id_1 4.8",
            "0_trace_id_0 4.8",
            "1_trace_id_0 4.8",
        }
        valid_event_ids = [
            f"{i}_span_{j}_{k}"
            for i in range(2)
            for j in range(2)
            for k in range(2)
        ]
        job_id_count = {}
        for job_name, pv_event_streams in result:
            assert job_name in valid_job_names
            for pv_event_gen in pv_event_streams:
                for pv_event in pv_event_gen:
                    job_id_count.setdefault(pv_event["jobId"], 0)
                    job_id_count[pv_event["jobId"]] += 1
                    events.append(pv_event)
                    assert pv_event["eventId"] in valid_event_ids
                    assert pv_event["jobId"] in valid_job_ids
                    valid_event_ids.remove(pv_event["eventId"])

        assert len(events) == 8
        assert all(count == 2 for count in job_id_count.values())
        assert len(valid_event_ids) == 0

        # Test 3: find_unique_graphs = True
        result = otel_to_pv(ingest_data_config, find_unique_graphs=True)

        events = []
        valid_job_names = {"test_name"}
        # job id test_id_0 is outside the config time buffer window, therefore
        # it is not included, reducing total events streamed to 8
        valid_event_ids = [f"{i}_{j}" for i in range(1, 5) for j in range(2)]
        valid_job_ids = {f"test_id_{i}" for i in range(1, 5)}
        job_id_count = {}
        for job_name, pv_event_streams in result:
            assert job_name in valid_job_names
            for pv_event_gen in pv_event_streams:
                for pv_event in pv_event_gen:
                    job_id_count.setdefault(pv_event["jobId"], 0)
                    job_id_count[pv_event["jobId"]] += 1
                    events.append(pv_event)
                    assert pv_event["eventId"] in valid_event_ids
                    assert pv_event["jobId"] in valid_job_ids
                    valid_event_ids.remove(pv_event["eventId"])

        assert len(events) == 8
        assert all(count == 2 for count in job_id_count.values())
        assert len(valid_event_ids) == 0
