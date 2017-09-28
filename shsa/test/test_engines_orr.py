import unittest
import itertools

from test.test_engines import SHSATestCase


class SHSAORRTestCase(SHSATestCase):
    """Tests substitution results of ORR search."""

    def setUp(self):
        self.tcindex = {
            'file': 0,
            'root': 1,
            'result': 2,
            'success': 3,
        }
        self.testcases = [
            ("test/model1.yaml", 'root', None, True),
            ("test/model2.yaml", 'a', frozenset([]), True),
            ("test/model3.yaml", 'a', frozenset(['r1']), True),
            ("test/model3.yaml", 'd', frozenset(['r2']), True),
            ("test/model_p1.yaml", 'a', frozenset(['r1', 'r2']), True),
            ("test/model_p3.yaml", 'c', set(), True),
            ("test/model_p4.yaml", 'root', set(['r5', 'r4', 'r1']), True),
            ("test/model_p6.yaml", 'a', frozenset(['r1', 'r2']), True),
        ]

    def __check_results(self, S, no):
        """Verifies results against output data."""
        # check if the solution is the best one
        success = True
        if S.best() is None:
            success = False
        if success and self.testcases[no][self.tcindex['result']] is not None:
            self.assertEqual(S.best().relations(),
                             self.testcases[no][self.tcindex['result']],
                             """substitution result wrong (TC{})""".format(no))
        # test success
        self.assertEqual(success,
                         self.testcases[no][self.tcindex['success']],
                         """success state mismatch (TC{})""".format(no))

    def test_orr(self):
        results = self.substitute_orr()  # execute testcases
        for i in range(len(results)):
            self.__check_results(results[i], i)


if __name__ == '__main__':
        unittest.main()
