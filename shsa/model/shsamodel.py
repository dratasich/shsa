"""Model for self-healing.

__author__ = "Denise Ratasich"

Nodes represent random variables or deterministic nodes which describe
relations between variables (originally transfer functions). Edges represent
dependence of nodes.

Each node has a unique name (key). The graph object saves the connection
between nodes (node -> adjacents). Furthermore each node can have several
properties (or attributes). Each property has a name (key) and a value, e.g.,
numeric, boolean (node -> properties -> property-value). SHSA needs specific
properties (e.g., 'provided') to perform self-healing. Others are used to find
the best possible reconfiguration, i.e., to calculate the utility.

Example:
    Node 'speed' has adjacents ['distance', 'acceleration'] (see class
    Graph). Each node has properties, whereas each property has a value, e.g.,
    'c' = {'need': False, 'provision': True, 'variance': 0.1}.

"""

from enum import IntEnum
from subprocess import call # call dot to generate .png out of .dot files
import yaml # read graph structure and properties from config file
import networkx as nx

# model #######################################################################

class SHSAModel(nx.DiGraph):
    """Model class.

    Currently it is a directed graph, though the knowledge base typically the
    relations between variables are undirected (use `Graph`), i.e., each
    variable can be input or output. A directed graph may be more suitable for
    final use, because relations doesn't have to be converted, for each output
    variable a function is defined given all other connected input variables.

    """

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
            raise RuntimeError("""either config file or graph structure &
            properties must be provided""")

    def __init(self, graph_dict, properties):
        edges = [(u,v) for u in graph_dict for v in graph_dict[u]]
        super(SHSAModel, self).__init__(edges)
        for name in properties:
            nx.set_node_attributes(self, name, properties[name])

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
            self.__init(data['graph'], data['properties'])

    def property_value_of(self, node, prop):
        """Returns the value of a property of a node."""
        return self.node[node][prop]

    def set_property_to(self, node, prop, value):
        """Sets the value of a property of a node."""
        self.node[node][prop] = value

    def utility_of(self, node):
        """Returns the utility of a relation node."""
        if self.node[node]['type'] == SHSANodeType.V:
            return 0
        return len(self.neighbors(node))

    def all_variables_provided(self, node):
        """Returns true, if all adjacents of a relation are provided."""
        # function not meant to be for variables
        if self.node[node]['type'] == SHSANodeType.V:
            return False
        # check all adjacents
        for a in self.neighbors(node):
            if not self.node[a]["provided"]:
                return False
        return True

    def __str__(self):
        res = "Nodes\n"
        res += str(self.nodes())
        res += "\nEdges\n"
        res += str(self.edges())
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
            for v in self.nodes():
                nodestyle = ""
                if self.property_value_of(v, 'type') == SHSANodeType.R:
                    nodestyle += "shape=box"
                elif self.property_value_of(v, 'provided'):
                    nodestyle += "style=filled,fillcolor=\"lightgrey\","
                f.write(" \"{0}\" [{1}];\n".format(v, nodestyle))
            for u, v in self.edges():
                edgestyle = ""
                if (u,v) in highlight_edges:
                    edgestyle = highlight
                f.write(" \"{0}\" {2} \"{1}\" [{3}];\n".format(u, v, etype,
                                                               edgestyle))
            f.write("}\n")
        if oformat:
            call(["/usr/bin/dot", "-T" + oformat, "-o",
                  basefilename + "." + oformat, basefilename + ".dot"])


# properties ##################################################################

class SHSANodeType(IntEnum):
    """Types of nodes that are distinguished in the model."""
    V = 0
    R = 1
