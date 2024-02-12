import re

with open('Jalergia2PUML/jAlergiaModel.dot', 'r') as file:
    data = file.read()

# format: {'event': 'node', ..}
nodeReference = {}
eventsReference = {}

# format: ["node1", "node2", ..]
nodeList = []

# format: {("edgestart", "edgeend"): {"weight":5, ..}
edgeList = {}


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



# print("nodeReference ######################################################")
# print("{")
# for item in eventsReference:
#   print("    \"" + item + "\" : \"" + str(eventsReference[item]) + "\",")
# print("}\n")

# print("nodeList ###########################################################")

# print("[")
# for item in nodeList:
#   print("    " + item + ",")
# print("]\n")


# print("edgeList ############################################################")

# print("[")
# for item in edgeList:
#   print("    " + str(item) + " : " + str(edgeList[item]) + ",")
# print("]\n")


################################################################################################################################################


import networkx as nx
graph = nx.MultiDiGraph()

for item in eventsReference:
  graph.add_node(item,label=eventsReference[item])


for item in edgeList:
  graph.add_edge(str(item[0]), str(item[1]), label=str(edgeList[item]["weight"]))


graph.edges(data=True)

nx.nx_agraph.write_dot(graph, "./graphtest.dot")