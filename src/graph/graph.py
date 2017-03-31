"""Functions for analyzing/manipulating a CFG.

__author__ = "Daniel Prokesch"

* compute dominators
      Keith D. Cooper, Timothy J. Harvey, and Ken Kennedy. A simple, fast
      dominance algorithm. 1991

* loop nest tree
      Robert E. Tarjan. Testing Flow Graph Reducibility. 1974
  extended by
      Ganesan Ramalingam. Identifying Loops in Almost Linear Time. 1999
  extended by me, to compute exit edges and correctly identify self-loops

* regions
      Thomas Ball. What's in a Region?: Or Computing Control Dependence Regions
      in Near-linear Time for Reducible Control Flow. 1993 (with corrected
      pseudocode)
"""

from subprocess import call # call dot to generate .png out of .dot files


def copy_cfg(G):
    """Makes a copy of the CFG (deep copy)."""
    return {k: G[k][:] for k in G}


def reversed_cfg(G):
    """Returns the reversed graph."""
    I = { n: [] for n in G }
    for u, succs in G.iteritems():
        for v in succs:
            I[v].append(u)
    return I


def from_edges(E):
    """Builds a CFG from edges."""
    G = {}
    for u, v in E:
        if u not in G: G[u] = []
        if v not in G: G[v] = []
        G[u].append(v)
    return G


def edges(CFG):
    """Generates edges of a CFG."""
    for u, succ in CFG.iteritems():
        for v in succ: yield (u,v)


def degrees(CFG):
    """Compute degrees of CFG nodes."""
    In  = { n: 0 for n in CFG }
    Out = { n: 0 for n in CFG }
    for u, succ in CFG.iteritems():
        for v in succ:
            Out[u] += 1
            In[v] += 1
    return In, Out


def entry(CFG):
    """Return the entry node of a CFG"""
    In, Out = degrees(CFG)
    for n, din in In.iteritems():
        if din == 0: return n
    return None


def exits(CFG):
    """Return a list of exit nodes of a CFG"""
    In, Out = degrees(CFG)
    return [ n for n, dout in Out.iteritems() if dout == 0 ]

def entry_exit(CFG):
    """Return the entry and the exit of a CFG.

    If there are multiple exits, merge them to a distinguished '_exit' node.
    """
    In, Out = degrees(CFG)
    S = [n for n, din in In.iteritems() if din == 0]
    assert len(S) == 1,\
            "A single entry node is required for a CFG!"
    T = [n for n, dout in Out.iteritems() if dout == 0]
    assert len(T) > 0, "At least one node must be a sink"
    if len(T) != 1:
        t = "_exit"
        assert t not in CFG
        # insert new exit node
        CFG[t] = []
        for n in T:
            CFG[n].append(t)
    else: t = T[0]
    return S[0], t


def edge_numbers(CFG):
    """Edge numbering (F/T branch condition)"""
    return {(n,succ) : bool(i) for n in CFG
            for i, succ in enumerate(CFG[n]) if len(CFG[n]) == 2}


def augment(CFG):
    """Insert unique start and stop nodes.

    Merge multiple exit nodes and insert a false edge _START->_STOP.
    """
    assert("_START" not in CFG)
    assert("_STOP"  not in CFG)
    en = entry(CFG)
    ex = exits(CFG)
    A = copy_cfg(CFG)
    A["_STOP"] = []
    for n in ex:
        A[n].append("_STOP")
    A["_START"] = ["_STOP", en]
    return A


def binarize(G):
    """Transform G such that each node has at most 2 outgoing edges."""
    G = copy_cfg(G)
    def getnextname(v, n):
        oldsfx = ".{:d}".format(n)
        if v.endswith(oldsfx):
            return "{}.{:d}".format(v[:-len(oldsfx)], n+1)
        else:
            return "{}.{:d}".format(v, n+1)

    visited = set()
    def dfs(v, splitnum=0):
        visited.add(v)
        if len(G[v])>2:
            # split
            left = G[v][0]
            right = getnextname(v, splitnum)
            G[right] = G[v][1:]
            G[v] = G[v][0:1]+[right] # strip
            if left not in visited: dfs(left)
            dfs(right, splitnum+1)
        else:
            for w in G[v]:
                if w not in visited: dfs(w)
    dfs(entry(G))
    return G


