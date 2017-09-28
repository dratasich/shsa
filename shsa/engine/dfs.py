"""Self-Healing by Structural Adaptation (SHSA) using classic depth-first
search to find substitutes.

"""

import itertools

from engine.shsa import SHSA
from model.shsamodel import SHSAModel, SHSANodeType
from model.substitutionlist import SubstitutionList
from model.substitution import Substitution


class DepthFirstSearch(SHSA):
    """Self-Healing by Structural Adaptation (SHSA) engine."""

    def __init__(self, model=None, graph=None, properties=None,
                 configfile=None):
        """Initializes the search engine."""
        super(DepthFirstSearch, self).__init__(model, graph, properties,
                                               configfile)

    def substitute(self, node, lastnode=None):
        """Returns all possible substitutes, via DFS.

        Recursive implementation.

        Returns: Possible substitutions.

        Possible improvements:
        - save solution, globally, as soon as available (anytime algorithm)

        """
        # init
        S = SubstitutionList()  # empty
        solutions = []  # list of substitution lists of adjacents
        # move on, but do not go back where we came from
        adjacents = set(self.model.predecessors(node)) - set([lastnode])
        # save solution of each adjacent separately
        for n in adjacents:
            s = self.substitute(n, node)
            if len(s) > 0:
                solutions.append(s)
        # depending on the type of node the solutions are combined or added
        if self.model.is_relation(node):
            # create combinations (take not / take for each adjacent)
            combs = list(itertools.product([0, 1], repeat=len(solutions)))
            for c in combs:
                # apply combination
                combsol = list(itertools.compress(solutions, c))
                if len(combsol) == 0:  # taking none is also possible
                    S.add_substitution()  # add empty one
                else:
                    # because these are lists, we have to create the product
                    # again to combine the individual substitution elements
                    combs2 = list(itertools.product(*combsol))
                    for c2 in combs2:
                        # merge substitutions from the combination
                        combsub = itertools.chain.from_iterable(c2)
                        S.append(Substitution(combsub,
                                              model=self.model, root=node))
            # add current relation node to all substitutions
            S.add_node_to(node)
            # root node (= last variable node) will/must be updated before
            # checking requirements
            S.update(lastnode, self.model)
            # filter the substitutions that fulfil the requirements
            new = list(filter(lambda s: s.requirements_ok(), S))
            S = SubstitutionList(new)
        elif self.model.is_variable(node):
            # simply add returned solutions
            for s in solutions:
                S.extend(s)
        # return substitutes from this node on
        return S
