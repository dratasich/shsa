import unittest

from model.shsamodel import SHSAModel
from model.substitution import Substitution
from model.substitutionlist import SubstitutionList


class SubstitutionTestCase(unittest.TestCase):
    """Test cases for substitution results."""

    def setUp(self):
        self.__nodes = ['t1', 't4']
        self.__model = SHSAModel(configfile="test/model1.yaml")

    def tearDown(self):
        self.__nodes = None
        self.__model = None

    def test_init(self):
        s = Substitution(self.__model, 'root', self.__nodes)
        self.assertEqual(len(s), 2,
                         "number of nodes mismatch after init")
        self.assertEqual(set(self.__nodes), s.relations(),
                         "nodes mismatch after init")
        s.append('t2')
        self.assertEqual(len(s), 3,
                         "number of nodes mismatch after append")
        s.extend(['t3', 't5'])
        self.assertEqual(len(s), 5,
                         "number of nodes mismatch after extend")

    def test_tree_creation(self):
        s = Substitution(self.__model, 'root', self.__nodes)
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
        self.__s1 = Substitution(self.__model, self.__root, ['t1', 't4'])
        self.__s2 = Substitution(self.__model, self.__root, ['t3'])

    def tearDown(self):
        self.__model = None
        self.__root = None
        self.__s1 = None
        self.__s2 = None

    def test_list_init(self):
        S = SubstitutionList(self.__model, self.__root)
        self.assertEqual(len(S), 0,
                         "number of substitutions mismatch after `new`")
        S = SubstitutionList(self.__model, self.__root, [self.__s1, self.__s2])
        self.assertEqual(len(S), 2,
                         "number of substitutions mismatch after `new`")

    def test_list_extend(self):
        S = SubstitutionList(self.__model, self.__root)
        S.extend([self.__s1, self.__s2])
        self.assertEqual(len(S), 2,
                         "number of substitutions mismatch after `extend`")
        S.add_substitution(['t2'])
        self.assertEqual(len(S), 3,
                         "number of substitutions mismatch after `new`")
        # append a node to all substitutions
        S = SubstitutionList(self.__model, self.__root, [self.__s1, self.__s2])
        S.add_node_to('t5')
        self.assertEqual(len(S), 2,
                         "number of substitutions mismatch after `add_node_to`")
        self.assertEqual(len(S[0]), 3,
                         "number of nodes mismatch after `add_node_to`")
        self.assertEqual(len(S[1]), 2,
                         "number of nodes mismatch after `add_node_to`")
        # append node to a single substitution in the set
        S.add_node_to('t2', 0)
        self.assertEqual(len(S[0]), 4,
                         "number of nodes mismatch after `add_node_to`")
        self.assertEqual(len(S[1]), 2,
                         "number of nodes mismatch after `add_node_to`")

    def test_print(self):
        S = SubstitutionList(self.__model, self.__root, [self.__s1, self.__s2])
        S.__str__() # may raise an error if it doesn't work

    def test_best(self):
        """Tests for correct utility and if best substitution is returned."""
        S = SubstitutionList(self.__model, self.__root)
        S.add_substitution(['t1', 't4'])
        S.add_substitution(['t1', 't5'])
        S.add_substitution(['t2'])
        S.add_substitution(['t3'])
        self.assertEqual(S.best().relations(), set(['t2']),
                         "does not return best substitution")


if __name__ == '__main__':
        unittest.main()
