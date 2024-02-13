import re


##### Initialisation #####


# format: {'event': 'node', ..}
nodeReference = {}

# format: {'node': ['event1', 'event2', ..]}
eventsReference = {}

# format: ["node1", "node2", ..]
nodeList = []

# format: {("edgestart", "edgeend"): {"weight":5, ..}}
edgeList = {}



##### Getting data #####


with open('Jalergia2PUML/jAlergiaModel.dot', 'r') as file:
    data = file.read()


##### Formatting #####


for node in re.findall("(.*?) \[shape=\".*?\",label=\"(.*?)\"",data):
  if(node[1] not in nodeReference):
    nodeReference[node[1]] = [node[0]]
    eventsReference[node[0]] = node[1]
    nodeList.append(node[1])
  else:
    nodeReference[node[1]].append([node[0]])
    eventsReference[node[0]] = node[1]

for edge in re.findall("(.*?)->(.*?) \[label=\"(.*?)\"",data):
  if(edge[0] != '__start0 '):
    if(edge[2] != ""):
      edgeList[(edge[0],edge[1])] = {"weight" : str(edge[2])}
    else:
      edgeList[(edge[0],edge[1])] = {}


##### Processing Data #####


import networkx as nx
graph = nx.MultiDiGraph()

for item in eventsReference:
  graph.add_node(item,label=eventsReference[item])


for item in edgeList:
  graph.add_edge(str(item[0]), str(item[1]), label=str(edgeList[item]["weight"]))



##### Output #####


graph.edges(data=True)

nx.nx_agraph.write_dot(graph, "./graphtest.dot")