import sys, math; sys.path.insert(0, sys.argv[1])
from ta import *; import ds
B = ds.bundle(*sys.argv[2:6])
def hma(x,n):
    h=max(1,n//2); s=max(1,int(round(math.sqrt(n))))
    a=wma(x,h); b=wma(x,n); d=[(2*a[i]-b[i]) if (a[i] is not None and b[i] is not None) else None for i in range(len(x))]
    st=next(i for i,v in enumerate(d) if v is not None); r=wma(d[st:],s); return [None]*st+r
def dema(x,n):
    e=ema(x,n); st=next(i for i,v in enumerate(e) if v is not None); e2=ema(e[st:],n); e2=[None]*st+e2
    return [(2*e[i]-e2[i]) if e2[i] is not None else None for i in range(len(x))]
def lsma(x,n):
    out=[None]*len(x); sx=n*(n-1)/2.0; sxx=(n-1)*n*(2*n-1)/6.0
    for i in range(n-1,len(x)):
        w=x[i-n+1:i+1]; sy=sum(w); sxy=sum(k*w[k] for k in range(n))
        b=(n*sxy-sx*sy)/(n*sxx-sx*sx); a=(sy-b*sx)/n; out[i]=a+b*(n-1)
    return out
def dbl(x,n):
    a=sma(x,n); st=n-1; r=sma(a[st:],n); return [None]*st+r
def donmid(H,L,n):
    return [None]*(n-1)+[(max(H[i-n+1:i+1])+min(L[i-n+1:i+1]))/2 for i in range(n-1,len(H))]
found={}
for name,(O,H,L,C,V,T,tick,tg) in B.items():
    n=len(C); K=min(n,700)                         # work on the last K bars (enough for len<=250 seeded MAs? use full for ema/rma)
    src={"close":C,"hl2":[(H[i]+L[i])/2 for i in range(n)],"hlc3":[(H[i]+L[i]+C[i])/3 for i in range(n)],"ohlc4":[(O[i]+H[i]+L[i]+C[i])/4 for i in range(n)],"open":O,"high":H,"low":L}
    tol=tick/2+1e-9; tgt=tg["TLLJ"]; hits=set()
    for sn,s in src.items():
        tail=s[-1500:] if n>1500 else s
        for ln in range(2,201):
            cands={"sma":sma(tail,ln),"ema":ema(s,ln),"rma":rma(s,ln)}
            if ln<=100: cands["wma"]=wma(tail[-400:],ln); cands["dbl_sma"]=dbl(tail[-600:],ln)
            if ln<=80: cands["hma"]=hma(tail[-400:],ln); cands["lsma"]=lsma(tail[-300:],ln); cands["dema"]=dema(s,ln)
            for mn,arr in cands.items():
                for sh in range(0,13):
                    v=arr[-1-sh]
                    if v is not None and abs(v-tgt)<=tol: hits.add((mn,sn,ln,sh))
    for ln in range(2,201):
        arr=donmid(H[-700:],L[-700:],ln)
        for sh in range(0,13):
            v=arr[-1-sh]
            if v is not None and abs(v-tgt)<=tol: hits.add(("donchian_mid","hl",ln,sh))
    found[name]=hits; print(name,"TLLJ",tgt,"hits:",sorted(hits)[:30], "... total", len(hits))
common=set.intersection(*found.values())
print("COMMON to all four:", sorted(common))
for a in ("IXIC_1D","SOXL_1W"):
    for b in ("BTC_1D","BTC_4H"):
        print("common",a,b,":",sorted(found[a]&found[b])[:10])
print("common IXIC & SOXL:", sorted(found["IXIC_1D"]&found["SOXL_1W"])[:20])
print("common BTC 1D & 4H:", sorted(found["BTC_1D"]&found["BTC_4H"])[:20])
