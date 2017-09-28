"""Experiments for IPSN paper."""

from profilehooks import profile, timecall
import argparse

from model.shsamodel import SHSAModel
from model.substitutionlist import SubstitutionList
from engine.orr import ORR
from engine.dfs import DepthFirstSearch
from engine.greedy import Greedy


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
    S = engine.substitute(root)
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
def rss(model, root):
    engine = Greedy(model)
    while(engine.substitute(root)):
        pass
    S = engine.last_results()
    return S


class Benchmark(object):

    def __init__(self, model=None, root=None):
        self._model = model
        self._root = root
        self._parser = argparse.ArgumentParser(description="""Experiment 1.""")
        self.__parse_args()  # register arguments
        self.__args = self._parser.parse_args()

    def __parse_args(self):
        self._parser.add_argument('-n', '--ncalls', type=int, default=10,
                                  help="Number of substitute-calls.")

    def setup(self):
        raise NotImplementedError

    def run(self):
        """Execute all engines under test n times."""
        S = {}
        for i in range(self.__args.ncalls):
            S['orr'] = orr(self._model, self._root)
        for i in range(self.__args.ncalls):
            S['dfs'] = dfs(self._model, self._root)
        for i in range(self.__args.ncalls):
            S['rss'] = rss(self._model, self._root)
        # check if the best result is the same
        print("rss: {}".format(S['rss']))
        for k, v in S.items():
            if v is not None and \
               S['rss'].best().relations() != v.best().relations():
                print("mismatch")
                print("{}: {}".format(k, v))
