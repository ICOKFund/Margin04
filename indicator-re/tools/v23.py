import sys, json, math, datetime as dt; sys.path.insert(0, sys.argv[1])
from PIL import Image
import numpy as np
from ta import *; import yh
ix = yh.cut(yh.load_daily(sys.argv[2]), dt.date(2023,5,10), last=(12286.66,12324.01,12211.58,12240.73))
C=[x[4] for x in ix]; n=len(ix)
im=np.asarray(Image.open(sys.argv[3]).convert("RGB")).astype(int)
P=lambda y: -4.2874*y + 15542.87 - 2.11
last_x=1642.0; sp=15.86
def runs_at(x, rgb, tol, y0=650, y1=1165):
    col=im[y0:y1,int(round(x))]; d=np.abs(col-np.array(rgb)).sum(axis=1); ys=np.nonzero(d<=tol)[0]+y0
    rr=[]; 
    for y in ys:
        if rr and y-rr[-1][1]<=1: rr[-1][1]=y
        else: rr.append([y,y])
    return [((a+b)/2, b-a+1) for a,b in rr]
# track the black line in the gaps between candles (x = centre - sp/2), starting near the known last value
prev=812.5; obs=[]
for k in range(0,44):
    x=last_x-k*sp - sp/2           # gap between bar k and bar k+1  -> average of the two bars' values
    rr=[r for r in runs_at(x,(54,58,69),45) if r[1]<=4]
    if not rr: continue
    y=min(rr,key=lambda r:abs(r[0]-prev))[0]
    if abs(y-prev)>12: continue
    prev=y; obs.append((n-1-k, P(y)))
print("gap samples:", len(obs))
json.dump(obs, open(sys.argv[4],"w"))
for i,v in obs[:8]: print("  between", ix[i-1][0], "and", ix[i][0], round(v,1))