def dfpo(G, rev=False):
    """Compute a DF reverse postorder."""
    post = []
    visited = set()
    def dfsnum(v):
        visited.add(v)
        for w in G[v]:
            if not w in visited: dfsnum(w)
        post.append(v)
    dfsnum(entry(G))
    if rev: post.reverse()
    return post

def dfo(G):
    """Compute a DF node order."""
    pre = []
    visited = set()
    W = [entry(G)]
    while len(W)>0:
        v = W.pop()
        if v in visited: continue
        visited.add(v)
        pre.append(v)
        W.extend(reversed(G[v]))
    return pre

def dfsnumbers(G, entry):
    """DFS numbers (pre/post) for each node in G, with entry node."""
    pre = {}
    post = {}
    nums = [0, 0]
    visited = set()
    def dfs(v):
        visited.add(v)
        pre[v] = nums[0]
        nums[0] += 1
        for w in G[v]:
            if not w in visited: dfs(w)
        post[v] = nums[1]
        nums[1] += 1
    dfs(entry)
    return pre, post


def dfsnumbers2(G, entry):
    """DFS numbers (start/finish) for each node in G, with entry node."""
    nums = {}
    cnt = [0]
    visited = set()
    def dfs(v):
        visited.add(v)
        start = cnt[0]
        cnt[0] += 1
        for w in G[v]:
            if not w in visited: dfs(w)
        nums[v] = (start, cnt[0])
        cnt[0] += 1
    dfs(entry)
    return nums


def dual_edge(G, e):
    assert type(e) == tuple
    a, b = e
    assert a in G and b in G[a] and len(G[a]) == 2
    succs = G[a]
    return (a, succs[1 - succs.index(b)])

###############################################################################

def dominators(CFG):
    """Compute dominator tree for a given graph."""
    rpo = dfpo(CFG, True)

    ### node <-> index (rpo)
    def idx(n): return rpo.index(n)
    def node(i): return rpo[i]

    ### function for predecessors
    I = reversed_cfg(CFG)
    def preds(n):
        return [idx(pred) for pred in I[node(n)]]

    # initialize doms array
    doms = [None for n in range(len(rpo))]
    # start node
    doms[0] = 0

    def intersect(b1, b2):
        if doms[b2] == None: return b1
        finger1, finger2 = b1 if b1 != None else b2, b2
        while finger1 != finger2:
            while finger1 > finger2:
                finger1 = doms[finger1]
            while finger2 > finger1:
                finger2 = doms[finger2]
        return finger1

    changed = True
    while(changed):
        changed = False
        for b in range(1,len(rpo)):
            new_idom = reduce(intersect, preds(b), None )
            if doms[b] != new_idom:
              doms[b] = new_idom
              changed = True
        #print [node(i) for i in doms]

    return {node(n): (node(idom) if n != 0 else None)
              for n, idom in enumerate(doms) }


def postdominators(CFG):
    return dominators(reversed_cfg(CFG))



def dominates(DT, d, n):
    while n:
        if n == d: return True
        n = DT[n]
    return False


def tree_depth(tree, n):
    t, d = n, 0
    while t:
        d += 1
        t = tree[t]
    return d

def tree_edges(tree):
    return sorted([(v, k) for k, v in tree.iteritems() if v != None],
                  cmp=lambda n1, n2:
                      tree_depth(tree, n1[0])-tree_depth(tree, n2[0]))

###############################################################################

def T1(G):
    """Remove self loops"""
    changed = False
    for k in G:
        if k in G[k]:
          G[k].remove(k)
          changed = True
    return changed


