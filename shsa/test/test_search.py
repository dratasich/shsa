import unittest
from graph.graph import Graph
from graph.search import *

class SearchTestCase(unittest.TestCase):
    def setUp(self):
        self.graph_dict = { "a" : ["d"],
              "b" : ["c"],
              "c" : ["b", "c", "d"],
              "d" : ["a", "c"],
              # "e" : [] # vertices without a connection to other nodes are not
                         # allowed in these tests (cannot be visited)
        }
        self.graph_inst = Graph(self.graph_dict)

    def tearDown(self):
        self.graph_dict = None
        self.graph_inst = None

    def test_bfs_visited(self):
        """Tests breadth-first search.

        """
        # test with dictionary
        g = self.graph_dict
        visited = bfs(g, "a")
        self.assertEqual(set(g.keys()), visited,
                         'not all vertices visited')
        # test with instance of Graph class
        g = self.graph_inst
        visited = bfs(g, "a")
        self.assertEqual(set(g.vertices()), visited,
                         'not all vertices visited')

    def test_bfs_reentrant(self):
        # test with instance of Graph class
        g = self.graph_inst
        visited = set() # breadth-first tree
        queue = ["a"] # start node
        # adjacents of start node should be next
        visited, queue = bfs_next(g, visited, queue)
        adjacents = g["a"]
        self.assertEqual(adjacents, queue,
                         'first step faulty (adjacents of start node != queue)')
        # go through the rest
        while queue:
            visited, queue = bfs_next(g, visited, queue)
        # done?
        self.assertEqual(set(g.vertices()), visited,
                         'not all vertices visited (visited != all vertices)')
        self.assertEqual(queue, [],
                         'not all vertices visited (queue not empty)')
