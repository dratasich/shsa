import unittest
from graph.graph import Graph

class GraphTestCase(unittest.TestCase):
    """Tests basic graph structure.

    """

    # def setUp(self):
    #     # TODO: init code for the testcases come here

    # def tearDown(self):
    #     # TODO: init code for the testcases come here

    def test_setup_graph(self):
        g = { "a" : ["d"],
              "b" : ["c"],
              "c" : ["b", "c", "d"],
              "d" : ["a", "c"],
              "e" : []
        }
        graph = Graph(g)
        self.assertEqual(len(graph.vertices()), 5,
                         'incorrect number of vertices')
        self.assertEqual(len(graph.edges()), 7,
                         'incorrect number of edges')

    def test_init_graph(self):
        graph = Graph()
        self.assertEqual(len(graph.vertices()), 0,
                         'incorrect number of vertices for empty graph')
        self.assertEqual(len(graph.edges()), 0,
                         'incorrect number of edges for empty graph')

    def test_add_vertex(self):
        graph = Graph()
        graph.add_vertex("a")
        self.assertEqual(len(graph.vertices()), 1,
                         'incorrect number of vertices after adding a vertex')
        graph.add_vertex("b")
        graph.add_vertex("c")
        self.assertEqual(len(graph.vertices()), 3,
                         'incorrect number of vertices after adding vertices')

    def test_add_edge(self):
        graph = Graph()
        graph.add_vertex("a")
        graph.add_vertex("b")
        graph.add_edge(("a", "b"))
        self.assertEqual(len(graph.edges()), 1,
                         'incorrect number of edges after adding a edges')
