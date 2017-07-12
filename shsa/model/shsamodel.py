"""Model for self-healing.

__author__ = "Denise Ratasich"

Nodes represent random variables or relations between variables (originally
transfer functions).

Each node has a unique name (key). The graph object saves the edges between
nodes (u -> v). Furthermore each node can have several properties (or
attributes). Each property has a name (key) and a value, e.g., numeric, boolean
(node -> properties -> property-value). SHSA needs specific properties (e.g.,
'provided') to perform self-healing. Others are used to find the best possible
reconfiguration, i.e., to calculate the utility.

Example:
    Node 'speed' has adjacents ['distance', 'acceleration']. Each node has
    properties, whereas each property has a value, e.g., 'c' = {'need': False,
    'provision': True, 'variance': 0.1}.

"""

from enum import IntEnum
from subprocess import call # call dot to generate .png out of .dot files
import yaml # read graph structure and properties from config file
import networkx as nx

# model #######################################################################

class SHSAModel(nx.DiGraph):
    """Model class.

    Currently it is a directed graph, though the knowledge base / the relations
    between variables are undirected, i.e., each variable can be input or
    output. A directed graph may be more suitable for final use, because
    - Relations/functions doesn't have to be converted, for each output
      variable a function is defined given all other connected input variables.
    - There are relations which cannot be converted, i.e., the relation can
      only be executed into specific direction, i.e., for a specific
      variable/output (cf. part-of relations).

    """

    def __init__(self, graph_dict=None, properties=None, configfile=None):
        """Initializes a model.

        The underlying graph must be initialized by setting graph_dict defining
        the graph's structure (see Graph constructor). Or by a graph
        dictionary, edges or relations from a configuration file. Additionally,
        the properties of each node in the graph must be provided in a
        dictionary, in particular to distinguish the node types.

        """
        if configfile:
            self.__init_from_file(configfile)
        elif graph_dict and properties:
            self.__init_with_graph(graph_dict, properties)
        else:
            raise RuntimeError("""either config file or graph structure &
            properties must be provided""")

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
            if 'relations' in data.keys():
                self.__init_with_relations(data['relations'], data['properties'])
            elif 'graph' in data.keys():
                self.__init_with_graph(data['graph'], data['properties'])
            else:
                raise RuntimeError("""Graph structure (graph or relations) is
                missing in the config file '{}'.""".format(configfile))

    def __init_with_edges(self, edges, properties):
        """Initializes the model with edges.

        Nodes are implicitly created. Once the graph is initialized, the node
        attributes can be set.

        """
        super(SHSAModel, self).__init__(edges)
        for name in properties:
            nx.set_node_attributes(self, name, properties[name])

    def __init_with_graph(self, graph_dict, properties):
        """Extracts edges from a graph dictionary ({node:list(adjacents)}).

        The graph dictionary with keys corresponds to nodes and the values to
        list of adjacents of the node.

        """
        edges = [(u,v) for u in graph_dict for v in graph_dict[u]]
        self.__init_with_edges(edges, properties)

    def __init_with_relations(self, relations, properties):
        """Extracts edges from a dictionary of relations.

        A dictionary of relations (key: relation name, value: dictionary). Each
        relation saves the output functions (key: 'variables', value: list of
        variable names) serving as input or output, and the functions for each
        possible output. For a specific output all other variables of the
        relation must serve as input, otherwise a separate relation shall be
        designated.

        relations:
          <relation node>:
            <output variable node>:
              in: <list of input variable nodes>
              fct: "<f(..)>"

        """
        edges = []
        for r in relations:
            outputs = relations[r].keys()
            inputs = []
            for o in relations[r]:
                inputs.extend(relations[r][o]['in'])
            # create input edges to relation
            edges.extend([(i,r) for i in set(inputs)])
            # create output edges from relation
            edges.extend([(r,o) for o in outputs])
        if 'type' not in properties.keys():
            # set the node 'type' according to 'relations'
            properties['type'] = {}
            variables = []
            for r in relations:
                variables.extend(relations[r].keys())
                for o in relations[r]:
                    variables.extend(relations[r][o]['in'])
            for v in set(variables):
                properties['type'][v] = 0
            for r in relations:
                properties['type'][r] = 1
        self.__init_with_edges(edges, properties)

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

    def provided(self, nodes):
        """Returns true, if all nodes are provided."""
        for n in nodes:
            if self.node[n]['type'] == SHSANodeType.R:
                raise RuntimeError("Relations have no property 'provided'.")
            if not self.node[n]["provided"]:
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
            # merge multi-edges into a single bidirectional edge (does not work
            # with labels, though)
            f.write("concentrate=true")
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
