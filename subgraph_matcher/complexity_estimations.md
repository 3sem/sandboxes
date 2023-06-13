Let N -- number of nodes, l -- limit on longest path in T, \mu(T) is the max number of nodes in T.
Then:

1) Algorithm performs \leq{N} iterations: foreach(node)
2) On each iteration, it picks siblings nodes.
In variant 2a), 2^\mu(T)
In 2b), there is more complex estimation...
3) For each subgraph, the isomorphism should be checked. Let the search of already matched subgraphs requires O(1) (dict with WL hash as a key)
Then, need to calculate WL hash for tested graph -- \mu(t) ^ x, where x ~ in [2..3].

Thus, total complexity is O(2 ^ \mu(t) * N * \mu(t) ^ x)
