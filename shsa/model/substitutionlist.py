"""Substitution list, i.e., (intermediate) results of self-healing by
structural adaptation.

Note, be careful to add `Substitution` instances only (not simply lists as the
members of root and model of `Substitution` are used).

"""

from collections import UserList
import networkx as nx

from model.shsamodel import SHSANodeType
from model.substitution import Substitution

class SubstitutionList(UserList):
    """Substitution list class."""

    def __init__(self, *args, **kwargs):
        """Initializes a substitution list.

        Model and root are retrieved from the first substitution if there is
        any. All substitutions will have the same underlying model and root
        node.

        """
        super(SubstitutionList, self).__init__(*args, **kwargs)
        # nothing todo

    def update(self, root, model=None):
        """Updates the root and optionally the model of all underlying
        substitutions.

        """
        # update substitutions
        for s in self:
            s.root = root
            if model is not None:
                s.model = model

    def best(self):
        """Returns substitution with highest utility."""
        if len(self) == 0: # no substitution results
            return None
        idx = 0
        u_max = self[idx].utility
        for i in range(0, len(self)):
            if self[i].utility > u_max:
                idx = i
                u_max = self[i].utility
        return self[idx]

    def add_substitution(self, nodes=[]):
        if len(self) > 0:
            model = self[0].model
            root = self[0].root
        else:
            model = None
            root = None
        self.append(Substitution(nodes, model=model, root=root))

    def add_node_to(self, node, idx=None):
        """Append the node and utility to all substitutions if idx is None,
        otherwise add it to the substitution with index `idx`."""
        if idx in range(0,len(self)):
            self[idx].append(node)
        else:
            for s in self:
                s.append(node)

    def relations(self):
        """Returns a list of substitutions (involved relations)."""
        return frozenset([frozenset(s.relations()) for s in self])

    def __str__(self):
        return "\n".join([str(s) for s in self])
