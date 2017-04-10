#!/usr/bin/python

from graph.graph import Graph
from graph.search import bfs

g = { "a" : ["d"],
      "b" : ["c"],
      "c" : ["b", "c", "d"],
      "d" : ["a", "c"],
      "e" : []
}

graph = Graph(g)
print graph
graph.write_dot("substitute_path", highlight_edges=[("a", "d"), ("d", "c")])
#graph.write_dot("substitute_path", oformat="eps", highlight_edges=[("a", "d"), ("d", "c")])

print bfs(graph, "a")
