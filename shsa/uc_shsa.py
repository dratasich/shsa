#!/usr/bin/python3
"""Test SHSA substitution."""

import argparse
import networkx as nx

from engine.dfs import DepthFirstSearch
from engine.greedy import Greedy
from engine.particlefilter import ParticleFilter
from model.substitution import Substitution

# parse optional config file
parser = argparse.ArgumentParser(description="""Execute SHSA engines given a
config file.""")
parser.add_argument('-r', '--root', type=str, default="root",
                    help="Node to substitute.")
parser.add_argument('-c', '--config', type=str,
                    default="../config/shsamodel1.yaml",
                    help="SHSA model in a config file.")
args = parser.parse_args()


print("DFS")
engine = DepthFirstSearch(configfile=args.config)
S = engine.substitute(args.root)
print("- results:\n{}".format(S))
print("- best: {}".format(S.best()))

print("PF")
engine = ParticleFilter(configfile=args.config)
S = engine.substitute(args.root, best=0.76)
print("- results:\n{}".format(S))
print("- best: {}".format(S.best()))

# substitution tree with highest utility
engine.model.write_dot("uc_shsa_model", 'pdf')
S.best().write_dot("uc_shsa_substitution", 'pdf')

# print("Greedy")
# engine = Greedy(configfile="../config/shsamodel1.yaml")
# u, t = engine.substitute('root')
# print("- utilities: " + str(u))
# print("- trees: " + str(t))
