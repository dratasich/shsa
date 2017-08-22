"""Self-Healing by Structural Adaptation (SHSA) using a greedy algorithm to
find a substitute.

"""

from engine.shsa import SHSA
from model.shsamodel import SHSAModel, SHSANodeType
from model.substitutionlist import SubstitutionList
from model.substitution import Substitution


class Greedy(SHSA):
    """Self-Healing by Structural Adaptation (SHSA) engine."""

    def __init__(self, graph=None, properties=None, configfile=None):
        """Initializes the search engine."""
        super(Greedy, self).__init__(graph, properties, configfile)

    def substitute(self, node, lastnode=None):
        """Search a substitute for the given node with greedy algorithm.

        Recursive implementation.

        No anytime algorithm. Gives one - the best - solution with given
        utility function (multiplied utilities [0,1]).

        Assumptions:
        - The given node must be of type `SHSANodeType.V`, i.e., a variable of
          the SHSA model.
        - Variables and relations alternate in the model, i.e., a variable node
          is only connected to relations and vice-versa.

        """
        assert self.model.is_variable(node), "Substitute variables only!"
        # init result
        S = SubstitutionList()  # empty list
        S.add_substitution()  # add empty substitution
        S.update(root=node, model=self.model)
        # variable is provided, we can stop here (assumption: utility can get
        # only worse by adding relations)
        if self.model.provided([node]):
            return S
        # move on to relations, but do not go back where we came from
        relations = set(self.model.predecessors(node)) - set([lastnode])
        # get best relation choice
        u = 0.0
        rbest = None
        for r in relations:
            if self.model.utility_of(r) > u:
                u = self.model.utility_of(r)
                rbest = r
        # add best relation
        S[0].append(rbest)
        # substitute upcoming variables if necessary
        variables = set(self.model.predecessors(rbest)) - set([node])
        for v in variables:
            s = self.substitute(v, lastnode=rbest)
            # extend with relation nodes (returned in a list of substitutions)
            S[0].extend(s[0])
        # update root, because sub-solutions have different root nodes
        S.update(root=node)
        return S
