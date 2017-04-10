#!/usr/bin/python

from graph.graph import Graph
from graph.search import bfs
from model.model import *

g = { "a" : ["d"],
      "b" : ["c"],
      "c" : ["b", "c", "d"],
      "d" : ["a", "c"],
      "e" : []
}

graph = Graph(g)
print graph
print
#graph.write_dot("ex_graph")
#graph.write_dot("ex_graph", oformat="pdf")

print bfs(graph, "a")
print

## SHSA model prints ##########################################################

g = {
    'speed': ['tf1.1'],
    'tf1.1': ['acc'],
    'acc': ['tf1.2'],
    'tf1.2': ['speed'],
}
p = {
    'speed': {'type': SHSANodeType.RV, 'label': "v",
              'need': True, 'provided': True},
    'tf1.1': {'type': SHSANodeType.TF, 'label': "a = dv/dt"},
    'tf1.2': {'type': SHSANodeType.TF, 'label': "v = int(a)"},
    'acc': {'type': SHSANodeType.RV, 'label': "a",
            'need': False, 'provided': True},
}
model = SHSAModel(g, p)
print model
print
#model.write_dot("ex_shsa-model", highlight_edges=[('speed','tf1')])
model.write_dot("ex_shsa-model", "pdf", [('speed','tf1')])
