"""Substitution, i.e., (intermediate) result of self-healing by structural
adaptation.

"""

import networkx as nx
from subprocess import call # call dot to generate .png out of .dot files

from model.shsamodel import SHSANodeType

class Substitution(object):
    """Substitution class."""

    def __init__(self, model, root, nodes=None, utility=None):
        """Initializes a substitution."""
        self.__model = model
        """SHSA model (used to get the utility of a node)."""
        self.__root = root
        self.__tree = []
        self.__utility = 0
        if nodes:
            self.__tree = nodes
        if utility:
            self.__utility = utility
        if utility and not nodes:
            raise RuntimeError("Only utilities specified without nodes")

    def __get_utility(self):
        return self.__utility

    utility = property(__get_utility)

    def add(self, node, utility):
        """Adds a node and its utility to the substitution."""
        if self.__model.node[node]['type'] == SHSANodeType.V:
            raise RuntimeError("Variable nodes are not allowed to be added")
        self.__tree.append(node)
        self.__utility += utility

    def add_node(self, node):
        """Adds a node and its utility to the substitution."""
        self.__tree.append(node)
        try:
            self.__utility += self.__model.utility_of(node)
        except:
            raise RuntimeError("Could not retrieve the utility (no model?)")

    def relations(self):
        """Returns set of relations involved in the substitution."""
        return frozenset(self.__tree)

    def tree(self):
        """Returns a graph based on the substitution nodes.

        Returns self.__model intersect self.__nodes + self.__model structure.
        Note, assumes only relations are part of the tree.

        """
        if len(self.__tree) == 0:
            raise RuntimeWarning("No solution found (substitution is empty).")
        g = nx.DiGraph()
        g.add_edge(self.__tree[0], self.__root) # add root node to graph
        visited = set(self.__root) # exclude added variables
        for r1 in self.__tree:
            variables = set(self.__model.predecessors(r1)) - visited
            for v in variables:
                visited.add(v)
                # check connected relation:
                # - should be part of the tree
                # - exclude relation where we are coming from (r!=r1)
                relations = list(filter(lambda r: r in self.__tree and r != r1,
                                        self.__model.predecessors(v)))
                if len(relations) == 1:
                    # following transfer function (passing v)
                    g.add_edge(relations[0], r1)
                elif len(relations) == 0:
                    # leaf/sink node
                    g.add_edge(v, r1)
                else:
                    # more than one transfer functions for a variable in the
                    # substitution is not allowed
                    raise RuntimeError("Substitution faulty.")
        return g

    def write_dot(self, basefilename, oformat=None):
        """Saves the model as dot-file and generates an image if oformat given.

        basefilename -- Name of the dot-file to generate.
        oformat -- Desired output format, e.g., "eps", "png" or "pdf". The
                   generated dot-file is converted to the given format.
        """
        # create structure
        tree = self.tree()
        # dot settings
        gtype = "graph"
        etype = "--"
        with open("{}.dot".format(basefilename), "w") as f:
            f.write("{} \"{}\" {{\n".format(gtype, basefilename))
            f.write("  node [fontname=\"sans-serif\"];\n")
            for n in tree.nodes():
                nodestyle = ""
                if self.__model.node[n]['type'] == SHSANodeType.R:
                    nodestyle += "shape=box"
                f.write(" \"{0}\" [{1}];\n".format(n, nodestyle))
            for u, v in tree.edges():
                f.write(" \"{0}\" {2} \"{1}\";\n".format(u, v, etype))
            f.write("}\n")
        if oformat:
            call(["/usr/bin/dot", "-T" + oformat, "-o",
                  basefilename + "." + oformat, basefilename + ".dot"])

    def __str__(self):
        return "U = " + str(self.__utility) + " | " + str(self.__tree)
