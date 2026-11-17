import sys, datetime as dt; sys.path.insert(0, sys.argv[1])
from ta import *; import bn
def table(name, b, i0, i1, marks):
    T=[x[0] for x in b]; O=[x[1] for x in b]; H=[x[2] for x in b]; L=[x[3] for x in b]; C=[x[4] for x in b]; V=[x[5] for x in b]; n=len(b)
    m20=sma(C,20); s20=stdev(C,20); tr=[H[0]-L[0]]+[max(H[i]-L[i],abs(H[i]-C[i-1]),abs(L[i]-C[i-1])) for i in range(1,n)]; atr=rma(tr,14)
    vs=sma(V,20); hl2=[(H[i]+L[i])/2 for i in range(n)]; lips=rma(hl2,5); teeth=rma(hl2,8); jaw=rma(hl2,13)
    print("=====",name)
    print("  bar               mark  O        H        L        C      | zC    zH    TR/ATR vol/SMA20 vol>v1 lips>teeth>jaw  C>H[1]")
    for i in range(i0,i1):
        print("  %-17s %-5s %-8.1f %-8.1f %-8.1f %-8.1f| %+5.2f %+5.2f %5.2f  %6.2f    %d      %d               %d" % (
            bn.ts(T[i]), marks.get(bn.ts(T[i]),""), O[i],H[i],L[i],C[i], (C[i]-m20[i])/s20[i], (H[i]-m20[i])/s20[i], tr[i]/atr[i-1], V[i]/vs[i-1], int(V[i]>V[i-1]),
            int(lips[i]>teeth[i]>jaw[i]), int(C[i]>H[i-1])))
b4 = bn.cut(bn.load(sys.argv[3]), bn.ms(2023,4,17,8), last=(29831.2,29913.6,29781.6,29835.1))
idx={bn.ts(x[0]):k for k,x in enumerate(b4)}
table("BTC 4H around the long dots", b4, idx["2023-04-10 00:00"], idx["2023-04-11 12:00"]+1,
      {"2023-04-10 12:00":"dot?","2023-04-10 16:00":"dot","2023-04-10 20:00":"dot","2023-04-11 00:00":"dotLS"})
table("BTC 4H around SS", b4, idx["2023-03-22 04:00"], idx["2023-03-23 04:00"]+1, {"2023-03-22 16:00":"SS"})
bd = bn.cut(bn.load(sys.argv[2]), bn.ms(2023,4,17), last=(30286.6,30307.4,29714.1,29835.3))
idd={bn.ts(x[0]):k for k,x in enumerate(bd)}
table("BTC 1D Jan rally", bd, idd["2023-01-08 00:00"], idd["2023-01-18 00:00"]+1, {"2023-01-14 00:00":"LS"})
table("BTC 1D March (no dots expected)", bd, idd["2023-03-09 00:00"], idd["2023-03-24 00:00"]+1, {})
table("BTC 1D Nov 2022", bd, idd["2022-11-06 00:00"], idd["2022-11-12 00:00"]+1, {"2022-11-09 00:00":"SS"})
