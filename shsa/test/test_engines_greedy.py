import unittest
import itertools

from test.test_engines import SHSATestCase
from engine.shpgsa import SHPGSA


class SHSAPGTestCase(SHSATestCase):
    """Tests substitution results of SH-PGSA search."""

    def setUp(self):
        self.tcindex = {
            'file': 0,
            'root': 1,
            'result': 2,
            'success': 3,
        }
        self.testcases = [
            ("test/model1.yaml", 'root', frozenset(['t2']), True),
            ("test/model2.yaml", 'a', frozenset([]), True),
            ("test/model3.yaml", 'a', frozenset(['r1']), True),
            ("test/model3.yaml", 'd', frozenset(['r2']), True),
            ("test/model_p1.yaml", 'a', frozenset(['r1', 'r2']), True),
            ("test/model_p3.yaml", 'c', set(), True),
            ("test/model_p4.yaml", 'root', set(['r2']), True),
            ("test/model_p5.yaml", 'a', set(), False),
            ("test/model_p6.yaml", 'a', frozenset(['r1', 'r2']), True),
        ]

    def __check_results(self, S, no):
        """Verifies results against output data."""
        # check if the solution is the best one
        success = True
        if S.best() is None:
            success = False
        if success:
            self.assertEqual(S.best().relations(),
                             self.testcases[no][self.tcindex['result']],
                             """substitution result wrong (TC{})""".format(no))
        # test success
        self.assertEqual(success,
                         self.testcases[no][self.tcindex['success']],
                         """success state mismatch (TC{})""".format(no))

    def test_shpgsa(self):
        results = self.substitute_shpgsa()  # execute testcases
        for i in range(len(results)):
            self.__check_results(results[i], i)


if __name__ == '__main__':
        unittest.main()
