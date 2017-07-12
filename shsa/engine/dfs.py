"""Self-Healing by Structural Adaptation (SHSA) using classic depth-first
search to find substitutes.

"""

from engine.shsa import SHSA
from model.shsamodel import SHSAModel, SHSANodeType
from model.substitutionlist import SubstitutionList

class DepthFirstSearch(SHSA):
    """Self-Healing by Structural Adaptation (SHSA) engine."""

    def __init__(self, graph=None, properties=None, configfile=None):
        """Initializes the search engine."""
        super(DepthFirstSearch, self).__init__(graph, properties, configfile)

    def substitute(self, node):
        """Returns all possible substitutes, via DFS.

        Recursive implementation.

        Returns: Possible substitutions.

        Possible improvements:
        - save solution, globally, as soon as available (anytime algorithm)

        """
        # local helpers
        is_relation = (self.model.property_value_of(node, 'type')
                       == SHSANodeType.R)
        # init
        S = SubstitutionList(self.model, node)
        # solution at this node
        u_node = self.model.utility_of(node)
        # move on
        for n in self.model.predecessors(node):
            s = self.substitute(n)
            if is_relation:
                s.add_node_to(node, u_node) # append this node to all trees
            S.extend(s) # add the solutions from the neighbor
        # add relation nodes only
        if is_relation:
            S.add_substitution([node], u_node)
        # return substitutes from this node on
        return S
