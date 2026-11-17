import sys; sys.path.insert(0, sys.argv[1])
from bn import *; from ta import *
D = load(sys.argv[2]); H4 = load(sys.argv[3])
sets = {
 "1D": (cut(D, ms(2023,4,17), last=(30286.6,30307.4,29714.1,29835.3)),
        dict(HH=31059.0, LL=27166.0, HL20=29184.8, LL20=26480.0, Fast=29806.6, Mid=29329.0, Slow=28570.9, TLLJ=27974.5, d=2755.0, LS=19882.6, SS=18574.9)),
 "4H": (cut(H4, ms(2023,4,17,8), last=(29831.2,29913.6,29781.6,29835.1)),
        dict(HH=30560.0, LL=29714.1, HL20=31059.0, LL20=29925.0, Fast=30116.7, Mid=30174.5, Slow=30134.6, TLLJ=30413.7, d=644.9, LS=29573.9, SS=28881.0)),
}
for name,(b,a) in sets.items():
    T=[x[0] for x in b]; O=[x[1] for x in b]; Hh=[x[2] for x in b]; L=[x[3] for x in b]; C=[x[4] for x in b]
    n=len(b); print("=====", name, "bars", n, "last", ts(T[-1]))
    # 1) fractal box: latest confirmed pivot (2,2)
    ph=pivots(Hh,2,2,True); pl=pivots(L,2,2,False)
    print("fractal(2,2): HH calc %.1f (pivot %s, confirmed %s) target %.1f | LL calc %.1f (pivot %s, confirmed %s) target %.1f" % (
        ph[-1][2], ts(T[ph[-1][1]]), ts(T[ph[-1][0]]), a["HH"], pl[-1][2], ts(T[pl[-1][1]]), ts(T[pl[-1][0]]), a["LL"]))
    # 2) long pivots: try several (left,right)
    for (l,r) in [(10,9),(9,10),(10,10),(9,9),(20,9),(20,10),(19,10),(20,20)]:
        ph=pivots(Hh,l,r,True); pl=pivots(L,l,r,False)
        print("  pivot(%d,%d): HL %.1f (pivot %s, conf %s) | LL %.1f (pivot %s, conf %s)  target %.1f / %.1f" % (
            l,r, ph[-1][2], ts(T[ph[-1][1]])[:13], ts(T[ph[-1][0]])[:13], pl[-1][2], ts(T[pl[-1][1]])[:13], ts(T[pl[-1][0]])[:13], a["HL20"], a["LL20"]))
    # 3) alligator
    hl2=[(Hh[i]+L[i])/2 for i in range(n)]
    for srcname,src in [("hl2",hl2),("close",C)]:
        f=rma(src,5)[-1]; m=rma(src,8)[-1]; s=rma(src,13)[-1]
        print("  alligator SMMA(%s 5/8/13) last-bar values: %.1f / %.1f / %.1f   target %.1f / %.1f / %.1f" % (srcname,f,m,s,a["Fast"],a["Mid"],a["Slow"]))
    # 5) LS / SS exact matches in OHLC
    for key in ("LS","SS"):
        v=a[key]; hits=[]
        for i in range(n):
            for nm,arr in (("O",O),("H",Hh),("L",L),("C",C)):
                if abs(arr[i]-v)<0.051: hits.append((ts(T[i]),nm))
        print("  %s=%.1f exact OHLC matches (last 3):" % (key,v), hits[-3:])
