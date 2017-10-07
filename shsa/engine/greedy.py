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
        """Active workers of substitute search."""
        self.__Wp = []
        """Parameters of potential workers, sorted by utility.

        List of sequences (initial utility incl. utility of pending relations,
        relations, pending relations (v, r)).

        """
        self.__S = None
        """Saves the results of last search."""

    def __create_worker(self, node):
        if len(self.__W) == 0 and len(self.__Wp) > 0:
            u, r, rp = self.__Wp.pop(0)
            self.__W.append(Worker(r, root=node, model=self.model, utility=u,
                                   relations=rp))

    def substitute(self, node):
        """Search a substitute for the given node with greedy algorithm.

        Maintains a sorted list of potential workers. Once the utility of the
        current worker drops below the utility of a potential worker, the
        worker is instantiated. Continue search at worker with the highest
        utility.

        Non-recursive and anytime algorithm implementation.

        """
        # initialize (at first call of new search)
        if self.__W is None:
            assert self.model.is_variable(node), "Substitute variables only!"
            # init result
            self.__S = SubstitutionList()  # list of substitutions (results)
            self.__W = []  # list of workers
            # create first worker (empty substitution, start at root node)
            self.__W.append(Worker(root=node, model=self.model,
                                   variables=[node]))
        # instantiate new best worker (from potential list) if no one left
        else:
            self.__create_worker(node)
        # work on with best worker (keep W sorted w.r.t. utility)
        while len(self.__W) > 0:
            while self.__W[0].has_next():
                wnew = self.__W[0].next()
                # insertion sort / move (instantiated workers)
                # W[0].utility may have dropped below another running worker
                i = 0
                while i < len(self.__W):
                    if self.__W[0].utility < self.__W[i].utility:
                        i = i + 1
                        continue
                    else:
                        break
                if i > 0:  # move W[0]
                    w = self.__W.pop(0)
                    self.__W.insert(i, w)
                # insertion sort (potential workers)
                for w in wnew:
                    i = 0
                    while i < len(self.__Wp):
                        if w[0] < self.__Wp[i][0]:  # compare utility
                            i = i + 1
                            continue
                        else:
                            break
                    self.__Wp.insert(i, w)
                # create new worker if a potential one has better utility
                if len(self.__Wp) > 0 and \
                   self.__Wp[0][0] > self.__W[0].utility:
                    # create new worker
                    u, r, rp = self.__Wp.pop(0)
                    w = Worker(r, root=node, model=self.model, utility=u,
                               relations=rp)
                    self.__W.insert(0, w)
            # current best worker done
            w = self.__W.pop(0)
            if w.successful():
                # add worker's substitution to results
                self.__S.append(w)
                return w
            else:
                self.__create_worker(node)
        # finally cleanup workers and return no solution
        self.__W = None
        return None

    def last_results(self):
        """Returns results of last substitution."""
        return self.__S