def T2(G):
    """Merge two nodes"""
    changed = False
    # all nodes with a single predecessor
    for n in G.keys():
        I = reversed_cfg(G)
        if len(I[n]) != 1: continue
        pred = I[n][0]
        G[pred].extend(G[n])
        G[pred] = list(set(G[pred]))
        for succs in G.values():
            if n in succs: succs.remove(n)
        del G[n]
        changed = True
    return changed


def reduceT1T2(G):
    """Subsequently perform T1-T2 transformations while possible."""
    Gr = copy_cfg(G)
    changed = True
    while changed:
        changed = T1(Gr) or T2(Gr)
    return Gr


###############################################################################

def backedges(CFG):
    """Natural loop backedges."""
    DT = dominators(CFG)
    #dfn = {n: i for i, n in enumerate(dfpo(CFG, True))}
    #return [(u, v) for u, v in edges(CFG)
    #        if dfn[u] > dfn[v] and dominates(DT, v, u) or v==u]
    return [(u, v) for u, v in edges(CFG) if dominates(DT, v, u)]


def dfo_backedges(CFG):
    """DFS determining order and backedges.

    Equivalent to natural loop backedges in reducible graphs.
    """
    #TODO classify all edges
    visited = set()
    finished = set()
    order = []
    be = []
    def dfs(v):
      visited.add(v)
      order.append(v)
      for w in CFG[v]:
          if w in visited and w not in finished: be.append((v, w))
          if w not in visited: dfs(w)
      finished.add(v)
    dfs(entry(CFG))
    return order, be

def loop(CFG, be):
    """Compute the natural loop for a backedge (maximal SCR)."""
    n, d = be
    if d==n: return [d] # shortcut for self-loops
    I = reversed_cfg(CFG)
    L = [d, n]
    stack = [n]
    while len(stack)>0:
        m = stack.pop()
        for p in I[m]:
            if p not in L:
                L.append(p)
                stack.append(p)
    exitedges = [(n,m) for n in L for m in CFG[n] if m not in L]
    return L, exitedges


def domfrontiers(CFG, DT=None):
    """Compute dominance frontier edges for each node."""
    if not DT: DT = dominators(CFG)
    DF = { n: [] for n in CFG }
    ce = [ (a,b) for a, b in edges(CFG) if len(CFG[a])>1 ]
    for a, b in ce:
        t = b
        while t != DT[a]:
            DF[t].append((a,b))
            t = DT[t]
    return DF


def controldep(CFG):
    """Compute control dependence edges for each node."""
    PDT = postdominators(CFG)
    return domfrontiers(CFG, PDT)


def iterated_cd(CFG, node):
    """Compute the iterated control dependence of a CFG node."""
    E = set() # resulting set of edges
    CD = controldep(CFG)
    W = list(CD[node]) # worklist
    while len(W)>0:
      (u,v) = W.pop()
      E.add((u,v))
      #W.extend([e for e in CD[u] if e not in E])
      W.extend(filter(lambda e: e not in E, CD[u]))
    return E

def regions(CFG):
    """Compute weak regions in CFG. (Ball 92, with correction)"""
    # domtree: n -> n.parent view
    DT = dominators(CFG)
    # postdomtree: p -> p.children view
    PDT = {}
    for n, par in postdominators(CFG).iteritems():
        if par: PDT.setdefault(par, []).append(n)
    whead, wtail = {}, {}
    wregion, wnext, wprev = {}, {}, {}
    region_num = [1]
    def dfs(v, num):
        wregion[v], wprev[v] = num, None
        whead[num] = v
        for w in PDT.get(v, []):
            if DT[v] == w:
                wprev[v], wnext[w] = w, v
                dfs(w, num)
            else:
                region_num[0] += 1
                wtail[region_num[0]], wnext[w] = w, None
                dfs(w, region_num[0])

    ex = exits(CFG)
    assert len(ex) == 1, "require a single exit node"
    exn = ex[0]
    wtail[region_num[0]] = exn
    wnext[exn] = None
    dfs(exn, 1)
    print "wregion", wregion
    print "whead", whead
    print "wtail", wtail
    print "wnext", wnext
    print "wprev", wprev


