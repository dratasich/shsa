"""Exporting graphs.

__author__ Daniel Prokesch
"""

def write_graph(self, fname):
    with open(fname + ".dot", "w") as f:
        f.write(('digraph DynCFG_{0} {{\n'
                '  graph[label="Dynamic CFG for \'{0}\' from trace", '
                         'ranksep=0.25, fontname="sans-serif"];\n'
                '  edge [fontname="sans-serif"];\n'
                '  node [shape=rectangle, '
                         'fontname="sans-serif"];\n').format(self.name))
        # print blocks in dfs-order
        visited = set()
        # due to python's bad recursion handling, use an iteratively
        # implemented depth-first search
        stack = [(None, self.entry)]
        while len(stack) > 0:
            prev, addr = stack.pop()
            if addr not in visited:
                label = "{0:#08x}".format(addr) \
                        if type(addr) == type(0xffffffff) else addr
                f.write('  {} [label="{}"];\n'.format(addr, label))
            if prev:
                f.write('  {} -> {} [label="{}"];\n'.format(
                    prev, addr, self.cfg[prev][addr]))
            if addr in visited: continue
            visited.add(addr)
            if addr in self.cfg:
                stack.extend([(addr, succ) for succ in self.cfg[addr]])
        f.write('}\n')
    assert(f.closed)
    call(["/usr/bin/dot", "-Tpng", "-o", fname + ".png", fname + ".dot"])
