"""Module to generate JSON data representing OTel data
"""

import json
import random
import string


def generate_id() -> str:
    """Function to generate a random unique id"""
    return "".join(
        random.choices(string.ascii_lowercase + string.digits, k=16)
    )


def generate_dummy_data(
    num_traces: int = 1, max_depth: int = 2
) -> list[dict[str, str | None]]:
    """Function to generate dummy OTel data.

    :param num_traces: Number of traces to generate
    :type num_traces: `int`
    :param max_depth: The max depth of the tree to be generated
    :type max_depth: `int`
    :return: List of dictionaries representing an OTel event
    :rtype: `list`[`dict`[`str`,`str`]]
    """
    data = []
    event_types = ["A", "B", "C", "D"]
    job_names = ["job_1", "job_2", "job_3"]

    def generate_spans(
        job_name: str,
        trace_id: str,
        prev_span_id: str | None,
        current_depth: int,
    ) -> None:
        """Recursive function to generate OTel Spans.

        :param job_name: The job name
        :type job_name: `str`
        :param trace_id: The trace ID of the Span
        :type trace_id: `str`
        :param prev_span_id: The span ID of the parent Span
        :type prev_span_id: `str` | `None`
        :param current_depth: The current depth of the tree generated
        :type current_depth: `int`
        """

        if current_depth > max_depth:
            return

        num_branches = random.randint(1, 3)
        for _ in range(num_branches):
            span_id = generate_id()
            event_type = random.choice(event_types)

            span = {
                "span_id": span_id,
                "trace_id": trace_id,
                "event_type": event_type,
                "prev_span_id": prev_span_id,
                "job_name": job_name,
            }

            data.append(span)

            # Recursively generate child spans
            generate_spans(job_name, trace_id, span_id, current_depth + 1)

    for _ in range(num_traces):
        trace_id = generate_id()
        root_span_id = generate_id()
        job_name = random.choice(job_names)

        # Create root span
        root_span = {
            "span_id": root_span_id,
            "trace_id": trace_id,
            "event_type": "start",
            "prev_span_id": None,
            "job_name": job_name,
        }
        data.append(root_span)

        # Generate the rest of the trace
        generate_spans(job_name, trace_id, root_span_id, 1)

    return data


if __name__ == "__main__":
    # Generate dummy data
    dummy_data = generate_dummy_data()

    # Save to a file
    with open("./graph_solution_poc/data/dummy_trace_data.json", "w") as f:
        json.dump(dummy_data, f, indent=2)
