import unittest
from model.model import *

class SHSAModelTestCase(unittest.TestCase):
    """Tests SHSA model."""

    def setUp(self):
        self.graph_dict = { "a" : ["d"],
              "b" : ["c"],
              "c" : ["b", "c", "d"],
              "d" : ["a", "c"],
              # "e" : [] # vertices without a connection to other nodes are not
                         # allowed in these tests (cannot be visited)
        }
        self.properties = {
            'speed': {'type': SHSANodeType.RV, 'need': True, 'provided': True},
            'tf1': {'type': SHSANodeType.TF},
            'acc': {'type': SHSANodeType.RV, 'need': False, 'provided': True},
        }

    def tearDown(self):
        self.graph_dict = None
        self.properties = None

    def test_setup_model(self):
        m = SHSAModel(self.graph_dict)
        # graph check
        g = m.graph()
        self.assertEqual(len(g.vertices()), 4,
                         'incorrect number of vertices')
        self.assertEqual(len(g.edges()), 7,
                         'incorrect number of edges')
        # properties check
        p = m.properties()
        self.assertEqual(len(p), len(g.vertices()),
                         'not every node has properties')
        p0 = m.properties_of(m.nodes()[0])
        self.assertNotEqual(len(p0), 0,
                            'no default properties')
        # initialize with property dict
        m = SHSAModel(self.graph_dict, self.properties)
        self.assertTrue(m.property_value_of('speed','need'),
                        'wrong initialized property')
        self.assertEqual(m.property_value_of('speed','type'), SHSANodeType.RV,
                         'wrong initialized property')

    def test_set_property(self):
        m = SHSAModel(self.graph_dict, self.properties)
        self.assertTrue(m.property_value_of('speed','need'),
                        'wrong initialized property')
        m.set_property_to('speed', 'need', False)
        self.assertFalse(m.property_value_of('speed','need'),
                        'wrong initialized property')
