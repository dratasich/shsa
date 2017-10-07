import networkx as nx

import benchmark
from model.shsamodel import SHSAModel, SHSANodeType


class CaseStudy(benchmark.Benchmark):
    def __init__(self):
        super(CaseStudy, self).__init__()

    def _parse_args(self):
        super(CaseStudy, self)._parse_args()
        self._parser.add_argument('root', type=str,
                                  help="""Variable to substitute.""")
        self._parser.add_argument('configfile', type=str,
                                  help="""Configuration file incl. model for
                                  case study.""")
        self._parser.add_argument('-p', '--plot', type=str,
                                  help="""Plots the model to the given
                                  filename (without extension).""")

    def setup(self):
        # set internal variables model and root for experiment
        self._model = SHSAModel(configfile=self._args.configfile)
        self._root = self._args.root

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
        ret += "  configfile: {}\n".format(self._args.configfile)
        ret += "  root: {}\n".format(self._root)
        ret += "  numnodes: {}\n".format(len(self._model.nodes()))
        ret += "  numedges: {}\n".format(len(self._model.edges()))
        return ret

    def export_model(self):
        if self._args.plot is not None:
            self._model.write_dot(self._args.plot, oformat="pdf")


if __name__ == "__main__":
    ex = CaseStudy()
    ex.setup()
    try:
        groups = ex.run(['rss', 'rss_once', 'orr', 'dfs_mem', 'dfs'])
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
