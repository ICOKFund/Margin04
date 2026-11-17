import sys; sys.path.insert(0, sys.argv[1])
from ta import *; import ds, bn
B = ds.bundle(*sys.argv[2:6])
def held(n, piv):
    out=[None]*n; cur=None; j=0
    for i in range(n):
        while j<len(piv) and piv[j][0]==i: cur=piv[j][2]; j+=1
        out[i]=cur
    return out
for name,(O,H,L,C,V,T,tick,tg) in B.items():
    n=len(C)
    a_h=held(n,pivots(H,8,9,True)); b_h=held(n,pivots(H,9,9,True))
    a_l=held(n,pivots(L,8,9,False)); b_l=held(n,pivots(L,9,9,False))
    lab=lambda i: str(T[i]) if not isinstance(T[i],int) else bn.ts(T[i])
    diffs=[(lab(i), a_h[i], b_h[i], a_l[i], b_l[i]) for i in range(n-200, n) if a_h[i]!=b_h[i] or a_l[i]!=b_l[i]]
    print(name, "bars (last 200) where (8,9) and (9,9) differ:", len(diffs))
    for d in diffs[:12]: print("   %s  HL20 %s vs %s | LL20 %s vs %s" % d)
