"""Graph.

__author__ = "Denise Ratasich"

Modified from http://www.python-course.eu/graphs_python.php (Bernd Klein).
See also https://www.python.org/doc/essays/graphs/

Write/print functions from Daniel Prokesch.

"""

from subprocess import call # call dot to generate .png out of .dot files

class Graph(object):
    """Graph class with directed edges."""

    def __init__(self, graph_dict=None):
        """Initializes a graph object.

        If no dictionary or None is given, an empty dictionary will be used.

        The graph is saved in a dictionary. Vertices are keys. Successors of a
        key are saved in a list, corresponding the value of a key.

        Example:

        g = { "a" : ["d"],
              "b" : ["c"],
              "c" : ["b", "c", "d"],
              "d" : ["a", "c"],
              "e" : []
            }

        """
        if graph_dict == None:
            graph_dict = {}
        self.__graph_dict = graph_dict

    def __getitem__(self, item):
        """Returns adjacents of a vertex."""
        return self.__graph_dict[item]

    def adjacents(self, vertex):
        """Returns adjacents of a vertex."""
        return self.__graph_dict[vertex]

    def vertices(self):
        """Returns the vertices of a graph."""
        return list(self.__graph_dict.keys())

    def edges(self):
        """Returns the edges of a graph."""
        return self.__generate_edges()

    def add_vertex(self, vertex):
        """Adds a vertex with the key "vertex" if not yet exists.

        If the vertex "vertex" is not in self.__graph_dict, a key "vertex" with
        an empty list as a value is added to the dictionary. Otherwise nothing
        has to be done.

        """
        if vertex not in self.__graph_dict:
            self.__graph_dict[vertex] = []

    def add_edge(self, edge):
        """Adds a directed edge, represented by a tuple or list of two vertices.

        Assumes that edge is of type tuple or list; two vertices can have
        multiple edges.

        """
        (vertex1, vertex2) = tuple(edge)
        if vertex1 in self.__graph_dict:
            self.__graph_dict[vertex1].append(vertex2)
        else:
            self.__graph_dict[vertex1] = [vertex2]

    def __generate_edges(self):
        """Generates the edges of the graph "graph".

        Edges are represented as tuples with two vertices.

        """
        edges = []
        for vertex in self.__graph_dict:
            for neighbour in self.__graph_dict[vertex]:
                if {neighbour, vertex} not in edges:
                    edges.append(tuple((vertex, neighbour)))
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
