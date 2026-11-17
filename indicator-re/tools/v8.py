import sys, math, datetime as dt; sys.path.insert(0, sys.argv[1])
from ta import *; from yh import *
ix = cut(load_daily(sys.argv[2]), dt.date(2023,5,10), last=(12286.66,12324.01,12211.58,12240.73))
sx = cut(to_weekly(load_daily(sys.argv[3])), dt.date(2023,4,17), last=(15.10,16.36,14.48,14.67))
T = {"IXIC 1D": (ix, dict(MA3=12225.73,MA5=12175.80,MA10=12156.63,MA20=12107.35,MA60=11847.12,MA120=11481.23,MA240=11500.48,MA360=12273.08,MA480=12946.90,MA600=13054.67,
                          BBU=12349.80,BBL=11864.91,HH=12261.32,LL=11925.37,HL20=12227.93,LL20=11798.77,Fast=12158.55,Mid=12122.82,Slow=12066.53,LS=12024.14,SS=10599.34)),
     "SOXL 1W": (sx, dict(MA3=15.30,MA5=16.16,MA10=15.65,MA20=14.18,MA60=17.34,MA120=31.14,MA360=16.90,MA480=13.13,
                          BBU=18.93,HH=18.34,LL=13.15,HL20=18.40,LL20=6.21,Fast=15.63,Mid=15.11,Slow=15.00,LS=56.78,SS=11.92))}
for name,(b,a) in T.items():
    Dt=[x[0] for x in b]; O=[x[1] for x in b]; Hh=[x[2] for x in b]; L=[x[3] for x in b]; C=[x[4] for x in b]; n=len(b)
    print("=====",name,"bars",n,"last",Dt[-1],"OHLC",b[-1][1:5], " prev bar",Dt[-2],b[-2][1:5])
    out=[]
    for k in (3,5,10,20,60,120,240,360,480,600):
        key="MA%d"%k
        if key in a and n>=k: out.append("%s %.2f (target %.2f)"%(key, sma(C,k)[-1], a[key]))
    print("  SMA:", " | ".join(out))
    m=sma(C,20)[-1]; sdv=stdev(C,20)[-1]
    print("  BB(20,2): upper %.2f lower %.2f (target %s / %s)   sigma20=%.4f" % (m+2*sdv, m-2*sdv, a.get("BBU"), a.get("BBL"), sdv))
    ph=pivots(Hh,2,2,True); pl=pivots(L,2,2,False)
    print("  fractal(2,2): HH %.2f [%s] LL %.2f [%s]  (target %.2f / %.2f)" % (ph[-1][2], Dt[ph[-1][1]], pl[-1][2], Dt[pl[-1][1]], a["HH"], a["LL"]))
    ph=pivots(Hh,9,10,True); pl=pivots(L,9,10,False)
    print("  pivot(9,10): HL20 %.2f [%s, confirmed %s] LL20 %.2f [%s, confirmed %s]  (target %.2f / %.2f)" % (ph[-1][2], Dt[ph[-1][1]], Dt[ph[-1][0]], pl[-1][2], Dt[pl[-1][1]], Dt[pl[-1][0]], a["HL20"], a["LL20"]))
    hl2=[(Hh[i]+L[i])/2 for i in range(n)]
    print("  alligator SMMA(hl2,5/8/13): %.2f / %.2f / %.2f  (target %.2f / %.2f / %.2f)" % (rma(hl2,5)[-1], rma(hl2,8)[-1], rma(hl2,13)[-1], a["Fast"], a["Mid"], a["Slow"]))
    for key in ("LS","SS"):
        v=a[key]; hits=[(str(Dt[i]),nm) for i in range(n) for nm,arr in (("O",O),("H",Hh),("L",L),("C",C)) if abs(arr[i]-v)<0.0051]
        print("  %s=%.2f exact OHLC matches:"%(key,v), hits[-3:])
