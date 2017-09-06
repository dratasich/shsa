import unittest
import itertools

from test.test_engines import SHSATestCase
from engine.dfs import DepthFirstSearch


class SHSADFSTestCase(SHSATestCase):
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
                 frozenset([]),
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
                 frozenset([]),
                 frozenset(['r2']),
                 frozenset(['r2', 'r5']),
             ])),
            ("test/model2.yaml", 'c',
             frozenset([
                 frozenset([]),
                 frozenset(['r1']),
                 frozenset(['r1', 'r2']),
                 frozenset(['r1', 'r2', 'r5']),
                 frozenset(['r3']),
                 frozenset(['r3', 'r4']),
             ])),
            ("test/model2.yaml", 'f',
             frozenset([
                 frozenset([]),
                 frozenset(['r4']),
             ])),
            ("test/model3.yaml", 'a', frozenset([frozenset(['r1'])])),
            ("test/model3.yaml", 'd', frozenset([frozenset(['r2'])])),
            ("test/model3.yaml", 'g', frozenset([frozenset(['r3'])])),
            ("test/model3.yaml", 'j', frozenset([frozenset(['r4'])])),
            ("test/model3.yaml", 'l', frozenset([frozenset(['r5'])])),
        ]

    def __check_results(self, S, no):
        """Verifies results against output data."""
        self.assertEqual(len(S.relations()),
                         len(self.testcases[no][self.tcindex['result']]),
                         """number of substitution trees mismatch
                         (TC{})""".format(no))
        # check if all solution trees are in the results
        self.assertEqual(len(S.relations()
                             & self.testcases[no][self.tcindex['result']]),
                         len(S.relations()),
                         """substitution result wrong (TC{})""".format(no))
        # no double entries
        for x, y in itertools.combinations(S, 2):
            self.assertNotEqual(set(x), set(y),
                                "double entries in result (TC{})".format(no))

    def test_dfs(self):
        results = self.substitute_dfs()  # execute testcases
        for i in range(len(results)):
            self.__check_results(results[i], i)


class SHSADFSUtilityTestCase(SHSATestCase):
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
        pass
        # TODO: check utility

    def test_dfs(self):
        results = self.substitute_dfs()  # execute testcases
        for i in range(len(results)):
            self.__check_results(results[i], i)


class SHSADFSProvidedTestCase(SHSATestCase):
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
        self.assertEqual(len(S.relations()
                             & self.testcases[no][self.tcindex['result']]),
                         len(S.relations()),
                         """substitution result wrong (TC{})""".format(no))

    def test_dfs(self):
        results = self.substitute_dfs()  # execute testcases
        for i in range(len(results)):
            self.__check_results(results[i], i)


if __name__ == '__main__':
        unittest.main()
