#!/usr/bin/python
"""Test SHSA substitution."""

from engine.dfs import DepthFirstSearch
from engine.greedy import Greedy
from engine.particlefilter import ParticleFilter
from graph.graph import Graph

print "DFS"
engine = DepthFirstSearch(configfile="../config/shsamodel1.yaml")
u, t = engine.substitute('root')
print "- utilities: " + str(u)
print "- trees: " + str(t)

# create substitution tree out of t with highest utility
t_best = t[u.index(max(u))]
print "- best: " + str(t_best)

print "PF"
engine = ParticleFilter(configfile="../config/shsamodel1.yaml")
u, t = engine.substitute('root', best=0.76)
print "- utilities: " + str(u)
print "- trees: " + str(t)

print "Greedy"
engine = Greedy(configfile="../config/shsamodel1.yaml")
u, t = engine.substitute('root')
print "- utilities: " + str(u)
print "- trees: " + str(t)

# # substitution tree with highest utility
# g = Graph(t[u.index(max(u))])
# g.write_dot("uc_shsamodel1_subtree", 'pdf')

# variables, tree = engine.greedy('root')
# print variables
# print tree

#r = engine.next_solution()
#print r
#r.write_dot("ex_st1", "pdf")
