#!/usr/bin/python

from engine.shsa import SHSA
from graph.graph import Graph

# test SHSA substitution
engine = SHSA(configfile="../config/shsamodel1.yaml")

print "DFS"
u, t = engine.dfs('root')
print "- utilities: " + str(u)
print "- trees: " + str(t)

# create substitution tree out of t with highest utility
t_best = t[u.index(max(u))]
print "- best: " + str(t_best)

print "PF"
u, t = engine.particle_filter('root', best=0.76)
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
