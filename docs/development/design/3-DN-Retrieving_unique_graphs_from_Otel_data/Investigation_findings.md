# Investigation into Storage and Evaluation Methods to Find Unique Graphs within OpenTelemetry Data

## 1. Current Implementation

### 1.1 Data Storage
- OpenTelemetry (OTel) data is parsed and stored in a SQLite database.
- Relations between data points are formed within the database structure.

### 1.2 Graph Evaluation Method
- Unique graph structures are identified through a comparison process.
- The current method involves sorting graph data into alphanumerical ordered lists before comparison.
- This approach is not 100% accurate due to limitations in the sorting-based comparison.

### 1.3 Limitations
- Potential for false positives or negatives in graph isomorphism determination (graph uniqueness).

## 2. Investigation Objectives

The primary goal is to explore alternative methods for storing and evaluating graph data derived from OTel traces. Specifically, we aim to:

1. Identify more accurate methods for determining graph isomorphism.
2. Explore storage solutions optimised for graph data.
3. Evaluate the performance and scalability of different approaches.
4. Assess the ease of implementation and maintenance of new solutions.

## 3. Proposed Solutions for Investigation

### 3.1 Graph Databases
#### 3.1.1 Neo4j
- Native graph storage and querying capabilities.
- Cypher query language for complex graph operations.
- Built-in visualization tools.
- Disk-based
- Written in Java
- Most popular graph database solution

#### 3.1.2 ArangoDB
- Supports JSON documents, graphs and key/values.
- Uses AQL (ArangoDB Query Language)
- Disk-based
- Written in C++

#### 3.1.3 Memgraph
- Memgraph is an open-source graph database built for streaming and compatible with Neo4j.
- Supports both property graph and RDF models.
- Written in C++
- In-memory based (disk based available) for faster querying
- Uses Cypher as its query language
- Compatible for use with Networkx
- Allows custom procedures to be written in Python
- Networkx has built in methods for finding graph isomorphism

#### 3.1.4 SQLite
- Lightweight, serverless, self-contained relational database engine
- Written in C
- File-based: entire database stored in a single file on disk
- ACID-compliant
- Supports standard SQL syntax with some extensions
- No native graph capabilities, but can be used to store graph-like structures
- Requires custom implementation for graph operations and traversals
- Efficient for smaller datasets and embedded applications
- Limited concurrency support
- No built-in support for graph algorithms or isomorphism detection

### 3.2 Advanced Graph Algorithms
#### 3.2.1 Graph Isomorphism Algorithms
- VF2 algorithm for graph and subgraph isomorphism detection.
- Ullmann's algorithm for subgraph isomorphism.

#### 3.2.2 Graph Hashing Techniques
- WL (Weisfeiler-Lehman) graph kernels for structure comparison.

## 4. Evaluation Criteria

For each proposed solution, we will evaluate:

1. Accuracy in identifying unique graph structures.
2. Query performance for common graph operations.
3. Scalability with increasing data volume.
4. Ease of integration with existing OTel data processing pipeline.
5. Maintenance overhead and long-term viability.

### 4.1 Custom Solution with Memgraph and NetworkX

#### 4.1.1 Memgraph with NetworkX Integration
- Utilise Memgraph's ability to write custom procedures in Python
- Implement a procedure to convert Memgraph graphs to NetworkX DiGraph objects
- Leverage NetworkX's implementation of the Weisfeiler-Lehman graph hashing algorithm
- Use the generated hash for graph isomorphism comparisons

#### 4.1.2 Findings
- Memgraph's lack of native graph isomorphism capabilities necessitated a custom solution.
- To load JSON data into memgraph, the data had to be transformed to a specific format containing data for a "node" and for a "relationship". This created more overhead.
- Integration with NetworkX provides access to a wide range of graph algorithms.
- The Weisfeiler-Lehman algorithm implemented in NetworkX offers an efficient and precise method for graph hashing.
- This approach allows for flexibility in implementing custom graph analysis procedures.
- Initial tests show promising results for identifying unique graph structures in OTel data.
- Relatively slow, for 10,000 graphs of depth 3 with 1-3 branches per node resulted in a processing time of around 3-6 mins. This included optimisations such as batch queries. 


#### 4.1.3 Algorithm Overview

1. OTel data converted to JSON of nodes and relationships. Data could then be loaded into memgraph using the procedure import_util.json()
2. Query database for root nodes.
3. Extract job_name and trace_id from root nodes, mapping job names to trace ids.
4. Loop over trace_id within each job_name. Query database with a batch of trace_id
5. Iterate over trace_id within the cypher query using the UNWIND statement. Call the custom procedure within the query that converts a memgraph graph to a networkx digraph, and returns the weisfeler-lehman hash value
6. Store hashes within a defaultdict(set), mapping job names to unique graph hashes

