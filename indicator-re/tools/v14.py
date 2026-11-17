import sys, math; sys.path.insert(0, sys.argv[1])
from ta import *; import ds
B = ds.bundle(*sys.argv[2:6])
targets = {"IXIC_1D": (12227.93, 11798.77), "SOXL_1W": (18.40, 6.21), "BTC_1D": (29184.8, 26480.0), "BTC_4H": (31059.0, 29925.0)}
ok_pairs = None
for name,(O,H,L,C,V,T,tick,tg) in B.items():
    good=set()
    for l in range(1,16):
        for r in range(1,16):
            ph=pivots(H,l,r,True); pl=pivots(L,l,r,False)
            if ph and pl and abs(ph[-1][2]-targets[name][0])<tick/2 and abs(pl[-1][2]-targets[name][1])<tick/2:
                good.add((l,r))
    print(name, "valid (left,right):", sorted(good))
    ok_pairs = good if ok_pairs is None else ok_pairs & good
print("valid on all four:", sorted(ok_pairs))
