import sys, datetime as dt; sys.path.insert(0, sys.argv[1])
from ta import *; import yh, bn
def analyze(name, bars, lab, dots_hi, dots_lo, start, ls_lab, ss_lab, show=True):
    O=[x[1] for x in bars]; H=[x[2] for x in bars]; L=[x[3] for x in bars]; C=[x[4] for x in bars]; V=[x[5] for x in bars]; n=len(bars)
    hl2=[(H[i]+L[i])/2 for i in range(n)]
    lips=rma(hl2,5); teeth=rma(hl2,8); jaw=rma(hl2,13)
    mfi=[(H[i]-L[i])/V[i] if V[i] else 0 for i in range(n)]
    out=[]
    for i in range(start,n):
        squat = V[i]>V[i-1] and mfi[i]<mfi[i-1]
        green = V[i]>V[i-1] and mfi[i]>mfi[i-1]
        fake  = V[i]<V[i-1] and mfi[i]>mfi[i-1]
        fade  = V[i]<V[i-1] and mfi[i]<mfi[i-1]
        t = "squat" if squat else "green" if green else "fake" if fake else "fade"
        mark = "●H" if lab(i) in dots_hi else "●L" if lab(i) in dots_lo else ""
        if lab(i)==ls_lab: mark+="(LS)"
        if lab(i)==ss_lab: mark+="(SS)"
        out.append((lab(i), t, mark, C[i]>O[i], C[i]<jaw[i-8], C[i]<teeth[i-5], C[i]<lips[i-3]))
    if show:
        print("=====",name)
        for r in out: print("  %-17s %-5s %-8s up=%d below_jaw=%d below_teeth=%d below_lips=%d" % (r[0], r[1], r[2], r[3], r[4], r[5], r[6]))
    return out
w = yh.cut(yh.to_weekly(yh.load_daily(sys.argv[2])), dt.date(2023,4,17), last=(15.10,16.36,14.48,14.67))
dots_hi={dt.date(2022,2,28),dt.date(2022,4,18),dt.date(2022,4,25),dt.date(2022,5,2),dt.date(2022,5,9),dt.date(2022,6,6),dt.date(2022,6,13),dt.date(2022,6,27),dt.date(2022,10,3)}
s=next(i for i,x in enumerate(w) if x[0]>=dt.date(2022,2,7)); e=next(i for i,x in enumerate(w) if x[0]>=dt.date(2022,11,7))
analyze("SOXL 1W (2022)", w[:e+1], lambda i: w[i][0], dots_hi, set(), s, dt.date(2021,12,6), dt.date(2022,10,3))
