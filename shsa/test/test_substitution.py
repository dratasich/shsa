import unittest
from graph.graph import Graph
from model.shsamodel import SHSAModel
from engine.shsa import SHSA

class SHSATestCase(unittest.TestCase):
    """Test cases to check basic requirements of the engine."""
    def test_init(self):
        engine = SHSA(configfile="test/test_substitution_m1.yaml")
        self.assertEqual(len(engine.model().nodes()), 14,
                         "incorrect number of vertices")

class SubstitutionTestCase(unittest.TestCase):
    """Test cases to show that SHSA substitution returns correct result.

    """

    def setUp(self):
        self.engine = SHSA(configfile="test/test_substitution_m1.yaml")

    def tearDown(self):
        self.engine = None

    def __check_substitution_results(self, u, t):
        self.assertEqual(len(u), len(t),
                         "number of utilities and trees mismatch")
        self.assertEqual(len(u), 5,
                         "does not return all possible substitution trees")
        # all transfer nodes adjacent to 'root' should be in at least one tree
        t1 = False
        t2 = False
        t3 = False
        for tree in t:
            t1 = t1 or ('t1' in tree)
            t2 = t2 or ('t2' in tree)
            t3 = t3 or ('t3' in tree)
        self.assertTrue(t1, "no substitution tree with 't1'")
        self.assertTrue(t2, "no substitution tree with 't2'")
        self.assertTrue(t3, "no substitution tree with 't3'")

    def test_dfs(self):
        """Test DFS with utilities.

        """
        u, t = self.engine.dfs('root')
        self.__check_substitution_results(u, t)

    def test_bfs(self):
        """Test BFS with utilities.

        """
        pass
        #v, t = self.engine.bfs('root')
        # example should give a number of possibilities
        # results have to be in order of BFS
        # TODO

    def test_greedy(self):
        """Test greedy search.

        """
        pass
        #v, t = self.engine.greedy('root')
        # example should give a number of possibilities
        # results have to be in order of BFS
        # TODO

    def test_pf(self):
        """Graph has to be searched for possibilities according to breadth-first
        search.

        """
        u, t = self.engine.particle_filter('root')
        self.__check_substitution_results(u, t)
        # check with PF specific search parameters
        pass
        # # keep only 20% of best particles
        # u, t = self.engine.particle_filter('root', best=0.2)
        # # lookahead of 2 transfer functions for better search
        # u, t = self.engine.particle_filter('root', lookahead=2)
