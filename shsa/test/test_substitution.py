import unittest
from model.shsamodel import SHSAModel
from model.substitution import Substitution
from model.substitutionlist import SubstitutionList
from engine.shsa import SHSA
from engine.dfs import DepthFirstSearch
from engine.greedy import Greedy
from engine.particlefilter import ParticleFilter


class SHSATestCase(unittest.TestCase):
    """Test cases to check basic requirements of the engine."""
    def test_init(self):
        engine = SHSA(configfile="test/model1.yaml")
        self.assertEqual(len(engine.model.nodes()), 14,
                         "incorrect number of vertices")


class SubstitutionTestCase(unittest.TestCase):
    """Test cases to show that SHSA substitution returns correct result.

    """

    def setUp(self):
        self.__filename = "test/model1.yaml"
        self.__solutions = [['t3'], ['t1'], ['t2'], ['t3', 't7'], ['t2', 't4'],
                            ['t3', 't6'], ['t2', 't5']]

    def tearDown(self):
        self.__filename = None

    def __check_substitution_results(self, S):
        self.assertTrue(len(S.substitutions) >= 5,
                         "does not return all possible substitution trees")
        # check if all solution trees are in the results
        # TODO

    def test_dfs(self):
        """Test DFS with utilities.

        """
        engine = DepthFirstSearch(configfile=self.__filename)
        S = engine.substitute('root')
        self.__check_substitution_results(S)

    def test_greedy(self):
        """Test greedy search.

        """
        engine = Greedy(configfile=self.__filename)
        u, t = engine.substitute('root')
        self.__check_substitution_results(u, t)

    def test_pf(self):
        """Graph has to be searched for possibilities via particle filter.

        """
        engine = ParticleFilter(configfile=self.__filename)
        S = engine.substitute('root')
        self.__check_substitution_results(S)
        # check with PF specific search parameters
        pass
        # # keep only 20% of best particles
        # u, t = self.engine.particle_filter('root', best=0.2)
        # # lookahead of 2 transfer functions for better search
        # u, t = self.engine.particle_filter('root', lookahead=2)


class SubstitutionTestCase(unittest.TestCase):
    """Test cases for substitution results."""

    def setUp(self):
        self.__nodes = ['t1', 't4']
        self.__utility = 3.1
        self.__model = SHSAModel(configfile="test/model1.yaml")

    def tearDown(self):
        self.__nodes = None
        self.__utility = None
        self.__model = None

    def test_substitution_init(self):
        s = Substitution(self.__model, self.__nodes, self.__utility)
        self.assertEqual(s.utility, self.__utility,
                         "utility does not match after initialization")

    def test_substitution_tree_creation(self):
        s = Substitution(self.__model, self.__nodes, self.__utility)
        t = s.tree()
        self.assertTrue(len(t.nodes()) > len(self.__nodes),
                        "no variable nodes added")
        s.add_node('r6') # variables have zero utility
        self.assertEqual(s.utility, self.__utility,
                         "utility does not match after adding node")
        s.add('t3', 1)
        self.assertEqual(s.utility, self.__utility + 1,
                         "utility does not match after adding node + utility")


class SubstitutionListTestCase(unittest.TestCase):
    """Test cases for substitution results."""

    def setUp(self):
        self.__model = SHSAModel(configfile="test/model1.yaml")
        self.__s1 = Substitution(self.__model, ['t2', 't4'], 3)
        self.__s2 = Substitution(self.__model, ['t3', 't7'], 0)

    def tearDown(self):
        self.__s1 = None
        self.__s2 = None

    def test_substitution_list_init(self):
        S = SubstitutionList(self.__model)

    def test_substitution_list_extend(self):
        S = SubstitutionList(self.__model)
        S.extend([self.__s1, self.__s2])
        self.assertEqual(len(S), 2,
                         "number of substitutions mismatch after `extend`")
        S.add_substitution(['t1'], 2)
        self.assertEqual(len(S), 3,
                         "number of substitutions mismatch after `new`")
        s = S.best()
        self.assertEqual(s.utility, 3,
                         "utility of best substitution does not match")
        # append a node to all substitutions
        S.add_node_to('t5', 1)
        self.assertEqual(len(S), 3,
                         "number of substitutions mismatch after `append`")
        s = S.best()
        self.assertEqual(s.utility, 4,
                         "utility of best substitution does not match")
        # append node to a single substitution in the set
        idx = 0
        u_before = S[idx].utility
        S.add_node_to('t5', -1, idx)
        self.assertEqual(S[idx].utility, u_before-1,
                         "utility of best substitution does not match")
