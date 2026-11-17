import sys, math, itertools; sys.path.insert(0, sys.argv[1])
from ta import *; import ds
B = ds.bundle(*sys.argv[2:6])
def held(n, piv):
    out=[None]*n; cur=None; j=0
    for i in range(n):
        while j<len(piv) and piv[j][0]==i: cur=piv[j][2]; j+=1
        out[i]=cur
    return out
feats={}
for name,(O,H,L,C,V,T,tick,tg) in B.items():
    n=len(C); f={}
    for k in (3,5,10,20,60,120,240):
        f["MA%d"%k]=sma(C,k)[-1]
    m=sma(C,20)[-1]; s=stdev(C,20)[-1]; f["BBu"]=m+2*s; f["BBl"]=m-2*s
    f["HH"]=held(n,pivots(H,2,2,True))[-1]; f["LL"]=held(n,pivots(L,2,2,False))[-1]
    f["HL20"]=held(n,pivots(H,9,9,True))[-1]; f["LL20"]=held(n,pivots(L,9,9,False))[-1]
    hl2=[(H[i]+L[i])/2 for i in range(n)]
    f["Fast"]=rma(hl2,5)[-1]; f["Mid"]=rma(hl2,8)[-1]; f["Slow"]=rma(hl2,13)[-1]
    f["Fast3"]=rma(hl2,5)[-4]; f["Mid5"]=rma(hl2,8)[-6]; f["Slow8"]=rma(hl2,13)[-9]
    f["C"]=C[-1]; f["O"]=O[-1]; f["H"]=H[-1]; f["L"]=L[-1]; f["C1"]=C[-2]
    f["HH20"]=max(H[-20:]); f["LL20d"]=min(L[-20:])
    feats[name]=(f, tg["TLLJ"], tick)
keys=list(next(iter(feats.values()))[0].keys())
hits=[]
for r in (2,3,4):
    for combo in itertools.combinations(keys, r):
        ok=True
        for name,(f,t,tick) in feats.items():
            v=sum(f[k] for k in combo)/r
            if abs(v-t)>tick/2+1e-9: ok=False; break
        if ok: hits.append(combo)
print("equal-weight averages of 2-4 known lines matching TLLJ on all four datasets:", hits[:20])
near=[]
for r in (2,3,4):
    for combo in itertools.combinations(keys, r):
        errs=[]
        for name,(f,t,tick) in feats.items():
            errs.append(abs(sum(f[k] for k in combo)/r-t)/t)
        near.append((max(errs), combo))
near.sort()
print("closest (max relative error):")
for e,c in near[:10]: print("  %.5f%%  %s" % (100*e, c))
