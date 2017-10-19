import unittest
import itertools

from engine.shsa import SHSA
from engine.orr import ORR
from engine.dfs import DepthFirstSearch
from engine.shpgsa import SHPGSA
from model.substitutionlist import SubstitutionList


class SHSAInitTestCase(unittest.TestCase):
    """Test cases to check initialization of the engine."""
    def test_init(self):
        engine = SHSA(configfile="test/model1.yaml")
        self.assertEqual(len(engine.model.nodes()), 14,
                         "incorrect number of vertices")


class SHSATestCase(unittest.TestCase):
    """Base class for all engine testcases, simply executing substitution.

    Testcases are set in sub-class to self.testcases. Testcases is a list of
    sequences, where each sequence field is defined by self.tcindex.

    """

    def setUp(self):
        self.__tc = None
        # default index mapping (only the given keys are allowed, the index is
        # subject to change)
        self.__tcidx = self.__tcindex_default()

    def tearDown(self):
        self.__tc = None
        self.__tcidx = None

    def __get_testcases(self):
        return self.__tc

    def __set_testcases(self, tc):
        self.__tc = tc

    testcases = property(__get_testcases, __set_testcases)
    """List of testcases as sequence of parameters."""

    def __tcindex_default(self):
        return {
            'file': 0,
            'root': 1
        }

    def __get_tcindex(self):
        return self.__tcidx

    def __set_tcindex(self, tcidx):
        # keys of the new dict 'tcidx' must contain the ones used in this class
        used = set(self.__tcindex_default().keys())
        set(used).issubset(set(tcidx.keys()))
        self.__tcidx = tcidx

    tcindex = property(__get_tcindex, __set_tcindex)
    """Map of parameters to index in testcase sequence."""

    # run testcases (methods below are called by subclass to execute testcases;
    # add a method for each new engine)

    def substitute_orr(self):
        """Returns testcase results of orr search."""
        if not self.testcases:  # no testcases
            return
        results = []
        for i in range(len(self.testcases)):
            engine = ORR(configfile=self.testcases[i][self.tcindex['file']])
            engine.substitute_init()
            _, tree = engine.substitute(
                self.testcases[i][self.tcindex['root']])
            S = SubstitutionList()
            if tree is not None:
                S.add_substitution([n for n in tree
                                    if engine.model.is_relation(n)])
                S.update(self.testcases[i][self.tcindex['root']],
                         model=engine.model)
            results.append(S)
        return results

    def substitute_dfs(self, substitute_provided=True):
        """Returns testcase results of depth-first search."""
        if not self.testcases:  # no testcases
            return
        results = []
        for i in range(len(self.testcases)):
            engine = DepthFirstSearch(
                configfile=self.testcases[i][self.tcindex['file']])
            S = engine.substitute(self.testcases[i][self.tcindex['root']],
                                  None, substitute_provided)
            # workaround for dfs start --
            # dfs cannot handle substitutions where the root node is already
            # provided (recursive implementation would cause double entries),
            # so we add the solution (empty substitution) manually
            root = self.testcases[i][self.tcindex['root']]
            if engine.model.is_variable(root) \
               and engine.model.provided([root]):
                S.add_substitution()  # add empty substitution
            # workaround for dfs done --
            results.append(S)
        return results

    def substitute_shpgsa(self):
        """Returns testcase results of SH-PGSA search."""
        if not self.testcases:  # no testcases
            return
        results = []
        for i in range(len(self.testcases)):
            engine = SHPGSA(
                configfile=self.testcases[i][self.tcindex['file']])
            while(engine.substitute(self.testcases[i][self.tcindex['root']])):
                pass
            S = engine.last_results()
            results.append(S)
        return results


if __name__ == '__main__':
        unittest.main()
