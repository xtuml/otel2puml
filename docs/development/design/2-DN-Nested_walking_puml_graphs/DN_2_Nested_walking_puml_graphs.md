# Design Note 1: Nested walking of PUML logic graphs
## Problem
The current implementation of the walking of the PUML logic graphs is not able to handle nested loops. We need to update to handle nested walking of the PUML logic graphs.
## Solution
### Overview
In the current solution there is functionality to walk a PUML logic graph without nested subgraphs. It is intended to extend the functionality by:
* Adding `SubGraphNode` class that extends the `Node` class by including a `sub_graph` attribute to that contains the subgraph of the node
* Creating a function to create a nested `Node` class graph from a graph of `Event` classes
* Creating a function to walk the nested graph reusing the existing walking function

### Algorithm
The basic algorithms for setting up the nested node class graph and walking the nested graph are presented below as activity diagram

![](/docs/development/design/2-DN-Nested_walking_puml_graphs/Algorithm_Overview.svg)

It is also required to indentify update the `Node` classes with:

* lonely merge nodes - these are "paths" out of logic nodes, within a loop, in which all other paths from the logic node must be killed as they do not reach the loops end and therefore the lonely merge node is identified so that logic blocks can do a single (or "lonely") merge with the identified node. Implementation details found in [Lonely Merges](./lonely_merge_nodes/lonely_merge_nodes.md)
* paths that must kill - these are paths from a logic block within a loop that do not reach the end of the loop and therefore are identified as paths that do not merge the logic block when walking the PUML logic graph.

### Class Diagram

The class diagram for the SCC loop detection is presented below

![](/docs/development/design/2-DN-Nested_walking_puml_graphs/class_diagrams.svg)

### Functions

The following functions required using the activity diagram and class diagram are

```python

def create_node_graph_from_event_graph(event_graph: EventGraph) -> NodeGraph:
    """Create a node graph from the event graph

    :param event_graph: The event graph to create the node graph from
    :return: The node graph created from the event graph
    """
    pass

def create_node_from_event(event: Event) -> Node:
    """Create a node from an event

    :param event: The event to create the node from
    :return: The node created from the event
    """
    pass

def update_graph_with_node_tuple(node_edge: NodeTuple, node_graph: NodeGraph) -> NodeGraph:
    """Update the graph with the node tuple

    :param node_edge: The node tuple to update the graph with
    :param node_graph: The node graph to update
    :return: The node graph updated with the node tuple
    """
    pass

def update_outgoing_logic_nodes(event: Event, node: Node) -> None:
    """Update the outgoing logic nodes

    :param event: The event to update the outgoing logic nodes
    :param node: The node to update the outgoing logic nodes
    """
    pass

def walk_nested_graph(node_graph: NodeGraph) -> PUMLGraph:
    """Walk the nested graph

    :param node_graph: The node graph to walk
    :return: The PUML graph created from the nested graph
    """
    pass

def add_sub_graph_to_puml_node(puml_parent_graph: PUMLGraph, puml_sub_graph: PUMLGraph, ref: Hashable) -> None:
    """Add the sub graph to the PUML nodes of the parent graph

    :param puml_parent_graph: The PUML parent graph that contains the nodes
    :param puml_sub_graph: The PUML sub graph to add
    :param ref: The reference used to find the PUMLNodes in the PUMLGraph
    """
    pass

```

##### Call Graph
The call graphs for the functions are presented below:

![](/docs/development/design/2-DN-Nested_walking_puml_graphs/call_graph.svg)