import sys, datetime as dt, math; sys.path.insert(0, sys.argv[1])
from ta import *; import yh
w = yh.cut(yh.to_weekly(yh.load_daily(sys.argv[2])), dt.date(2023,4,17), last=(15.10,16.36,14.48,14.67))
D=[x[0] for x in w]; O=[x[1] for x in w]; H=[x[2] for x in w]; L=[x[3] for x in w]; C=[x[4] for x in w]; n=len(w)
dots={dt.date(2022,2,28),dt.date(2022,4,18),dt.date(2022,4,25),dt.date(2022,5,2),dt.date(2022,5,9),dt.date(2022,6,6),dt.date(2022,6,13),dt.date(2022,6,27),dt.date(2022,10,3)}
hl2=[(H[i]+L[i])/2 for i in range(n)]
lips=rma(hl2,5); teeth=rma(hl2,8); jaw=rma(hl2,13)
m5=sma(C,5); m10=sma(C,10); m20=sma(C,20); sd20=stdev(C,20)
tr=[H[0]-L[0]]+[max(H[i]-L[i],abs(H[i]-C[i-1]),abs(L[i]-C[i-1])) for i in range(1,n)]; atr=rma(tr,14)
def piv_held(x,l,r,hi):
    out=[None]*n; cur=None; ev={c:v for c,p,v in pivots(x,l,r,hi)}
    for i in range(n):
        if i in ev: cur=ev[i]
        out[i]=cur
    return out
FrH=piv_held(H,2,2,True); FrL=piv_held(L,2,2,False)
s=next(i for i,x in enumerate(w) if x[0]>=dt.date(2022,2,7)); e=next(i for i,x in enumerate(w) if x[0]>=dt.date(2022,11,7))
print("week        dot  C>O  H>lips Hx>lips[3] H>teeth[5] H>jaw[8] C<lips[3] C<teeth[5] lips<teeth<jaw(sh) H>m5 H>m10 C<FrL[1] H>FrH[1] L<FrL[1] zC   TR/ATR")
for i in range(s,e+1):
    li3=lips[i-3]; te5=teeth[i-5]; ja8=jaw[i-8]
    order = lips[i-3] < teeth[i-5] < jaw[i-8]
    print("%s  %s   %s   %s     %s        %s        %s      %s       %s          %s           %s   %s    %s       %s       %s     %+5.2f %4.2f" % (
        D[i], "●" if D[i] in dots else "·", int(C[i]>O[i]), int(H[i]>lips[i]), int(H[i]>li3), int(H[i]>te5), int(H[i]>ja8), int(C[i]<li3), int(C[i]<te5),
        int(order), int(H[i]>m5[i]), int(H[i]>m10[i]), int(C[i]<FrL[i-1]), int(H[i]>FrH[i-1]), int(L[i]<FrL[i-1]), (C[i]-m20[i])/sd20[i], tr[i]/atr[i-1]))
