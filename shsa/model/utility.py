"""Utility functions."""

import networkx as nx


class Utility(object):
    """Base class for all utility functions."""

    def __init__(self):
        pass

    def utility_of_relation(self, model, r, v):
        pass

    def utility_of_substitution(self, s):
        pass

    def best(self):
        pass

    def add(self, u1, u2):
        pass


class UtilityNorm(Utility):
    """Normalized utility."""

    def utility_of_relation(self, model, r, v):
        """Returns the utility of a relation node r that should substitute the
        given variable v.

        Utility depends on the variable to substitute (v). Relations may be
        executed in a specific direction, i.e, the input nodes change,
        consequently, also the properties change, which influence the utility
        (e.g., sample rate).

        The properties of relations may differ, hence only the available ones
        are included in calculation.

        """
        # input variables for relation
        rin = set(model.predecessors(r)) - set([v])
        # relation should have at least one predecessor (i.e., be connected)
        assert len(rin) >= 1, """relation node {} must be connected to
        variable(s)""".format(r)
        # utility function by weighted sum
        w = [
            1,
            0.5,
            0.1,
        ]
        u = [1.0] * len(w)
        # only one node, perfect; the more nodes, the worse
        u[0] = 1.0 / len(rin)
        # penalize computational costs (cost > 0, penalizes more relations)
        if model.has_property(r, 'cost'):
            u[1] = 1.0 / model.property_value_of(r, 'cost')
        else:
            u[1] = 1
        # penalize unprovided variables (penalizes more relations too)
        u[2] = 1.0 / (len(model.unprovided(rin)) + 1)
        # penalize low sample rate (or difference to desired sample rate?)
        # penalize inaccuracy
        # weighted sum and normalize
        uf = sum([wi*ui for wi, ui in zip(w, u)]) / sum(w)
        assert uf >= 0 and uf <= 1, "utility not normalized"
        return uf

    def utility_of_substitution(self, s):
        """Returns the product of node-utilities.

        Utility of a node depends on the tree structure (execution direction of
        relations from root node) and the input variables (e.g., sample rate).

        """
        # empty substitution is also fine
        if len(s) == 0:
            return self.best()
        # get substitution tree with intermediate variables (for utility
        # calculation we need the predecessor variables for relations)
        t, vin = s.tree(collapse_variables=False)
        t = t.to_undirected()  # ignore direction
        # get all predecessors (by bfs)
        pre = nx.bfs_predecessors(t, s.root)
        # product of utilities (of all relations given their predecessors)
        u = 1.0
        for r in s:
            ui = self.utility_of_relation(s.model, r, pre[r])
            assert ui >= 0 and ui <= 1, "Utility must be normalized!"
            u = self.add(u, ui)
        return u

    def best(self):
        """Returns best utility, i.e., initial of an empty substitution."""
        return 1.0

    def add(self, u1, u2):
        """Adds up utilities, and returns the result.

        Defines how the utilities are added up in a substitution (e.g., sum
        vs. product).

        """
        return u1 * u2
