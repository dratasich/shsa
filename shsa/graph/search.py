"""Search algorithms.

__author__ = "Denise Ratasich"

Algorithms are taken from:
(1) Introduction to Algorithms by Cormen, Leiserson, Rivest and Stein (MIT
    Press, 2009).

"""

# (1) #########################################################################

def bfs(graph, start):
    """Breadth-first search."""
    visited = set()
    queue = [start] # first-in, first-out queue
    # as long as there is an unvisited vertex
    while queue:
        vertex = queue.pop(0)
        if vertex not in visited:
            # mark vertex as processed
            visited.add(vertex)
            # add all (not yet visited) adjacents of vertex to the queue
            adjacents = set(graph[vertex])
            queue.extend(adjacents - visited)
    return visited

# adapted from bfs(..)
def bfs_next(graph, visited=set(), queue=[]):
    """Re-entrant BFS additionally returning the breadth-first tree (current
    queue of unvisited vertices).

    """
    if queue:
        # next vertex to process
        vertex = queue.pop(0)
        if vertex not in visited:
            # mark vertex as processed
            visited.add(vertex)
            # add all (not yet visited) adjacents of vertex to the queue
            adjacents = set(graph[vertex])
            queue.extend(adjacents - visited)
    return visited, queue
