"""Self-Healing by Structural Adaptation.

Implements substitute search algorithm with various search methods.

"""

from model.shsamodel import SHSAModel, SHSANodeType

class SHSA(object):
    """Self-Healing by Structural Adaptation (SHSA) engine."""

    def __init__(self, graph=None, properties=None, configfile=None):
        """Initializes the engine with a model."""
        self.__model = SHSAModel(graph, properties, configfile)
        """Knowledge base for SHSA."""

    def model(self):
        """Returns the underlying SHSA model."""
        return self.__model

    def dfs(self, node):
        """Returns possible substitutes, via DFS.

        Recursive implementation.

        Returns: Possible substitutions as array of relation nodes and its
          corresponding utilities.

        Possible improvements:
        - if not relation: go through adjacents, append and return
        - save solution as soon as available (anytime algorithm)

        """
        # local helpers
        relation = self.__model.property_value_of(node, 'type') == SHSANodeType.R
        # init
        U = []
        T = []
        # solution at this node
        u_node = 0 # variable node
        if relation:
            u_node = self.__model.utility_of(node) # relation node
        # move on
        for n in self.__model.adjacents_of(node):
            u, t = self.dfs(n)
            # add subtree solutions (if there are any)
            if relation and len(u) > 0:
                # add up this nodes' utility and node
                u = [utility+u_node for utility in u]
                t = [tree+[node] for tree in t]
            U.extend(u)
            T.extend(t)
        # add current relation node
        if relation:
            U.append(u_node)
            T.append([node])
        # return substitutes from this node on
        return U, T

    def bfs(self, node):
        """Substitute search via BFS.

        Recursive implementation.

        """
        assert False, "not yet implemented"

    def greedy(self, node):
        """Search a substitute for the given node with greedy algorithm.

        Recursive implementation.

        Assumptions:
        - The given node must be of type `SHSANodeType.V`, i.e., a variable of
          the SHSA model.
        - Variables and relations alternate in the model, i.e., a variable node
          is only connected to relations and vice-versa.

        """
        assert False, "not yet impelemented"
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
        print r
        tree.append(r)
        for v in self.__model.adjacents_of(r):
            # ignore the node where we are coming from
            if v == node:
                continue
            v, t = self.greedy(v)
            variables.extend(v)
            tree.extend(t)
        return variables, tree

    def particle_filter(self, node):
        """Substitute search via particles.

        Recursive implementation.

        """
        assert False, "not yet implemented"
