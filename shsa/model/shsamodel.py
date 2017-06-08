"""Model for self-healing.

__author__ = "Denise Ratasich"

Nodes represent random variables or deterministic nodes which describe
relations between variables (originally transfer functions). Edges represent
dependence of nodes.

Each node has a unique name (key). The graph object saves the connection
between nodes (node -> adjacents). Furthermore each node can have several
properties. Each property has a name (key) and a value, e.g., numeric, boolean
(node -> properties -> property-value). SHSA needs specific properties (e.g.,
'provided') to perform self-healing. Others are used to find the best possible
reconfiguration, i.e., to calculate the utility.

Example:
    Node 'speed' has adjacents ['distance', 'acceleration'] (see class
    Graph). Each node has properties, whereas each property has a value, e.g.,
    'c' = {'need': False, 'provision': True, 'variance': 0.1}.

"""

from subprocess import call # call dot to generate .png out of .dot files
import yaml # read graph structure and properties from config file

from graph.graph import Graph


# model #######################################################################

class SHSAModel(Graph):
    """Model class."""

    def __init__(self, graph_dict=None, properties=None, configfile=None):
        """Initializes a model.

        The underlying graph must be initialized by setting graph_dict defining
        the graph's structure (see Graph constructor). Additionally, the
        properties of each node in the graph must be provided in a dictionary,
        in particular to distinguish the node types.

        """
        if configfile:
            self.__init_from_file(configfile)
        elif graph_dict and properties:
            self.__init(graph_dict, properties)
        else:
            raise Exception("""either config file or graph structure &
            properties must be provided""")

    def __init(self, graph_dict, properties):
        self.__graph = Graph(graph_dict)
        """Model's structure."""
        self.__properties = properties
        """Nodes' properties (key: node, value: dict of properties)."""

    def __init_from_file(self, configfile):
        """Initializes a model based on a yaml file.

        The config file must include two dictionaries `graph` and `properties`
        defining the structure of the graph and the nodes' properties.

        """
        with open(configfile, 'r') as f:
            try:
                data = yaml.load(f)
            except yaml.YAMLError as e:
                print(e)
            self.__init__(data['graph'], data['properties'])

    def properties_of(self, node):
        """Returns the properties of a node."""
        return self.__properties[node]

    def property_value_of(self, node, prop):
        """Returns the value of a property of a node."""
        return self.__properties[node][prop]

    def properties(self):
        """Returns properties of all nodes."""
        return self.__properties

    def nodes(self):
        """Returns all nodes of the model."""
        return list(self.__properties.keys())

    def graph(self):
        """Returns the underlying graph."""
        return self.__graph

    def set_property_to(self, node, prop, value):
        """Sets the value of a property of a node."""
        self.__properties[node][prop] = value

    def adjacents_of(self, node):
        """Returns all adjacents of a node in a list."""
        return self.__graph[node]

    def utility_of(self, node):
        """Returns the utility of a relation node."""
        return len(self.adjacents_of(node))

    def __str__(self):
        res = "Graph\n"
        res += str(self.__graph)
        res += "\nProperties"
        for n in self.__properties:
            res += "\n'" + str(n) + "': " + str(self.__properties[n])
        res += "\n"
        return res

    def write_dot(self, basefilename, oformat=None, highlight_edges=[]):
        """Saves the model as dot-file and generates an image if oformat given.

        basefilename -- Name of the dot-file to generate.
        oformat -- Desired output format, e.g., "eps", "png" or "pdf". The
                   generated dot-file is converted to the given format.
        highlight_edges -- Highlights given edges, a list of tuples.

        """
        # bold red line
        highlight = "color=\"#ff0000\", penwidth=2"
        gtype = "digraph"
        etype = "->"
        with open("{}.dot".format(basefilename), "w") as f:
            f.write("{} \"{}\" {{\n".format(gtype, basefilename))
            f.write("  node [fontname=\"sans-serif\"];\n")
            for u, v in self.__graph.edges():
                f.write(" \"{0}\" {2} \"{1}\" [{3}];\n".format(u, v, etype,
                                                               highlight if
                                                               (u,v) in
                                                               highlight_edges
                                                               else ""))
            f.write("}\n")
        if oformat:
            call(["/usr/bin/dot", "-T" + oformat, "-o",
                  basefilename + "." + oformat, basefilename + ".dot"])


# properties ##################################################################

def enum(*sequential, **named):
    """Enum implementation (for Python < 3.4).

    http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
    """
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

SHSANodeType = enum(
    'V', # variable
    'R', # relation
)
"""Types of nodes that are distinguished in the model."""