### 4.2 Custom Solution with SQLite

4.2.1 Performance Findings

- Initial Implementation: The basic SQLite implementation demonstrated a significant performance advantage, computing graphs at least 5 times faster than the Memgraph solution.
- Custom Hashing Algorithm: We developed a tailored hashing solution that computes a node's hash by combining:
    * The hash of the node's event_type
    * The sorted hashes of its children's event_types
    * This approach proved both efficient and accurate, matching the Memgraph NetworkX solution in identifying unique graphs when tested on a dataset of 10,000 graphs.
- In-Memory Processing: By loading the dataset into memory, we achieved a 40% speed improvement for processing 10,000 graphs of depth 3 with 1-3 branches per node.
- Query Optimisation: Implementing batch processing with a size of 500 nodes gave remarkable results:
    * SQLite solution: 1.6 seconds
    * Memgraph solution: 200 seconds
    * This represents a 125x speed improvement over the Memgraph approach.

4.2.2 Architectural Advantages

- Flexible Data Modeling: The SQLite solution allows for easy modifications to the Node model, accommodating changes in data structure without significant refactoring.
- Reduced Data Manipulation: Unlike the Memgraph solution, which required post-processing of data, the SQLite approach eliminates the need for data transformation, resulting in less overhead and simpler data pipeline.
- Scalability: The performance gains observed with the SQLite solution suggest better scalability for larger datasets, addressing one of the key objectives of this investigation.

4.2.3 Comparative Analysis
When compared to the Memgraph solution, the SQLite approach offers:

- Substantially faster processing times (125x improvement in our tests)
- Simpler data pipeline with reduced manipulation requirements
- Greater flexibility in data modeling
- Potential for better scalability with larger datasets

#### 4.1.4 Algorithm Overview
Database Setup:
- Create an SQLite database (in-memory for this implementation).
- Define a Node model representing the structure of OTel data.

Data Loading:
- Load node data from a JSON file into the SQLite database.
- Each node contains span_id, trace_id, event_type, job_name, and prev_span_id.

Graph Processing:
- Retrieve distinct job names from the database.
- For each job name:
    * Query for root nodes (nodes with no prev_span_id) for that job.
    * Process root nodes in batches (batch size = 500).

Graph Hashing:

- For each batch of root nodes:
    * Retrieve all related nodes for the batch from the database.
    * Create a mapping of nodes to their children.
    * For each root node in the batch:
- Recursively compute a hash for the graph starting from the root node.
- The hash is based on the node's event_type and its children's hashes.

Unique Graph Identification:
- Maintain a hash set for each job name.
- Add computed graph hashes to the corresponding job name's hash set.
- Keep track of which trace_ids correspond to each unique graph hash.

Result Compilation:
- Count the total number of unique graph structures across all job names.

Performance Optimisation:
- Use in-memory SQLite database for faster access.
- Process nodes in batches to reduce database query overhead.
- Use efficient hashing algorithm (SHA-256) for graph structure comparison.


## 7. Conclusion

This investigation into storage and evaluation methods for OpenTelemetry data has given valuable insights, particularly in comparing SQLite and Memgraph solutions for identifying unique graph structures.

The custom SQLite solution has demonstrated significant performance advantages over the Memgraph approach:

- Speed: SQLite computed graphs 5 times faster than the Memgraph solution with a basic implementation. With optimisations like in-memory processing and query batching, the SQLite approach processed 10,000 graphs in just 1.6 seconds, compared to Memgraph's 200 seconds.
- Efficiency: The custom hashing algorithm implemented for SQLite proved to be both fast and accurate, matching the Memgraph/NetworkX solution in identifying unique graphs.
- Flexibility: SQLite allowed for easier modifications to the Node model and required less data manipulation, resulting in reduced overhead compared to Memgraph.
- Scalability: The SQLite solution showed better performance with larger datasets, addressing one of our key investigation objectives.

While Memgraph offered some advantages, such as native graph storage and compatibility with NetworkX for advanced algorithms, these benefits were outweighed by the performance gains and simplicity of the SQLite approach for our specific use case.
The investigation also highlighted the importance of custom implementations tailored to specific needs. The SQLite solution, despite lacking native graph capabilities, outperformed the specialised graph database when optimised for our particular requirements.

Moving forward, we recommend:

- Further optimisation and refinement of the SQLite-based solution.
- Conducting additional scalability tests with even larger datasets.
- Exploring ways to incorporate some of the beneficial features of graph databases (like visualisation) into our SQLite-based system.

In conclusion, this investigation has provided a clear direction for improving our OTel trace analysis infrastructure, favoring a highly optimised SQLite-based approach over more complex graph database solutions for our current needs.