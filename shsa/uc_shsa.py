#!/usr/bin/python3
"""Test SHSA substitution."""

import argparse

from model.shsamodel import SHSAModel
from model.substitution import Substitution

from engine.dfs import DepthFirstSearch
from engine.greedy import Greedy


# parse optional config file
parser = argparse.ArgumentParser(description="""Execute SHSA engines given a
config file.""")
parser.add_argument('-r', '--root', type=str, default="root",
                    help="Node to substitute.")
parser.add_argument('-c', '--config', type=str,
                    default="../config/shsamodel1.yaml",
                    help="SHSA model in a config file.")
parser.add_argument('-d', '--dfs', action="store_true",
                    help="Depth-first-search.")
parser.add_argument('-g', '--greedy', action="store_true",
                    help="Greedy search.")
args = parser.parse_args()

# additional input validation
model = SHSAModel(configfile=args.config)
assert args.root in model.nodes(), \
    "root '{}' is not part of the model".format(args.root)
assert model.is_variable(args.root), "relation nodes cannot be substituted"

# print model
model.write_dot("uc_shsa_model", 'pdf')
print("config: {}".format(args.config))

#
# search
#

S = None

if args.dfs:
    print("DFS")
    engine = DepthFirstSearch(configfile=args.config)
    S = engine.substitute(args.root)
    # when the root is already provided, an empty substitution is also valid
    if engine.model.provided([args.root]):
        s = Substitution(root=args.root, model=engine.model)
        S.append(s)
    print("- results:\n{}".format(S))
    print("- best: {}".format(S.best()))

if args.greedy:
    print("Greedy")
    engine = Greedy(configfile=args.config)
    while(engine.substitute(args.root)):
        pass
    S = engine.last_results()
    print("- results:\n{}".format(S))
    print("- best: {}".format(S.best()))

# print substitution tree with highest utility
if S is not None:
    sbest = S.best()
    if sbest is not None:
        sbest.write_dot("uc_shsa_substitution", 'pdf')
