# minimal TA helpers mirroring Pine semantics (lists of floats, None = na)
import math
def sma(x, n):
    out=[None]*len(x); s=0.0
    for i,v in enumerate(x):
        s+=v
        if i>=n: s-=x[i-n]
        if i>=n-1: out[i]=s/n
    return out
def ema(x, n):
    out=[None]*len(x); a=2.0/(n+1); e=None
    for i,v in enumerate(x):
        if i<n-1: continue
        if e is None: e=sum(x[i-n+1:i+1])/n      # Pine seeds with SMA
        else: e=a*v+(1-a)*e
        out[i]=e
    return out
def rma(x, n):  # = SMMA, Pine ta.rma (seeded with SMA)
    out=[None]*len(x); e=None
    for i,v in enumerate(x):
        if i<n-1: continue
        if e is None: e=sum(x[i-n+1:i+1])/n
        else: e=(e*(n-1)+v)/n
        out[i]=e
    return out
def wma(x, n):
    out=[None]*len(x); w=n*(n+1)/2.0
    for i in range(n-1,len(x)):
        out[i]=sum(x[i-n+1+k]*(k+1) for k in range(n))/w
    return out
def stdev(x, n, sample=False):
    out=[None]*len(x)
    for i in range(n-1,len(x)):
        w=x[i-n+1:i+1]; m=sum(w)/n
        out[i]=math.sqrt(sum((v-m)**2 for v in w)/(n-1 if sample else n))
    return out
def highest(x,n,i): return max(x[i-n+1:i+1])
def lowest(x,n,i): return min(x[i-n+1:i+1])
def pivots(x, left, right, high=True):
    """return list of (confirm_index, pivot_index, value) using Pine ta.pivothigh/low semantics"""
    out=[]
    for i in range(left+right, len(x)):
        p=i-right; v=x[p]
        win=x[p-left:i+1]
        if high:
            ok = v==max(win) and all(x[j]<v for j in range(p+1,i+1)) and all(x[j]<=v for j in range(p-left,p))
        else:
            ok = v==min(win) and all(x[j]>v for j in range(p+1,i+1)) and all(x[j]>=v for j in range(p-left,p))
        if ok: out.append((i,p,v))
    return out
