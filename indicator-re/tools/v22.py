import sys, json, math, datetime as dt; sys.path.insert(0, sys.argv[1])
from ta import *; import yh
ix = yh.cut(yh.load_daily(sys.argv[2]), dt.date(2023,5,10), last=(12286.66,12324.01,12211.58,12240.73))
O=[x[1] for x in ix]; H=[x[2] for x in ix]; L=[x[3] for x in ix]; C=[x[4] for x in ix]; n=len(ix)
blk={int(k):v for k,v in json.load(open(sys.argv[3])).items()}; org={int(k):v for k,v in json.load(open(sys.argv[4])).items()}
P=lambda y: -4.2874*y + 15542.87
def at(tr, x):
    xs=[k for k in tr if abs(k-x)<=1]
    return None if not xs else P(sum(tr[k] for k in xs)/len(xs))
best=None
for last_x in (1642.0,1642.7,1643.4):
  for sp in (15.80,15.86,15.92,15.98,16.04):
    m20=sma(C,20); res=[]
    for k in range(0,44):
        x=last_x-k*sp; v=at(org, round(x))
        if v is not None: res.append(v-m20[n-1-k])
    if len(res)>20:
        rms=math.sqrt(sum(r*r for r in res)/len(res)); bias=sum(res)/len(res)
        if best is None or rms<best[0]: best=(rms,last_x,sp,bias,len(res))
print("orange=SMA20 check: rms %.2f pts (bias %+.2f) using last_x=%.1f spacing=%.2f over %d bars" % (best[0],best[3],best[1],best[2],best[4]))
_,last_x,sp,bias,_=best
obs=[]
for k in range(0,44):
    v=at(blk, round(last_x-k*sp))
    if v is not None: obs.append((n-1-k, v-bias))
print("black-line samples:", len(obs), " first:", ix[obs[-1][0]][0], "last:", ix[obs[0][0]][0])
json.dump(obs, open(sys.argv[5],"w"))
for i,v in obs[:6]: print("  ", ix[i][0], round(v,1))
