# PUML Models
## Introdcution
Internally `tel2puml` uses a model that it builds from event sequences that are passed into it. This model is built with the following components:


- **EventSet** - This is a unique "set" of `eventTypes` and their counts e.g., `A: 3, B: 2, C: 1`. This is used to represent a single possibility specific events and their occurence 
- **Event**: Represents a single event with:
    - `eventType` - e.g., `A`, `B`, `C`, etc.
    - `outgoingEventSets` - This is a list of `EventSet` objects that represent the possible next events that can occur after this event with a forward connection.
    - `incomingEventSets` - This is a list of `EventSet` objects that represent the possible previous events that can occur before this event with a backwards connection.
- **EventModel**: This is the main model that is built from the event sequences. It contains a list of `Event` objects that represent the events in the sequence. It also contains a list of `EventSet` objects that represent the possible event sets that can occur in the sequence.

Functionality is present in tel2puml to input and save these "models" as JSON files. Saved models can be loaded back into the tool to be updated with new event sequences. This can provide a way to build up a model over time as more event sequences are collected or in the circumstances that there are large volumes of data that need to be processed.

## Model JSON file format
The model file is provided as a specific JSON file format. This file format is used to save the model that is built from the event sequences. It should be noted that there will always be a "Dummy" starting event added with `eventType` of `|||START|||` to represent the start of the sequence. This is added to ensure that all events have a starting point so that logic can be derived even for multiple starting points in the actual data.

The JSON file format has the following JSON schema

```json
{
    "$schema": "http://json-schema.org/schema#",
    "type": "object",
    "properties": {
        "job_name": {
            "type": "string"
        },
        "events": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "eventType": {
                        "type": "string"
                    },
                    "outgoingEventSets": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "eventType": {
                                        "type": "string"
                                    },
                                    "count": {
                                        "type": "integer"
                                    }
                                },
                                "required": [
                                    "count",
                                    "eventType"
                                ]
                            }
                        }
                    },
                    "incomingEventSets": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "eventType": {
                                        "type": "string"
                                    },
                                    "count": {
                                        "type": "integer"
                                    }
                                },
                                "required": [
                                    "count",
                                    "eventType"
                                ]
                            }
                        }
                    }
                },
                "required": [
                    "eventType",
                    "incomingEventSets",
                    "outgoingEventSets"
                ]
            }
        }
    },
    "required": [
        "events",
        "job_name"
    ]
}
```

An example derived using the data in the [end-to-end walkthrough](/docs/e2e_walkthrough/example_pv_event_sequence_files) is shown below

```json 
{
    "job_name": "Users_Service",
    "events": [
        {
            "eventType": "return_response_200",
            "outgoingEventSets": [],
            "incomingEventSets": [
                [{"eventType": "fetch_user_data_200", "count": 1}],
                [{"eventType": "request_data_200", "count": 1}]
            ]
        },
        {
            "eventType": "fetch_user_data_200",
            "outgoingEventSets": [
                [{"eventType": "return_response_200", "count": 1}]
            ],
            "incomingEventSets": [
                [{"eventType": "authorization_check_200", "count": 1}]
            ]
        },
        {
            "eventType": "authorization_check_200",
            "outgoingEventSets": [
                [{"eventType": "fetch_user_data_200", "count": 1}],
                [{"eventType": "authorization_check_200", "count": 1}]
            ],
            "incomingEventSets": [
                [{"eventType": "user_login_200", "count": 1}],
                [{"eventType": "authorization_check_200", "count": 1}]
            ]
        },
        {
            "eventType": "user_login_200",
            "outgoingEventSets": [
                [{"eventType": "authenticate_credentials_200", "count": 1}],
                [{"eventType": "authorization_check_200", "count": 1}]
            ],
            "incomingEventSets": [
                [{"eventType": "|||START|||", "count": 1}]
            ]
        },
        {
            "eventType": "|||START|||",
            "outgoingEventSets": [
                [{"eventType": "user_login_200", "count": 1}]
            ],
            "incomingEventSets": []
        },
        {
            "eventType": "request_data_200",
            "outgoingEventSets": [
                [{"eventType": "return_response_200", "count": 1}]
            ],
            "incomingEventSets": [
                [{"eventType": "session_expired_200", "count": 1}],
                [{"eventType": "validate_session_200", "count": 1}]
            ]
        },
        {
            "eventType": "validate_session_200",
            "outgoingEventSets": [
                [{"eventType": "authenticate_credentials_200","count": 1}],
                [{"eventType": "request_data_200", "count": 1}]
            ],
            "incomingEventSets": [
                [{"eventType": "authenticate_credentials_200", "count": 1}]
            ]
        },
        {
            "eventType": "authenticate_credentials_200",
            "outgoingEventSets": [
                [{"eventType": "session_expired_200", "count": 1}],
                [{"eventType": "validate_session_200", "count": 1}]
            ],
            "incomingEventSets": [
                [{"eventType": "user_login_200", "count": 1}],
                [{"eventType": "session_expired_200", "count": 1}],
                [{"eventType": "validate_session_200", "count": 1}]
            ]
        },
        {
            "eventType": "session_expired_200",
            "outgoingEventSets": [
                [{"eventType": "authenticate_credentials_200", "count": 1}],
                [{"eventType": "request_data_200", "count": 1}]
            ],
            "incomingEventSets": [
                [{"eventType": "authenticate_credentials_200", "count": 1}]
            ]
        }
    ]
}
```