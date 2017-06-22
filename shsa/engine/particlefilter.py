"""Self-Healing by Structural Adaptation (SHSA) using a particle filter for
substitute search.

"""

from engine.shsa import SHSA
from model.shsamodel import SHSAModel, SHSANodeType

class ParticleFilter(SHSA):
    """Self-Healing by Structural Adaptation (SHSA) particle filter."""

    def __init__(self, graph=None, properties=None, configfile=None):
        """Initializes the search engine."""
        super(ParticleFilter, self).__init__(graph, properties, configfile)

    def substitute(self, root, best=1.0, lookahead=0):
        """Substitute search via particles.

        The "working tree" is the tree with the highest utility (which is the
        sum of utilities of the nodes). The working tree is processed until its
        utility falls below the utility of another tree in the list. For each
        tree a queue of nodes to proceed exists.

        Returns: Possible substitutions as array of relation nodes and its
          corresponding utilities. Variables are not part of the substitution
          tree.

        Possible improvements:
          - Create class of this method (SHSA is the engine's interface,
            SHSAParticleFilter the implementation).
          - Class for U,T,queues (e.g., Substitution).

        """
        # validate inputs
        assert self.model.property_value_of(root, 'type') == SHSANodeType.V, \
        "substitution for relation"
        if best <= 0 or best > 1:
            assert False, "invalid param 'best', must be within ]0,1]"
        if lookahead > 0:
            assert False, "param 'lookahead': not yet implemented"
        # init
        wti = 0 # index of the working tree in T
        U = [0] # utilities (one utility per tree; sum over nodes' utilities)
        T = [[]] # (substitution) trees
        queues = [[root]] # queues (one queue per tree)
        visited = set()
        # helper functions (TODO: refactor)
        def next_wti():
            """Returns index of first tree with non-empty queue."""
            for i in range(len(queues)):
                if queues[i]:
                    return i
            return -1
        # as long as there is an unvisited vertex
        while queues[wti]:
            # print "wti: " + str(wti)
            # print "visited: " + str(len(visited))
            # print "queue: " + str(queues[wti])
            node = queues[wti].pop(0)
            # print "node: " + node
            adjacents = self.model.adjacents_of(node)
            adjacents_sorted = adjacents
            # local helpers
            is_variable = self.model.property_value_of(node, 'type') == SHSANodeType.V
            is_relation = self.model.property_value_of(node, 'type') == SHSANodeType.R
            # update U, T, queue
            U[wti] += self.model.utility_of(node)
            if is_relation: # add only relations to substitution trees
                T[wti].append(node)
            # sample on variable nodes
            if is_variable:
                # draw samples from P(edge(node->n))
                # calculate weight for utility
                #w = [p / num_particles for p in particles]
                # probability on edges will reflect the accuracy of fit of the
                # relation given the current value of the variable
                #TODO
                # same probability to get selected for substitution
                weights = [1] * len(adjacents)
                # get utilities
                utilities = [self.model.utility_of(n) for n in adjacents]
                # weight path w.r.t. probability
                utilities = [utilities[i] * weights[i] for i in
                             range(0,len(utilities))]
                adjacents_sorted = [a for (u,a) in
                                    sorted(zip(utilities,adjacents),
                                           reverse=True)]
                # # remove worst relations from the queue and mark them as visited
                # keep = int(round(best*len(adjacents),0))
                # adjacents_sorted = adjacents_sorted[0:keep]
            # add selected adjacents to queue
            if node not in visited:
                visited.add(node)
                if is_variable:
                    # go on ... extend and create new trees if there are
                    # further relations
                    if adjacents_sorted:
                        # copy and append adjacents (i>0) to new trees
                        for a in adjacents_sorted[1:]:
                            U.append(U[wti])
                            t = list(T[wti])
                            #t.append(a)
                            T.append(t)
                            queues.append([a])
                        # extend current working tree with best adjacent
                        a = adjacents_sorted[0]
                        queues[wti].append(a) # append adjacent to queue
                elif is_relation:
                    # if all variables provided it is a valid substitution
                    # stay at this tree because we are almost done
                    # however, we might go on trying to find something better
                    # ... add relations to (new) tree
                    if self.model.all_variables_provided(node):
                        # copy tree
                        U.append(U[wti])
                        t = list(T[wti])
                        T.append(t)
                        queues.append(list(set(adjacents_sorted) - visited))
                        # at sink/leaf nodes, this produces a new tree although
                        # are no more relations
                    else:
                        # append to current working tree
                        queues[wti].extend(set(adjacents_sorted) - visited)
            # sort solutions
            # T = [t for (u,t) in sorted(zip(U,T), reverse=True)]
            # U = sorted(U, reverse=True)
            # TODO: keep best trees
            if not queues[wti]:
                # solution found, proceed to next tree with queue
                # print "Substitution found: " + str(T[wti])
                # TODO: to go on tree with highest utility: sort first
                wti = next_wti()
            print
            print U
            print T
            print queues
        return U, T
