import networkx as nx

import matplotlib.pyplot as plt


def convex_single_src_dst_mining(G: nx.DiGraph, constr: dict):
    max_path_len = constr.get("max_path_len", 5)
    mined_subgraphs = []
    mined_paths = []
    nodeattrs = nx.get_node_attributes(g, 'name')
# get u,v
    for u in G.nodes:
        for v in G.nodes:
            if u == v: # not interested in self-loops
                continue
            #  At first, check reachability from u to v. Then, extract the longest path and check len constrains
            #  If suitable, extract all the paths into template subgraph.
            #  Implementation note:
            #  Sure, there are more convenient ways to check reachability between 2 nodes in graph,
            #  without paths extraction
            #  Nevertheless, I've use all simple paths extraction in this point because of a list of throughouts:
            #  1) We need, at least, extract the longest path, additionally to reachability check
            #  2) If the subgraph is suitable, we also need all paths from it
            #  3) There are function in NetworkX, for prototyping it is acceptable.
            #  Note: on release, there should be not paths extraction, but reachability checking,
            #  then longest path extraction
            sg_paths = list(nx.all_simple_paths(G, u, v))
            if len(sg_paths) > 0:
                max_len = len(max(sg_paths, key=len))
                print("paths", sg_paths, "from", u , "to", v, "max_len", max_len)
                if max_len <= max_path_len:
                    mined_paths.append(sg_paths)
            else:
                continue

    return mined_paths

def get_digraphs_from_sg_paths_list(l: list):
    mined_subgraphs = []
    for sg_paths in l:
        U = nx.subgraph(g, list(set(x for l in sg_paths for x in l)))
        mined_subgraphs.append(U)
    return mined_subgraphs


def convex_multiple_src_mining(G: nx.DiGraph, constr: dict):
    max_path_len = constr.get("max_path_len", 5)
    mined_subgraphs = []
    mined_paths = []
    max_len = 0
# get u,v
    for u in G.nodes:
        for v in G.nodes:
            if u == v: # not interested in self-loops
                continue
            #  At first, check reachability from u to v. Then, extract the longest path and check len constrains
            #  If suitable, extract all the paths into template subgraph.
            #  Implementation note:
            #  Sure, there are more convenient ways to check reachability between 2 nodes in graph,
            #  without paths extraction
            #  Nevertheless, I've use all simple paths extraction in this point because of a list of throughouts:
            #  1) We need, at least, extract the longest path, additionally to reachability check
            #  2) If the subgraph is suitable, we also need all paths from it
            #  3) There are function in NetworkX, for prototyping it is acceptable.
            #  Note: on release, there should be not paths extraction, but reachability checking,
            #  then longest path extraction
            sg_paths = list(nx.all_simple_paths(G, u, v))
            if len(sg_paths) > 0:
                max_len = len(max(sg_paths, key=len))
                print("paths", sg_paths, "from",u , "to", v, "max_len", max_len)
                if max_len <= max_path_len:
                    U = nx.DiGraph()
                    for path in sg_paths:
                       #U.add_nodes_from([(nd, nx.get_node_attributes(g, 'name')) for nd in path] )
                       for i, item in enumerate(path[1:]):
                           U.add_edge(path[i], item)
                    mined_paths.append(sg_paths)
                    mined_subgraphs.append(U)

            else:
                continue

    return mined_paths, mined_subgraphs


def testG1(hop_w=-1):
    g = nx.DiGraph()
    g.add_node(1, name="load")
    g.add_node(2, name="un_op")
    g.add_node(3, name="bin_op2")
    g.add_node(4, name="bin_op1")
    g.add_node(5, name="store")
    g.add_node(6, name="load")
    g.add_node(7, name="store")
    g.add_node(8, name="load")
    g.add_edge(1, 2, hop=hop_w)
    g.add_edge(1, 3, hop=hop_w)
    g.add_edge(2, 4, hop=hop_w)
    g.add_edge(3, 4, hop=hop_w)
    g.add_edge(3, 5, hop=hop_w)
    g.add_edge(6, 7, hop=hop_w)
    g.add_edge(8, 3, hop=hop_w)
    return g


if __name__ == '__main__':
    g = testG1()

    res_ = convex_single_src_dst_mining(g,  {})
    res = get_digraphs_from_sg_paths_list(res_)

    for g in res:
        color_map = []
        for node in g:
            if g.in_degree(node) == 0:
                color_map.append('orange')
            elif g.out_degree(node) == 0:
                color_map.append('red')
            else:
                color_map.append('lightblue')
        nx.draw_networkx(g, node_color=color_map, with_labels=True)
        plt.show()
