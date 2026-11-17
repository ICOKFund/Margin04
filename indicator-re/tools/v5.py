import sys, math; sys.path.insert(0, sys.argv[1])
from bn import *; from ta import *
D = load(sys.argv[2])
b = cut(D, ms(2023,4,17), last=(30286.6,30307.4,29714.1,29835.3))
T=[x[0] for x in b]; O=[x[1] for x in b]; Hh=[x[2] for x in b]; L=[x[3] for x in b]; C=[x[4] for x in b]; n=len(b)
idx={ts(t)[:10]:i for i,t in enumerate(T)}
# approximate d(t) read from the screenshot (pixel precision about +-30), exact on 04-17
obs={"2023-02-09":2850,"2023-02-24":2851,"2023-03-14":2857,"2023-03-20":2779,"2023-03-27":2730,"2023-04-04":2739,"2023-04-17":2755.0}
tr=[Hh[0]-L[0]]+[max(Hh[i]-L[i],abs(Hh[i]-C[i-1]),abs(L[i]-C[i-1])) for i in range(1,n)]
rng=[Hh[i]-L[i] for i in range(n)]
dc=[0.0]+[C[i]-C[i-1] for i in range(1,n)]; adc=[abs(v) for v in dc]
def pnr(w,p):
    s=sorted(w); k=max(1, math.ceil(p/100.0*len(s))); return s[k-1]
def sd(w):
    m=sum(w)/len(w); return math.sqrt(sum((x-m)**2 for x in w)/len(w))
fam={
 "p90(TR)":   lambda i,N: pnr(tr[i-N+1:i+1],90),
 "p90(H-L)":  lambda i,N: pnr(rng[i-N+1:i+1],90),
 "p90|dC|":   lambda i,N: pnr(adc[i-N+1:i+1],90),
 "p95|dC|":   lambda i,N: pnr(adc[i-N+1:i+1],95),
 "sd(dC)":    lambda i,N: sd(dc[i-N+1:i+1]),
 "sd(TR)":    lambda i,N: sd(tr[i-N+1:i+1]),
 "mean(TR)":  lambda i,N: sum(tr[i-N+1:i+1])/N,
 "sd(C)":     lambda i,N: sd(C[i-N+1:i+1]),
}
res=[]
for fn,f in fam.items():
    for N in list(range(20,400,10))+list(range(400,1150,25)):
        i0=idx["2023-04-17"]
        if i0-N+1<0: continue
        base=f(i0,N); k=2755.0/base
        err=0; ok=True; vals=[]
        for dstr,tv in obs.items():
            i=idx[dstr]
            if i-N+1<0: ok=False; break
            v=k*f(i,N); vals.append(v); err+=(v-tv)**2
        if ok: res.append((math.sqrt(err/len(obs)), fn, N, k, vals))
res.sort()
print("best shape fits (rms error vs screenshot-read d(t), scale k fitted on 04-17):")
for r in res[:14]:
    print("rms %6.1f  %-9s N=%4d  k=%.4f  series: %s" % (r[0], r[1], r[2], r[3], " ".join("%.0f"%v for v in r[4])))
print("targets:                                      ", " ".join(str(int(v)) for v in obs.values()))
