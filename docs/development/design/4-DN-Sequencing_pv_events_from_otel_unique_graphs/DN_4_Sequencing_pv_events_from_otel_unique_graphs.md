# Design Note 4: Sequencing pv events from otel unique graphs
## Problem
Once we have the unique graphs from the otel data, we need to sequence the pv events from these graphs. There are two ways to sequence the pv events:
1. Synchronous sequencing: events are in order of their start time
2. Asynchronous sequencing: some sequences of events occur in parallel

## Solution
### Overview
We will combine the following two approaches to sequence the pv events from the otel unique graphs:

#### Synchronous Sequencing
1. We will start by sequencing the root node of the graph.
2. We will then recursively sequence the descendant nodes of the root node in order of their start time so that child nodes are sequenced before their parent nodes.
3. We will continue this process until all the nodes in the graph have been sequenced with the root node being the last node to be sequenced.

#### Asynchronous Sequencing
1. We will start by sequencing the root node of the graph.
2. We will then recursively sequence the descendant nodes of the root node in parallel if they either overlap in time or the user has input extra information to indicate that they should be sequenced in parallel (as well as the resulting sequence of their ancestors), otherwise, we will sequence them synchronously.
3. We will continue this process until all the nodes in the graph have been sequenced with the root node being the last node to be sequenced.

### Algorithm
The basic algorithms for sequencing the pv events from the otel unique graphs are presented below as activity diagram

![](/docs/development/design/4-DN-Sequencing_pv_events_from_otel_unique_graphs/Algorithm_Overview.svg)

