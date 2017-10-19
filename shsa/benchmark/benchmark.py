"""Experiments for IPSN paper."""

from profilehooks import profile, timecall
import argparse

from model.shsamodel import SHSAModel
from model.substitutionlist import SubstitutionList
from engine.orr import ORR
from engine.dfs import DepthFirstSearch
from engine.shpgsa import SHPGSA


@timecall(immediate=False)
def orr(model, root):
    engine = ORR(model)
    engine.substitute_init()
    _, tree = engine.substitute(root)
    S = SubstitutionList()
    S.add_substitution([n for n in tree if model.is_relation(n)])
    S.update(root, model=model)
    return S


@timecall(immediate=False)
def dfs(model, root):
    engine = DepthFirstSearch(model)
    S = engine.substitute(root, substitute_provided=False,
                          check_requirements=False)
    # workaround for dfs start --
    # dfs cannot handle substitutions where the root node is already
    # provided (recursive implementation would cause double entries),
    # so we add the solution (empty substitution) manually
    if engine.model.is_variable(root) \
       and engine.model.provided([root]):
        S.add_substitution()  # add empty substitution
    # workaround for dfs done --
    # check requirements
    S.update(root, model)
    new = list(filter(lambda s: s.requirements_ok(), S))
    S = SubstitutionList(new)
    return S


@timecall(immediate=False)
def dfs_mem(model, root):
    engine = DepthFirstSearch(model)
    S = engine.substitute(root, substitute_provided=False,
                          check_requirements=True)
    # workaround for dfs start --
    # dfs cannot handle substitutions where the root node is already
    # provided (recursive implementation would cause double entries),
    # so we add the solution (empty substitution) manually
    if engine.model.is_variable(root) \
       and engine.model.provided([root]):
        S.add_substitution()  # add empty substitution
    # workaround for dfs done --
    return S


@timecall(immediate=False)
def shpgsa(model, root):
    engine = SHPGSA(model)
    while(engine.substitute(root)):
        pass
    S = engine.last_results()
    return S


@timecall(immediate=False)
def shpgsa_once(model, root):
    engine = SHPGSA(model)
    engine.substitute(root)
    S = engine.last_results()
    return S


class Benchmark(object):

    def __init__(self, model=None, root=None):
        self._model = model
        self._root = root
        self._parser = argparse.ArgumentParser(description="""Experiment 1.""")
        self._parse_args()  # register arguments
        self._args = self._parser.parse_args()
        self._results = {}
        self._failed = False

    def __get_model(self):
        return self._model

    def __set_model(self, model):
        self._model = model

    model = property(__get_model, __set_model)

    def _parse_args(self):
        self._parser.add_argument('-n', '--ncalls', type=int, default=10,
                                  help="Number of substitute-calls.")

    def setup(self):
        raise NotImplementedError

    def check(self, algorithms=[]):
        raise NotImplementedError

    def run(self, algorithms=['dfs', 'dfs_mem', 'shpgsa', 'orr',
                              'shpgsa_once']):
        """Execute all engines under test n times."""
        try:
            if 'dfs' in algorithms:
                for i in range(self._args.ncalls - 1):
                    dfs(self._model, self._root)
                self._results['dfs'] = dfs(self._model, self._root)
            if 'dfs_mem' in algorithms:
                for i in range(self._args.ncalls - 1):
                    dfs_mem(self._model, self._root)
                self._results['dfs_mem'] = dfs_mem(self._model, self._root)
            if 'shpgsa' in algorithms:
                for i in range(self._args.ncalls - 1):
                    shpgsa(self._model, self._root)
                self._results['shpgsa'] = shpgsa(self._model, self._root)
            if 'orr' in algorithms:
                for i in range(self._args.ncalls - 1):
                    orr(self._model, self._root)
                self._results['orr'] = orr(self._model, self._root)
            if 'shpgsa_once' in algorithms:
                for i in range(self._args.ncalls - 1):
                    shpgsa_once(self._model, self._root)
                self._results['shpgsa_once'] = shpgsa_once(self._model,
                                                           self._root)
        except Exception as e:
            self._failed = True
            raise
        # group the algorithms for comparison
        g1 = set(['dfs', 'dfs_mem', 'shpgsa']) & set(algorithms)
        g2 = set(['orr', 'shpgsa_once']) & set(algorithms)
        return [list(g1), list(g2)]
