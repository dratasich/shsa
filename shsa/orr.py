#!/usr/bin/python

from engine.orr import ORR

# test ORR substitution
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
    'root': {'type': 'P', 'provided': False},
    'r1': {'type': 'P', 'provided': True},
    'r2': {'type': 'P', 'provided': False},
    'r3': {'type': 'P', 'provided': True},
    'r4': {'type': 'P', 'provided': True},
    'r5': {'type': 'P', 'provided': True},
    'r6': {'type': 'P', 'provided': True},
    'r7': {'type': 'P', 'provided': True},
    't1': {'type': 'T'},
    't2': {'type': 'T'},
    't3': {'type': 'T'},
    't4': {'type': 'T'},
}
engine = ORR(g, p)
engine.substitute_init()
s, t = engine.substitute_search('root')
print s
print t
