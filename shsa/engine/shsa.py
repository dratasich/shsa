"""Self-Healing by Structural Adaptation.

Implements substitute search algorithm with various search methods.

"""

from model.shsamodel import SHSAModel

class SHSA(object):
    """Self-Healing by Structural Adaptation (SHSA) engine."""

    def __init__(self, graph=None, properties=None, configfile=None):
        """Initializes the engine with a model."""
        self.__model = SHSAModel(graph, properties, configfile)
        """Knowledge base for SHSA."""
        self.__failed_node = None
        """Failed node for which a substitute shall be found."""

    def model(self):
        """Returns the underlying SHSA model."""
        return self.__model

    def greedy(self, node):
        """Search a substitute for the given node with greedy algorithm.

        Recursive implementation.

        Assumptions:
        - The given node must be of type `SHSANodeType.V`, i.e., a variable of
          the SHSA model.
        - Variables and relations alternate in the model, i.e., a variable node
          is only connected to relations and vice-versa.

        """
        print node
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

    def dfs(self, node):
        """Optimal substitute search for a given node (depth-first search).

        Recursive implementation.

        """
        assert("shsa.dfs not yet implemented")

    def dfs_next_solution(self, state=None):
        """Get next possible substitution path.

        Assumes dfs(..) is called before the first call, which initializes the
        state of the search (DFS variables).

        Search may be executed in parallel with bfs. For each relation, start a
        new process (see http://www.python-kurs.eu/forking.php) and execute the
        substitution.

        """
        found = False
        substitution_tree = {}
        # search for next possible substitution tree or until the search ends
        # (queue empty)
        while ~found and self.__bfs_queue:
            curnode = self.__bfs_queue[0]
            if self.__model.property_value_of(curnode, 'type') == SHSANodeType.RV:
                # TODO
                print "(RV)",
            print curnode
            # traverse the search tree
            self.__bfs_visited, self.__bfs_queue = bfs_next(
                self.__model.graph(), self.__bfs_visited, self.__bfs_queue)
        # check if the current tree is a valid substitution
        # TODO
        # calculate utility
        # TODO
        # update best substitute if necessary
        # TODO
        return self.__model
