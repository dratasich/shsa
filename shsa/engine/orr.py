"""Ontology-based Runtime Reconfiguration.

Implements substitute search algorithm as stated in Hoeftberger, 2013:
Ontology-based Runtime Reconfiguration of Distributed Embedded Real-Time
Systems.

"""

from graph.graph import Graph

class ORR(object):
    """Ontology-based runtime reconfiguration (ORR) engine."""

    def __init__(self, graph, properties):
        """Initializes the engine with a model.

        The keys represent the vertex IDs. Keys of graph and properties must
        match, i.e., each node must have initilialized properties.

        graph -- Graph structure as dictionary.
        properties -- Type and provision of nodes in the graph.

        """
        self.__model = Graph(graph)
        self.__type = {}
        self.__provided = {}
        for n in self.__model.nodes():
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
