from profilehooks import timecall
import networkx as nx

from model.shsamodel import SHSAModel

import benchmark


class Ex1(benchmark.Benchmark):
    def __parse_args(self):
        self._parser.add_argument('-b', '--branch', type=int, default=5,
                                  help="Branching factor.")
        self._parser.add_argument('-d', '--deptch', type=int, default=5,
                                  help="Depth of the tree.")

    def setup(self):
        # generate model or read from config file
        # balanced
        # nx.generators.classic.balanced_tree(r, h)
        # set internal variables model and root for experiment
        self._model = SHSAModel(configfile="test/model_p6.yaml")
        self._root = 'a'


if __name__ == "__main__":
    print("""test/model_p6.yaml""")
    ex1 = Ex1()
    ex1.setup()
    ex1.run()
