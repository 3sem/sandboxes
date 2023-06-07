import networkx as nx


def load2nxgraph(fn):
    g = nx.DiGraph()
    with open(fn, 'r') as f:
        lines = f.readlines()
        for l in lines:
            ll = l.split(" ")
            if l[0] == "node":
                num = int(ll[1])
                attr = None
                try:
                    attr = l[2]
                except:
                    pass
                g.add_node(ll, name=attr)
            elif l[0] == "edge":
                u = int(l[1])
                v = int(l[2])
                e_attr = None
                try:
                    e_attr = l[3]
                except:
                    pass
                g.add_edge(u, v, attr=e_attr)


def isomorphic(G1, G2) -> bool:
    return nx.is_isomorphic(G1, G2, node_match=True, edge_match=True)
