def get_layers(G, start_nodes):
    levels = dict()
    for start in start_nodes:
        for idx, level in enumerate(nx.bfs_layers(G, start)):
            print(level)
            levels.update({x:idx for x in level})
    return levels


test = [[1,2],[3,4],[1,2]]

# flatten also suitable for all iterables in list, not only for lists
def flatten(l):
    return [item for sublist in l for item in sublist]

# it should be checked, may be we need to canonize the l by sorting firstly.
def dedup_listof_lists(ll):
    return list(set([tuple(l) for l in ll]))

res = dedup_listof_lists(test)
print("Dedup:", res)
print("Flattened:", flatten(res))
print("Set of:", set(flatten(res)))
