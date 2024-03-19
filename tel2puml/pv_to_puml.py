"""Module to convert a stream of PV event sequences to a PlantUML sequence
diagram, inferring the logic from the PV event sequences.
"""
from typing import Iterable
from itertools import tee

from tel2puml.utils import convert_nested_generator_to_generator_of_list
from tel2puml.tel2puml_types import PVEvent
from tel2puml.pipelines.logic_detection_pipeline import (
    update_all_connections_from_clustered_events,
)
from tel2puml.jAlergiaPipeline import audit_event_sequences_to_network_x
from tel2puml.node_map_to_puml.node_population_functions import (
    convert_to_nodes,
    create_event_node_ref
)
from tel2puml.node_map_to_puml.node import load_all_logic_trees_into_nodes
from tel2puml.node_map_to_puml.node_map_to_puml import convert_nodes_to_puml


def pv_to_puml_string(
    pv_stream: Iterable[Iterable[PVEvent]],
    puml_name: str = "default_name",
) -> str:
    """Converts a stream of PV event sequences to a PlantUML sequence diagram,
    inferring the logic from the PV event sequences and the structure from the
    Markov chain analysis.

    :param pv_stream: A Iterable of PV event sequences
    :type pv_stream: `Iterable`[`Iterable`[:class:`PVEvent`]]
    :param puml_name: The name of the PlantUML group to create
    :type puml_name: `str`
    """
    pv_stream_logic, pv_stream_markov = tee(
        convert_nested_generator_to_generator_of_list(
            pv_stream
        ),
        2
    )
    # run the logic detection pipeline
    forward_logic, backward_logic = (
        update_all_connections_from_clustered_events(pv_stream_logic)
    )
    # run the markov chain analysis
    markov_graph, event_node_references = audit_event_sequences_to_network_x(
        pv_stream_markov
    )
    # run the node population pipeline
    lookup_tables, node_trees, _ = convert_to_nodes(
        [markov_graph], [event_node_references["event_reference"]]
    )
    lookup_table, node_tree, event_reference = (
        lookup_tables[0], node_trees[0],
        event_node_references["event_reference"]
    )
    event_node_ref = create_event_node_ref(
        lookup_table,
        event_node_references["node_reference"]
    )
    # load incoming and outgoing connections
    load_all_logic_trees_into_nodes(
        forward_logic, event_node_ref, direction="outgoing"
    )
    # TODO: Need to use backward logic correctly in the entire process
    # load_all_logic_trees_into_nodes(
    #     backward_logic, event_node_ref, direction="incoming"
    # )
    return "\n".join(
        convert_nodes_to_puml(
            lookup_table=lookup_table,
            head_node=node_tree,
            event_reference=event_reference,
            puml_name=puml_name,
        )
    )
