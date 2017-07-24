import unittest

from model.shsamodel import SHSAModel
from model.substitution import Substitution
from model.substitutionlist import SubstitutionList


class SubstitutionTestCase(unittest.TestCase):
    """Test cases for substitution results."""

    def setUp(self):
        self.__nodes = ['t2', 't4']
        self.__model = SHSAModel(configfile="test/model1.yaml")

    def tearDown(self):
        self.__nodes = None
        self.__model = None

    def test_init(self):
        s = Substitution(self.__nodes, model=self.__model, root='root')
        self.assertEqual(len(s), 2,
                         "number of nodes mismatch after init")
        self.assertEqual(set(self.__nodes), s.relations(),
                         "nodes mismatch after init")
        # check tree to see if model and root is correctly initialized
        t = s.tree()
        self.assertEqual(set(t.nodes()),
                         {'root', 't2', 't4', 'r3', 'r6', 'r7'},
                         "number of nodes mismatch after init")
        # check if the substitution can be extended
        s.append('t2')
        self.assertEqual(len(s), 3,
                         "number of nodes mismatch after append")
        s.extend(['t3', 't5'])
        self.assertEqual(len(s), 5,
                         "number of nodes mismatch after extend")
        # without model and root in constructor
        s = Substitution(self.__nodes)
        self.assertEqual(len(s), 2,
                         "number of nodes mismatch after init")
        # init later
        s.model = self.__model
        s.root = 'root'
        self.assertEqual(len(s), 2,
                         "number of nodes mismatch after init")

    def test_tree_creation(self):
        s = Substitution(self.__nodes, model=self.__model, root='root')
        t = s.tree()
        self.assertTrue(len(t.nodes()) > len(self.__nodes),
                        "no variable nodes added")
        self.assertTrue('root' in t.nodes(),
                        "root node is not part of the substitution tree")
        self.assertTrue('r3' in t.nodes()
                        and 'r6' in t.nodes() and 'r7' in t.nodes(),
                        "leaf nodes are missing in the substitution tree")


class SubstitutionListTestCase(unittest.TestCase):
    """Test cases for substitution results."""

    def setUp(self):
        self.__model = SHSAModel(configfile="test/model1.yaml")
        self.__root = 'root'
        self.__s1 = Substitution(['t1', 't4'],
                                 model=self.__model, root=self.__root)
        self.__s2 = Substitution(['t3'],
                                 model=self.__model, root=self.__root)

    def tearDown(self):
        self.__model = None
        self.__root = None
        self.__s1 = None
        self.__s2 = None

    def test_list_init(self):
        S = SubstitutionList()
        self.assertEqual(len(S), 0,
                         "number of substitutions mismatch after `new`")
        S = SubstitutionList([self.__s1, self.__s2])
        self.assertEqual(len(S), 2,
                         "number of substitutions mismatch after `new`")

    def test_list_extend(self):
        S = SubstitutionList()
        S.extend([self.__s1, self.__s2])
        self.assertEqual(len(S), 2,
                         "number of substitutions mismatch after `extend`")
        S.add_substitution(['t2'])
        self.assertEqual(len(S), 3,
                         "number of substitutions mismatch after `new`")
        # append a node to all substitutions
        S = SubstitutionList([self.__s1, self.__s2])
        S.add_node_to('t5')
        self.assertEqual(len(S), 2,
                         """number of substitutions mismatch after
                         `add_node_to`""")
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
        S = SubstitutionList([self.__s1, self.__s2])
        S.__str__()  # may raise an error if it doesn't work

    def test_update(self):
        S = SubstitutionList([self.__s1, self.__s2])
        # update root
        S.update('r2')
        self.assertEqual(S[0].root, 'r2', "root update failed")
        self.assertEqual(S[1].root, 'r2', "root update failed")
        S.add_substitution()
        self.assertEqual(S[2].root, 'r2', "new substitution has other/no root")
        # update model too
        S.update(self.__root, self.__model)
        S.add_substitution(['t2'])
        self.assertEqual(S[3].root, self.__root,
                         "new substitution has other/no root")
        self.assertEqual(S[3].model, self.__model,
                         "new substitution has other/no model")

    def test_best(self):
        """Tests for correct utility and if best substitution is returned."""
        S = SubstitutionList()
        S.append(Substitution(['t1', 't4']))
        S.append(Substitution(['t1', 't5']))
        S.append(Substitution(['t2']))
        S.append(Substitution(['t3']))
        S.update(self.__root, self.__model)  # needs model for evaluation
        self.assertEqual(S.best().relations(), set(['t2']),
                         "does not return best substitution")


if __name__ == '__main__':
        unittest.main()
