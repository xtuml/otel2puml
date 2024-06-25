# Design Note 1: Strongly Connected Components loop detection
## Problem
Due to loop current loop detection failing for complex cases in the current implementation, we need to implement a new loop detection algorithm that uses the concept of Strongly Connected Components (SCC) to detect loops in the graph and walk the graph.
## Solution
### Overview
It is possible to use SCC to detect loops in the graph, as SCCs are subgraphs where every node is reachable from every other node in the subgraph. This means that if a node is part of an SCC, it is part of a loop. We can therefore separate the graph into SCCs (recursively if necessary) and walk the graph from the nodes in the SCCs as loop subgraphs. Care will be needed when replacing SCCs with a single node, as the graph may have multiple SCCs that are not connected to each other.
### Algorithm
The basic algorithm for detecting SCCs is presented below as an activity diagram

![](/docs/development/design/1-DN-SCC_loop_detection/Algorithm_Overview.svg)

### Class Diagram
The class diagram for the SCC loop detection is presented below

![](/docs/development/design/1-DN-SCC_loop_detection/class_diagrams.svg)

### Functions

The following functions required using the activity diagram and class diagram are presented below

```python

def create_graph_from_events(events: Iterable[Event]) -> EventGraph:
    """Create a graph from the events using the information in the `event_sets` attribute for links

    :param events: The events to create the graph from
    :return: The graph created from the events
    """
    pass

def detect_loops(graph: EventGraph) -> EventGraph:
    """Detect the loops in the graph using SCCs and create LoopEvent nodes that contain subgraphs describing the loop

    :param graph: The graph to detect the loops in
    :return: The graph with the loops detected
    """
    pass

def calc_components_of_loop(scc_events: set[Event], graph: EventGraph) -> Loop:
    """Calculate the components of the loop that is:
    * scc events of the loop
    * the start events of the loop
    * the end events of the loop
    * the break events in the loop
    * the event edges that create the loop
    
    :param scc_events: The events in the SCC
    :param graph: The graph to calculate the loop from
    :return: The loop components
    """
    pass

def calc_loop_end_break_and_loop_edges(start_events: set[Event], scc_events: set[Events], graph: EventGraph) -> tuple[set[Event], set[Event], set[EventTuple]]:
    """Calculate the
    * end events of the loop
    * break events in the loop
    * event edges that create the loop

    :param start_events: The start events of the loop
    :param scc_events: The events in the SCC
    :param graph: The graph to calculate the loop from
    :return: The end events and the break events in the loop and the edges that create the loop
    """
    pass

def create_sub_graph_of_loop(loop: Loop, graph: EventGraph) -> EventGraph:
    """Create a subgraph of the loop from the graph and the loop components

    :param loop: The components of the loop to create the subgraph from
    :param graph: The parent graph to create the subgraph from
    :return: The subgraph of the loop
    """
    pass

def remove_loop_edges(loop: Loop, graph: EventGraph) -> None:
    """Remove the edges of the loop from the graph and return a deep copied graph with loop edges removed and the loop components

    :param loop: The components of the loop to remove the edges from
    :param graph: The graph to remove the edges from
    """
    pass

def get_disconnected_loop_sub_graph(scc_nodes: set[T], graph: DiGraph[T]) -> DiGraph[T]:
    """Get the disconnected subgraph of the loop from the graph

    :param loop: The components of the loop to get the disconnected subgraph from
    :param graph: The graph to get the disconnected subgraph from
    :return: The disconnected subgraph of the loop
    """
    pass

def add_start_and_end_events_to_sub_graph(loop: Loop, sub_graph: EventGraph) -> EventGraph:
    """Add the start and end events of the loop to the subgraph

    :param loop: The components of the loop to add the start and end events to the subgraph
    :param sub_graph: The subgraph to add the start and end events to
    :return: The subgraph with the start and end events added
    """
    pass

def remove_nodes_without_path_back_to_loop(
    nodes: set[T],
    loop_nodes: set[T],
    graph: "nx.DiGraph[T]",
) -> None:
    """Remove nodes that do not have a path back to the loop nodes.

    :param nodes: The set of nodes to remove.
    :type nodes: `set`[:class:`T`]
    :param loop_nodes: The set of loop nodes.
    :type loop_nodes: `set`[:class:`T`]
    :param graph: The graph to remove the nodes from.
    :type graph: :class:`DiGraph`[:class:`T`]
    """
    pass

def create_loop_event(loop: Loop, sub_graph: EventGraph, graph: EventGraph) -> LoopEvent:
    """Create a LoopEvent from the loop components and the subgraph

    :param loop: The components of the loop to create the LoopEvent from
    :param sub_graph: The subgraph to create the LoopEvent from
    :param graph: The parent graph to create the LoopEvent from
    :return: The LoopEvent created from the loop components and the subgraph
    """
    pass

def calculate_updated_graph_with_loop_event(loop: Loop,loop_event: LoopEvent, graph: EventGraph) -> EventGraph:
    """Calculate the updated graph with the LoopEvent added

    :param loop: The components of the loop to add the LoopEvent to
    :param loop_event: The LoopEvent to add to the graph
    :param graph: The graph to add the LoopEvent to
    :return: The updated graph with the LoopEvent added
    """
    pass
```

##### Call Graph
The call graph for the functions is presented below:

![](/docs/development/design/1-DN-SCC_loop_detection/call_graph.svg)

