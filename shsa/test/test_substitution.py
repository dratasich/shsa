import unittest

from model.shsamodel import SHSAModel
from model.substitution import Substitution
from model.substitutionlist import SubstitutionList


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

    def test_init(self):
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

    def test_tree_creation(self):
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

    def test_list_init(self):
        S = SubstitutionList(self.__model, self.__root)

    def test_list_extend(self):
        S = SubstitutionList(self.__model, self.__root)
        S.extend([self.__s1, self.__s2])
        self.assertEqual(len(S), 2,
                         "number of substitutions mismatch after `extend`")
        S.add_substitution(['t1'], 2)
        self.assertEqual(len(S), 3,
                         "number of substitutions mismatch after `new`")
        self.assertEqual(S[0].utility, 3,
                         "utility of first substitution does not match")
        # append a node to all substitutions
        S.add_node_to('t5', 1)
        self.assertEqual(len(S), 3,
                         "number of substitutions mismatch after `add node`")
        self.assertEqual(S[-1].utility, 3,
                         "utility of last substitution does not match")
        # append node to a single substitution in the set
        idx = 0
        u_before = S[idx].utility
        S.add_node_to('t5', -1, idx)
        self.assertEqual(S[idx].utility, u_before-1,
                         """utility of substitution[{}] does not
                         match""".format(idx))

    def test_best(self):
        S = SubstitutionList(self.__model, self.__root)
        S.extend([self.__s1, self.__s2])
        self.assertEqual(S.best(), self.__s1,
                         "does not return best substitution")


if __name__ == '__main__':
        unittest.main()
