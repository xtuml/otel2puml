# Import JSON into memgraph
```
CALL import_util.json("/usr/lib/memgraph/query_modules/import.json");
```
# Delete all nodes and relationships
```
MATCH (n)
DETACH DELETE n
```
# Return all nodes and relationships
```
MATCH (n)-[r]->(m)
RETURN n, r, m
```
