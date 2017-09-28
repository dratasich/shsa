"""Self-Healing by Structural Adaptation (SHSA) using a greedy algorithm to
find a substitute.

"""

from engine.shsa import SHSA
from engine.worker import Worker
from model.substitution import Substitution
from model.substitutionlist import SubstitutionList


class Greedy(SHSA):
    """Self-Healing by Structural Adaptation (SHSA) engine."""

    def __init__(self, model=None, graph=None, properties=None,
                 configfile=None):
        """Initializes the search engine."""
        super(Greedy, self).__init__(model, graph, properties, configfile)
        self.__W = None
        """Workers of substitute search."""
        self.__S = None
        """Saves the results of last search."""

    def substitute(self, node):
        """Search a substitute for the given node with greedy algorithm.

        Maintains a sorted list of workers, each proceeding to search along a
        substitution path. Continue search at worker with the highest utility.

        Non-recursive and anytime algorithm implementation.

        """
        # initialize (at first call of new search)
        if self.__W is None:
            assert self.model.is_variable(node), "Substitute variables only!"
            # init result
            self.__S = SubstitutionList()  # list of substitutions (results)
            self.__W = []  # list of workers
            # create first worker (empty substitution, start at root node)
            self.__W.append(Worker(Substitution(root=node, model=self.model),
                                   variables=[node]))
        # work on with best worker (keep W sorted w.r.t. utility)
        while len(self.__W) > 0:
            while self.__W[0].has_next():
                wnew = self.__W[0].next()
                # insertion sort
                for w in wnew:
                    i = 0
                    while i < len(self.__W):
                        if w.utility < self.__W[i].utility:
                            i = i + 1
                            continue
                        else:
                            break
                    self.__W.insert(i, w)
            # current best worker done
            w = self.__W.pop(0)
            if w.successful():
                # add worker's substitution to results
                self.__S.append(w.substitution)
                return w.substitution
        # finally cleanup workers and return no solution
        self.__W = None
        return None

    def last_results(self):
        """Returns results of last substitution."""
        return self.__S
