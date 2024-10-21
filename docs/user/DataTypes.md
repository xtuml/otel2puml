# OTel to PUML data types

OTel2PUML has two data types that are used internally to represent the data that is being processed/output. These are:

- `OTelEvent`: This datatype holds information on relationships between nodes in a call graph or, as applied to OpenTelemetry, the relationship between the spans within a trace. It is used to represent the relationship between a parent and children spans and the tree structure that this forms. This can also be applied to a call graph where the parent is the caller and the children are the callees.

- `PVEvent`: This datatype holds information on relationships between nodes in a causal sequence of "events". This datatype is an exact copy (for the most part) of "audit events" datatype used as input to the [Protocol Verifier software](https://github.com/xtuml/munin) , to which OTel2PUML is applied to. This is used to represent the relationship between a parent and children events and the sequence that this forms. 

## OTelEvent

The `OTelEvent` datatype is defined as follows:

```python
class OTelEvent(NamedTuple):
    job_name: str
    job_id: str
    event_type: str
    event_id: str
    start_timestamp: int
    end_timestamp: int
    application_name: str
    parent_event_id: Optional[str] = None
    child_event_ids: Optional[list[str]] = None
```

The fields of the `OTelEvent` datatype are as follows:

- `job_name`: The name of the workflow that the span/event is associated with. This is used to group traces/instances that are part of the same workflow together.

- `job_id`: The unique identifier of the trace/instance that the span/event is associated with. This is used to group together spans/events that are part of the same trace/instance.

- `event_type`: The type of the span/event. This is used to differentiate between different types of spans/events, such as `start`, `end`, `log`, etc.

- `event_id`: The unique identifier of the span/event. This is used to uniquely identify the span/event within the trace/instance.

- `start_timestamp`: The timestamp at which the span/event started. Along with the `end_timestamp`, this is used to calculate the time window of the span/event. Currently, this is represented as a unix timestmap in nanoseconds.

- `end_timestamp`: The timestamp at which the span/event ended. Along with the `start_timestamp`, this is used to calculate the time window of the span/event. Currently, this is represented as a unix timestmap in nanoseconds.

- `application_name`: The name of the application that generated the span/event. This has no relevance to any computation but is required by the Protocol Verifier software so has been included in the datatype.

- `parent_event_id`: The unique identifier of the parent span/event. This is used to represent the relationship between the parent and child spans/events. If this is `None`, then the span/event is considered to be the root of the trace/instance.

- `child_event_ids`: A list of unique identifiers of the child spans/events. This can be used to represent the relationship between the parent and child spans/events. This information is not currently used as it can be found from the `parent_event_id` information.

The grouped data heirarchy is given by `job_name -> job_id -> event_id`. For example the groups from some data may look something like:
```
data
|
|-job_name: "workflow1"
|   |-job_id: "instance1"
|   |   |-event_id: "span1"
|   |   |-event_id: "span2"
|   |   |-event_id: "span4"
|   |-job_id: "instance2"
|       |-event_id: "span3"
|       |-event_id: "span5"
|-job_name: "workflow2"
    |-job_id: "instance3"
    |   |-event_id: "span6"
    |   |-event_id: "span7"
    |-job_id: "instance4"
        |-event_id: "span8"
        |-event_id: "span9"
```

When calculating PVEvents from data in the above format data will be grouped by `job_name -> job_id` and the `event_id` will be used to provide links between the events.

when caluclating PUML's from the data PUML's will be grouped by `job_name` showing the workflow that the data is associated with.

An example of a simple trace using the pertinent fields of the `OTelEvent` datatype is given below:

![Caption](/docs/images/user/otel_tree.svg)



## PVEvent

The `PVEvent` datatype is defined as follows:

```python
class PVEvent(NamedTuple):
    job_name: str
    job_id: str
    event_type: str
    event_id: str
    timestamp: int
    application_name: str
    previous_event_ids: Optional[list[str]] = None
```

The fields of the `PVEvent` datatype are as follows:

- `job_name`: The name of the workflow that the event is associated with. This is used to group events that are part of the same workflow together.

- `job_id`: The unique identifier of the instance that the event is associated with. This is used to group together events that are part of the same instance.

- `event_type`: The type of the event. This is used to differentiate between different types of events, such as `start`, `end`, `log`, etc.

- `event_id`: The unique identifier of the event. This is used to uniquely identify the event within the instance.

- `timestamp`: The timestamp at which the event occurred. This is used to order the events in a causal sequence.

- `application_name`: The name of the application that generated the event. This has no relevance to any computation but is required by the Protocol Verifier software so is included in the datatype.

- `previous_event_ids`: A list of unique identifiers of the previous events. This is used to represent the causal relationship between the events. If this is `None`, then the event is considered to be a start event in the causal sequence.

An example of a simple causal sequence using the pertinent fields of the `PVEvent` datatype is given below:

![](/docs/images/user/pv_sequence_from_otel_procession.svg)



