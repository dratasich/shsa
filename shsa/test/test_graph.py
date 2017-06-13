import unittest
from graph.graph import Graph

class GraphTestCase(unittest.TestCase):
    """Tests basic graph structure."""

    # def setUp(self):
    #     # TODO: init code for the testcases come here

    # def tearDown(self):
    #     # TODO: init code for the testcases come here

    def test_setup_graph(self):
        g = { 'a' : ['d'],
              'b' : ['c'],
              'c' : ['b', 'c', 'd'],
              'd' : ['a', 'c'],
              'e' : []
        }
        graph = Graph(g)
        self.assertEqual(len(graph.nodes()), 5,
                         "incorrect number of nodes")
        self.assertEqual(len(graph.edges()), 7,
                         "incorrect number of edges")

    def test_init_graph(self):
        graph = Graph()
        self.assertEqual(len(graph.nodes()), 0,
                         "incorrect number of nodes for empty graph")
        self.assertEqual(len(graph.edges()), 0,
                         "incorrect number of edges for empty graph")

    def test_add_node(self):
        graph = Graph()
        graph.add_node('a')
        self.assertEqual(len(graph.nodes()), 1,
                         "incorrect number of nodes after adding a node")
        graph.add_node('b')
        graph.add_node('c')
        self.assertEqual(len(graph.nodes()), 3,
                         "incorrect number of nodes after adding nodes")

    def test_add_edge(self):
        graph = Graph()
        graph.add_node('a')
        graph.add_node('b')
        graph.add_node('c')
        graph.add_edge('a', 'b')
        self.assertEqual(len(graph.edges()), 1,
                         "incorrect number of edges after adding an edge")
        graph.add_edge('b', 'c')
        self.assertEqual(len(graph.edges()), 2,
                         "incorrect number of edges after adding an edge")
