# Identify and Add Lonely Merge Nodes 
This file include the simple implementation for lonely merge nodes.

## Implementation
The implementation can be simply found by replacing the attribute `lonely_merge_node` in the `Node` class with a property. This property checks if there is a single path that is not a kill path whilst other are and if so returns the node of that path and if not returns None. This implementation means that we only need find and update the kill paths.

