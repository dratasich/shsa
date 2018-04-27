"""Substitution, i.e., (intermediate) result of self-healing by structural
adaptation.

"""

from future.standard_library import install_aliases
install_aliases()
from collections import UserList
import networkx as nx
from subprocess import call  # call dot to generate .png out of .dot files

from model.shsamodel import SHSANodeType
from model.utility import *


class Substitution(UserList):
    """Substitution class."""

    def __init__(self, *args, **kwargs):
        """Initializes a substitution.

        Constructor is required to have this shape (model and root optional in
        `**kwargs`).
        https://docs.python.org/3.2/library/collections.html#collections.UserList

        """
        # defaults
        self.model = None
        """SHSA model (used to get the utility of a node)."""
        self.root = None
        """SHSA root, the node to substitute."""
        self.utility_fct = UtilityNorm()
        """Utility function to use."""
        # extract substitution related arguments
        if 'model' in kwargs.keys():
            self.model = kwargs['model']
            del kwargs['model']
        if 'root' in kwargs.keys():
            self.root = kwargs['root']
            del kwargs['root']
        if 'utility_fct' in kwargs.keys():
            self.utility_fct = kwargs['utility_fct']
            del kwargs['utility_fct']
        # initialize list
        super(Substitution, self).__init__(*args, **kwargs)

    def __get_model(self):
        return self.__model

    def __set_model(self, model):
        self.__model = model

    model = property(__get_model, __set_model)

    def __get_root(self):
        return self.__root

    def __set_root(self, root):
        if self.model is not None:  # if model already set
            if root not in self.model.nodes():
                raise RuntimeError("""Root node {} is not part of the
                model.""".format(root))
        self.__root = root

    root = property(__get_root, __set_root)

    def __get_utility_fct(self):
        return self.__utility_fct

    def __set_utility_fct(self, utility_fct):
        self.__utility_fct = utility_fct

    utility_fct = property(__get_utility_fct, __set_utility_fct)

    def __get_utility(self):
        return self.__utility_fct.utility_of_substitution(self)

    utility = property(__get_utility)

    def relations(self):
        """Returns set of relations involved in the substitution."""
        return frozenset(self)

    def requirements_ok(self):
        """Returns false if the substitution does not fulfil the requirements.

        Uses `self.tree()` to get the substitution tree and input
        variables. Note, that the properties are not saved in the graph
        returned by `self.tree()`, so the original model has to be used to
        retrieve properties of nodes.

        Possible improvement:
        - Maintain the requirements_ok flag by checking the requirements of the
          last added node.

          LEMMA (to be proven): subtrees and combinations of subtrees from the
          adjacents are ok, hence only the added relation node has to be
          checked.

        """
        # substitution empty, thats also fine
        if len(self) == 0:
            return True
        # get tree and input variables
        _, vin = self.tree()
        # check provision of source nodes
        return self.model.provided(vin)

    def tree(self, collapse_variables=True):
        """Returns a graph based on the substitution nodes.

        Returns self.model intersect self (nodes) + self.model structure (by
        BFS). Additionally saves the properties from the SHSA model. Note,
        assumes only relations are part of the nodes in this list.

        Possible improvement:
        - Maintain the tree with adding nodes.

        """
        if len(self) == 0:
            raise RuntimeWarning("Substitution is empty.")
        g = nx.DiGraph()
        inputs = []
        # bfs through relations
        visited = set()
        queue = [self.root]  # first-in, first-out queue
        # as long as there is an unvisited vertex
        while queue:
            node = queue.pop(0)
            if node not in visited:
                # mark node as processed
                visited.add(node)
                # get predecessors excluding the node where we come from
                adjacents = set(self.model.predecessors(node)) - visited
                # if its a variable node we proceed only with the relation in
                # the substitution list and add edges
                if self.model.is_variable(node):
                    # filter relations that are part of the substitution
                    adjacents = adjacents & set(self)
                    # save the input variables additionally
                    if len(adjacents) == 0:
                        inputs.append(node)
                queue.extend(adjacents - visited)
                for a in adjacents:
                    g.add_edge(a, node)
        # remove intermediate variables
        if collapse_variables:
            nremove = []
            for n in g.nodes():
                # skip relation nodes
                if self.model.is_relation(n):
                    continue
                # get all variable nodes with 2 edges
                e1 = list(g.predecessors(n))
                e2 = list(g.successors(n))
                if len(e1) != 1 or len(e2) != 1:
                    continue
                e1 = e1[0]
                e2 = e2[0]
                g.add_edge(e1, e2)
                nremove.append(n)
            # finally remove variable nodes including adjacent edges
            g.remove_nodes_from(nremove)
        return g, inputs

    def __gen_code(self):
        """Generates code and inputs for the given substitution.

        Returns the input topics and the python code to execute. The transfer
        node executes the code in the form of "y=f(x)". Whereas x is a vector
        of values received as inputs, and y is the value of the output.

        """
        # dfs of substitution tree
        t, vin = self.tree(collapse_variables=False)
        n_ordered = nx.dfs_postorder_nodes(nx.Graph(t), self.__root)
        # execute functions (start with sources)
        code = "\n"
        for n in n_ordered:
            if self.__model.is_relation(n):
                # I/O variables of relation
                iv = ",".join(t.predecessors(n))  # input
                ov = list(t.successors(n))[0]  # output
                # define relation as function
                code += "def " + n + "(" + iv + "):\n"
                code += "    return (" \
                        + self.__model.property_value_of(n, 'fct')[ov] \
                        + ")\n\n"
                # execute relation
                code += ov + " = " + n + "(" + iv + ")\n\n"
        # set output
        code += "substitution_result = " + self.__root  # assign output
        return vin, code

    def execute(self, inputs):
        """Executes the substitution given the value per input variable.

        inputs -- Dictionary of variable->value.

        """
        output = None
        # code generate substitution tree (ROS shsa_node.py)
        vin, code = self.__gen_code()
        if not set(vin).issubset(set(inputs.keys())):
            raise RuntimeError("Missing inputs to execute the substitution.")
        # execute the code
        local_vars = inputs
        exec(code, None, local_vars)
        return local_vars['substitution_result']

    def write_dot(self, basefilename, oformat=None):
        """Saves the model as dot-file and generates an image if oformat given.

        basefilename -- Name of the dot-file to generate.
        oformat -- Desired output format, e.g., "eps", "png" or "pdf". The
                   generated dot-file is converted to the given format.
        """
        # create structure
        tree, vin = self.tree(collapse_variables=True)
        # dot settings
        gtype = "graph"
        etype = "--"
        with open("{}.dot".format(basefilename), "w") as f:
            f.write("{} \"{}\" {{\n".format(gtype, basefilename))
            f.write("  node [fontname=\"sans-serif\"];\n")
            for n in tree.nodes():
                nodestyle = ""
                if self.model.is_relation(n):
                    nodestyle += "shape=box"
                f.write(" \"{0}\" [{1}];\n".format(n, nodestyle))
            for u, v in tree.edges():
                f.write(" \"{0}\" {2} \"{1}\";\n".format(u, v, etype))
            f.write("}\n")
        if oformat:
            call(["/usr/bin/dot", "-T" + oformat, "-o",
                  basefilename + "." + oformat, basefilename + ".dot"])

    def __str__(self):
        u = self.utility_fct.best()
        if len(self) > 0:
            u = self.utility
        return "U = " + str(u) + " | " + str(list(self))
