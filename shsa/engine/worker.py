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
import warnings

from model.substitution import Substitution


class Worker(Substitution):
    """Worker class."""

    def __init__(self, *args, **kwargs):
        """Initializes the worker."""
        # defaults
        # do not use self.utility (still initializing)
        self.__utility = 1.0  # self.utility_fct.best()
        """Utility of the worker (maintained utility of the underlying
        substitution)."""
        self.__vars = []
        """Queue of variables, i.e., variables to proceed."""
        self.__rels = []
        """Queue of relations, i.e., relations to proceed."""
        self.__rels_u = []
        """Utility of queue of relations."""
        # extract worker parameters
        if 'utility' in kwargs.keys():
            self.__utility = kwargs['utility']
            del kwargs['utility']
        if 'variables' in kwargs.keys():
            self.__vars = kwargs['variables']
            del kwargs['variables']
        if 'relations' in kwargs.keys():
            self.__rels = kwargs['relations']
            del kwargs['relations']
        if 'relations_u' in kwargs.keys():
            self.__rels_u = kwargs['relations_u']
            del kwargs['relations_u']
        # initialize substitution
        super(Worker, self).__init__(*args, **kwargs)
        # sanity check of parameters
        if len(self.__vars) == 0 and len(self.__rels) == 0:
            raise RuntimeError("A new worker must have nodes to continue.")
        for v in self.__vars:
            if not self.model.is_variable(v):
                raise RuntimeError("{} is not a variable.".format(v))
        for (v, r) in self.__rels:
            if not (self.model.is_variable(v)
                    and self.model.is_relation(r)):
                raise RuntimeError("({},{}) wrong node type.".format(v, r))
        # filter, to substitute only unprovided variables
        self.__vars = self.model.unprovided(self.__vars)
        self.__failed = False
        """True, if worker failed (reached unprovided leafs)."""

    def __set_utility(self, u):
        if len(self) > 0:
            assert abs(super(Worker, self).utility - u) < 0.000001, \
                """Utility not properly maintained ({} !=
                {})!""".format(super(Worker, self).utility, u)
        self.__utility = u

    def __get_utility(self):
        """Returns utility including pending relations."""
        # not yet added relations
        u = self.__utility
        for (v, r) in self.__rels:
            ur = self.utility_fct.utility_of_relation(self.model, r, v)
            u = self.utility_fct.add(u, ur)
        return u

    utility = property(__get_utility, __set_utility)
    """Utility of the worker."""

    def __add(self, r, u):
        # update underlying substitution first, such that utility will fit (and
        # assertion is not triggered in __set_utility
        self.append(r)
        # use internal variable self.__utility, because self.utility returns
        # utiltity of pending relations added
        self.utility = self.utility_fct.add(self.__utility, u)

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
            # update substitution (utility should be added already)
            self.append(r)
            # collect successor variables
            vnext.extend(set(self.model.predecessors(r)) - set([v]))
        # update queues
        self.__vars = self.model.unprovided(vnext)
        self.__rels = []

    def next(self):
        """Continue with the substitution path with one step.

        Proceeds to the next variables. First the best relation of unprovided
        variables in self.__vars are selected to add up to the substitution of
        this worker. From the remaining possible relations params for new
        workers are created.

        """
        # abort, if queues are empty
        if not self.has_next():
            return []
        # choose relations
        rpick = {}  # collect best relation per variable
        rpick_u = {}  # collect utility of best relation per variable
        rall = {}  # collect all possible relations per variable
        rall_u = {}  # collect utility of all possible relations per variable
        vnext = []  # next variables w.r.t. selected relations
        for v in self.__vars:
            assert not self.model.provided([v]), """only vars that are
            unprovided will be continued"""
            # select best relation
            rbest = None
            ubest = 0
            # get possible relations
            rset = set(self.model.predecessors(v)) - self.relations()
            # no adjacent relations although unprovided variable
            if len(rset) == 0:
                # stop worker immediately and forever
                self.__mark_as_failed()  # clears queue
                return []
            # identify best relation (highest utility)
            for r in rset:
                # utility of this relation
                u = self.utility_fct.utility_of_relation(self.model, r, v)
                # save for other workers (performance)
                rall_u[(v, r)] = u
                # update best relation
                if u > ubest:
                    rbest = r
                    ubest = u
            # collect all relations (for additional workers)
            rpick[v] = rbest
            rpick_u[v] = ubest
            rall[v] = rset
        # additional workers for relations that are not handled in this worker
        w = self.__create_worker_params(rall, rall_u, rpick)
        # update current worker
        for v in self.__vars:
            # add the chosen relation's variables
            vnext.extend(set(self.model.predecessors(rpick[v])) - set([v]))
            # update substitution and utility
            self.__add(rpick[v], rpick_u[v])
        # save (and filter) next variables to continue
        # provided? remove the variable from the list, to stop continuing from
        # this variable
        self.__vars = self.model.unprovided(vnext)
        return w

    def __create_worker_params(self, relations, relations_u, chosen):
        w = []
        # create combinations of variable's relations
        rcombs = itertools.product(*relations.values())
        # create worker for remaining combinations
        for rc in rcombs:
            # skip already selected relations
            if set(rc) == set(chosen.values()):
                continue
            # save parameters for new workers: utility, relations, pending
            # relations = list of tuples (v, r) (variable root and relation,
            # such that worker knows where the relation comes from)
            # ASSUMPTION: dictionary stays ordered between relations.values()
            # and relations.keys() call
            R = list(zip(relations.keys(), list(rc)))
            U = self.__utility
            for r in R:
                U = self.utility_fct.add(U, relations_u[r])
            wnew = U, list(self), R
            w.append(wnew)
        return w

    def __mark_as_failed(self):
        self.__failed = True
        # do not continue (has_next should fail)
        self.__vars = []
        self.__rels = []

    def successful(self):
        if self.__failed:
            return False
        if not self.requirements_ok():
            return False
        return True

    def __str__(self):
        s = "Worker: " + super(Worker, self).__str__()
        if len(self.__rels) > 0:
            s += " | pending relations: " + str(self.__rels)
        elif len(self.__vars) > 0:
            s += " | pending variables: " + str(self.__vars)
        elif self.__failed:
            s += " | failed"
        else:
            s += " | done"
        return s
