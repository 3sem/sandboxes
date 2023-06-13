Let $N$ -- number of nodes, $t$ -- limit on longest path length in $T, \mu(T)$ is the max number of nodes in $T$.
Then:

1) Algorithm performs $\leq{N}$ iterations: foreach(non-start node) is is needed to extract all of constrained subgraphs to check.
2) On each iteration, it picks siblings nodes.
In variant 2a), $2^{\mu(T)}$
In 2b), there is more complex estimation...
3) For each subgraph, the isomorphism should be checked. Let the search of already matched subgraphs requires O(1) (dict with WL hash as a key)
Then, need to calculate WL hash for tested graph -- $\mu(t) ^ {x}$, where $x  \in [2..3]$.

Thus, total complexity is $O(2 ^ \mu(t) \cdot N \cdot \mu(t) ^ x)$.
