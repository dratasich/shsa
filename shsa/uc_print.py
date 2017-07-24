#!/usr/bin/python3

from model.shsamodel import SHSAModel, SHSANodeType

g = {
    'speed': ['tf1.1'],
    'tf1.1': ['acc'],
    'acc': ['tf1.2'],
    'tf1.2': ['speed'],
}
p = {
    'type': { 'speed': SHSANodeType.V, 'acc': SHSANodeType.V,
              'tf1.1': SHSANodeType.R, 'tf1.2': SHSANodeType.R },
    'need': { 'speed': True, 'acc': False },
    'provided': { 'speed': True, 'acc': True },
    'function': { 'tf1.1': "a = dv/dt", 'tf1.2': "v = int(a)" },
}
model = SHSAModel(g, p)
print(model)
model.write_dot("uc_print_highlight-edges1",
                highlight_edges=[('speed','tf1.1')])
model.write_dot("uc_print_highlight-edges2", "pdf", [('speed','tf1.1')])

# yaml example
model = SHSAModel(configfile="../config/shsamodel1.yaml")
model.write_dot("uc_print_config-shsamodel1-yaml", "pdf")
print(model)
