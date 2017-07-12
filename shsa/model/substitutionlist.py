"""Substitution list, i.e., (intermediate) results of self-healing by
structural adaptation.

"""

import networkx as nx

from model.shsamodel import SHSANodeType
from model.substitution import Substitution

class SubstitutionList(list):
    """Substitution list class."""

    def __init__(self, model, root, *args):
        """Initializes a substitution list (all substitutions will have the
        same underlying model and root node)."""
        super(SubstitutionList, self).__init__(self, *args)
        self.__model = model
        """SHSA model (used to get the utility of a node)."""
        self.__root = root
        """The node to substitute."""

    def best(self):
        """Returns substitution with highest utility."""
        if len(self) == 0:
            return None
        idx = 0
        u_max = self[idx].utility
        for i in range(0, len(self)):
            if self[i].utility > u_max:
                idx = i
                u_max = self[i].utility
        return self[idx]

    def add_substitution(self, nodes=None, utility=0):
        self.append(Substitution(self.__model, self.__root, nodes, utility))

    def add_node_to(self, node, utility, idx=None):
        """Append the node and utility to all substitutions if idx is None,
        otherwise add it to the substitution with index `idx`."""
        if idx in range(0,len(self)):
            self[idx].add(node, utility)
        else:
            for s in self:
                s.add(node, utility)

    def relations(self):
        """Returns a list of substitutions (involved relations)."""
        return frozenset([frozenset(s.relations()) for s in self])

    def __str__(self):
        return "\n".join([str(s) for s in self])
