import sys, math; sys.path.insert(0, sys.argv[1])
from ta import *; import ds
B = ds.bundle(*sys.argv[2:6])
def pnr(w,p):
    s=sorted(w); k=max(1, math.ceil(p/100.0*len(s))); return s[k-1]
def sd(w):
    m=sum(w)/len(w); return math.sqrt(sum((x-m)**2 for x in w)/len(w))
def rms(w): return math.sqrt(sum(x*x for x in w)/len(w))
rows={}
for name,(O,H,L,C,V,T,tick,tg) in B.items():
    n=len(C); d=tg["d"]
    tr=[H[0]-L[0]]+[max(H[i]-L[i],abs(H[i]-C[i-1]),abs(L[i]-C[i-1])) for i in range(1,n)]
    dc=[0.0]+[C[i]-C[i-1] for i in range(1,n)]; adc=[abs(v) for v in dc]
    up=[max(v,0) for v in dc]; hl=[H[i]-L[i] for i in range(n)]
    for N in (240,360,480,500,520,550,600,650,685):
        if N>n: continue
        w=slice(n-N,n)
        rows.setdefault(N,{})[name]=dict(
            meanTR=d/(sum(tr[w])/N), meanADC=d/(sum(adc[w])/N), sdDC=d/sd(dc[w]), rmsDC=d/rms(dc[w]), sdTR=d/sd(tr[w]),
            p90TR=d/pnr(tr[w],90), p90ADC=d/pnr(adc[w],90), p95ADC=d/pnr(adc[w],95), p75TR=d/pnr(tr[w],75), p80TR=d/pnr(tr[w],80), medTR=d/pnr(tr[w],50),
            sdC=d/sd(C[w]), maxTR=d/max(tr[w]))
names=list(B)
for N in sorted(rows):
    print("N=%d   (ratio d/stat per dataset: %s)" % (N, ", ".join(names)))
    for k in rows[N][names[0]]:
        vals=[rows[N][nm][k] for nm in names if nm in rows[N]]
        mean=sum(vals)/len(vals); spread=(max(vals)-min(vals))/mean
        flag="  <==" if spread<0.06 else ""
        print("   %-8s %s   spread %.3f%s" % (k, " ".join("%7.4f"%v for v in vals), spread, flag))
