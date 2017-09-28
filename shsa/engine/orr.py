"""Ontology-based Runtime Reconfiguration.

Implements substitute search algorithm as stated in Hoeftberger, 2013:
Ontology-based Runtime Reconfiguration of Distributed Embedded Real-Time
Systems.

"""

from engine.shsa import SHSA


class ORR(SHSA):
    """Ontology-based runtime reconfiguration (ORR) engine."""

    def __init__(self, model=None, graph=None, properties=None,
                 configfile=None):
        """Initializes the search engine."""
        super(ORR, self).__init__(model, graph, properties, configfile)
        self.__provided = {}
        for n in self.model.nodes():
            if self.model.is_variable(n):
                self.__provided[n] = self.model.provided([n])

    def substitute_init(self):
        """Initializes the variables for a substitute search."""
        self.__sub_visited = []
        # list of nodes that can be provided by substitution
        self.__sub_provided = []
        # results, i.e., substitution tree
        self.__sub_service = {}
        self.__sub_tree = {}

    def substitute(self, r):
        """Original substitute search by Oliver.

        Call substitute_init first!

        This method is called recursively and is self-contained.

        """
        m = self.model
        # substitute called for a variable although provided
        if m.provided([r]):
            return [r], [r]
        # for all n \elemof r.inputs do
        rinputs = set(m.predecessors(r))
        if len(rinputs) == 0:
            # no relations, no substitution possible
            return None, None
        for n in rinputs:
            if m.is_relation(n):
                # transfer concept
                # omit: check requirements
                # init substitution path
                S = []
                T = [n]
                provided = True
                # for all i \elemof n.inputs \ {r} do
                ninputs = set(self.model.predecessors(n)) - set([r])
                for i in ninputs:
                    # check provision
                    if self.__provided[i] is False:
                        # property not provided -> try to substitute
                        if i not in self.__sub_visited:
                            # n.visited <- true
                            self.__sub_visited.append(i)
                            # recursive substitute search
                            s, t = self.substitute(i)
                            # if result is empty
                            if not (s or t):
                                provided = False
                                break  # no substitute for n
                            else:
                                self.__sub_provided.append(i)
                                self.__sub_service[i] = s
                                self.__sub_tree[i] = t
                            S.extend(s)
                            T.extend(t)
                        else:
                            provided = False
                            break  # no substiute for n
                    else:
                        # property is provided (without substitution)
                        self.__sub_visited.append(n)
                        S.append(i)
                        T.append(i)
                if provided:
                    return S, T
            else:
                # property concept, i.e., direct mapping (same property)
                if self.__provided[n] is False:
                    # property not provided -> try to substitute
                    if i not in self.__sub_visited:
                        # n.visited <- true
                        self.__sub_visited.append(i)
                        # recursive substitute search
                        s, t = self.substitute(i)
                        if s and t:
                            self.__sub_provided.append(n)
                            self.__sub_service[n] = s
                            self.__sub_tree[n] = t
                            return s, t
                else:
                    # property provided
                    self.__sub_visited.add(i)
                    return self.__sub_service[n], self.__sub_tree[n]
