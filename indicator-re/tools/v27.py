import sys, math; sys.path.insert(0, sys.argv[1])
import ds
from v26lib import ss_fareid
B = ds.bundle(*sys.argv[2:6])
print("dataset    d        SS(TR,200)  d/SS     d/(pi*SS)")
for name,(O,H,L,C,V,T,tick,tg) in B.items():
    n=len(C); tr=[None]+[max(H[i]-L[i],abs(H[i]-C[i-1]),abs(L[i]-C[i-1])) for i in range(1,n)]
    for ln in (100,200):
        r=ss_fareid(tr,ln)[-1]
        print("%-9s %8.2f  len%3d %9.3f  %6.4f  %6.4f" % (name, tg["d"], ln, r, tg["d"]/r, tg["d"]/(math.pi*r)))
