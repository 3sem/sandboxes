import sys
import pprint
import more_itertools
import itertools
import copy
import numpy as np
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt
import networkx.algorithms.isomorphism as isomorph


def convex_single_src_dst_mining(G: nx.DiGraph, constr: dict, fixed_output=None):
    max_path_len = constr.get("max_path_len", 5)
    mined_subgraphs = []
    mined_paths = []
    nodeattrs = nx.get_node_attributes(G, 'name')
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
        if G.in_degree(v) <= 0:
            continue
        #lgn.remove(v)
        siblings_space = list(set(G.predecessors(v)))
        for i in range(1, max_path_len):
            __ss = []
            for item in set(siblings_space):
                __ss += [s for s in set(G.predecessors(item))]
            siblings_space += __ss

        subgraph_paths_list = []
        pss = more_itertools.powerset(siblings_space)
        pss.__next__() # skip emply set
        space = 2 ** len(siblings_space)
        for i in range(1, space): # for each set S in powerset
            S = pss.__next__()
            if len(S) > max_path_len: # heuristics
                break
            subgraph_paths_list.clear()
            for u in S: # for each element u in S
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


maxmiso = dict() # format is key-num_of_maxmiso : {nodes: list, induced_subgraph(nodes): nx.DiGraph}

def get_fanout(G):
    fanout = dict()
    for n in G.nodes:
        out_deg = G.out_degree(n)
        fanout[n] = out_deg
    return fanout


def gen_mms(G: nx.DiGraph, n, cn, fanout):
    global maxmiso
    if cn not in maxmiso.keys():
        maxmiso[cn] = [cn]
    for p in G.predecessors(n):
        if (fanout[p] == 1):
            maxmiso[cn].append(p)
            gen_mms(G, p, cn, fanout)
            fanout[p] = 0
        elif fanout[p] == 0:
            return
        else:
            fanout[p] -= 1 # all of fanouts of picked node should be consumed by the current MAXMISO


def gen_mms_iteratively(G: nx.DiGraph, n, fanout):
    global maxmiso
    stack = [n]
    if n not in maxmiso.keys():
        maxmiso[n] = [n]
    while len(stack) != 0:
        top = stack.pop()
        for p in G.predecessors(top):
            if fanout[p] == 1:
                maxmiso[n].append(p)
                stack.append(p)
                fanout[p] = 0
            elif fanout[p] == 0:
                return
            else:
                fanout[p] -= 1  # all of fanouts of picked node should be consumed by the current MAXMISO


def maxmiso_original(G, mode="recursive"):
    global maxmiso
    maxmiso = dict()
    fanout_orig = get_fanout(G)

    while G.number_of_nodes() > 0:
        for item in G.nodes:
            if G.out_degree(item) > 0:
                continue
            else:
                n = item
        fanout = copy.copy(fanout_orig)
        if mode == "recursive":
            gen_mms(G, n, n, fanout)
        else:
            gen_mms_iteratively(G, n, fanout)
        G.remove_nodes_from(maxmiso[n])
    return maxmiso


def miso_convexes_recursive(G):
    global maxmiso
    global fanout
    maxmiso = dict()
    fanout = dict()
    fanout = get_fanout(G)
    for n in G.nodes:
        gen_mms(G, n, n)
        #G.remove_nodes_from(maxmiso[n])
    return maxmiso


def maxmiso_nx_extractor(G):
    while G.number_of_nodes() > 0:
        for item in G.nodes:
            if G.out_degree(item) > 0:
                continue
            else:
                n = item
                if n not in maxmiso.keys():
                    maxmiso[n] = [n]
                break
        for m in G.nodes:
            if n != m:
                asp = list(nx.all_simple_paths(G, m, n))
                if len(asp) > 0:
                    flat_list = [item for sublist in asp for item in sublist]
                    maxmiso[n].extend(flat_list)
        maxmiso[n] = list(set(maxmiso[n]))
        G.remove_nodes_from(maxmiso[n])
    return maxmiso


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
    g.add_node(5, name="A")
    g.add_node(6, name="B")

    g.add_edge(1, 2, hop=hop_w)
    g.add_edge(3, 4, hop=hop_w)
    g.add_edge(1, 4, hop=hop_w)
    g.add_edge(3, 2, hop=hop_w)
    g.add_edge(5, 6, hop=hop_w)

    return g


def testGmaxmiso(hop_w=-1):
    g = nx.DiGraph()
    g.add_node(1, name="+")
    g.add_node(2, name="+")
    g.add_node(3, name="*")
    g.add_node(4, name="*")
    g.add_node(5, name="*")
    g.add_node(6, name="+")
    g.add_node(7, name="str")
    g.add_edge(1, 4, hop=hop_w)
    g.add_edge(2, 4, hop=hop_w)
    g.add_edge(2, 5, hop=hop_w)
    #g.add_edge(3, 5, hop=hop_w)
    g.add_edge(4, 6, hop=hop_w)
    g.add_edge(5, 6, hop=hop_w)
    g.add_edge(6, 7, hop=hop_w)
    return g

