"""
This module contains functions for formatting and retrieving event lists from a
    PlantUML file.

Functions:
- format_events_list_as_nested_json(
        audit_event_lists: list,
        debug: bool
    ) -> dict:
    Formats a list of audit event lists as nested JSON.

- recursive_get_type(
    event_tree: dict,
    output_wip: str,
    max_depth: int = 10,
    depth: int = 0
) -> str:
    Recursively traverses an event tree and returns a string representation of
        the event types.

- get_event_list_from_puml(puml_file:str,
    puml_key:str,
    output_file:str=""
) -> str:
    Retrieves event lists from a PlantUML file based on the specified key.
"""

import re
from test_event_generator.solutions.graph_solution import (
    get_audit_event_jsons_and_templates_all_topological_permutations,
    GraphSolution,
)
from test_event_generator.io.run import puml_file_to_test_events


def format_events_list_as_nested_json(
    audit_event_lists: list, debug: bool
) -> dict:
    """
    Formats a list of audit event lists as nested JSON.

    Args:
        audit_event_lists (list): A list of audit event lists.
        debug (bool): A flag indicating whether to enable debugging.

    Returns:
        dict: A dictionary representing the formatted nested JSON.
    """

    # Initialize a counter to keep track of the event lists
    counter = 0
    event_lists = []
    events = {}

    # Iterate over each event list in audit_event_lists
    for event_list in audit_event_lists:
        counter += 1

        # Break the loop if the counter exceeds 100 and debug is enabled
        if counter > 100 and debug:
            break

        # Iterate over each event in the event list
        for event in event_list[0]:
            # Append the event to the event_lists with the resource key as the
            #   counter
            event_lists.append({**event, "resource": f"{counter}"})

            # Create a dictionary entry for the event in the events dictionary
            events[event["eventId"]] = {"eventType": event["eventType"]}

            # Check if the event contains previousEventIds
            if "previousEventIds" in event:
                events[event["eventId"]]["previousEventIds"] = {}

                # Check if previousEventIds is a list
                if isinstance(event["previousEventIds"], list):
                    # Iterate over each previous event id and add it to the
                    #   previousEventIds dictionary
                    for prev in event["previousEventIds"]:
                        events[event["eventId"]]["previousEventIds"][prev] = (
                            event["previousEventIds"]
                        )
                else:
                    # Add the single previous event id to the previousEventIds
                    #   dictionary
                    events[event["eventId"]]["previousEventIds"][
                        event["previousEventIds"]
                    ] = {}

    # Iterate over each event in the events dictionary
    for event in events:
        # Check if the event has previousEventIds
        if "previousEventIds" in events[event]:
            # Check if previousEventIds is a dictionary
            if isinstance(events[event]["previousEventIds"], dict):
                # Iterate over each previous event id and replace it with the
                #   corresponding event dictionary
                for prev in events[event]["previousEventIds"]:
                    events[event]["previousEventIds"][prev] = events[prev]
            else:
                # Replace the previous event id with the corresponding event
                #   dictionary
                events[event]["previousEventIds"] = events[
                    events[event]["previousEventIds"]
                ]

    # Return the events dictionary representing the formatted nested JSON
    return events


def recursive_get_type(
    event_tree: dict, output_wip: str, max_depth: int = 10, depth: int = 0
) -> str:
    """
    Recursively traverses an event tree and returns a string representation of
        the event types.

    Args:
        event_tree (dict): The event tree to traverse.
        output_wip (str): The intermediate output string.
        max_depth (int, optional): The maximum depth to traverse.
            Defaults to 10.
        depth (int, optional): The current depth of traversal.
            Defaults to 0.

    Returns:
        str: The string representation of event types.
    """
    if depth > max_depth:
        print("max depth exceeded when running recursive_get_type")
        return output_wip
    if output_wip != "":
        output = ",".join([output_wip, event_tree["eventType"]])
    else:
        output = event_tree["eventType"]

    if "previousEventIds" in event_tree:

        outputs_list = []
        for prev in event_tree["previousEventIds"]:
            outputs_list.append(
                recursive_get_type(
                    event_tree["previousEventIds"][prev],
                    output,
                    max_depth,
                    depth + 1,
                )
            )

        output = ",,".join(outputs_list)

    return output


def stringify_events(events):
    """
    Converts a dictionary of events into a string representation.

    Args:
        events (dict): A dictionary containing events.

    Returns:
        str: A string representation of the events.
    """

    event_keys = list(events.keys())
    output = ""

    for loop in range(0, len(event_keys)):
        if loop < len(event_keys):
            if loop < len(event_keys) - 1:
                next_event = events[event_keys[loop + 1]]
            if (loop == len(event_keys) - 1) | (
                "previousEventIds" not in next_event
            ):
                output = (
                    output
                    + "\n"
                    + re.sub(
                        ",,",
                        "\n",
                        ",".join(
                            reversed(
                                recursive_get_type(
                                    events[event_keys[loop]], "", 100
                                ).split(",")
                            )
                        ),
                    )
                )

    output = output[1:]

    return output


def get_puml_data(puml_file, puml_key):
    """
    Retrieves audit event lists from a PlantUML file based on the specified
        key.

    Args:
        puml_file (str): The path to the PlantUML file.
        puml_key (str): The key to identify the desired audit event lists.

    Returns:
        list: A list of audit event lists.
    """
    test_events_templates = puml_file_to_test_events(puml_file)
    test_events = test_events_templates[list(test_events_templates.keys())[0]][
        puml_key
    ][0]
    graph_solutions = [
        GraphSolution.from_event_list(event_list[0])
        for event_list in test_events
    ]

    audit_event_lists = (
        get_audit_event_jsons_and_templates_all_topological_permutations(
            graph_solutions
        )
    )

    return audit_event_lists


def get_event_list_from_puml(
    puml_file: str, puml_key: str, output_file: str = "", debug=False
):
    """
    Retrieves event lists from a PlantUML file based on the specified key.

    Args:
        puml_file (str): The path to the PlantUML file.
        puml_key (str): The key used to identify the event list in the
            PlantUML file.
        output_file (str, optional): The path to the output file where the
            event list will be saved. Defaults to "".

    Returns:
        str: The event list as a string.

    """
    events = {}
    audit_event_lists = []
    output = ""

    audit_event_lists = get_puml_data(puml_file, puml_key)

    events = format_events_list_as_nested_json(audit_event_lists, debug)

    output = stringify_events(events)

    if output_file != "":
        with open(output_file, "w") as f:
            f.write(str(output))

    return output


if __name__ == "__main__":

    get_event_list_from_puml(
        puml_file="puml_files/sequence_branch_counts.puml",
        puml_key="ValidSols",
        output_file="events_list.txt",
    )
