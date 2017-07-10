#!/usr/bin/python3
"""Test SHSA substitution."""

import networkx as nx

from engine.dfs import DepthFirstSearch
from engine.greedy import Greedy
from engine.particlefilter import ParticleFilter
from model.substitution import Substitution

print("DFS")
engine = DepthFirstSearch(configfile="../config/shsamodel1.yaml")
S = engine.substitute('root')
print("- results:\n{}".format(S))
print("- best: {}".format(S.best()))

print("PF")
engine = ParticleFilter(configfile="../config/shsamodel1.yaml")
S = engine.substitute('root', best=0.76)
print("- results:\n{}".format(S))
print("- best: {}".format(S.best()))

# substitution tree with highest utility
engine.model.write_dot("uc_shsa_config-shsamodel1", 'pdf')
S.best().write_dot("uc_shsa_config-shsamodel1_substitution", 'pdf')

# print("Greedy")
# engine = Greedy(configfile="../config/shsamodel1.yaml")
# u, t = engine.substitute('root')
# print("- utilities: " + str(u))
# print("- trees: " + str(t))
