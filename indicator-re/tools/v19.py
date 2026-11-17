import sys, datetime as dt, math; sys.path.insert(0, sys.argv[1])
from ta import *; import yh, bn
w = yh.cut(yh.to_weekly(yh.load_daily(sys.argv[2])), dt.date(2023,4,17), last=(15.10,16.36,14.48,14.67))
D=[x[0] for x in w]; O=[x[1] for x in w]; H=[x[2] for x in w]; L=[x[3] for x in w]; C=[x[4] for x in w]; V=[x[5] for x in w]; n=len(w)
dots={dt.date(2022,2,28),dt.date(2022,4,18),dt.date(2022,4,25),dt.date(2022,5,2),dt.date(2022,5,9),dt.date(2022,6,6),dt.date(2022,6,13),dt.date(2022,6,27),dt.date(2022,10,3)}
vs20=sma(V,20); vs10=sma(V,10); vs50=sma(V,50)
s=next(i for i,x in enumerate(w) if x[0]>=dt.date(2021,11,1)); e=n
print("SOXL weekly: week, dot, vol/SMA10, vol/SMA20, vol/SMA50, vol>vol[1], vol rank in last 20")
for i in range(s,e):
    rank=sorted(V[i-19:i+1],reverse=True).index(V[i])+1
    mark="●" if D[i] in dots else ("LS" if D[i]==dt.date(2021,12,6) else "·")
    print(D[i], mark, "%5.2f %5.2f %5.2f %d %2d" % (V[i]/vs10[i-1], V[i]/vs20[i-1], V[i]/vs50[i-1], int(V[i]>V[i-1]), rank))
