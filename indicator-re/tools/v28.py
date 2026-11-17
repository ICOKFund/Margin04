import sys, math; sys.path.insert(0, sys.argv[1])
from ta import *; import ds
B = ds.bundle(*sys.argv[2:6])
def pnr(w,p):
    s=sorted(w); k=max(1, math.ceil(p/100.0*len(s))); return s[k-1]
def pli(w,p):
    s=sorted(w); n=len(s); r=p/100.0*n-0.5
    if r<=0: return s[0]
    if r>=n-1: return s[-1]
    lo=int(math.floor(r)); return s[lo]+(s[lo+1]-s[lo])*(r-lo)
def sd(w):
    m=sum(w)/len(w); return math.sqrt(sum((x-m)**2 for x in w)/len(w))
allhits={}
for name,(O,H,L,C,V,T,tick,tg) in B.items():
    d=tg["d"]; n=len(C)
    for (lp,rp) in ((2,2),(9,9)):
        ph=pivots(H,lp,rp,True); pl=pivots(L,lp,rp,False)
        ev=sorted([(c,'H',v) for c,p,v in ph]+[(c,'L',v) for c,p,v in pl])
        # series
        dH=[abs(ev2[2]-ev1[2]) for ev1,ev2 in zip([e for e in ev if e[1]=='H'][:-1],[e for e in ev if e[1]=='H'][1:])]
        dL=[abs(ev2[2]-ev1[2]) for ev1,ev2 in zip([e for e in ev if e[1]=='L'][:-1],[e for e in ev if e[1]=='L'][1:])]
        pooled=dH+dL
        # box height after each event
        fh=fl=None; box=[]
        for c,t,v in ev:
            if t=='H': fh=v
            else: fl=v
            if fh is not None and fl is not None: box.append(abs(fh-fl))
        # zigzag swings: consecutive opposite-type events
        zz=[]; last=None
        for c,t,v in ev:
            if last is None: last=(t,v); continue
            if t!=last[0]: zz.append(abs(v-last[1])); last=(t,v)
            else:
                if (t=='H' and v>last[1]) or (t=='L' and v<last[1]): last=(t,v)
        alts=[abs(ev[k][2]-ev[k-1][2]) for k in range(1,len(ev)) if ev[k][1]!=ev[k-1][1]]
        series={"dH":dH,"dL":dL,"pooled|dFr|":pooled,"box":box,"zigzag":zz,"alt":alts}
        for sn,s in series.items():
            for N in list(range(5,len(s)+1)):
                w=s[-N:]
                for p in (50,75,80,85,90,95):
                    for kind,f in (("pnr",pnr),("pli",pli)):
                        v=f(w,p)
                        if abs(v-d)<=tick/2+1e-9: allhits.setdefault(name,set()).add(("piv%d"%lp,sn,kind,p,N if N<len(s) else "all"))
                m=sum(w)/N
                for k in (0.5,1.0,1.5,2.0):
                    if abs(k*m-d)<=tick/2+1e-9: allhits.setdefault(name,set()).add(("piv%d"%lp,sn,"mean*%g"%k,0,N if N<len(s) else "all"))
                for z in (1.0,1.2816,1.645,1.96,2.0):
                    if abs(m+z*sd(w)-d)<=tick/2+1e-9: allhits.setdefault(name,set()).add(("piv%d"%lp,sn,"mean+%gsd"%z,0,N if N<len(s) else "all"))
for k,v in allhits.items(): print(k, len(v), sorted(v, key=str)[:8])
fam={k:{(a,b,c,p,N) for (a,b,c,p,N) in v} for k,v in allhits.items()}
keys=list(fam)
if len(keys)==4:
    print("common exact (incl. N):", set.intersection(*fam.values()))
    famN={k:{(a,b,c,p) for (a,b,c,p,N) in v} for k,v in allhits.items()}
    print("common family (any N):", set.intersection(*famN.values()))
