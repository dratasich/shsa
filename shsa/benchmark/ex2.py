import networkx as nx
import random

from ex1 import Ex1
from model.shsamodel import SHSAModel, SHSANodeType


class Ex2(Ex1):
    def __init__(self):
        super(Ex2, self).__init__()
        self.__visited = None
        self.__sub = None
        random.seed()  # initialize random number generator

    def _parse_args(self):
        super(Ex2, self)._parse_args()
        self._parser.add_argument('-a', '--availability', type=float,
                                  default=0.5, help="""Probability that a
                                  variable is provided in [0,1].""")
        self._parser.add_argument('-i', '--increase', action='store_true',
                                  default=False, help="""Increase the
                                  probability of provided from 'availability'
                                  at root to '1.0' at leaves.""")
        self._parser.add_argument('algorithms', type=str, nargs='+',
                                  choices=['rss', 'rss_once', 'orr', 'dfs',
                                           'dfs_mem'], help="""Algorithms to
                                           execute.""")

    def __properties_provided(self, node, current_depth=0):
        """Recursively sets the provided property of a node randomly
        w.r.t. args.availability."""
        self.__visited.append(node)
        props_prov = {}
        # following nodes
        pre = set(self._model.predecessors(node)) - set(self.__visited)
        # set provided for variable nodes only
        if self._model.is_variable(node) and current_depth > 0:
            rf = random.uniform(0, 1)
            margin = self._args.availability
            if self._args.increase:
                margin = self._args.availability \
                         + (1.0 - self._args.availability) \
                         * (current_depth / self._args.depth)
            if rf <= margin:
                props_prov[node] = True
            else:
                props_prov[node] = False
        # set provided recursively for following nodes
        for n in pre:
            props = self.__properties_provided(n,
                                               current_depth=current_depth+1)
            props_prov.update(props)
        return props_prov

    def _add_solution(self, node):
        """Recursively selects a valid substitution."""
        rels = []
        props_prov = {}
        # following nodes
        pre = set(self._model.predecessors(node)) - set(self.__visited)
        # reached a leaf
        if len(pre) == 0:
            props_prov[node] = True
            return rels, props_prov
        # process following nodes recursively
        if self._model.is_variable(node):
            # node is provided, we don't have to proceed :)
            if self._model.provided([node]):
                return rels, props_prov
            # select the relation with most provided input variables
            rbest = None
            vmost = 0
            for r in pre:
                vin = set(self._model.predecessors(r)) - set([node])
                vin_num_provided = len(vin) - len(self._model.unprovided(vin))
                if vin_num_provided > vmost:
                    r = rbest
                    vmost = vin_num_provided
            R, P = self._add_solution(rbest)
            props_prov.update(P)  # update provided variables (leaves)
            rels.extend(R)  # add relations chosen subsequently
            rels.append(r)  # add chosen relation
        elif self._model.is_relation(node):
            # substitute all unprovided variables
            for v in pre:
                if not self._model.provided([v]):
                    R, P = self._add_solution(node)
                    props_prov.update(P)
                    rels.append(R)
        else:
            assert True, "no other node type"
        return rels

    def setup(self):
        # args check
        if self._args.availability < 0 and self._args.availability > 1:
            raise RuntimeError("""Availability ({}) must be within 0 and 1
            (incl.).""".format(self._args.availability))
        # generate graph, sets model and root
        super(Ex2, self).setup()
        # set provided
        self.__visited = []
        props_prov = self.__properties_provided(self._root)
        nx.set_node_attributes(self._model, 'provided', props_prov)
        # add a solution, such that at least one substitution is possible
        # if not self._args.increase:
        #     self.__visited = []
        #     self.__sub, props_prov = self._add_solution(self._root)
        #     nx.set_node_attributes(self._model, 'provided', props_prov)
        self.algorithms = self._args.algorithms

    def check(self, algorithms=[]):
        # basic checks
        super(Ex2, self).check(algorithms)
        # check if at least the added substitution is found by all algorithms
        if not self._args.increase:
            print("")
            for alg in algorithms:
                found = set(self.__sub) not in self._results[alg].relations()
                print("  {}: {}".format(alg, found))

    def __str__(self):
        ret = super(Ex2, self).__str__()
        ret += "  availability: {}\n".format(self._args.availability)
        ret += "  increase: {}\n".format(self._args.increase)
        return ret


if __name__ == "__main__":
    ex = Ex2()
    ex.setup()
    try:
        groups = ex.run(ex.algorithms)
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
