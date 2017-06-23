#!/usr/bin/python
"""Test SHSA substitution."""

import networkx as nx

from engine.dfs import DepthFirstSearch
from engine.greedy import Greedy
from engine.particlefilter import ParticleFilter
from model.substitution import Substitution

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

# substitution tree with highest utility
s = Substitution(engine.model, t[0], u[0])
s.write_dot("uc_shsamodel1_substitution", 'pdf')

print "Greedy"
engine = Greedy(configfile="../config/shsamodel1.yaml")
u, t = engine.substitute('root')
print "- utilities: " + str(u)
print "- trees: " + str(t)
