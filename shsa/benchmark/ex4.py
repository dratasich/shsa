import networkx as nx
import random
import numpy as np

from ex2 import Ex2
from model.shsamodel import SHSAModel, SHSANodeType


class Ex4(Ex2):
    def __init__(self):
        super(Ex4, self).__init__()
        random.seed()

    def __random_branch_sequence(self):
        seq = {}
        # create branch sequence
        first_node = 0
        num_nodes = 1
        for d in range(self._args.depth):
            seq[d] = []
            num_nodes_next = 0
            for n in range(first_node, first_node + num_nodes):
                # create a random number of predecessor nodes
                branch = random.randint(1, self._args.branch)
                seq[d].append(branch)
                num_nodes_next += branch
            # prepare for the next depth
            first_node = first_node + num_nodes_next
            num_nodes = num_nodes_next
        seq[len(seq)] = [0] * num_nodes
        return seq

    def __random_tree(self):
        self._seq = self.__random_branch_sequence()
        G = nx.DiGraph()
        props = {}
        props['type'] = {}
        props['provided'] = {}
        # add nodes
        nodes = {}
        nodes[0] = [0]
        first_node = 1
        for d in range(1, self._args.depth + 1):
            numnodes = sum(self._seq[d-1])
            nodes[d] = list(range(first_node, first_node + numnodes))
            first_node += numnodes
        for n in nodes.values():
            G.add_nodes_from(n)
        # add edges, set properties
        for d in range(self._args.depth + 1):
            first_target_i = 0
            for i in range(len(nodes[d])):
                n = nodes[d][i]
                branches = self._seq[d][i]
                indices = range(first_target_i, first_target_i + branches)
                targets = [nodes[d+1][i] for i in indices]
                # add edges
                for t in targets:
                    G.add_edge(t, n)
                first_target_i += branches
                # set properties
                props['type'][n] = self.__property_type(d)
                props['provided'][n] = self.__property_provided(d)
        return G, props

    def __property_type(self, depth):
        return self.__ntypes[depth % 2]

    def __property_provided(self, depth):
        if depth == 0:
            return False
        return random.uniform(0, 1) <= self.__availability[depth-1]

    def setup(self):
        # prepare variables from argument parsing
        self.__ntypes = [SHSANodeType.V, SHSANodeType.R]
        self.__availability = np.linspace(self._args.availability, 1.0,
                                          self._args.depth)
        # generate graph structure
        G, props = self.__random_tree()
        # set internal variables model and root for experiment
        self._model = SHSAModel(G, properties=props)
        self._root = 0

    def __str__(self):
        ret = super(Ex4, self).__str__()
        return ret


if __name__ == "__main__":
    ex = Ex4()
    ex.setup()
    try:
        groups = ex.run(ex._args.algorithms)
    except Exception as e:
        raise
    finally:
        print(ex)
        ex.export_model()
        # separately check different types of algorithms executed by run
        print("results:")
        for algs in groups:
            ex.check(algs)
        print("\nmeasurements:")
        # here come the profilehooks results
