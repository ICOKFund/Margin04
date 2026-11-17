import sys, datetime as dt; sys.path.insert(0, sys.argv[1])
from ta import *; import yh
w = yh.cut(yh.to_weekly(yh.load_daily(sys.argv[2])), dt.date(2023,4,17), last=(15.10,16.36,14.48,14.67))
# red dots read from the SOXL weekly pane (price from pixel calibration, +-0.15)
dots=[42.22,30.80,26.23,28.15,22.80,25.44,17.37,16.59,11.95]
D=[x[0] for x in w]; O=[x[1] for x in w]; H=[x[2] for x in w]; L=[x[3] for x in w]; C=[x[4] for x in w]
s=next(i for i,x in enumerate(w) if x[0]>=dt.date(2022,2,14)); e=next(i for i,x in enumerate(w) if x[0]>=dt.date(2022,10,24))
for i in range(s,e+1):
    tag=[]
    for p in dots:
        if abs(H[i]-p)<=0.25: tag.append("H~%.2f"%p)
        if abs(L[i]-p)<=0.25: tag.append("L~%.2f"%p)
    print(D[i], "O %6.2f H %6.2f L %6.2f C %6.2f %s %s" % (O[i],H[i],L[i],C[i], "up" if C[i]>O[i] else "dn", " ".join(tag)))
