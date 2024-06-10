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