import sys, math, bisect; sys.path.insert(0, sys.argv[1])
from ta import *; import ds
B = ds.bundle(*sys.argv[2:6])
ZS=(1.0,1.2816,1.6449,1.645,1.96,2.0,2.326,2.576,3.0)
def held(n, piv):
    out=[None]*n; cur=None; j=0; piv=sorted(piv)
    for i in range(n):
        while j<len(piv) and piv[j][0]==i: cur=piv[j][2]; j+=1
        out[i]=cur
    return out
allh={}
for name,(O,H,L,C,V,T,tick,tg) in B.items():
    n=len(C); tgt=tg["d"]; tol=tick/2+1e-9
    tr=[H[0]-L[0]]+[max(H[i]-L[i],abs(H[i]-C[i-1]),abs(L[i]-C[i-1])) for i in range(1,n)]
    fh=held(n,pivots(H,2,2,True)); fl=held(n,pivots(L,2,2,False))
    st=next(i for i in range(n) if fh[i] is not None and fl[i] is not None)
    X={"TR":tr,"H-L":[H[i]-L[i] for i in range(n)],"dC":[0.0]+[C[i]-C[i-1] for i in range(1,n)],"|C-O|":[abs(C[i]-O[i]) for i in range(n)],
       "C":C,"H":H,"L":L,"hl2":[(H[i]+L[i])/2 for i in range(n)],
       "box":[(fh[i]-fl[i]) if i>=st else 0.0 for i in range(n)]}
    X["|dC|"]=[abs(v) for v in X["dC"]]
    hits=[]
    for xn,x in X.items():
        s1=0.0; s2=0.0; srt=[]
        lim = n-st if xn=="box" else n
        for N in range(1,lim+1):
            v=x[n-N]; s1+=v; s2+=v*v; bisect.insort(srt,v)
            if N<5: continue
            m=s1/N; var=max(s2/N-m*m,0.0); sdp=math.sqrt(var); sds=math.sqrt(var*N/(N-1))
            for z in ZS:
                for lab_,sdv in (("sdP",sdp),("sdS",sds)):
                    if abs(z*sdv-tgt)<=tol: hits.append((xn,"%s*%g"%(lab_,z),N))
                    if abs(m+z*sdv-tgt)<=tol: hits.append((xn,"mean+%s*%g"%(lab_,z),N))
            for k in (0.5,1.0,1.5,2.0,2.5,3.0):
                if abs(k*m-tgt)<=tol: hits.append((xn,"mean*%g"%k,N))
            for p in (50,75,80,90,95,99):
                kk=max(1, math.ceil(p/100.0*N)); pv=srt[kk-1]
                if abs(pv-tgt)<=tol: hits.append((xn,"pnr%d"%p,N))
                r=p/100.0*N-0.5
                if 0<r<N-1:
                    lo=int(math.floor(r)); pl=srt[lo]+(srt[lo+1]-srt[lo])*(r-lo)
                    if abs(pl-tgt)<=tol: hits.append((xn,"pli%d"%p,N))
    allh[name]=hits
    fams={}
    for (a,b,N) in hits: fams.setdefault((a,b),[]).append(N)
    print(name,"d",tgt,"exact hits:",len(hits),"families:",len(fams))
sets_={k:{(a,b) for (a,b,N) in v} for k,v in allh.items()}
common=set.intersection(*sets_.values())
print("families hitting ALL four:", sorted(common))
for fam in sorted(common):
    print("  ",fam, {k:[N for (a,b,N) in v if (a,b)==fam][:8] for k,v in allh.items()})
from itertools import combinations
for k1,k2,k3 in combinations(allh.keys(),3):
    c=sets_[k1]&sets_[k2]&sets_[k3]
    print("three-way",k1,k2,k3,":",sorted(c)[:12])
