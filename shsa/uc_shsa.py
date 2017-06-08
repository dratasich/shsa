#!/usr/bin/python

from engine.shsa import SHSA

# test SHSA substitution
g = {
    'root': ['t1', 't2', 't3'],
    't1': ['r1', 'r2'],
    't2': ['r3'],
    't3': ['r4', 'r5'],
    'r1': [],
    'r2': ['t4'],
    't4': ['r6', 'r7'],
    'r3': [],
    'r4': [],
    'r5': [],
    'r6': [],
    'r7': [],
}
p = {
    'root': {'type': SHSANodeType.V,
             'need': True, 'provided': False},
    'r1': {'type': SHSANodeType.V,
           'need': False, 'provided': True},
    'r2': {'type': SHSANodeType.V,
           'need': False, 'provided': False},
    'r3': {'type': SHSANodeType.V,
           'need': False, 'provided': True},
    'r4': {'type': SHSANodeType.V,
           'need': False, 'provided': True},
    'r5': {'type': SHSANodeType.V,
           'need': False, 'provided': True},
    'r6': {'type': SHSANodeType.V,
           'need': False, 'provided': True},
    'r7': {'type': SHSANodeType.V,
           'need': False, 'provided': True},
    't1': {'type': SHSANodeType.R},
    't2': {'type': SHSANodeType.R},
    't3': {'type': SHSANodeType.R},
    't4': {'type': SHSANodeType.R},
}
#engine = SHSA(g, p)
#engine.model().write_dot("ex_greedy", "pdf")
engine = SHSA(configfile="../config/shsamodel1.yaml")
engine.model().write_dot("ex_greedy", "pdf")
variables, tree = engine.greedy('root')
print variables
print tree
#r = engine.next_solution()
#print r
#r.write_dot("ex_st1", "pdf")
