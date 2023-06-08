def it_superset(l=[1,2,3,4], lim=3)
    space = 2 ** min(lim, len(l))
    pss = more_itertools.powerset(l)
    pss.__next__()
    for i in range(1, space):
        print(pss.__next__())