def testGmaxmiso_3reg(hop_w=-1):
    g = nx.DiGraph()
    g.add_node(1, name="+")
    g.add_node(2, name="+")
    g.add_node(3, name="*")
    g.add_node(4, name="*")
    g.add_node(5, name="*")
    g.add_node(6, name="/")

    g.add_node(11, name="+")
    g.add_node(12, name="+")
    g.add_node(13, name="*")
    g.add_node(14, name="*")
    g.add_node(15, name="*")
    g.add_node(16, name="/")

    g.add_node(21, name="-")
    g.add_node(22, name="+")
    g.add_node(23, name="*")
    g.add_node(24, name="*")
    g.add_node(25, name="*")
    g.add_node(26, name="/")

    g.add_edge(1, 4, hop=hop_w)
    g.add_edge(2, 4, hop=hop_w)
    g.add_edge(2, 5, hop=hop_w)
    g.add_edge(3, 5, hop=hop_w)
    g.add_edge(4, 6, hop=hop_w)
    g.add_edge(5, 6, hop=hop_w)

    g.add_edge(11, 14, hop=hop_w)
    g.add_edge(12, 14, hop=hop_w)
    g.add_edge(12, 15, hop=hop_w)
    g.add_edge(13, 15, hop=hop_w)
    g.add_edge(14, 16, hop=hop_w)
    g.add_edge(15, 16, hop=hop_w)

    g.add_edge(21, 24, hop=hop_w)
    g.add_edge(22, 24, hop=hop_w)
    g.add_edge(22, 25, hop=hop_w)
    g.add_edge(23, 25, hop=hop_w)
    g.add_edge(24, 26, hop=hop_w)
    g.add_edge(25, 26, hop=hop_w)

    g.add_edge(6, 13, hop=hop_w)
    g.add_edge(6, 21, hop=hop_w)
    return g


def oneout_templates_mining(g: nx.DiGraph):
    res_ = convex_multiple_src_mining(g, {}) # convex_single_src_dst_mining(g,  {})
    res = get_digraphs_from_sg_paths_list(res_, g)
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


def visualize_templates(graphs_: list, need_node_name=False, save_prefix=None):
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
            node_lables[k] = f'''{k + ' ' if need_node_name else ""}''' + node_lables[k]

        nx.draw_networkx(g, pos, node_color=color_map, labels=node_lables, arrows=True)
        plt.show()
        if save_prefix:
            plt.savefig(str(i)+".png")


def largest_isomorph_miso_graphs(l:list)->dict:
    res = dict()
    for G1 in l:
        for G2 in l:
            if G1 != G2:
                gen = nx.isomorphism.ISMAGS(G1, G2, node_match=nx.isomorphism.categorical_node_match("name", None))
                for subgraph in gen: # and also, convexity should be checked!
                    hash = nx.weisfeiler_lehman_graph_hash(subgraph, node_attr="name")
                    entry = res.get(hash, {"graph", {"graph":subgraph,"count":0}})
                    entry["count"] += 1
                    res[hash] = entry
    return res

def flatten(l):
    return [item for sublist in l for item in sublist]


def miso_conv_checker(G, nodes):
    subgraph = G.subgraph(nodes)
    out = [n for n in nodes if subgraph.out_degree(n) == 0]
    asp = list()
    for n in nodes:
        if n == out:
            continue
        asp.extend(list(nx.all_simple_paths(G, n, out)))
    asp = flatten(asp)
    asp_set = set(asp)
    if asp_set == set(nodes):
        return True
    else:
        return False

if __name__ == '__main__':
    freq = dict()
    G = testG1()
    miso = testGmaxmiso_3reg()
    miso_orig = copy.deepcopy(miso)
    res = maxmiso_original(miso, "iterative")

    for k, v in res.items():
        subgraph = miso_orig.subgraph(v)
        res[k] = {"nodes": v,
                  "output": k,
                  "graph": subgraph,
                  "hash": nx.weisfeiler_lehman_graph_hash(subgraph, node_attr='name'),
                  "freq": 1}

    freq = dict()
    #visualize_templates(v["graph"] for k,v in res.items())
    for k1, v1 in res.items():
        for k2, v2 in res.items():
            if k2 != k1:
                g1 = v1["graph"]
                g2 = v2["graph"]
                gen = nx.isomorphism.ISMAGS(g1, g2, node_match=nx.isomorphism.categorical_node_match("name", None))
                for sg in gen.largest_common_subgraph():
                    # convexity should be checked!

                    nodes_to_check = [list(sg.keys()), [v for _,v in sg.items()]]
                    if miso_conv_checker(g1, nodes_to_check[0]) and miso_conv_checker(g2, nodes_to_check[1]):
                        hash = nx.weisfeiler_lehman_graph_hash(v1['graph'].subgraph(list(sg.keys())), node_attr="name")
                        freq_entry = freq.get(hash, {'graph': sg, 'cnt': 0, 'node_subsets': [list(sg.keys())]})
                        freq_entry['cnt'] += 1
                        freq_entry['node_subsets'].append([v for _, v in sg.items()])
                        freq[hash] = freq_entry
    for k, v in freq.items():
        result = []
        [result.append(x) for x in v['node_subsets'] if x not in result]
        v['node_subsets'] = result

    pprint.pprint(freq)
    visualize_templates([miso_orig])
    visualize_templates(miso_orig.subgraph(list(v["graph"].keys())) for k,v in freq.items())


    sys.exit(0)
    '''
    wcc = list(nx.weakly_connected_components(G))
    for i, w in enumerate(wcc):
        subgraph = nx.subgraph(G, w)
        paths, graphs_list = oneout_templates_mining(subgraph)
        for p in graphs_list:
            phash = nx.weisfeiler_lehman_graph_hash(p, node_attr='name')

            entry = freq.get(phash, {'graph': p, 'count': 0})
            entry['count'] += 1
            freq[phash] = entry

        #visualize_templates(graphs_list, save_prefix="G"+str(i)+"_")
    '''
    # visualize_templates([v['graph'] for k, v in freq.items()], need_node_num=False)
