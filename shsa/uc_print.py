#!/usr/bin/python

from graph.graph import Graph
from graph.search import bfs, dfs
from model.shsamodel import SHSAModel, SHSANodeType

## graph prints ###############################################################

g = { "a" : ["d"],
      "b" : ["c"],
      "c" : ["b", "c", "d"],
      "d" : ["a", "c"],
      "e" : []
}

graph = Graph(g)
print graph
print
graph.write_dot("ex_graph")
graph.write_dot("ex_graph", oformat="pdf")

print "BFS"
print bfs(graph, "a")
print

print "DFS"
print dfs(graph, "a")
print

## SHSA model prints ##########################################################

g = {
    'speed': ['tf1.1'],
    'tf1.1': ['acc'],
    'acc': ['tf1.2'],
    'tf1.2': ['speed'],
}
p = {
    'type': { 'speed': SHSANodeType.V, 'acc': SHSANodeType.V,
              'tf1.1': SHSANodeType.R, 'tf1.2': SHSANodeType.R },
    'need': { 'speed': True, 'acc': False },
    'provided': { 'speed': True, 'acc': True },
    'function': { 'tf1.1': "a = dv/dt", 'tf1.2': "v = int(a)" },
}
model = SHSAModel(g, p)
print model
model.write_dot("ex_shsa-model", highlight_edges=[('speed','tf1.1')])
model.write_dot("ex_shsa-model", "pdf", [('speed','tf1.1')])

# yaml example
model = SHSAModel(configfile="../config/shsamodel1.yaml")
model.write_dot("ex_shsa-model-1", "pdf")
print model
