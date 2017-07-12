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


class SHSAEnginesTestCase(unittest.TestCase):
    """Test cases to show that SHSA substitution returns correct result.

    """

    def setUp(self):
        # testcases - there has to be a unique best solution. Otherwise the
        # best-check may fail, because the engines traverse the substitution
        # tree differently
        self.__filename = [
            "test/model1.yaml",
            "test/model2.yaml",
        ]
        self.__root = [
            'root',
            'v1',
        ]
        self.__solutions = [
            frozenset([
                frozenset(['t1']),
                frozenset(['t2']),
                frozenset(['t3']),
                frozenset(['t1', 't4']),
                frozenset(['t1', 't5']),
            ]),
            frozenset([
                frozenset(['r1', 'r3']),
            ]),
        ]
        self.__best = [
            {'t3', 't7'},
            {'r1', 'r3'},
        ]

    def tearDown(self):
        self.__filename = None
        self.__root = None
        self.__best = None
        self.__solutions = None

    def __check_substitution_results(self, S, idx):
        self.assertTrue(len(S) >= 5,
                        "does not return all possible substitution trees")
        # check if all solution trees are in the results
        self.assertTrue(len(S.relations() & self.__solutions[idx])
                        == len(S.relations()),
                        "substitution result is incorrect")
        # check best
        # TODO - need a unique solution
        self.assertTrue(S.best() == self.__best[idx],
                        "best substitution is incorrect")

    def test_dfs(self):
        """Test DFS with utilities.

        """
        for i in range(len(self.__filename)):
            engine = DepthFirstSearch(configfile=self.__filename[i])
            S = engine.substitute(self.__root[i])
            self.__check_substitution_results(S, i)

    def test_pf(self):
        """Graph has to be searched for possibilities via particle filter.

        """
        for i in range(len(self.__filename)):
            engine = ParticleFilter(configfile=self.__filename[i])
            S = engine.substitute(self.__root[i])
            self.__check_substitution_results(S, i)
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
        s = Substitution(self.__model, 'root', self.__nodes, self.__utility)
        self.assertEqual(s.utility, self.__utility,
                         "utility does not match after initialization")
        # should have no effect
        s.add_node('r6') # variables have zero utility
        self.assertEqual(s.utility, self.__utility,
                         "utility does not match after adding node")
        s.add('t3', 1)
        self.assertEqual(s.utility, self.__utility + 1,
                         "utility does not match after adding node + utility")

    def test_substitution_tree_creation(self):
        s = Substitution(self.__model, 'root', self.__nodes, self.__utility)
        t = s.tree()
        self.assertTrue(len(t.nodes()) > len(self.__nodes),
                        "no variable nodes added")
        self.assertTrue('root' in t.nodes(),
                        "root node is not part of the substitution tree")
        self.assertTrue('r1' in t.nodes() \
                        and 'r6' in t.nodes() and 'r7' in t.nodes(),
                        "leaf nodes are missing in the substitution tree")

class SubstitutionListTestCase(unittest.TestCase):
    """Test cases for substitution results."""

    def setUp(self):
        self.__model = SHSAModel(configfile="test/model1.yaml")
        self.__root = 'root'
        self.__s1 = Substitution(self.__model, self.__root, ['t2', 't4'], 3)
        self.__s2 = Substitution(self.__model, self.__root, ['t3', 't7'], 0)

    def tearDown(self):
        self.__model = None
        self.__root = None
        self.__s1 = None
        self.__s2 = None

    def test_substitution_list_init(self):
        S = SubstitutionList(self.__model, self.__root)

    def test_substitution_list_extend(self):
        S = SubstitutionList(self.__model, self.__root)
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
