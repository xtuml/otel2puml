# Design Note 4: Sequencing pv events from otel unique graphs
## Problem
Once we have the unique graphs from the otel data, we need to sequence the pv events from these graphs. There are two ways to sequence the pv events:
1. Synchronous sequencing: events are in order of their start time
2. Asynchronous sequencing: some sequences of events occur in parallel

## Solution
### Overview
We will combine the following two approaches to sequence the pv events from the otel unique graphs:

#### Synchronous Sequencing
1. We will start by sequencing the root node of the graph.
2. We will then recursively sequence the descendant nodes of the root node in order of their start time so that child nodes are sequenced before their parent nodes.
3. We will continue this process until all the nodes in the graph have been sequenced with the root node being the last node to be sequenced.

#### Asynchronous Sequencing
1. We will start by sequencing the root node of the graph.
2. We will then recursively sequence the descendant nodes of the root node in parallel if they either overlap in time or the user has input extra information to indicate that they should be sequenced in parallel (as well as the resulting sequence of their ancestors), otherwise, we will sequence them synchronously.
3. We will continue this process until all the nodes in the graph have been sequenced with the root node being the last node to be sequenced.

### Algorithm
The basic algorithms for sequencing the pv events from the otel unique graphs are presented below as activity diagram

![](/docs/development/design/4-DN-Sequencing_pv_events_from_otel_unique_graphs/Algorithm_Overview.svg)

### Functions

The following functions required using the activity diagram are

```python

def order_groups_by_start_timestamp(
    groups: list[list[OTelEvent]],
) -> list[list[OTelEvent]]:
    """Order the groups of otel events by their start time

    :param groups: the groups of otel events to order
    :return: the groups of otel events ordered by their start time
    """

def sequence_events_by_async_event_types(
    events: list[OTelEvent],
    async_event_types: dict[str, str],
) -> list[list[OTelEvent]]:
    """Sequence the pv events from the otel unique graph asynchronously given the event types that should be sequenced in parallel
    
    :param events: the list of otel events to sequence in order of their start time
    :param async_event_types: a dict mapping event type to a group id
    :return: a list of lists of otel events with those in the same list parallel
    """

def sequence_groups_of_otel_events_asynchronously(
    events: list[OTelEvent],
) -> list[list[OTelEvent]]:
    """Sequence the pv events from the otel unique graph asynchronously

    :param events: the list of otel events to sequence in order of their start time
    :return: a list of lists of otel events with those in the same list parallel
    """

def sequence_otel_event_and_ancestors(
    event: OTelEvent,
    event_id_to_event_map: dict[str, OTelEvent],
    previous_event_ids: list[str] | None = None,
    async_flag: bool = False,
    event_type_to_async_events_map: dict[str, dict[str, str]] | None = None,
) -> Iterable[PVEvent]:
    """Sequence the pv events from the otel unique graph

    :param event: the otel event to sequence and its ancestors
    :param event_id_to_event_map: a map of event ids to otel events
    :param previous_event_ids: a list of previous event ids to sequence before the event
    :param async_flag: a flag to indicate if the sequencing should be done asynchronously
    :param event_type_to_async_events_map: a map of event types to a dict mapping event type to a group id
    """

def sequence_otel_event_job(
    job: dict[str, OTelEvent],
    async_flag: bool = False,
    event_type_to_async_events_map: dict[str, dict[str, str]] | None = None,
) -> Iterable[PVEvent]:
    """Sequence the pv events from the otel unique graph

    :param job: the otel unique graph as a dictionary of event ids to otel events
    :param async_flag: a flag to indicate if the sequencing should be done asynchronously
    :param event_type_to_async_events_map: a map of event types to a dict mapping event type to a group id
    :return: an Iterable of pv events sequenced from the otel unique graph
    """


def sequence_otel_jobs(
    jobs: Iterable[dict[str, OTelEvent]],
    async_flag: bool = False,
    event_type_to_async_events_map: dict[str, dict[str, str]] | None = None,
) -> Iterable[Iterable[PVEvent]]:
    """Sequences the pv events from the otel unique graphs

    :param jobs: the otel unique graphs as an iterable of dictionaries
    of event ids to otel events
    :param async_flag: a flag to indicate if the sequencing should be done asynchronously
    :param event_type_to_async_events_map: a map of event types to a dict mapping event type to a group id
    :return: an iterable of iterables of pv events for each of the jobs
    """
    pass
```

#### Call Graph
The call graphs for the functions are presented below:

![](/docs/development/design/4-DN-Sequencing_pv_events_from_otel_unique_graphs/call_graph.svg)