"""Self-Healing by Structural Adaptation (SHSA) using classic depth-first
search to find substitutes.

"""

from engine.shsa import SHSA
from model.shsamodel import SHSAModel, SHSANodeType

class DepthFirstSearch(SHSA):
    """Self-Healing by Structural Adaptation (SHSA) engine."""

    def __init__(self, graph=None, properties=None, configfile=None):
        """Initializes the search engine."""
        super(DepthFirstSearch, self).__init__(graph, properties, configfile)

    def substitute(self, node):
        """Returns all possible substitutes, via DFS.

        Recursive implementation.

        Returns: Possible substitutions as array of relation nodes and its
          corresponding utilities.

        Possible improvements:
        - if not relation: go through adjacents, append and return
        - save solution, globally, as soon as available (anytime algorithm)

        """
        # local helpers
        is_relation = self.model.property_value_of(node, 'type') == SHSANodeType.R
        # init
        U = []
        T = []
        # solution at this node
        u_node = 0 # variable node
        if is_relation:
            u_node = self.model.utility_of(node) # relation node
        # move on
        for n in self.model.adjacents_of(node):
            u, t = self.substitute(n)
            # add subtree solutions (if there are any)
            if is_relation and len(u) > 0:
                # add up this nodes' utility and node
                u = [utility+u_node for utility in u]
                t = [tree+[node] for tree in t]
            U.extend(u)
            T.extend(t)
        # add current relation node
        if is_relation:
            U.append(u_node)
            T.append([node])
        # return substitutes from this node on
        return U, T
