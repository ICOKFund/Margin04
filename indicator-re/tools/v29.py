import sys, math; sys.path.insert(0, sys.argv[1])
from ta import *; import ds
B = ds.bundle(*sys.argv[2:6])
def pnr(w,p):
    s=sorted(w); k=max(1, math.ceil(p/100.0*len(s))); return s[k-1]
def pli(w,p):
    s=sorted(w); n=len(s); r=p/100.0*n-0.5
    if r<=0: return s[0]
    if r>=n-1: return s[-1]
    lo=int(math.floor(r)); return s[lo]+(s[lo+1]-s[lo])*(r-lo)
hits={}
for name,(O,H,L,C,V,T,tick,tg) in B.items():
    d=tg["d"]; n=len(C)
    ph={c:v for c,p,v in pivots(H,2,2,True)}; pl={c:v for c,p,v in pivots(L,2,2,False)}
    fh=fl=None; FH=[None]*n; FL=[None]*n
    for i in range(n):
        if i in ph: fh=ph[i]
        if i in pl: fl=pl[i]
        FH[i]=fh; FL[i]=fl
    series={}
    # per-bar positive excursions beyond previous bar's box (high/low and close variants)
    for src in ("hl","c"):
        up=[]; dn=[]; both=[]
        for i in range(1,n):
            if FH[i-1] is None or FL[i-1] is None: continue
            hi = H[i] if src=="hl" else C[i]; lo = L[i] if src=="hl" else C[i]
            eu=hi-FH[i-1]; ed=FL[i-1]-lo
            if eu>0: up.append(eu); both.append(eu)
            if ed>0: dn.append(ed); both.append(ed)
        series["bar_%s_pooled"%src]=both
    # per-episode max excursion (episode = run of bars with the same box)
    for src in ("hl","c"):
        ep=[]; cur_u=0; cur_d=0
        for i in range(1,n):
            if FH[i-1] is None or FL[i-1] is None: continue
            if FH[i]!=FH[i-1] or FL[i]!=FL[i-1]:
                if cur_u>0: ep.append(cur_u)
                if cur_d>0: ep.append(cur_d)
                cur_u=cur_d=0
            hi = H[i] if src=="hl" else C[i]; lo = L[i] if src=="hl" else C[i]
            cur_u=max(cur_u, hi-FH[i-1]); cur_d=max(cur_d, FL[i-1]-lo)
        series["episode_%s_pooled"%src]=ep
    for sn,s in series.items():
        for N in range(5,len(s)+1):
            w=s[-N:]
            for p in (75,80,85,90,95):
                for kind,f in (("pnr",pnr),("pli",pli)):
                    if abs(f(w,p)-d)<=tick/2+1e-9: hits.setdefault(name,set()).add((sn,kind,p,N if N<len(s) else "all"))
            m=sum(w)/N
            for k in (1.0,1.5,2.0):
                if abs(k*m-d)<=tick/2+1e-9: hits.setdefault(name,set()).add((sn,"mean*%g"%k,0,N if N<len(s) else "all"))
for k in B: print(k, len(hits.get(k,[])), sorted(hits.get(k,[]), key=str)[:6])
fam={k:{(a,b,c) for (a,b,c,N) in v} for k,v in hits.items()}
print("families matching all four:", set.intersection(*fam.values()) if len(fam)==4 else "n/a (some dataset had no hits)")
