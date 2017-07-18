"""Substitution, i.e., (intermediate) result of self-healing by structural
adaptation.

"""

import networkx as nx
from subprocess import call # call dot to generate .png out of .dot files

from model.shsamodel import SHSANodeType

class Substitution(list):
    """Substitution class."""

    def __init__(self, model, root, *args, **kwargs):
        """Initializes a substitution."""
        super(Substitution, self).__init__(*args, **kwargs)
        self.__model = model
        """SHSA model (used to get the utility of a node)."""
        self.__root = root

    def __get_utility(self):
        """Returns the sum of node-utilities.

        Could be improved by saving the overall utility when adding nodes,
        i.e., utility could be maintained. However, each list extension has to
        be overloaded.

        """
        return sum([self.__model.utility_of(n) for n in self])

    utility = property(__get_utility)

    def relations(self):
        """Returns set of relations involved in the substitution."""
        return frozenset(self)

    def tree(self):
        """Returns a graph based on the substitution nodes.

        Returns self.__model intersect self.__nodes + self.__model structure.
        Note, assumes only relations are part of the tree.

        """
        if len(self) == 0:
            raise RuntimeWarning("Substitution is empty.")
        g = nx.DiGraph()
        g.add_edge(self[0], self.__root) # add root node to graph
        visited = set(self.__root) # exclude added variables
        for r1 in self:
            variables = set(self.__model.predecessors(r1)) - visited
            for v in variables:
                visited.add(v)
                # check connected relation:
                # - should be part of the tree
                # - exclude relation where we are coming from (r!=r1)
                relations = list(filter(lambda r: r in self and r != r1,
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
        return "U = " + str(self.utility) + " | " + str(list(self))
