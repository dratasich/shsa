import unittest
from model.shsamodel import *


class SHSAModelTestCase(unittest.TestCase):
    """Tests SHSA model."""

    def setUp(self):
        self.__graph_dict = {
            'a': ['d'],
            'b': ['c'],
            'c': ['b', 'c', 'd'],
            'd': ['a', 'c'],
            # unconnected nodes are not allowed, no edge can be created for the
            # networkx graph structure
            # 'e' : [],
        }
        self.__properties = {
            'type': {'a': SHSANodeType.V, 'b': SHSANodeType.R,
                     'c': SHSANodeType.V, 'd': SHSANodeType.R},
            'need': {'a': True, 'c': False},
            'provided': {'a': True, 'c': True},
        }

    def tearDown(self):
        self.__graph_dict = None
        self.__properties = None

    def test_setup_model(self):
        m = SHSAModel(self.__graph_dict, self.__properties)
        self.assertEqual(len(m.nodes()), 4,
                         "incorrect number of nodes")
        self.assertEqual(len(m.edges()), 7,
                         "incorrect number of edges")
        # properties check
        self.assertTrue(m.property_value_of('a', 'need'),
                        "wrong initialized property")
        self.assertEqual(m.property_value_of('a', 'type'), SHSANodeType.V,
                         "wrong initialized property")
        # nodes check
        self.assertEqual(set(m.variables), set(['a', 'c']))

    def test_setup_model_from_file(self):
        # load with classical graph dict given in the yaml
        m = SHSAModel(configfile="test/model1.yaml")
        self.assertEqual(len(m.nodes()), 14,
                         "incorrect number of nodes")
        self.assertEqual(len(m.edges()), 13,
                         "incorrect number of edges")
        # load with relations instead of graph structure
        m = SHSAModel(configfile="test/model2.yaml")
        self.assertEqual(len(m.nodes()), 15,
                         "incorrect number of nodes")
        self.assertEqual(len(m.edges()), 18,
                         "incorrect number of edges")

    def test_set_property(self):
        m = SHSAModel(self.__graph_dict, self.__properties)
        self.assertTrue(m.property_value_of('a', 'need'),
                        "wrong initialized property")
        m.set_property_to('a', 'need', False)
        self.assertFalse(m.property_value_of('a', 'need'),
                         "wrong initialized property")
        # the property 'provided' of constants cannot be set to false
        m = SHSAModel(configfile="test/model_p6.yaml")
        # provision is fine
        m.set_property_to('a', 'provided', False)
        # constant 'provided' status is not allowed to be set
        with self.assertRaises(RuntimeError):
            m.set_property_to('c', 'provided', False)

    def test_has_property(self):
        m = SHSAModel(self.__graph_dict, self.__properties)
        self.assertTrue(m.has_property('a', 'need'),
                        "property missing")
        self.assertFalse(m.has_property('a', 'dummy'),
                         "property available although not in config")

    def test_provided(self):
        m = SHSAModel(configfile="test/model_p6.yaml")
        # provision vs. provided
        self.assertTrue(m.has_property('a', 'provision'),
                        "property 'provision' missing")
        self.assertFalse(m.has_property('a', 'provided'),
                         "property 'provided' available")
        # constants and multiple provisions
        self.assertTrue(m.has_property('c', 'constant'),
                        "property 'constant' missing")
        self.assertTrue(m.provided(['c', 'd']),
                        "provided check failed")
        # filter unprovided nodes
        self.assertEqual(m.unprovided(['a', 'b', 'c']), ['a', 'b'],
                         "unprovided check failed")

    def test_variable_to_itoms_map(self):
        m = SHSAModel(configfile="test/model_p6.yaml")
        # map variable to provisions
        itoms = m.itoms('a')
        self.assertEqual(itoms, [])
        itoms = m.itoms('d')
        self.assertEqual(itoms, ['/d1', '/d2'])
        # map variable to constant
        itoms = m.itoms('c')
        self.assertEqual(itoms, 0.2, "map from variable to constant failed")
        # map itoms to variables
        variable = m.variable('/d1')
        self.assertEqual(variable, 'd')


if __name__ == '__main__':
        unittest.main()
