

def bfs(graph, start):
    """Breadth-first search.

    See CLRS - Introduction to Algorithms.
    """
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

def bfs_next(graph, visited=set(), queue=[]):
    """Re-entrant BFS additionally returning the breadth-first tree (current queue
    of unvisited vertices).

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
