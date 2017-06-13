"""Graph.

__author__ = "Denise Ratasich"

Modified from http://www.python-course.eu/graphs_python.php (Bernd Klein).
See also https://www.python.org/doc/essays/graphs/

Write/print functions from Daniel Prokesch.

A possible substitute for this class would be https://networkx.readthedocs.io/

"""

from subprocess import call # call dot to generate .png out of .dot files

class Graph(object):
    """Graph class with directed edges."""

    def __init__(self, graph_dict=None):
        """Initializes a graph object.

        If no dictionary or None is given, an empty dictionary will be used.

        The graph is saved in a dictionary. Nodes are keys. Successors of a
        key are saved in a list, corresponding the value of a key.

        Example:

        g = { 'a' : ['d'],
              'b' : ['c'],
              'c' : ['b', 'c', 'd'],
              'd' : ['a', 'c'],
              'e' : []
            }

        """
        if graph_dict == None:
            graph_dict = {}
        self.__graph_dict = graph_dict

    def __getitem__(self, item):
        """Returns adjacents of a node."""
        return self.__graph_dict[item]

    def adjacents(self, node):
        """Returns adjacents of a node."""
        return self.__graph_dict[node]

    def nodes(self):
        """Returns the nodes of a graph."""
        return list(self.__graph_dict.keys())

    def edges(self):
        """Returns the edges of a graph."""
        return self.__generate_edges()

    def add_node(self, node):
        """Adds a node with the key "node" if not yet exists.

        If the node "node" is not in self.__graph_dict, a key "node" with
        an empty list as a value is added to the dictionary. Otherwise nothing
        has to be done.

        """
        if node not in self.__graph_dict:
            self.__graph_dict[node] = []

    def add_edge(self, u, v):
        """Adds a directed edge.

        """
        if u in self.__graph_dict:
            self.__graph_dict[u].append(v)
        else:
            self.__graph_dict[u] = [v]

    def __generate_edges(self):
        """Generates the edges of the graph "graph".

        Edges are represented as tuples with two nodes.

        """
        edges = []
        for node in self.__graph_dict:
            for neighbour in self.__graph_dict[node]:
                if {neighbour, node} not in edges:
                    edges.append(tuple((node, neighbour)))
        return edges

    def __str__(self):
        res = "V: "
        for k in self.__graph_dict:
            res += "'" + str(k) + "' "
        res += "\nE: "
        for edge in self.__generate_edges():
            res += str(edge) + " "
        return res

    def write_dot(self, basefilename, oformat=None):
        """Saves the graph as dot-file and generates an image if oformat given.

        basefilename -- Name of the dot-file to generate.
        oformat -- Desired output format, e.g., "eps", "png" or "pdf". The
                   generated dot-file is converted to the given format.

        """
        gtype = "digraph"
        etype = "->"
        with open("{}.dot".format(basefilename), "w") as f:
            f.write("{} \"{}\" {{\n".format(gtype, basefilename))
            f.write("  node [fontname=\"sans-serif\"];\n")
            for u, v in self.edges():
                f.write(" \"{0}\" {2} \"{1}\";\n".format(u, v, etype))
            f.write("}\n")
        if oformat:
            call(["/usr/bin/dot", "-T" + oformat, "-o",
                  basefilename + "." + oformat, basefilename + ".dot"])
