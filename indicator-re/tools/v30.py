import sys, datetime as dt; sys.path.insert(0, sys.argv[1])
from ta import *; import yh
w = yh.cut(yh.to_weekly(yh.load_daily(sys.argv[2])), dt.date(2023,4,17), last=(15.10,16.36,14.48,14.67))
D=[x[0] for x in w]; H=[x[2] for x in w]; L=[x[3] for x in w]; n=len(w)
ph={c:v for c,p,v in pivots(H,2,2,True)}; pl={c:v for c,p,v in pivots(L,2,2,False)}
fh=fl=None; FH={}; FL={}
for i in range(n):
    if i in ph: fh=ph[i]
    if i in pl: fl=pl[i]
    FH[D[i]]=fh; FL[D[i]]=fl
# dot rows read from the SOXL weekly 'Livermore' pane (pixel -> price, about +-0.04), with the weeks they span
rows=[("up",24.96,dt.date(2022,10,24),dt.date(2022,11,21)),("dn",3.54,dt.date(2022,10,24),dt.date(2023,1,2)),
      ("up",17.08,dt.date(2022,11,28),dt.date(2023,2,13)),("dn",6.13,dt.date(2023,1,9),dt.date(2023,2,27)),
      ("up",21.07,dt.date(2023,2,20),dt.date(2023,4,17)),("dn",10.42,dt.date(2023,3,6),dt.date(2023,4,17))]
for side,price,a,b in rows:
    ws=[d for d in D if a<=d<=b]
    box=sorted(set(FH[d] if side=="up" else FL[d] for d in ws))
    ds_=[ (price-FH[d]) if side=="up" else (FL[d]-price) for d in ws]
    print("%s row %.2f (%s..%s): box edge values %s -> implied d %s" % (side, price, a, b, box, sorted(set(round(x,2) for x in ds_))))
