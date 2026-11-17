import math
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
