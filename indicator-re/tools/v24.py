import sys, json, math, datetime as dt; sys.path.insert(0, sys.argv[1])
from ta import *; from mas import *; import yh
ix = yh.cut(yh.load_daily(sys.argv[2]), dt.date(2023,5,10), last=(12286.66,12324.01,12211.58,12240.73))
ix = ix[-1500:]
O=[x[1] for x in ix]; H=[x[2] for x in ix]; L=[x[3] for x in ix]; C=[x[4] for x in ix]; V=[x[5] for x in ix]; n=len(ix)
obs=json.load(open(sys.argv[3])); obs=[(i-(len(yh.load_daily(sys.argv[2]))-1-(n-1)) if False else i, v) for i,v in obs]
# re-index obs (they were computed on the full series ending 2023-05-10): convert to tail index
full_n = len(yh.cut(yh.load_daily(sys.argv[2]), dt.date(2023,5,10)))
obs=[(i-(full_n-n), v) for i,v in obs]
TLLJ=12061.70
srcs={"close":C,"hl2":[(H[i]+L[i])/2 for i in range(n)],"hlc3":[(H[i]+L[i]+C[i])/3 for i in range(n)],"ohlc4":[(O[i]+H[i]+L[i]+C[i])/4 for i in range(n)],"hlcc4":[(H[i]+L[i]+2*C[i])/4 for i in range(n)]}
res=[]
def score(name, s):
    if s[-1] is None or any(s[i-1] is None or s[i] is None for i,_ in obs): return
    last_err=abs(s[-1]-TLLJ)
    r=[((s[i-1]+s[i])/2 - v) for i,v in obs]
    rms=math.sqrt(sum(e*e for e in r)/len(r))
    res.append((rms+last_err*0.5, rms, last_err, name))
for sn,x in srcs.items():
    for ln in range(2,121):
        score("sma %s %d"%(sn,ln), sma(x,ln)); score("ema %s %d"%(sn,ln), ema(x,ln)); score("rma %s %d"%(sn,ln), rma(x,ln))
        score("wma %s %d"%(sn,ln), wma(x,ln))
        if ln<=80:
            score("hma %s %d"%(sn,ln), hma(x,ln)); score("dema %s %d"%(sn,ln), dema(x,ln)); score("tema %s %d"%(sn,ln), tema(x,ln))
            score("alma %s %d"%(sn,ln), alma(x,ln)); score("lsma %s %d"%(sn,ln), lsma(x,ln)); score("zlema %s %d"%(sn,ln), zlema(x,ln))
            score("t3 %s %d"%(sn,ln), t3(x,ln)); score("mcg %s %d"%(sn,ln), mcginley(x,ln)); score("ss %s %d"%(sn,ln), supersmoother(x,ln))
            score("vwma %s %d"%(sn,ln), vwma(x,V,ln))
            for ph in (-100,0,50,100):
                for pw in (1,2,3):
                    score("jma %s %d ph%d pw%d"%(sn,ln,ph,pw), jma(x,ln,ph,pw))
        if ln<=40: score("kama %s %d"%(sn,ln), kama(x,ln))
    for g in [k/100 for k in range(10,96,2)]:
        score("laguerre %s %.2f"%(sn,g), laguerre(x,g))
res.sort()
print("observations:", len(obs), "(TLLJ trace between candles) + last value 12061.70")
for r in res[:25]: print("  score %.2f  rms %.2f  last_err %.2f  %s" % r)
