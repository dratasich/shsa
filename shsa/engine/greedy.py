"""Self-Healing by Structural Adaptation (SHSA) using a greedy algorithm to
find a substitute.

"""

from engine.shsa import SHSA
from engine.worker import Worker
from model.substitution import Substitution
from model.substitutionlist import SubstitutionList


class Greedy(SHSA):
    """Self-Healing by Structural Adaptation (SHSA) engine."""

    def __init__(self, graph=None, properties=None, configfile=None):
        """Initializes the search engine."""
        super(Greedy, self).__init__(graph, properties, configfile)

    def substitute(self, node, lastnode=None):
        """Search a substitute for the given node with greedy algorithm.

        Maintains a sorted list of workers, each proceeding to search along a
        substitution path. Continue search at worker with the highest utility.

        Non-recursive implementation.

        Can be implemented as anytime algorithm.

        Assumptions:
        - The given node must be of type `SHSANodeType.V`, i.e., a variable of
          the SHSA model.
        - Variables and relations alternate in the model, i.e., a variable node
          is only connected to relations and vice-versa.

        """
        assert self.model.is_variable(node), "Substitute variables only!"
        # init result
        S = SubstitutionList()  # list of substitutions (results)
        W = []  # list of workers
        # create first worker (empty substitution, start at root node)
        W.append(Worker(Substitution(root=node, model=self.model),
                        variables=[node]))
        # work on with best worker (keep W sorted w.r.t. utility)
        while len(W) > 0:
            while W[0].has_next():
                wnew = W[0].next()
                # insertion sort
                for w in wnew:
                    for i in range(len(W)):
                        if w.utility < W[i].utility:
                            W.insert(i, w)
            # current best worker done, but we move on to find better
            # solutions (we could here return an intermediate result)
            # remove finished worker from list
            w = W.pop(0)
            # add worker's substitution to results
            S.append(w.substitution)
        # all solutions found
        return S
