import unittest
from model.shsamodel import *

class SHSAModelTestCase(unittest.TestCase):
    """Tests SHSA model."""

    def setUp(self):
        self.__graph_dict = { 'a': ['d'],
              'b': ['c'],
              'c': ['b', 'c', 'd'],
              'd': ['a', 'c'],
              # unconnected nodes are not allowed, no edge can be created for
              # the networkx graph structure
              #'e' : [],
        }
        self.__properties = {
            'type': {'a': SHSANodeType.V, 'b': SHSANodeType.R,
                     'c': SHSANodeType.V, 'd': SHSANodeType.R},
            'need': {'a': True, 'c': False},
            'provided': {'a': True, 'c': True},
        }
        self.__filename = "test/model1.yaml"

    def tearDown(self):
        self.__graph_dict = None
        self.__properties = None
        self.__filename = None

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

    def test_setup_model_from_file(self):
        m = SHSAModel(configfile=self.__filename)
        self.assertEqual(len(m.nodes()), 14,
                         "incorrect number of nodes")
        self.assertEqual(len(m.edges()), 13,
                         "incorrect number of edges")

    def test_set_property(self):
        m = SHSAModel(self.__graph_dict, self.__properties)
        self.assertTrue(m.property_value_of('a', 'need'),
                        "wrong initialized property")
        m.set_property_to('a', 'need', False)
        self.assertFalse(m.property_value_of('a', 'need'),
                        "wrong initialized property")
