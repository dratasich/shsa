#!/usr/bin/python

from graph.graph import Graph

## ORR substitution ###########################################################

class ORR(object):
    """Ontology-based runtime reconfiguration (ORR) engine."""

    def __init__(self, graph, properties):
        """Initializes the engine with a model.

        The keys represent the vertex IDs. Keys of graph and properties must
        match, i.e., each node must have initilialized properties.

        """
        self.__model = Graph(graph)
        self.__type = {}
        self.__provided = {}
        for n in self.__model.vertices():
            self.__type[n] = properties[n]['type']
            if self.__type[n] == 'P':
                self.__provided[n] = properties[n]['provided']

    def substitute_init(self):
        """Initializes the variables for a substitute search."""
        self.__sub_visited = []
        # list of nodes that can be provided by substitution
        self.__sub_provided = []
        # results, i.e., substitution tree
        self.__sub_service = {}
        self.__sub_tree = {}

    def substitute_search(self, r):
        """Original substitute search by Oliver.

        Call substitute_init first!

        This method is called recursively and is self-contained.

        """
        m = self.__model
        # for all n \elemof r.inputs do
        for n in m.adjacents(r):
            if self.__type[n] == 'T':
                # transfer concept
                # omit: check requirements
                # init substitution path
                S = []
                T = [n]
                provided = True
                # for all i \elemof n.inputs \ {r} do
                for i in m.adjacents(n):
                    # ignore where we are coming from
                    if i == r:
                        continue
                    print i
                    # check provision
                    if self.__provided[i] == False:
                        # property not provided -> try to substitute
                        if i not in self.__sub_visited:
                            # n.visited <- true
                            self.__sub_visited.append(i)
                            # recursive substitute search
                            s,t = self.substitute_search(i)
                            # if result is empty
                            if not (s or t):
                                provided = False
                                break # no substitute for n
                            else:
                                self.__sub_provided.append(i)
                                self.__sub_service[i] = s
                                self.__sub_tree[i] = t
                            S.extend(s)
                            T.extend(t)
                        else:
                            provided = false
                            break # no substiute for n
                    else:
                        # property is provided (without substitution)
                        self.__sub_visited.append(n)
                        S.append(i)
                        T.append(i)
                if provided:
                    return S,T
            else:
                # property concept, i.e., direct mapping (same property)
                if self.__provided[n] == False:
                    # property not provided -> try to substitute
                    if i not in self.__sub_visited:
                        # n.visited <- true
                        self.__sub_visited.append(i)
                        # recursive substitute search
                        s,t = self.substitute_search(i)
                        if s and t:
                            self.__sub_provided.append(n)
                            self.__sub_service[n] = s
                            self.__sub_tree[n] = t
                            return s,t
                else:
                    # property provided
                    self.__sub_visited.add(i)
                    return self.__sub_service[n], self.__sub_tree[n]

# test substitution
g = {
    'root': ['t1', 't2', 't3'],
    't1': ['r1', 'r2'],
    't2': ['r3'],
    't3': ['r4', 'r5'],
    'r1': [],
    'r2': ['t4'],
    't4': ['r6', 'r7'],
    'r3': [],
    'r4': [],
    'r5': [],
    'r6': [],
    'r7': [],
}
p = {
    'root': {'type': 'P', 'provided': False},
    'r1': {'type': 'P', 'provided': True},
    'r2': {'type': 'P', 'provided': False},
    'r3': {'type': 'P', 'provided': True},
    'r4': {'type': 'P', 'provided': True},
    'r5': {'type': 'P', 'provided': True},
    'r6': {'type': 'P', 'provided': True},
    'r7': {'type': 'P', 'provided': True},
    't1': {'type': 'T'},
    't2': {'type': 'T'},
    't3': {'type': 'T'},
    't4': {'type': 'T'},
}
engine = ORR(g, p)
engine.substitute_init()
s, t = engine.substitute_search('root')
print s
print t
