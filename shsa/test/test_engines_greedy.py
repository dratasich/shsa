import unittest
import itertools

from test.test_engines import SHSATestCase
from engine.greedy import Greedy


class SHSAGreedyTestCase(SHSATestCase):
    """Tests substitution results of greedy search."""

    def setUp(self):
        self.tcindex = {
            'file': 0,
            'root': 1,
            'result': 2,
        }
        self.testcases = [
            ("test/model1.yaml", 'root', frozenset(['t2'])),
            ("test/model2.yaml", 'a', frozenset([])),
            ("test/model3.yaml", 'a', frozenset(['r1'])),
            ("test/model3.yaml", 'd', frozenset([])),
            ("test/model_p1.yaml", 'a', frozenset(['r1', 'r2'])),
        ]

    def __check_results(self, S, no):
        """Verifies results against output data."""
        self.assertEqual(len(S), 1,
                         """greedy must return exactly one result
                         (TC{})""".format(no))
        # check if the solution is the best one
        self.assertEqual(S[0].relations()
                         & self.testcases[no][self.tcindex['result']],
                         S[0].relations(),
                         """substitution result wrong (TC{})""".format(no))

    def test_greedy(self):
        results = self.substitute_greedy()  # execute testcases
        for i in range(len(results)):
            self.__check_results(results[i], i)


if __name__ == '__main__':
        unittest.main()
