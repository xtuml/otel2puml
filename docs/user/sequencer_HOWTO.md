# Sequencer HOW TO

## Overview


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
This field is a boolean field that specifies whether the sequencer should run asynchronously. If set to `true`, the sequencer will run asynchronously. If set to `false`, the sequencer will run synchronously. The default value is `false`.

If this field is set to `true`, the sequencer will use a procession method using start and end timestamps taken from the data to determine if events are occurring asynchronously. An example of this is shown below whereby the three events in Async Group 1 are occurring asynchronously and there is overlap in time windows that creates a chain - it is not required that all events in a group time windows overlap, only that there is at a minimum a chain of overlapping time windows:

![](/docs/user/otel_sequence_async.svg)

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
So if there was an event with a `job_name` of `job_name_1` and an `event_type` of `D` with child event types `A`, `B`, `C` then the sequencer would group any occurences of `A`, `B` and `C` and these would sequence into `D` if there were no other children od `D` as below:

![](/docs/user/otel_sequence_async_prior.svg)

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
    "job_name": "job_name_1"
    "job_id": "job_id_1"
    "event_type": "event_type_1"
    "event_id": "event_id_1"
    "start_timestamp": 1
    "end_timestamp": 2
    "application_name": "app_name"
    "parent_event_id": "parent_event_id_1"
    "child_event_ids": ["child_event_id_1", "child_event_id_2"]
}
```
this will become

```python
{
    "job_name": "job_name_1"
    "job_id": "job_id_1"
    "event_type": "mapped_event_type_1"
    "event_id": "event_id_1"
    "start_timestamp": 1
    "end_timestamp": 2
    "application_name": "app_name"
    "parent_event_id": "parent_event_id_1"
    "child_event_ids": ["child_event_id_1", "child_event_id_2"]
}
```



