import unittest

from model.shsamodel import SHSAModel
from model.substitution import Substitution
from model.substitutionlist import SubstitutionList
from model.utility import *


class SubstitutionTestCase(unittest.TestCase):
    """Test cases for substitution results."""

    def setUp(self):
        self.__nodes = ['t1', 't4']
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
        self.assertEqual(s.model, self.__model, "model mismatch")
        self.assertEqual(s.root, 'root', "root mismatch")
        # init without model and root in constructor
        s = Substitution(self.__nodes)
        self.assertEqual(len(s), 2,
                         "number of nodes mismatch after init")
        self.assertEqual(s.model, None, "model mismatch")
        self.assertEqual(s.root, None, "root mismatch")
        # init model and root later
        s.model = self.__model
        s.root = 'root'
        self.assertEqual(s.model, self.__model, "model mismatch")
        self.assertEqual(s.root, 'root', "root mismatch")

    def test_list(self):
        s = Substitution(self.__nodes)
        # check if the substitution can be extended
        s.append('t2')
        self.assertEqual(len(s), 3,
                         "number of nodes mismatch after append")
        s.extend(['t3', 't5'])
        self.assertEqual(len(s), 5,
                         "number of nodes mismatch after extend")

    def test_tree_creation(self):
        s = Substitution(self.__nodes, model=self.__model, root='root')
        t, vin = s.tree(collapse_variables=False)
        self.assertTrue(len(t.nodes()) > len(self.__nodes),
                        "no variable nodes added")
        self.assertTrue('root' in t.nodes(),
                        "root node is not part of the substitution tree")
        self.assertEqual(set(vin), {'r1', 'r6', 'r7'},
                         "wrong variable source nodes")
        # model with more directions on edges
        s = Substitution(['r4', 'r3'],
                         model=SHSAModel(configfile="test/model_p1.yaml"),
                         root='c')
        t, vin = s.tree()
        self.assertEqual(set(t.edges()),
                         {('g', 'r4'), ('r4', 'r3'), ('r3', 'c')},
                         "wrong substitution tree (edge mismatch)")
        self.assertEqual(set(vin), {'g'},
                         "wrong variable source nodes")
        # order of list should not matter
        s = Substitution(['r3', 'r4'],
                         model=SHSAModel(configfile="test/model_p1.yaml"),
                         root='c')
        t, vin = s.tree()
        self.assertEqual(set(t.edges()),
                         {('g', 'r4'), ('r4', 'r3'), ('r3', 'c')},
                         "wrong substitution tree (edge mismatch)")
        self.assertEqual(set(vin), {'g'},
                         "wrong variable source nodes")

    def test_execute(self):
        m = SHSAModel(configfile="test/model_e1.yaml")
        s = Substitution(['r1', 'r2'], model=m, root='a')
        result = s.execute({'c': 0, 'd': 1, 'e': 2})
        self.assertEqual(result, 2, "execute gives wrong result")
        s = Substitution(['r3', 'r4'], model=m, root='a')
        result = s.execute({'g': 0, 'h': 1, 'i': 2, 'j': 3})
        self.assertEqual(result, -3, "execute gives wrong result")


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
        # update utility function too
        uf_new = UtilityNorm()
        S.update(self.__root, utility_fct=uf_new)
        self.assertEqual(S[2].utility_fct, uf_new,
                         "new substitution has other/no utility_fct")

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
