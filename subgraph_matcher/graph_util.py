import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt
import more_itertools
import itertools


def convex_single_src_dst_mining(G: nx.DiGraph, constr: dict, fixed_output=None):
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


def get_digraphs_from_sg_paths_list(l: list, g: nx.DiGraph, max_path_len=5):
    mined_subgraphs = []
    for sg_paths in l:
        U = nx.subgraph(g, list(set(x for l in sg_paths for x in l)))
        lp = nx.dag_longest_path(U)
        lp_len = len(lp)
        if 0 < lp_len <= max_path_len:
            mined_subgraphs.append(U)
    return mined_subgraphs


def flatten(l):
    return [item for sublist in l for item in sublist]


def convex_multiple_src_mining(G: nx.DiGraph, constr: dict):
    max_path_len = constr.get("max_path_len", 5)
    mined_subgraphs = []
    mined_paths = []
    res = []
    max_len = 0
# get u,v
    for v in G.nodes:
        lgn = list(G.nodes)
        lgn.remove(v)
        subgraph_paths_list = []
        power_set = list(more_itertools.powerset(lgn))[1:]

        for S in power_set: # for each set S in powerset
            subgraph_paths_list.clear()
            for u in S: # for each element u in set S
                sg_paths = list(nx.all_simple_paths(G, u, v)) # extract paths from u to v
                if len(sg_paths) > 0:
                    max_len = len(max(sg_paths, key=len))
                    print("paths", sg_paths, "from", u, "to", v, "max_len", max_len)
                    if 0 < max_len <= max_path_len:
                        subgraph_paths_list.append(sg_paths)
                else:
                    continue
            if len(subgraph_paths_list) > 0:
                paths_to_append = flatten(subgraph_paths_list)
                if len(paths_to_append) > 0:
                    res.append(paths_to_append)
    res.sort()
    return list(k for k, _ in itertools.groupby(res))


def testG1(hop_w=-1):
    # 2 components
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


def testG2(hop_w=-1):
    # two edges, two components
    g = nx.DiGraph()
    g.add_node(1, name="A")
    g.add_node(2, name="B")
    g.add_node(3, name="C")
    g.add_node(4, name="D")

    g.add_edge(1, 2, hop=hop_w)
    g.add_edge(3, 4, hop=hop_w)

    return g


def testG3(hop_w=-1):
    # non-semi-lattice, 1 component
    g = nx.DiGraph()
    g.add_node(1, name="A")
    g.add_node(2, name="B")
    g.add_node(3, name="C")
    g.add_node(4, name="D")

    g.add_edge(1, 2, hop=hop_w)
    g.add_edge(3, 4, hop=hop_w)
    g.add_edge(1, 4, hop=hop_w)
    g.add_edge(3, 2, hop=hop_w)

    return g


def oneout_templates_mining(g: nx.DiGraph):
    res_ = convex_multiple_src_mining(G, {}) # convex_single_src_dst_mining(g,  {})
    res = get_digraphs_from_sg_paths_list(res_, G)
    return res_, res


def multiout_templates_mining(g: nx.DiGraph):
    wccs = list(nx.weakly_connected_components(G))
    unconn_paths = []
    unconn_graphs_list = []
    for _wcc in wccs:
        nx_WCC = nx.subgraph(g, list(_wcc))
        paths, graphs_list = oneout_templates_mining(nx_WCC)
        unconn_paths.append(paths)
        unconn_graphs_list.append(graphs_list)
    return unconn_paths, unconn_graphs_list


def visualize_templates(graphs_: list):
    for i, g in enumerate(graphs_):
        color_map = []
        for node in g:
            if g.in_degree(node) == 0:
                color_map.append('orange')
            elif g.out_degree(node) == 0:
                color_map.append('red')
            else:
                color_map.append('lightblue')
        plt.title('draw_networkx')
        pos = graphviz_layout(g, prog='dot')
        node_lables = nx.get_node_attributes(g, 'name')
        for k in node_lables.keys():
            node_lables[k] = str(k) + ' ' + node_lables[k]

        nx.draw_networkx(g, pos, node_color=color_map, labels=node_lables, arrows=True)
        plt.show()


if __name__ == '__main__':
    freq = dict()
    G = testG3()
    wcc = list(nx.weakly_connected_components(G))
    print([v for v in wcc])
    paths, graphs_list = oneout_templates_mining(G)
    graphs_list.sort(key=lambda x:nx.weisfeiler_lehman_graph_hash(x))
    for p in graphs_list:
        phash = nx.weisfeiler_lehman_graph_hash(p, node_attr='name')
        entry = freq.get(phash, {'graph':p,'count': 0})
        entry['count'] += 1
        freq[phash] = entry
    visualize_templates(graphs_list)
    visualize_templates([v['graph'] for k,v in freq.items()])
