import networkx as nx

import benchmark
from model.shsamodel import SHSAModel, SHSANodeType


class Ex1(benchmark.Benchmark):
    def __init__(self):
        super(Ex1, self).__init__()

    def _parse_args(self):
        super(Ex1, self)._parse_args()
        self._parser.add_argument('-b', '--branch', type=int, default=2,
                                  help="Branching factor.")
        self._parser.add_argument('-d', '--depth', type=int, default=2,
                                  help="Depth of the tree.")
        self._parser.add_argument('-p', '--plot', type=str,
                                  help="""Plots the model to the given
                                  filename (without extension).""")

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
        # (linear) walk through nodes to set provided
        first_node = 0
        for d in range(0, self._args.depth + 1):
            # number of nodes at level d
            num_nodes = self._args.branch**d
            # skip relations
            if (d % 2) == 1:
                first_node = first_node + num_nodes
                continue
            # set provided value of leaves to True
            for n in range(first_node, first_node + num_nodes):
                if d == self._args.depth:
                    props_prov[n] = True
                else:
                    props_prov[n] = False
            # set id of first node of next level
            first_node = first_node + num_nodes
        return props_prov

    def setup(self):
        # args check
        if self._args.depth % 2 == 1:
            raise RuntimeError("""Depth must be an even number (leaves of the
            graph must be variables).""")
        # generate graph structure
        G = nx.generators.classic.balanced_tree(self._args.branch,
                                                self._args.depth)
        G = G.to_directed()
        # properties
        props = {}
        props['type'] = self.__properties_type()
        props['provided'] = self.__properties_provided()
        # set internal variables model and root for experiment
        self._model = SHSAModel(G, properties=props)
        self._root = 0

    def check(self, algorithms=[]):
        if not self._failed:
            # check results
            # single results won't be compared
            single = True
            for alg, sublist in self._results.items():
                # check only listed algorithms
                if alg not in algorithms:
                    continue
                if len(sublist) != 1:
                    single = False
                print("\n  {}:".format(alg))
                print("    len: {}".format(len(sublist)))
                if self._failed:
                    print("    S: {}".format(list(sublist)))
            # compare results
            print()
            if single:
                return
            for a1, s1 in self._results.items():
                for a2, s2 in self._results.items():
                    # check only listed algorithms
                    if not (a1 in algorithms and a2 in algorithms):
                        continue
                    diff1 = s1.relations() - s2.relations()
                    diff2 = s2.relations() - s1.relations()
                    if len(diff1) > 0:
                        print("  {} - {}: {}".format(a1, a2, diff1))
                    if len(diff2) > 0:
                        print("  {} - {}: {}".format(a2, a1, diff2))

    def __str__(self):
        ret = "\n"
        if self._failed:
            ret += "status: failed\n\n"
            ret += "model:\n"
            ret += "  nodes: {}\n".format(self._model.nodes())
            ret += "  edges: {}\n\n".format(self._model.edges())
        else:
            ret += "status: ok\n\n"
        ret += "parameters:\n"
        ret += "  ncalls: {}\n".format(self._args.ncalls)
        ret += "  branch: {}\n".format(self._args.branch)
        ret += "  depth: {}\n".format(self._args.depth)
        ret += "  root: {}\n".format(self._root)
        ret += "  numnodes: {}\n".format(len(self._model.nodes()))
        ret += "  numedges: {}\n".format(len(self._model.edges()))
        return ret

    def export_model(self):
        if self._args.plot is not None:
            self._model.write_dot(self._args.plot, oformat="pdf")


if __name__ == "__main__":
    ex = Ex1()
    ex.setup()
    try:
        groups = ex.run(['rss', 'rss_once', 'orr', 'dfs_mem'])
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
