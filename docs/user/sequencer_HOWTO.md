# Sequencer HOW TO

## Table of Contents
1. [Overview](#overview)
    1. [Synchronous Sequencing](#synchronous-sequencing)
    2. [Asynchronous Sequencing](#asynchronous-sequencing)
        1. [Procession Method](#procession-method)
        2. [Prior Information](#prior-information)
2. [Configuration Options](#configuration-options)
    1. [`async`](#async)
    2. [`async_event_groups`](#async_event_groups)
    3. [`event_name_map_information`](#event_name_map_information)

## Overview
The purpose of the sequencer is to take a call tree of events - that could be an OpenTelemetry [trace](https://opentelemetry.io/docs/concepts/signals/traces/) of [spans](https://opentelemetry.io/docs/concepts/signals/traces/#spans) - and sequence them into a causal order.

The data that is ingested into the sequencer has the form

```json
{
    "job_name": <identifier for what the trace does>,
    "job_id": <unique id for tree instance>,
    "event_type": <identifier for type of call event>,
    "event_id": <unique id for call event instance>,
    "start_timestamp": <integer timestamp when call event starts>,
    "end_timestamp": <integer timestampt when call event ends>,
    "application_name": <name of application used>,
    "parent_event_id": <unique identifier for call event that called this instance>,
    "child_event_ids": <array of all child call events called | not required>
}
```

There are two ways that are used to sequence the tree of events:
1. Synchronous sequencing: events are sequenced in a recursive manner in which parents occur after their children and children occur in order of their start time
2. Asynchronous sequencing: events are sequenced in a recursive manner in which parents occur after their children and children occur in order of their start time but can occur in parallel
    * if they overlap in time
    * or if the user has provided extra information to indicate that they should be sequenced in parallel

In following for full examples we use the otel tree below as an example of a call tree to be sequenced:

###### Figure 1 OTelTree
![Caption](/docs/images/user/otel_tree.svg)


### Synchronous Sequencing
The synchronous sequencing algorithm is as follows:
1. Find the root event
2. Find all the children of the root event
3. Sort the children by their start time
4. For each child, sequence the child and its children
5. Return the sequence of the root event and its children

An example of synchronous sequencing is shown below using the tree of events shown in [OTel Tree](#figure-1-oteltree) that are then sequenced into a causal order (see [DataTypes](/docs/user/DataTypes.md) for info on the PVEvent datatype used):

![](/docs/images/user/pv_sequence_from_otel.svg)

Note how `child1` becomes the previous event to `grandchild3` as `child1` occurs before `child2` starts but `grandchild3` must occur before `child2` as its parent is `child2`. Also note how `grandchild1` becomes the first event as it is the first child of `child1` which itself is the first child of `root`.

### Asynchronous Sequencing

The code has two forms of asynchronous sequencing:

1. If the `async` (see [async](#async)) field is set to `true` in the configuration file, the sequencer will use a procession method (see [Procession Method](#procession-method) below) using start and end timestamps taken from the data to determine if events are occurring asynchronously.
2. If the user provides extra information (see [async_event_group](#async_event_groups)) in the configuration file, the sequencer will use this information to determine if events are occurring asynchronously (see [Extra Information](#prior-information)).

#### Procession Method
The procession method is as follows:
1. Find the root event
2. Find all the children of the root event
3. Sort the children by their start time
4. Group the children in chains of overlapping time windows of start and end times and sequence the children in each chain, then sequence the chains as in synchronous sequencing
5. Return the sequence of the root event and its children

An example of this for one event is shown below whereby the three events in Async Group 1 are occurring asynchronously and there is overlap in time windows that creates a chain - it is not required that all events in a group time windows overlap, only that there is at a minimum a chain of overlapping time windows:

###### Figure 2 OTel Sequence Async
![](/docs/images/user/otel_sequence_async.svg)

The full example as in figure [OTel Tree](#oteltree) would be sequenced the following way using the procession method:

![](/docs/images/user/pv_sequence_from_otel_procession.svg)

Notice that `child1` has previous events `grandchild1` and `grandchild2` as they form a chain of overlapping time windows which are, [11,15] and [14,19], respectively.

#### Prior Information
The user can provide prior information in the configuration file to indicate that certain events should be sequenced asynchronously. This is done by providing a dictionary of event types that should be sequenced asynchronously and the child event types that should be grouped together. The sequencer will then group the child event types together and sequence them asynchronously. An example of this is shown below:

###### Figure 3 OTel Sequence Async Prior
![](/docs/images/user/otel_sequence_async_prior.svg)

In this example, the user has provided prior information that the events `A`, `B` and `C` should be grouped together and sequenced asynchronously. The sequencer will then group these events together and sequence them asynchronously. The sequencer will then sequence the events into `D`.

Using the full example in figure [OTel Tree](#oteltree) and setting the extra information that `child1` and `child2` should be sequenced asynchronously if they are called by `root` - but no other asynchronous sequencing other than this - the following sequence is produced:

![](/docs/images/user/pv_sequence_from_otel_extra_info.svg)

Notice that `child1` and `child2` are sequenced asynchronously as they are called by `root` and are identified in the "prior information" and that `grandchild1` and `grandchild2` are sequenced synchronously as is `grandchild3` as there is no prior information about them.

## Configuration Options
The sequencer configuration is provided as a field in the configuration file (see [Config](/docs/user/Config.md)) and is provided in the `sequencer` field. The sequencer configuration has the following fields:
* `async`
* `async_event_groups`
* `event_name_map_information`

An example configuration file is provided below:
    
```yaml
sequencer:
    async: false
    async_event_groups:
        job_name_1:
            event_type_1:
                A: group_1
                B: group_1
                C: group_1
                D: group_2
            event_type_4:
                event_type_5: group_3
        job_name_2:
            event_type_6:
                event_type_7: group_4
                event_type_8: group_4
    event_name_map_information:
        job_name_1:
            event_type_1:
                mapped_event_type: mapped_event_type_1
                child_event_types:
                    - child_event_type_1
                    - child_event_type_2
            event_type_2:
                mapped_event_type: mapped_event_type_2
                child_event_types:
                    - child_event_type_3
                    - child_event_type_4
        job_name_2:
            event_type_3:
                mapped_event_type: mapped_event_type_3
                child_event_types:
                    - child_event_type_5
                    - child_event_type_6
```

### `async`
This field is a boolean field that specifies whether the sequencer should run asynchronously. If set to `true`, the sequencer will run asynchronously. If set to `false`, the sequencer will run synchronously. The default value is `false`. An example of when this is set to true is shown for the yaml above is shown in figure [OTel sequence async](#figure-2-otel-sequence-async) above.

### `async_event_groups`
This field is a dictionary that specifies the event groups that should be run asynchronously. The dictionary is structured as follows:
* The keys are the names of the jobs that should use the value dictionary provided.
* The values are dictionaries that specify the event groups that should be run asynchronously for the job. The keys are the names of the event types whose specified child event types should be grouped asynchrnously, and the values are a dictionary mapping child event types to the group they should be in.

In the example above the `async_event_groups` would be converted to the following python dictionary internally
```python
{
    'job_name_1': {
        'D': {
            "A": 'group_1',
            "B": 'group_1',
            "C": 'group_1',
        },
        'event_type_4': {
            'event_type_5': 'group_2'
        }
    },
    'job_name_2': {
        'event_type_6': {
            'event_type_7': 'group_3',
            'event_type_8': 'group_3'
        }
    }
}
```
So if there was an event with a `job_name` of `job_name_1` and an `event_type` of `D` with child event types `A`, `B`, `C` then the sequencer would group any occurences of `A`, `B` and `C` that were all children of an event `D` would then be sequenced into `D` if there were no other children of `D`, as in figure [OTel Sequence Async Prior](#figure-3-otel-sequence-async-prior) above.

### `event_name_map_information`
This field is a dictionary that specifies the mapping of event types to other event types. The dictionary is structured as follows:
* The keys are the names of the jobs that should use the value dictionary provided.
* The values are dictionaries that specify the mapping of event types to other event types. The keys are the names of the event types whose child event types should be mapped to other event types, and the values are dictionaries that specify the mapping of the event type to another event type and the child event types, one of which should appear for the mapping to be applied.

In the example above the `event_name_map_information` would be converted to the following python dictionary internally
```python
{
    'job_name_1': {
        'event_type_1': {
            'mapped_event_type': 'mapped_event_type_1',
            'child_event_types': [
                'child_event_type_1',
                'child_event_type_2'
            ]
        },
        'event_type_2': {
            'mapped_event_type': 'mapped_event_type_2',
            'child_event_types': [
                'child_event_type_3',
                'child_event_type_4'
            ]
        }
    },
    'job_name_2': {
        'event_type_3': {
            'mapped_event_type': 'mapped_event_type_3',
            'child_event_types': [
                'child_event_type_5',
                'child_event_type_6'
            ]
        }
    }
}
```

So if there was an event with a `job_name` of `job_name_1` and an `event_type` of `event_type_1` with at least one child event that had on the the event types `child_event_type_1`, `child_event_type_2` then the sequencer would rename that event to `mapped_event_type_1` i.e. using OTelEvent datatype:

```python
{
    "job_name": "job_name_1",
    "job_id": "job_id_1",
    "event_type": "event_type_1",
    "event_id": "event_id_1",
    "start_timestamp": 1,
    "end_timestamp": 2,
    "application_name": "app_name",
    "parent_event_id": "parent_event_id_1",
    "child_event_ids": ["child_event_id_1", "child_event_id_2"]
}
```
this will become

```python
{
    "job_name": "job_name_1",
    "job_id": "job_id_1",
    "event_type": "mapped_event_type_1",
    "event_id": "event_id_1",
    "start_timestamp": 1,
    "end_timestamp": 2,
    "application_name": "app_name",
    "parent_event_id": "parent_event_id_1",
    "child_event_ids": ["child_event_id_1", "child_event_id_2"]
}
```



