import networkx as nx
import random
import numpy as np

from ex1 import Ex1
from model.shsamodel import SHSAModel, SHSANodeType


class Ex2(Ex1):
    def __init__(self):
        super(Ex2, self).__init__()
        random.seed()  # initialize random number generator

    def _parse_args(self):
        super(Ex2, self)._parse_args()
        self._parser.add_argument('-a', '--availability', type=float,
                                  default=0.5, help="""Probability that a
                                  variable is provided in [0,1].""")
        self._parser.add_argument('algorithms', type=str, nargs='+',
                                  choices=['rss', 'rss_once', 'orr', 'dfs',
                                           'dfs_mem'], help="""Algorithms to
                                           execute.""")

    def __properties_type(self):
        props_type = {}
        # (linear) walk through nodes to set type
        first_node = 0
        ntypes = [SHSANodeType.V, SHSANodeType.R]
        for d in range(self._args.depth + 1):
            # number of nodes at level d
            num_nodes = self._args.branch**d
            # set equal type on level d
            ntype = ntypes[d % 2]
            for n in range(first_node, first_node + num_nodes):
                props_type[n] = ntype
            # set id of first node of next level
            first_node = first_node + num_nodes
        return props_type

    def __properties_provided(self):
        props_prov = {}
        # variable to substitute always not provided
        props_prov[0] = False
        # (linear) walk through nodes to set provided
        availability = np.linspace(self._args.availability, 1.0,
                                   self._args.depth)
        first_node = 1
        for d in range(1, self._args.depth + 1):
            # number of nodes at level d
            num_nodes = self._args.branch**d
            # skip relations
            if (d % 2) == 1:
                first_node = first_node + num_nodes
                continue
            # set provided value randomly
            for n in range(first_node, first_node + num_nodes):
                props_prov[n] = random.uniform(0, 1) <= availability[d-1]
            # set id of first node of next level
            first_node = first_node + num_nodes
        return props_prov

    def setup(self):
        # args check
        if self._args.availability < 0 and self._args.availability > 1:
            raise RuntimeError("""Availability ({}) must be within 0 and 1
            (incl.).""".format(self._args.availability))
        # generate graph, sets model and root
        super(Ex2, self).setup()
        # set provided
        props_prov = self.__properties_provided()
        nx.set_node_attributes(self._model, props_prov, name='provided')

    def __str__(self):
        ret = super(Ex2, self).__str__()
        ret += "  availability: {}\n".format(self._args.availability)
        return ret


if __name__ == "__main__":
    ex = Ex2()
    ex.setup()
    try:
        groups = ex.run(ex._args.algorithms)
    except Exception as e:
        raise
    finally:
        print(ex)
        # separately check different types of algorithms executed by run
        print("results:")
        for algs in groups:
            ex.check(algs)
        ex.export_model()
        print("\nmeasurements:")
        # here come the profilehooks results
