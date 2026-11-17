import sys, math; sys.path.insert(0, sys.argv[1])
from bn import *; from ta import *
D = load(sys.argv[2]); H4 = load(sys.argv[3])
sets = {"1D": (cut(D, ms(2023,4,17), last=(30286.6,30307.4,29714.1,29835.3)), 2755.0),
        "4H": (cut(H4, ms(2023,4,17,8), last=(29831.2,29913.6,29781.6,29835.1)), 644.9)}
def pnr(vals,p):
    s=sorted(vals); k=max(1, math.ceil(p/100.0*len(s))); return s[k-1]
def sd(w):
    m=sum(w)/len(w); return math.sqrt(sum((x-m)**2 for x in w)/len(w))
for name,(b,tgt) in sets.items():
    O=[x[1] for x in b]; Hh=[x[2] for x in b]; L=[x[3] for x in b]; C=[x[4] for x in b]; n=len(b)
    tr=[Hh[0]-L[0]]+[max(Hh[i]-L[i],abs(Hh[i]-C[i-1]),abs(L[i]-C[i-1])) for i in range(1,n)]
    dc=[0.0]+[C[i]-C[i-1] for i in range(1,n)]
    ret=[0.0]+[C[i]/C[i-1]-1 for i in range(1,n)]
    lret=[0.0]+[math.log(C[i]/C[i-1]) for i in range(1,n)]
    print("=====",name,"target d =",tgt,"  last close",C[-1])
    print("%6s %9s %9s %9s %10s %10s %12s %12s %12s" % ("N","p90(TR)","p90|dC|","mean(TR)","1.645sd(dC)","1.645sd(TR)","C*1.645sd(r)","C*p90|r|","C*sd(r)"))
    for N in (20,50,100,150,200,250,300,400,500,600,750,900,1000,1200,2000,3000,5000,n):
        if N>n: continue
        w=slice(n-N,n)
        print("%6d %9.1f %9.1f %9.1f %10.1f %10.1f %12.1f %12.1f %12.1f" % (N, pnr(tr[w],90), pnr([abs(v) for v in dc[w]],90), sum(tr[w])/N,
              1.645*sd(dc[w]), 1.645*sd(tr[w]), C[-1]*1.645*sd(ret[w]), C[-1]*pnr([abs(v) for v in ret[w]],90), C[-1]*sd(ret[w])))