###############################################################################

def loop_nest_tree(CFG):
    """Compute the loop nest tree (Tarjan74)"""
    dfo, backedges = dfo_backedges(CFG)
    loop_parent = {}
    loops = {}
    exitedges = {}

    RCFG = reversed_cfg(CFG)
    lp = {} # partition, merged bottom up as we build the nesting

    # add artificial back edge for top-level pseudo-loop
    backedges.append(("_STOP", "_START"))

    def collapse(body, h):
        """Collapse a loop found (an empty body denotes a self-loop)."""
        loops[h] = body
        for z in body:
            loop_parent[z] = h
            uf_union(lp, h, z)

        # determine exit edges for h
        # find any edges going out the (enlarged) partition of h
        exitedges[h] = []
        for a in body.union([h]):
            # edges to consider: successors of subloops/nodes
            E = exitedges[a] if a != h and a in loops \
                             else [(a,b) for b in CFG[a]]
            for u, v in E:
                if uf_find(lp, v) != h:
                    exitedges[h].append((u,v))

    def findloop(h):
        body = set()
        # all latch nodes with a backedge to header h
        latches = [uf_find(lp, y) for y, dst in backedges if dst==h]

        # collect body members
        W = set(latches).difference([h])
        while len(W) > 0: # while worklist not empty
            y = W.pop()
            assert dfo.index(y) > dfo.index(h), "Irreducible loop!"
            body.add(y)
            # for every predecessor z of y such that z->y is not a backedge
            for z in RCFG[y]:
                if (z,y) in backedges: continue
                zp = uf_find(lp, z)
                if zp not in body | W | set([h]):
                    W.add(zp)

        # store and collapse the loop
        collapse(body, h)

    # initialize
    for n in dfo:
        loop_parent[n] = None
        uf_add(lp, n)
    # for every header node (in reverse dfs-order) find loop
    headers = set(h for (l,h) in backedges)
    for n in reversed(dfo):
        if n in headers: findloop(n)

    backedges.remove(("_STOP", "_START"))
    return loops, loop_parent, backedges, exitedges


###############################################################################

def dot2png(basefilename):
    """Call dot to convert the graphviz file"""
    call(["/usr/bin/dot", "-Tpng", "-o",
          "{}.png".format(basefilename),
          "{}.dot".format(basefilename)])


def write_graph(basefilename, edges, tree=False, highlight_edges=[]):
    # bold red line
    highlight = " [color=\"#ff0000\", penwidth=2]"
    if tree:
        gtype="graph"
        etype="--"
    else:
        gtype="digraph"
        etype="->"
    with open("{}.dot".format(basefilename), "w") as f:
        f.write("{} \"{}\" {{\n".format(gtype, basefilename))
        f.write("  node [fontname=\"sans-serif\"];\n")
        for u, v in edges:
            f.write("  \"{0}\" {2} \"{1}\"{3};\n".format(u, v, etype,
                    highlight if (u,v) in highlight_edges else ""))
        f.write("}\n")
    dot2png(basefilename)


def load_file(fname):
    """Return the contents of a file (caution: eval -> security!)

    Intended to be used as loading a CFG dictionary from a file.
    """
    with open(fname, "r") as f:
        X = eval(f.read())
    return X



###############################################################################

def uf_add(uf, v):
    uf[v] = v

def uf_find(uf, v):
    """Union-find 'find' operation with path compression."""
    w = v
    while uf[w] != w:
        w = uf_find(uf, uf[w])
    return w

def uf_union(uf, s1, s2):
    """Union-find 'union' operation.

    Don't use ranking as we need control of the representative."""
    r1, r2 = uf_find(uf, s1), uf_find(uf, s2)
    uf[r2] = r1
    return r1
