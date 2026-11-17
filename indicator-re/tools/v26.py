import sys, math; sys.path.insert(0, sys.argv[1])
import bn
def ss_fareid(src, n):
    a1=math.exp(-math.sqrt(2)*math.pi/n); b1=2*a1*math.cos(math.sqrt(2)*math.pi/n); c3=-a1*a1; c2=b1; c1=1-c2-c3
    out=[None]*len(src)
    for i,v in enumerate(src):
        if v is None: continue
        p1 = out[i-1] if i>=1 and out[i-1] is not None else (src[i-1] if i>=1 else None)
        p2 = out[i-2] if i>=2 and out[i-2] is not None else (src[i-2] if i>=2 else None)
        if p1 is None or p2 is None: continue
        out[i]=c1*v+c2*p1+c3*p2
    return out
b = bn.cut(bn.load(sys.argv[2]), bn.ms(2023,5,7), last=(28837.9,29137.0,28691.2,28746.8))
H=[x[2] for x in b]; L=[x[3] for x in b]; C=[x[4] for x in b]; n=len(b)
hlc3=[(H[i]+L[i]+C[i])/3 for i in range(n)]
tr=[None]+[max(H[i]-L[i],abs(H[i]-C[i-1]),abs(L[i]-C[i-1])) for i in range(1,n)]
for length in (200,):
    m=ss_fareid(hlc3,length)[-1]; r=ss_fareid(tr,length)[-1]
    lv=[m+r*math.pi*2.415, m+r*math.pi*1.0, m, m-r*math.pi*1.0, m-r*math.pi*2.415]
    print("MRC(SuperSmoother, hlc3, %d, inner 1.0, outer 2.415) @2023-05-07:" % length)
    for nm,v,obs in zip(["outer up","inner up","mean","inner dn","outer dn"], lv, [34517,29676,26228,22814,17938]):
        print("   %-9s computed %9.1f   screenshot(pixel) %7d   diff %+6.1f (%.2f px)" % (nm, v, obs, v-obs, (v-obs)/34.83))
