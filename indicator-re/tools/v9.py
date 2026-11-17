import sys, math, datetime as dt; sys.path.insert(0, sys.argv[1])
from ta import *; import yh, bn
ix = yh.cut(yh.load_daily(sys.argv[2]), dt.date(2023,5,10), last=(12286.66,12324.01,12211.58,12240.73))
sx = yh.cut(yh.to_weekly(yh.load_daily(sys.argv[3])), dt.date(2023,4,17), last=(15.10,16.36,14.48,14.67))
bd = bn.cut(bn.load(sys.argv[4]), bn.ms(2023,4,17), last=(30286.6,30307.4,29714.1,29835.3))
b4 = bn.cut(bn.load(sys.argv[5]), bn.ms(2023,4,17,8), last=(29831.2,29913.6,29781.6,29835.1))
def lab(b,i): 
    t=b[i][0]; return str(t) if not isinstance(t,int) else bn.ts(t)
sets={"IXIC 1D":(ix,"2023-02-02","2022-12-22"),"SOXL 1W":(sx,"2021-12-06","2022-10-03"),
      "BTC 1D":(bd,"2023-01-14 00:00","2022-11-09 00:00"),"BTC 4H":(b4,"2023-04-11 00:00","2023-03-22 16:00")}
for name,(b,ls,ss) in sets.items():
    O=[x[1] for x in b]; Hh=[x[2] for x in b]; L=[x[3] for x in b]; C=[x[4] for x in b]; n=len(b)
    m20=sma(C,20); s20=stdev(C,20)
    tr=[Hh[0]-L[0]]+[max(Hh[i]-L[i],abs(Hh[i]-C[i-1]),abs(L[i]-C[i-1])) for i in range(1,n)]
    atr=rma(tr,14)
    print("=====",name)
    for tag,key in (("LS(long) bar",ls),("SS(short) bar",ss)):
        i=next(k for k in range(n) if lab(b,k)==key)
        for j in range(i-2,i+3):
            z=(C[j]-m20[j])/s20[j]; zh=(Hh[j]-m20[j])/s20[j]; zl=(L[j]-m20[j])/s20[j]
            hh20=max(Hh[j-20:j]); ll20=min(L[j-20:j])
            print("  %s%-17s O %-9.2f H %-9.2f L %-9.2f C %-9.2f | zC %+5.2f zH %+5.2f zL %+5.2f | TR/ATR[1] %4.2f | C>HH20[1]? %s C<LL20[1]? %s" % (
                "*" if j==i else " ", lab(b,j), O[j],Hh[j],L[j],C[j], z,zh,zl, tr[j]/atr[j-1], C[j]>hh20, C[j]<ll20))
        print("   ^", tag)
