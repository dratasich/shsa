import unittest
import itertools

from test.test_engines import SHSATestCase
from engine.shpgsa import SHPGSA


class SHSABestTestCase(SHSATestCase):
    """Tests engines, that can return the globally optimal substitution."""

    def setUp(self):
        self.tcindex = {
            'file': 0,
            'root': 1,
            'best': 2,
        }
        self.testcases = [
            ("test/model1.yaml", 'root', {'t2'}),
            ("test/model2.yaml", 'a', set()),
            ("test/model3.yaml", 'a', {'r1'}),
            ("test/model3.yaml", 'd', {'r2'}),
            ("test/model4.yaml", 'a', {'r1', 'r2'}),
            ("test/model_p1.yaml", 'a', {'r1', 'r2'}),
            ("test/model_p1.yaml", 'c', set()),
            ("test/model_p2.yaml", 'a', {'r2'}),
            ("test/model_p3.yaml", 'a', {'r1'}),
        ]

    def __check_results(self, S, no):
        """Verify if the returned result is the best substitution."""
        self.assertEqual(S.best().relations(),
                         self.testcases[no][self.tcindex['best']],
                         """best substitution wrong (TC{})""".format(no))

    def test_shpgsa(self):
        results = self.substitute_shpgsa()  # execute testcases
        for i in range(len(results)):
            self.__check_results(results[i], i)

    def test_dfs(self):
        results = self.substitute_dfs()  # execute testcases
        for i in range(len(results)):
            self.__check_results(results[i], i)


if __name__ == '__main__':
        unittest.main()
