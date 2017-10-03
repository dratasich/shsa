import networkx as nx

import benchmark
from model.shsamodel import SHSAModel, SHSANodeType


class Ex1(benchmark.Benchmark):
    def __init__(self):
        super(Ex1, self).__init__()
        self.__visited = None

    def _parse_args(self):
        super(Ex1, self)._parse_args()
        self._parser.add_argument('-b', '--branch', type=int, default=2,
                                  help="Branching factor.")
        self._parser.add_argument('-d', '--depth', type=int, default=2,
                                  help="Depth of the tree.")
        self._parser.add_argument('-p', '--plot', type=str,
                                  help="""Plots the model to the given
                                  filename (without extension).""")

    def __properties_type(self, graph, node, ntype=SHSANodeType.V):
        """Recursively sets the type of a node (alternating between variable
        and relation)."""
        self.__visited.append(node)
        props_type = {}
        props_type[node] = ntype
        if ntype == SHSANodeType.V:
            ntype_next = SHSANodeType.R
        elif ntype == SHSANodeType.R:
            ntype_next = SHSANodeType.V
        else:
            assert True, "no/wrong node type"
        pre = set(graph.predecessors(node)) - set(self.__visited)
        for n in pre:
            props = self.__properties_type(graph, n, ntype_next)
            props_type.update(props)
        return props_type

    def __properties_provided(self, graph, node):
        """Recursively sets the provided property of a node (leafs will be
        provided)."""
        self.__visited.append(node)
        props_prov = {}
        # following nodes
        pre = set(graph.predecessors(node)) - set(self.__visited)
        # reached leaf?
        if len(pre) == 0:
            props_prov[node] = True
        else:
            props_prov[node] = False
        # set provided recursively for following nodes
        for n in pre:
            props = self.__properties_provided(graph, n)
            props_prov.update(props)
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
        root = 0
        props = {}
        # set type
        self.__visited = []
        ntype = self.__properties_type(G, root, SHSANodeType.V)
        props['type'] = ntype
        # set provided
        self.__visited = []
        nprovided = self.__properties_provided(G, root)
        props['provided'] = nprovided
        # set internal variables model and root for experiment
        self._model = SHSAModel(G, properties=props)
        self._root = root

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
        ret = ""
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
    ex1 = Ex1()
    ex1.setup()
    try:
        groups = ex1.run(['rss', 'rss_once', 'orr', 'dfs_mem'])
    except Exception as e:
        raise
    finally:
        print(ex1)
        # separately check different types of algorithms executed by run
        print("results:")
        for algs in groups:
            ex1.check(algs)
        ex1.export_model()
        print("\nmeasurements:")
        # here come the profilehooks results
