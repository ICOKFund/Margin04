import sys, math, bisect; sys.path.insert(0, sys.argv[1])
from bn import *; from ta import *
D = load(sys.argv[2]); H4 = load(sys.argv[3])
sets = {"1D": (cut(D, ms(2023,4,17), last=(30286.6,30307.4,29714.1,29835.3)), 2755.0),
        "4H": (cut(H4, ms(2023,4,17,8), last=(29831.2,29913.6,29781.6,29835.1)), 644.9)}
def held(n, piv):
    out=[None]*n; cur=None; j=0; piv=sorted(piv)
    for i in range(n):
        while j<len(piv) and piv[j][0]==i: cur=piv[j][2]; j+=1
        out[i]=cur
    return out
ZS=(0.5,1.0,1.2816,1.6449,1.645,1.96,2.0,2.326,2.576,3.0)
allh={}
for name,(b,tgt) in sets.items():
    Hh=[x[2] for x in b]; L=[x[3] for x in b]; C=[x[4] for x in b]; n=len(b)
    fh=held(n,pivots(Hh,2,2,True)); fl=held(n,pivots(L,2,2,False))
    st=next(i for i in range(n) if fh[i] is not None and fl[i] is not None)
    X={"box":[ (fh[i]-fl[i]) if i>=st else 0.0 for i in range(n)],
       "absbox":[ abs(fh[i]-fl[i]) if i>=st else 0.0 for i in range(n)],
       "C-FrH":[ (C[i]-fh[i]) if i>=st else 0.0 for i in range(n)],
       "FrL-C":[ (fl[i]-C[i]) if i>=st else 0.0 for i in range(n)],
       "H-FrH":[ (Hh[i]-fh[i]) if i>=st else 0.0 for i in range(n)],
       "FrL-L":[ (fl[i]-L[i]) if i>=st else 0.0 for i in range(n)],
       "FrH":[ fh[i] if i>=st else 0.0 for i in range(n)], "FrL":[ fl[i] if i>=st else 0.0 for i in range(n)],
       "mid":[ (fh[i]+fl[i])/2 if i>=st else 0.0 for i in range(n)],
       "dFrH":[0.0]+[ (fh[i]-fh[i-1]) if i>st else 0.0 for i in range(1,n)], "dFrL":[0.0]+[ (fl[i]-fl[i-1]) if i>st else 0.0 for i in range(1,n)]}
    print("=====",name,"target",tgt,"current box",X["box"][-1])
    tol=0.06; hits=[]
    for xn,x in X.items():
        s1=0.0; s2=0.0; srt=[]
        for N in range(1,n-st+1):
            v=x[n-N]; s1+=v; s2+=v*v; bisect.insort(srt,v)
            if N<5: continue
            m=s1/N; var=max(s2/N-m*m,0.0); sdp=math.sqrt(var); sds=math.sqrt(var*N/(N-1))
            for z in ZS:
                for lab,sdv in (("sdP",sdp),("sdS",sds)):
                    if abs(z*sdv-tgt)<=tol: hits.append((xn,"%s*%g"%(lab,z),N,round(z*sdv,2)))
                    if abs(m+z*sdv-tgt)<=tol: hits.append((xn,"mean+%s*%g"%(lab,z),N,round(m+z*sdv,2)))
            for k in (0.5,0.618,0.9,1.0,1.5,2.0):
                if abs(k*m-tgt)<=tol: hits.append((xn,"mean*%g"%k,N,round(k*m,2)))
            for p in (10,20,25,50,75,80,90,95):
                kk=max(1, math.ceil(p/100.0*N)); pv=srt[kk-1]
                if abs(pv-tgt)<=tol: hits.append((xn,"pnr%d"%p,N,round(pv,2)))
                r=p/100.0*N-0.5
                if 0<r<N-1:
                    lo=int(math.floor(r)); pl=srt[lo]+(srt[lo+1]-srt[lo])*(r-lo)
                    if abs(pl-tgt)<=tol: hits.append((xn,"pli%d"%p,N,round(pl,2)))
        if xn=="box":
            for N in (20,50,100,200,300,500,1000,n-st):
                w=sorted(x[n-N:]); print("  box stats N=%d: mean %.1f median %.1f p90 %.1f sd %.1f" % (N, sum(w)/N, w[N//2], w[max(0,math.ceil(0.9*N)-1)], math.sqrt(sum((v-sum(w)/N)**2 for v in w)/N)))
    allh[name]=hits; print("  exact hits:",len(hits)); 
    for h in hits[:40]: print("    ",h)
k1={(a,b) for (a,b,N,v) in allh["1D"]}; k2={(a,b) for (a,b,N,v) in allh["4H"]}
print("families hitting both:", sorted(k1&k2))
for fam in sorted(k1&k2):
    print(fam, "1D N:", [N for (a,b,N,v) in allh["1D"] if (a,b)==fam][:12], "| 4H N:", [N for (a,b,N,v) in allh["4H"] if (a,b)==fam][:12])
