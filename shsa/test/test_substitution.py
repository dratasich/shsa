import unittest
from graph.graph import Graph
from model.shsamodel import SHSAModel
from engine.shsa import SHSA

class SHSATestCase(unittest.TestCase):
    """Test cases to check basic requirements of the engine."""
    def test_init(self):
        engine = SHSA(configfile="test/test_substitution_m1.yaml")
        self.assertEqual(len(engine.model().nodes()), 12,
                         "incorrect number of vertices")

class SubstitutionTestCase(unittest.TestCase):
    """Test cases to show that SHSA substitution returns correct result.

    """

    def setUp(self):
        self.engine = SHSA(configfile="test/test_substitution_m1.yaml")

    def tearDown(self):
        self.engine = None

    def test_dfs(self):
        """Test DFS with utilities.

        """
        v, t = self.engine.dfs('root')
        # example should give a number of possibilities
        # results have to be in order of BFS
        # TODO

    def test_bfs(self):
        """Test BFS with utilities.

        """
        v, t = self.engine.bfs('root')
        # example should give a number of possibilities
        # results have to be in order of BFS
        # TODO

    def test_greedy(self):
        """Test greedy search.

        """
        v, t = self.engine.greedy('root')
        # example should give a number of possibilities
        # results have to be in order of BFS
        # TODO

    def test_pf(self):
        """Graph has to be searched for possibilities according to breadth-first
        search.

        """
        v, t = self.engine.particle_filter('root')
        # example should give a number of possibilities
        # TODO
