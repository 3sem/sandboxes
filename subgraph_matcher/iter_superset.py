def it_superset(l=[1,2,3,4], lim=3)
    space = 2 ** len(l)
    pss = more_itertools.powerset(l)
    pss.__next__()
    for i in range(1, space):
        p = pss.__next__()
        if len(p) > lim:
            break
        print(p)
