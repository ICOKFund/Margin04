import sys, math, bisect; sys.path.insert(0, sys.argv[1])
from bn import *; from ta import *
D = load(sys.argv[2]); H4 = load(sys.argv[3])
sets = {"1D": (cut(D, ms(2023,4,17), last=(30286.6,30307.4,29714.1,29835.3)), 2755.0),
        "4H": (cut(H4, ms(2023,4,17,8), last=(29831.2,29913.6,29781.6,29835.1)), 644.9)}
ZS=(1.0,1.2816,1.6449,1.645,1.96,2.0,2.326,2.5,2.576,3.0)
allhits={}
for name,(b,tgt) in sets.items():
    O=[x[1] for x in b]; Hh=[x[2] for x in b]; L=[x[3] for x in b]; C=[x[4] for x in b]; n=len(b)
    tr=[Hh[0]-L[0]]+[max(Hh[i]-L[i],abs(Hh[i]-C[i-1]),abs(L[i]-C[i-1])) for i in range(1,n)]
    X={"TR":tr,"H-L":[Hh[i]-L[i] for i in range(n)],"dC":[0.0]+[C[i]-C[i-1] for i in range(1,n)],
       "C":C,"H":Hh,"L":L,"hl2":[(Hh[i]+L[i])/2 for i in range(n)],"|C-O|":[abs(C[i]-O[i]) for i in range(n)],
       "dH":[0.0]+[Hh[i]-Hh[i-1] for i in range(1,n)],"dL":[0.0]+[L[i]-L[i-1] for i in range(1,n)]}
    X["|dC|"]=[abs(v) for v in X["dC"]]
    tol=0.06; hits=[]
    for xn,x in X.items():
        # running sums from the end for mean / sd with every N
        s1=0.0; s2=0.0; srt=[]
        for N in range(1,n+1):
            v=x[n-N]; s1+=v; s2+=v*v; bisect.insort(srt,v)
            if N<5: continue
            m=s1/N; var=max(s2/N-m*m,0.0); sdp=math.sqrt(var); sds=math.sqrt(var*N/(N-1))
            for z in ZS:
                for lab,sdv in (("sdP",sdp),("sdS",sds)):
                    if abs(z*sdv-tgt)<=tol: hits.append((xn,"%s*%g"%(lab,z),N,round(z*sdv,2)))
                    if abs(m+z*sdv-tgt)<=tol: hits.append((xn,"mean+%s*%g"%(lab,z),N,round(m+z*sdv,2)))
            for k in (1.0,1.5,2.0,2.5,3.0):
                if abs(k*m-tgt)<=tol: hits.append((xn,"mean*%g"%k,N,round(k*m,2)))
            for p in (80,90,95,99):
                kk=max(1, math.ceil(p/100.0*N)); pv=srt[kk-1]
                if abs(pv-tgt)<=tol: hits.append((xn,"pnr%d"%p,N,round(pv,2)))
                r=p/100.0*N-0.5
                if 0<r<N-1:
                    lo=int(math.floor(r)); pl=srt[lo]+(srt[lo+1]-srt[lo])*(r-lo)
                    if abs(pl-tgt)<=tol: hits.append((xn,"pli%d"%p,N,round(pl,2)))
            if xn in ("C","H","L","hl2"):
                # percentile spread (p95-p5, p90-p10) and range/2
                for (a_,b_) in ((90,10),(95,5)):
                    ka=max(1, math.ceil(a_/100.0*N)); kb=max(1, math.ceil(b_/100.0*N))
                    sp=srt[ka-1]-srt[kb-1]
                    for div in (1.0,2.0):
                        if abs(sp/div-tgt)<=tol: hits.append((xn,"(p%d-p%d)/%g"%(a_,b_,div),N,round(sp/div,2)))
    allhits[name]=hits
    print(name,"target",tgt,"exact hits:",len(hits))
    for h in hits[:60]: print("   ",h)
k1={(a,b) for (a,b,N,v) in allhits["1D"]}; k2={(a,b) for (a,b,N,v) in allhits["4H"]}
print("families hitting both:", sorted(k1&k2))
for fam in sorted(k1&k2):
    print(fam, "1D N:", [N for (a,b,N,v) in allhits["1D"] if (a,b)==fam][:12], "| 4H N:", [N for (a,b,N,v) in allhits["4H"] if (a,b)==fam][:12])
