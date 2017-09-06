"""Substitution worker.

Proceeds along a specific substitution tree to find a possible substitution.

A variable node in the SHSA model may have more than one relation. Instead of
chosing a specific relation, i.e., fixing the substitution path, a worker for
each possible relation is created.

A worker is defined by the substitution, i.e., a list of chosen relation nodes,
and the nodes where to proceed (or relations lastly added), i.e., the queue of
nodes to proceed.

"""

import itertools
import copy

from model.substitution import Substitution


class Worker(object):
    """Worker class."""

    def __init__(self, substitution, variables=[], relations=[]):
        """Initializes the worker."""
        if substitution is None:
            raise RuntimeError("A new worker must have a substitution.")
        self.__sub = substitution
        """Substitution path."""
        self.__sub_last = copy.deepcopy(substitution)
        """Last substitution path (used for new workers)."""
        self.__model = self.__sub.model
        """SHSA model (extracted for convinience)."""
        self.__utility_fct = substitution.utility_fct
        """Utility function (extracted for convinience)."""
        if len(variables) == 0 and len(relations) == 0:
            raise RuntimeError("A new worker must have nodes to continue.")
        for v in variables:
            if not substitution.model.is_variable(v):
                raise RuntimeError("{} is not a variable.".format(v))
        for (v, r) in relations:
            if not (substitution.model.is_variable(v)
                    and substitution.model.is_relation(r)):
                raise RuntimeError("({},{}) wrong node type.".format(v, r))
        self.__vars = self.__model.unprovided(variables)
        """Queue of variables, i.e., variables to proceed."""
        self.__rels = relations
        """Queue of relations, i.e., relations to proceed."""
        # do not use self.utility (still initializing)
        self.__utility = substitution.utility_fct.best()
        """Utility of the worker (maintained utility of the underlying
        substitution)."""
        if len(substitution) > 0:
            self.__utility = substitution.utility

    def __set_utility(self, u):
        if len(self.__sub) > 0:
            assert abs(self.__sub.utility - u) < 0.000001, \
                """Utility not properly maintained ({} !=
                {})!""".format(self.__sub.utility, u)
        self.__utility = u

    def __get_utility(self):
        """Returns utility including pending relations."""
        # not yet added relations
        u = self.__utility
        for (v, r) in self.__rels:
            ur = self.__utility_fct.utility_of_relation(self.__model, r, v)
            u = self.__utility_fct.add(u, ur)
        return u

    utility = property(__get_utility, __set_utility)
    """Utility of the worker."""

    def __get_substitution(self):
        return self.__sub

    substitution = property(__get_substitution)

    def __add(self, r, u):
        # update underlying substitution first, such that utility will fit (and
        # assertion is not triggered in __set_utility
        self.__sub.append(r)
        # use internal variable self.__utility, because self.utility returns
        # utiltity of pending relations added
        self.utility = self.__utility_fct.add(self.__utility, u)

    def has_next(self):
        """Returns true if the substitution is valid, i.e., done.

        If there are relations to continue, the variables are extracted. If no
        variables to proceed, this worker is done.

        """
        if len(self.__rels) > 0:
            self.__next_variables()
        if len(self.__vars) > 0:
            return True
        return False

    def __next_variables(self):
        """Creates pending variables from relations queue (relations queue is
        reset)."""
        # abort, if there are still variables to proceed
        if len(self.__vars) > 0:
            raise RuntimeWarning("Some variables are still remaining.")
            return
        # abort, if there are no relations to proceed
        if len(self.__rels) == 0:
            raise RuntimeWarning("No more relations to continue.")
            return
        # v .. variable root of relation, r .. relation
        vnext = []  # successor variables
        for v, r in self.__rels:
            # update substitution and utility
            u = self.__utility_fct.utility_of_relation(self.__model, r, v)
            self.__add(r, u)
            # collect successor variables
            vnext.extend(set(self.__model.predecessors(r)) - set([v]))
        # update queues
        self.__vars = self.__model.unprovided(vnext)
        self.__rels = []

    def next(self):
        """Continue with the substitution path with one step.

        Proceeds to the next variables. First the best relation of unprovided
        variables in self.__vars are selected to add up to the substitution of
        this worker. From the remaining possible relations new workers are
        created.

        """
        # abort, if queues are empty
        if not self.has_next():
            return []
        # choose relations
        rrest = {}  # collect other possible relations
        vnext = []  # next variables w.r.t. selected relations
        for v in self.__vars:
            assert not self.__model.provided([v]), """only vars that are
            unprovided will be continued"""
            # select best relation and create workers for others
            rbest = None
            ubest = 0
            rset = set(self.__model.predecessors(v)) - self.__sub.relations()
            for r in rset:
                # utility of this relation
                u = self.__utility_fct.utility_of_relation(self.__model, r, v)
                # update best relation
                if u > ubest:
                    rbest = r
                    ubest = u
            # add relation and its variables
            vnext.extend(set(self.__model.predecessors(rbest)) - set([v]))
            # update substitution and utility
            self.__add(rbest, ubest)
            # collect remaining relations (for additional workers)
            rrest[v] = rset - set([rbest])
        # save (and filter) next variables to continue
        # provided? remove the variable from the list, to stop continuing from
        # this variable
        self.__vars = self.__model.unprovided(vnext)
        # additional workers for relations that are not handled in this worker
        w = self.__create_workers(rrest)
        # update substitution setting for next round
        self.__sub_last = copy.deepcopy(self.__sub)
        return w

    def __create_workers(self, relations):
        w = []
        # create combinations of variable's relations
        rcombs = itertools.product(*relations.values())
        for rc in rcombs:
            # save list of sequences (v, r) (variable root and relation, such
            # that worker knows where the relation comes from)
            # ASSUMPTION: dictionary stays ordered between relations.values()
            # and relations.keys() call
            R = list(zip(list(relations.keys()), list(rc)))
            w.append(Worker(copy.deepcopy(self.__sub_last), relations=R))
        return w

    def __str__(self):
        s = "Worker: " + self.__sub.__str__()
        if len(self.__rels) > 0:
            s += " | pending relations: " + str(self.__rels)
        elif len(self.__vars) > 0:
            s += " | pending variables: " + str(self.__vars)
        else:
            s += " | done"
        return s
