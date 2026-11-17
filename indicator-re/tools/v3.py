import sys, math; sys.path.insert(0, sys.argv[1])
from bn import *; from ta import *
D = load(sys.argv[2]); H4 = load(sys.argv[3])
sets = {
 "1D": (cut(D, ms(2023,4,17), last=(30286.6,30307.4,29714.1,29835.3)), dict(TLLJ=27974.5, d=2755.0)),
 "4H": (cut(H4, ms(2023,4,17,8), last=(29831.2,29913.6,29781.6,29835.1)), dict(TLLJ=30413.7, d=644.9)),
}
def pct_nearest(vals, p):
    s=sorted(vals); k=max(1, math.ceil(p/100.0*len(s))); return s[k-1]
def pct_linear(vals, p):
    s=sorted(vals); n=len(s)
    # Pine percentile_linear_interpolation: rank = p/100*n - 0.5 (0-based), linear between closest ranks
    r=p/100.0*n-0.5
    if r<=0: return s[0]
    if r>=n-1: return s[-1]
    lo=int(math.floor(r)); f=r-lo; return s[lo]+(s[lo+1]-s[lo])*f
res = {}
for name,(b,a) in sets.items():
    O=[x[1] for x in b]; Hh=[x[2] for x in b]; L=[x[3] for x in b]; C=[x[4] for x in b]; n=len(b)
    src = {"close":C, "hl2":[(Hh[i]+L[i])/2 for i in range(n)], "hlc3":[(Hh[i]+L[i]+C[i])/3 for i in range(n)],
           "ohlc4":[(O[i]+Hh[i]+L[i]+C[i])/4 for i in range(n)], "open":O, "high":Hh, "low":L}
    # ---- TLLJ brute force
    hits=set()
    for sn,s in src.items():
        for ln in range(2,301):
            for mn,fn in (("sma",sma),("ema",ema),("rma",rma)):
                v=fn(s,ln)[-1]
                if v is not None and abs(v-a["TLLJ"])<=0.06: hits.add((mn,sn,ln))
            if ln<=120:
                v=wma(s,ln)[-1]
                if abs(v-a["TLLJ"])<=0.06: hits.add(("wma",sn,ln))
    res[name+"_tllj"]=hits
    print(name,"TLLJ target",a["TLLJ"],"matches:",sorted(hits))
    # ---- d brute force
    tr=[Hh[0]-L[0]]+[max(Hh[i]-L[i],abs(Hh[i]-C[i-1]),abs(L[i]-C[i-1])) for i in range(1,n)]
    rng=[Hh[i]-L[i] for i in range(n)]
    dc=[0.0]+[C[i]-C[i-1] for i in range(1,n)]
    adc=[abs(v) for v in dc]
    body=[abs(C[i]-O[i]) for i in range(n)]
    series={"TR":tr,"H-L":rng,"|dC|":adc,"dC":dc,"|C-O|":body}
    dh=set()
    lens=list(range(10,301,5))+[350,400,450,500,600,700,800,900,1000,1200,n]
    for sn,s in series.items():
        for ln in lens:
            if ln>n: continue
            w=s[n-ln:]
            for p in (80,85,90,95,97.5,99):
                for kind,fn in (("pnr",pct_nearest),("pli",pct_linear)):
                    v=fn(w,p)
                    if abs(v-a["d"])<=max(0.6,a["d"]*0.0005): dh.add((kind,sn,ln,p,round(v,2)))
            m=sum(w)/ln; sd=math.sqrt(sum((x-m)**2 for x in w)/ln)
            for z in (1.0,1.2816,1.5,1.645,1.96,2.0,2.326,2.576,3.0):
                if abs(z*sd-a["d"])<=max(0.6,a["d"]*0.0005): dh.add(("z*sd",sn,ln,z,round(z*sd,2)))
            for k in (1.0,1.5,2.0,2.5,3.0,1.645,1.2816,1.96):
                if abs(k*m-a["d"])<=max(0.6,a["d"]*0.0005): dh.add(("k*mean",sn,ln,k,round(k*m,2)))
    res[name+"_d"]=dh
    print(name,"d target",a["d"],"matches:",sorted(dh)[:40])
print("== common TLLJ definitions:", sorted(res["1D_tllj"] & res["4H_tllj"]))
c1={(k,s,l,p) for (k,s,l,p,v) in res["1D_d"]}; c2={(k,s,l,p) for (k,s,l,p,v) in res["4H_d"]}
print("== common d definitions:", sorted(c1 & c2))
