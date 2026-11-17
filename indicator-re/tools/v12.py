import sys, math; sys.path.insert(0, sys.argv[1])
from ta import *; import ds
B = ds.bundle(*sys.argv[2:6])
series={}
for name,(O,H,L,C,V,T,tick,tg) in B.items():
    n=len(C)
    tr=[H[0]-L[0]]+[max(H[i]-L[i],abs(H[i]-C[i-1]),abs(L[i]-C[i-1])) for i in range(1,n)]
    hl=[H[i]-L[i] for i in range(n)]
    adc=[0.0]+[abs(C[i]-C[i-1]) for i in range(1,n)]
    series[name]=dict(TR=tr,HL=hl,ADC=adc,d=tg["d"],n=n,tick=tick)
names=list(series)
def stat(kind, x, N):
    if kind=="sma": return sum(x[-N:])/N
    if kind=="rma": return rma(x,N)[-1]
    if kind=="ema": return ema(x,N)[-1]
    if kind=="sd":
        w=x[-N:]; m=sum(w)/N; return math.sqrt(sum((v-m)**2 for v in w)/N)
res=[]
for kind in ("sma","rma","ema","sd"):
    for xn in ("TR","HL","ADC"):
        for N in list(range(20,200,5))+list(range(200,685,5)):
            rs=[]
            for nm in names:
                s=series[nm]
                if N>s["n"]: rs=None; break
                rs.append(s["d"]/stat(kind,s[xn],N))
            if rs is None: continue
            mean=sum(rs)/4; spread=(max(rs)-min(rs))/mean
            res.append((spread,kind,xn,N,mean,rs))
res.sort()
print("best agreement of ratio d/stat across the 4 datasets (spread = (max-min)/mean):")
for r in res[:25]:
    print("spread %.4f  %s(%s,%d)  mean ratio %.4f   ratios: %s" % (r[0],r[1],r[2],r[3],r[4]," ".join("%.4f"%v for v in r[5])))
