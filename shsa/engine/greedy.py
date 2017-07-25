"""Self-Healing by Structural Adaptation (SHSA) using a greedy algorithm to
find a substitute.

"""

from engine.shsa import SHSA
from model.shsamodel import SHSAModel, SHSANodeType


class Greedy(SHSA):
    """Self-Healing by Structural Adaptation (SHSA) engine."""

    def __init__(self, graph=None, properties=None, configfile=None):
        """Initializes the search engine."""
        super(Greedy, self).__init__(graph, properties, configfile)

    def substitute(self, root):
        """Search a substitute for the given node with greedy algorithm.

        Recursive implementation.

        Assumptions:
        - The given node must be of type `SHSANodeType.V`, i.e., a variable of
          the SHSA model.
        - Variables and relations alternate in the model, i.e., a variable node
          is only connected to relations and vice-versa.

        """
        raise NotImplementedError("TODO - not yet implemented")
        variables = [node]
        tree = []
        # variable provided?
        if self.__model.property_value_of(node, 'provided'):
            # property is provided we don't have to search further
            return variables, tree
        # get possible relations
        relations = self.__model.adjacents_of(node)
        if not relations:
            # reached a leaf of the graph
            return variables, tree
        # make greedy choice: get relation with highest utility
        r = max(relations, key=self.__model.utility_of)
        print(r)
        tree.append(r)
        for v in self.__model.adjacents_of(r):
            # ignore the node where we are coming from
            if v == node:
                continue
            v, t = self.greedy(v)
            variables.extend(v)
            tree.extend(t)
        return variables, tree
