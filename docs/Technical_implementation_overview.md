# Technical implementation overview
## Introduction
This document provides an overview of the technical implementation of the project. It is intended to provide a high-level understanding of the project's technical implementation.

The purpose of the project is focussed on the reverse engineering of logical PlantUML diagrams from OpenTelemetry data for ingestion into the "Protocol Verifier" (PV) tool (https://github.com/xtuml/munin) which at a basic level verifies linked data against a set of logical rules.

Currently the project sits at the state of ingesting linked sequences of PV JSON events (example below):
```json
[
    {
        "jobName": "simple_AND_job",
        "jobId": "cd739a50-f262-4d34-817e-2d73d54d860a",
        "eventType": "A",
        "eventId": "6301e375-4bc8-48ee-8712-d94a17bf9175",
        "timestamp": "2023-06-13T17:57:09Z",
        "applicationName": "default_application_name"
    },
    {
        "jobName": "simple_AND_job",
        "jobId": "cd739a50-f262-4d34-817e-2d73d54d860a",
        "eventType": "B",
        "eventId": "9e7a1f7b-c20e-4aff-9bc3-10e26ec06675",
        "timestamp": "2023-06-13T17:57:10Z",
        "applicationName": "default_application_name",
        "previousEventIds": ["6301e375-4bc8-48ee-8712-d94a17bf9175"]
    },
]
```
These linked sequences are then converted into a PlantUML diagram which can be visualised using the PlantUML tool (https://plantuml.com/) (example below):

![](/end-to-end-pumls/constraints/simple/AND/simple_AND.svg)

The technical implementation of the project is broken down into the following components:
- Data ingestion
- Logic detection
- Markov graph
- Loop detection
- PUML Logical graph generation

## Data ingestion
Currently data ingestion stands at ingesting linked sequences of PV JSON events. The data is ingested using methods in `tel2puml/data_pipelines/data_ingestion.py`.

The methodology to ingest data is the following:
1. Read in the linked sequences of PV JSON events from file/s
2. For each sequence extract each event
3. For each event create an `Event` object (if does not already exist).
4. Update the `Event` object with the incoming and outgoing event data using lists of preceding and following event type occurrences.

The `Event` object (found in `tel2puml/events.py`) is a hashable custom object with a uid that holds the following data:
- `event_type`: the type of event taken from the PV JSON event
- `event_sets`: a set of `EventSet` that hold unique numbers of occurrences of outgoing event types from the current event
- `incoming_event_sets`: a set of `EventSet` that hold unique numbers of occurrences of incoming event types to the current event

An `EventSet` (found in `tel2puml/events.py`) is a custom data object that holds information on the number of occurrences of a particular event types. It is used to as a simple way to store the number of occurrences of a particular event type for a sequence in the incoming and outgoing events without having to hold all the graphs in memory and not needing to repeat the same data twice due to the hashable nature of the data structure. 

## Logic detection
The logic detection component is responsible for detecting the logical rules that are present in the accumulated data from the linked sequences of PV JSON events. The logic detection component is implemented in `tel2puml/logic_detection.py`.

The basic methodology for detecting logic is to use that data held in the outgoing `EventSet`'s that provide the unique possible occurrences of event types that follow a particular `Event`. Using this data an algorithm is used to reason on the logical gates that occur after each event (i.e. `AND`, `OR`, `XOR`). The algorithm is able to find arbitrary levels of nesting of logical gates following the data (except for bunched occurrence of the same logical gate type which has to be inferred when creating the logical graph).

An example of how the logical gates after an event is shown below:
Event A has the following set of outgoing `EventSet`'s (we write these as both lists and their representation as dictionaries for clarity):
- `[B, C]` or `{B: 1, C: 1}`
- `[D, C]` or `{C: 1, D: 1}`
    
The logical gates that would be inferred from this data would be:
```
          |-> C
A -> AND -|
          |        |-> B
          |-> XOR -|
                   |-> D
```

With all the data on each event the logical gates can be inferred for all the ingested data together.

## Markov graph
The markov graph component represents the data collected as a Markov graph i.e. a graph of all the possible transitions between events. The Markov graph is built using the data from the `Event` objects and the `EventSet` objects. The Markov graph is built using the `create_graph_from_events` method found in `tel2puml/events.py`.

The Markov graph is a directed graph where the nodes are the `Event` objects and the edges are the possible following `Event`'s that are found using the `EventSet` data on each `Event`.

A very simple example of Markov graph generation is explained below. Given the following data:
- Event A has the following set of outgoing `EventSet`'s:
    - `[B]` or `{B: 1}`
    - `[D]` or `{D: 1}`
- Event B has the following set of outgoing `EventSet`'s:
    - `[C]` or `{C: 1}`
- Event C has no outgoing `EventSet`'s
- Event D has no outgoing `EventSet`'s


The Markov graph would simply be:
```
   |-> B -> C
A -| 
   |-> D
```

## Loop detection

The loop detection component is responsible for detecting loops in the Markov graph. The loop detection component is implemented in `tel2puml/loop_detection` package.

The basic overall methodology of the loop detection component is:
1. Find Strongly Connected Components within the base Markov graph. The Strongly Connected Components are found using the Tarjan's algorithm (https://en.wikipedia.org/wiki/Tarjan%27s_strongly_connected_components_algorithm).
2. For each Strongly Connected Component:
    1. Get the following: 
        - start points - nodes that have incoming edges from outside the Strongly Connected Component
        - exit points - nodes that have outgoing edges to outside the Strongly Connected Component
        - loop back points - nodes that have edges back to the start points of the Strongly Connected Component
        - end points - loop back points of the Strongly Connected Component that do not have paths to any loop back points except through the start points - with the exception of loop back points that both have paths to each other
        - loop back edges - edges that go from the end points to the start points
        - break points - nodes that are descendants of the set exit points excluding end points 
    2. Remove the loop back edges
    3. Isolate the Strongly Connected Components from the base Markov graph (and any paths to break points) and create a subgraph with
        - all start points connected to a dummy start node
        - all end points connected to a dummy end node
    4. Replace the subgraph into the top level graph with a loop node and add all relevant connections into and out of the loop node
    5. Repeat full process on subgraphs recursively

### End Point strategy
The end point strategy is used to determine the end points of a loop. The strategy is as follows:
1. Get all loop back points (as described above)
2. Create a matrix of `1`'s and `0`'s where rows are the loop back points (`i`) and columns are the loop back points (`j`)
3. The following then provide the values for the cells of the matrix:
    - `1` if there is a path from loop back point `i` to loop back point `j`
    - `0` if there is no path from loop back point `i` to loop back point `j`
4. A loop back point, `i`, is then an end point if, for all `j`, the following holds `ij - ji >= 0`

This strategy means that any loop back points that are also in a loop each other can still be end points.

### Example
An example of the loop detection implementation is shown below for the following graph:

![](/tests/loop_detection/loop_test_graph.svg)

The Strongly Connected Components from this graph are `[F, E, D, G, I, H]` with:
- with start points: `[F, E, D]`
- with exit points: `[H, I, G, F]`
- with loop back points: `[I, H]`
- with end points: `[I, H]`
- with loop back edges: `[(I, F), (H, E), (H, D)]`
- with break points: `[M, N]`

Replacing this Strongly Connected Component with a loop node gives the following graph:

![](/tests/loop_detection/loop_test_graph_parent.svg)

The algorithm is then repeated on the loop subgraph and the only Strongly Connected Component from this is `[I, H]` with:
- with start points: `[I, H]`
- with exit points: `[I, H]`
- with loop back points: `[I, H]`
- with end points: `[I, H]`
- with loop back edges: `[(I, H), (H, I)]`
- with break points: `[]`

Replacing this Strongly Connected Component with a loop node gives the following graph (of the subgraph):

![](/tests/loop_detection/loop_test_graph_loop_sub_graph.svg)

and the subgraph of the loop node in that graph is then given by:

![](/tests/loop_detection/loop_test_graph_loop_sub_graph_sub_graph.svg)

## PUML Logical graph generation

The PUML Logical graph generation component is responsible for generating the PlantUML logical graph from the Markov graph with the loop nodes containing subgraphs. The PUML Logical graph generation component is implemented in `tel2puml/walk_puml_graph/walk_puml_logic_graph.py`.

The basic methodology for generating the PUML logical graph is to walk the Markov graph with the loop nodes and generate the PlantUML code for the logical graph. The walking of the graph is performed in the following way (starting at the root node of the Markov graph with loop edges removed):
1. look at the logical out gate that follows the current node
2. if there is a logical gate then:
    - create a logical gate node the PlantUML graph attached to the preceding node
    - look at the following nodes of the logical gate node
    - pick one path as the new current path repeat 1.
3. if there is no logical gate then:
    - check to see if the current node could possibly merge with another path of the current logic operator on the following node
    - if it can then:
        - check if all paths of the logic operator have been walked down to the following node and can merge
        - if they have then:
            - connect all the nodes in the logic operator to an end logical operator node
            - connect the end operator node to the following node (unless there is a bunched merge) and set the following node as the current node
            - repeat 1
        - if they have not then:
            - rotate to another path from the logic operator
            - repeat 1 on the new path 
    - if it cannot then:
        - if there are no following nodes in the current path:
            - the path must not merge and must kill/detach.
            - change to the next path of the logic operator and repeat 1. 
        - if there are following nodes in the current path:
            - create a new node in the PlantUML graph for the following node
            - set the new node as the current node and repeat 1.
4. if there are no following nodes then the walk is complete
5. find all loop nodes in the graph and repeat the above on the subgraph of each loop node

### Example
An example of the PUML Logical graph generation is shown below for the following markov graph:

```
   |-> B -> C -|
A -|           |-> E
   |-> D ------|
   |-> F
```

In the above only `A` has a logical gate of `AND` with the following structure:
```
          |-> B
A -> AND -|-> D
          |-> F
```

Data held on the incoming data on `E` shows that:

```
C -|
   |-> AND -> E
D -|
```
Therefore `C` and `D` can merge into `E` with and `AND` gate.

Firstly `A` is found as the root node so the PlantUML logic graph is started with a node `A`:
```
A
```
Next a logical `AND` out gate follows `A` so a logical gate node is created and connected to `A`:
```
A -> AND
```
The following nodes of the logical gate node are `B`, `D` and `F`. The first path is taken and `B` is the next node so a node is created for `B` and connected to the logical gate node:
```
A -> AND -> B
```
The following node of `B` is `C`, which has no data suggesting it merges so a node is created for `C` and connected to `B`:
```
A -> AND -> B -> C
```
The following node of `C` is `E` which has data suggesting it could merge with `D` so the paths is rotated to `D` and a node is created for `D` and connected to the current `AND` gate node:
```
          |-> B -> C
A -> AND -|
          |-> D
```
The following node of `D` is also `E` and data suggests it can merge with `E`, however there is still another path to walk so the path is rotated to `F` and a node is created for `F` and connected to the current `AND` gate node:
```
          |-> B -> C
A -> AND -|-> D
          |-> F
```
There is no following node of `F` and because there is an open logical operator the path must be killed, so a "kill" node is inserted that identifies the path as killed.

```
          |-> B -> C
A -> AND -|-> D
          |-> F -> KILL
```
A "kill" node is a dummy node and so is considered to merge with the bottom of the logical operator. Therefore an `AND` in operator is created and the "kill" node is directed into this

```
          |-> B -> C
A -> AND -|-> D          |-> AND
          |-> F -> KILL -|
```
Now that there are only two remaining paths and the data confirms that both those paths merge into `E`, the path is switched back to `C` and the node `C` is then connected into the logical `AND` node

```
          |-> B -> C ----|
A -> AND -|-> D          |-> AND
          |-> F -> KILL -|
```
Next the path is rotated to `D` and this is then connected into the `AND` node

```
          |-> B -> C ----|
A -> AND -|-> D ---------|-> AND
          |-> F -> KILL -|
```
The event that follows the merge was confirmed to be `E` so a node is created for `E` and the `AND` node is directed into the `E` node
```
          |-> B -> C ----|
A -> AND -|-> D ---------|-> AND -> E
          |-> F -> KILL -|
```
The walk is now complete as there are no following nodes from `E` and the PlantUML logical graph is complete.


