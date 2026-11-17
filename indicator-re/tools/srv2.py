# LonesomeTheBlue "Support Resistance - Dynamic v2" re-implementation (from memory; variants selectable)
import math
def pine_pivots(x, left, right, high=True):
    ev={}
    for i in range(left+right, len(x)):
        p=i-right; v=x[p]
        if high:
            ok = all(x[j]<v for j in range(p+1,i+1)) and all(x[j]<=v for j in range(p-left,p))
        else:
            ok = all(x[j]>v for j in range(p+1,i+1)) and all(x[j]>=v for j in range(p-left,p))
        if ok: ev[i]=v
    return ev
def sr_levels(H, L, end, prd=10, chw=10.0, maxpp=20, maxsr=5, minstr=2, loop=300, variant=1, tick=0.01, src="HL", O=None, C=None):
    if src=="HL": s1, s2 = H, L
    else: s1=[max(C[i],O[i]) for i in range(len(C))]; s2=[min(C[i],O[i]) for i in range(len(C))]
    s1=s1[:end+1]; s2=s2[:end+1]
    PH=pine_pivots(s1,prd,prd,True); PL=pine_pivots(s2,prd,prd,False)
    evbars=sorted(set(PH)|set(PL))
    last=evbars[-1]
    pv=[]
    for b in evbars:
        pv.insert(0, PH[b] if b in PH else PL[b])
        if len(pv)>maxpp: pv.pop()
        if b==last: break
    hh=max(H[last-loop+1:last+1]); ll=min(L[last-loop+1:last+1]); cw=(hh-ll)*chw/100.0
    up=[]; dn=[]; stg=[]
    def get_vals(ind):
        lo=pv[ind]; hi=lo; n=0
        for cpp in pv:
            if variant==1:
                w = hi-cpp if cpp<=lo else cpp-lo
                if w<=cw:
                    lo = cpp if cpp<=lo else lo
                    hi = cpp if cpp>lo else hi
                    n+=1
            else:
                w = hi-cpp if cpp<=hi else cpp-lo
                if w<=cw:
                    if cpp<=hi: lo=min(lo,cpp)
                    else: hi=max(hi,cpp)
                    n+=1
        return hi,lo,n
    for x in range(len(pv)):
        hi,lo,n=get_vals(x)
        ret=True
        for i in range(len(up)):
            if (lo<=up[i]<=hi) or (lo<=dn[i]<=hi):
                if n>=stg[i]:
                    del stg[i]; del up[i]; del dn[i]
                else: ret=False
                break
        if ret:
            loc=len(stg)
            for i in range(len(stg)-1,-1,-1):
                if n<=stg[i]: break
                loc=i
            if loc<maxsr and n>=minstr:
                stg.insert(loc,n); up.insert(loc,hi); dn.insert(loc,lo)
                if len(stg)>maxsr: stg.pop(); up.pop(); dn.pop()
    import math as _m
    def r2t(v):
        q=v/tick
        return (_m.floor(q+0.5) if q>=0 else -_m.floor(-q+0.5))*tick
    mids=[r2t((up[i]+dn[i])/2) for i in range(len(up))]
    return last, mids, stg, cw
