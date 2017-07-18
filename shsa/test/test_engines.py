import unittest

from engine.shsa import SHSA
from engine.dfs import DepthFirstSearch
from engine.greedy import Greedy
from engine.particlefilter import ParticleFilter


class SHSAInitTestCase(unittest.TestCase):
    """Test cases to check initialization of the engine."""
    def test_init(self):
        engine = SHSA(configfile="test/model1.yaml")
        self.assertEqual(len(engine.model.nodes()), 14,
                         "incorrect number of vertices")


class SHSATestCase(unittest.TestCase):
    """Base class for all testcases below, simply executing substitution."""

    def setUp(self):
        self.__tc = None
        # default index mapping (only the given keys are allowed, the index is
        # subject to change)
        self.__tcidx = self.__tcindex_default();

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

    def substitute_dfs(self):
        """Returns testcase results of depth-first search."""
        if not self.testcases: # no testcases
            return
        results = []
        for i in range(len(self.testcases)):
            engine = DepthFirstSearch(
                configfile=self.testcases[i][self.tcindex['file']])
            S = engine.substitute(self.testcases[i][self.tcindex['root']])
            results.append(S)
        return results

    def substitute_pf(self):
        """Returns testcase results of particle filter."""
        if not self.__tc: # no testcases
            return
        results = []
        for i in range(len(self.testcases)):
            engine = ParticleFilter(
                configfile=self.testcases[i][self.tcindex['file']])
            S = engine.substitute(self.testcases[i][self.tcindex['root']])
            results.append(S)
        return results


class SHSAEnginesTestCase(SHSATestCase):
    """Tests substitution results."""

    def setUp(self):
        self.tcindex = {
            'file': 0,
            'root': 1,
            'result': 2,
        }
        self.testcases = [
            ("test/model1.yaml", 'root',
             frozenset([
                 frozenset(['t1']),
                 frozenset(['t2']),
                 frozenset(['t3']),
                 frozenset(['t1', 't4']),
                 frozenset(['t1', 't5']),
             ])),
            ("test/model2.yaml", 'a',
             frozenset([
                 frozenset(['r1']),
                 frozenset(['r1', 'r2']),
                 frozenset(['r1', 'r2', 'r5']),
                 frozenset(['r1', 'r3']),
                 frozenset(['r1', 'r3', 'r4']),
                 frozenset(['r1', 'r2', 'r3']),
                 frozenset(['r1', 'r2', 'r3', 'r4']),
                 frozenset(['r1', 'r2', 'r3', 'r5']),
                 frozenset(['r1', 'r2', 'r3', 'r4', 'r5']),
             ])),
            ("test/model2.yaml", 'b',
             frozenset([
                 frozenset(['r2']),
                 frozenset(['r2', 'r5']),
             ])),
            ("test/model2.yaml", 'c',
             frozenset([
                 frozenset(['r1']),
                 frozenset(['r1', 'r2']),
                 frozenset(['r1', 'r2', 'r5']),
                 frozenset(['r3']),
                 frozenset(['r3', 'r4']),
             ])),
            ("test/model2.yaml", 'f',
             frozenset([
                 frozenset(['r4']),
             ])),
            ("test/model3.yaml", 'a', frozenset([ frozenset(['r1']) ])),
            ("test/model3.yaml", 'd', frozenset([ frozenset(['r2']) ])),
            ("test/model3.yaml", 'g', frozenset([ frozenset(['r3']) ])),
            ("test/model3.yaml", 'j', frozenset([ frozenset(['r4']) ])),
            ("test/model3.yaml", 'l', frozenset([ frozenset(['r5']) ])),
        ]

    def __check_results(self, S, no):
        """Verifies results against output data."""
        self.assertEqual(len(S.relations()),
                         len(self.testcases[no][self.tcindex['result']]),
                         """number of substitution trees mismatch
                         (TC{})""".format(no))
        # check if all solution trees are in the results
        self.assertEqual(len(S.relations() \
                             & self.testcases[no][self.tcindex['result']]),
                        len(S.relations()),
                         """substitution result wrong (TC{})""".format(no))

    def test_dfs(self):
        results = self.substitute_dfs() # execute testcases
        for i in range(len(results)):
            self.__check_results(results[i], i)

    def test_pf(self):
        results = self.substitute_pf() # execute testcases
        for i in range(len(results)):
            self.__check_results(results[i], i)


class SHSAUtilityTestCase(SHSATestCase):
    """Check utility calculation works and best substitution is selected."""

    def setUp(self):
        self.tcindex = {
            'file': 0,
            'root': 1,
            'utility': 2,
        }
        self.testcases = [
            ("test/model_p1.yaml", 'a', 2),
        ]

    def __check_results(self, S, no):
        raise NotImplementedError("""Test case - TODO - check utility""")

    def test_dfs(self):
        results = self.substitute_dfs() # execute testcases
        for i in range(len(results)):
            self.__check_results(results[i], i)

    def test_pf(self):
        results = self.substitute_pf() # execute testcases
        for i in range(len(results)):
            self.__check_results(results[i], i)


class SHSAProvidedTestCase(SHSATestCase):
    """Test cases to show that SHSA substitution returns correct result depending
    on the provided variables.

    """

    def setUp(self):
        self.tcindex = {
            'file': 0,
            'root': 1,
            'result': 2,
        }
        self.testcases = [
            ("test/model_p1.yaml", 'a', frozenset([
                frozenset(['r1', 'r2']),
                frozenset(['r1', 'r2', 'r3', 'r4']),
            ])),
        ]

    def __check_results(self, S, no):
        # check if number of relations (that fulfil the requirements) match
        self.assertEqual(len(S.relations()),
                         len(self.testcases[no][self.tcindex['result']]),
                         """number of substitution trees mismatch
                         (TC{})""".format(no))
        # check if all solution trees are in the results
        self.assertEqual(len(S.relations() \
                             & self.testcases[no][self.tcindex['result']]),
                        len(S.relations()),
                         """substitution result wrong (TC{})""".format(no))

    def test_dfs(self):
        results = self.substitute_dfs() # execute testcases
        for i in range(len(results)):
            self.__check_results(results[i], i)

    def test_pf(self):
        results = self.substitute_pf() # execute testcases
        for i in range(len(results)):
            self.__check_results(results[i], i)


if __name__ == '__main__':
        unittest.main()
