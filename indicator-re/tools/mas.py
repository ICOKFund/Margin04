import math
from ta import sma, ema, rma, wma
def _nz(v, d): return d if v is None else v
def hma(x,n):
    h=max(1,n//2); s=max(1,int(math.floor(math.sqrt(n))))
    a=wma(x,h); b=wma(x,n); d=[(2*a[i]-b[i]) if (a[i] is not None and b[i] is not None) else None for i in range(len(x))]
    st=next((i for i,v in enumerate(d) if v is not None), None)
    if st is None: return [None]*len(x)
    r=wma(d[st:],s); return [None]*st+r
def chain(f, x, n, times):
    out=x
    for _ in range(times):
        st=next((i for i,v in enumerate(out) if v is not None), None)
        r=f(out[st:], n); out=[None]*st+r
    return out
def dema(x,n):
    e1=ema(x,n); e2=chain(ema,e1,n,1); return [(2*a-b) if (a is not None and b is not None) else None for a,b in zip(e1,e2)]
def tema(x,n):
    e1=ema(x,n); e2=chain(ema,e1,n,1); e3=chain(ema,e2,n,1)
    return [(3*a-3*b+c) if (a is not None and b is not None and c is not None) else None for a,b,c in zip(e1,e2,e3)]
def t3(x,n,vf=0.7):
    e=[ema(x,n)]
    for _ in range(5): e.append(chain(ema,e[-1],n,1))
    a=vf; c1=-a**3; c2=3*a*a+3*a**3; c3=-6*a*a-3*a-3*a**3; c4=1+3*a+a**3+3*a*a
    out=[]
    for i in range(len(x)):
        if any(s[i] is None for s in e[2:]): out.append(None)
        else: out.append(c1*e[5][i]+c2*e[4][i]+c3*e[3][i]+c4*e[2][i])
    return out
def alma(x,n,off=0.85,sig=6.0):
    m=off*(n-1); s=n/sig; w=[math.exp(-((k-m)**2)/(2*s*s)) for k in range(n)]; ws=sum(w)
    return [None]*(n-1)+[sum(x[i-n+1+k]*w[k] for k in range(n))/ws for i in range(n-1,len(x))]
def lsma(x,n,off=0):
    out=[None]*len(x); sx=n*(n-1)/2.0; sxx=(n-1)*n*(2*n-1)/6.0
    for i in range(n-1,len(x)):
        w=x[i-n+1:i+1]; sy=sum(w); sxy=sum(k*w[k] for k in range(n))
        b=(n*sxy-sx*sy)/(n*sxx-sx*sx); a=(sy-b*sx)/n; out[i]=a+b*(n-1-off)
    return out
def zlema(x,n):
    lag=(n-1)//2; d=[None]*lag+[x[i]+(x[i]-x[i-lag]) for i in range(lag,len(x))]
    st=lag; r=ema(d[st:],n); return [None]*st+r
def kama(x,n=10,fast=2,slow=30):
    fs=2/(fast+1); ss=2/(slow+1); out=[None]*len(x); k=None
    for i in range(len(x)):
        if i<n: continue
        ch=abs(x[i]-x[i-n]); vol=sum(abs(x[j]-x[j-1]) for j in range(i-n+1,i+1)); er=ch/vol if vol else 0
        sc=(er*(fs-ss)+ss)**2; k = x[i-1] if k is None else k
        k=k+sc*(x[i]-k); out[i]=k
    return out
def mcginley(x,n):
    out=[None]*len(x); md=None
    e=ema(x,n)
    for i in range(len(x)):
        if md is None:
            if e[i] is not None: md=e[i]; out[i]=md
            continue
        md=md+(x[i]-md)/(n*(x[i]/md)**4); out[i]=md
    return out
def supersmoother(x,n):
    a1=math.exp(-math.sqrt(2)*math.pi/n); b1=2*a1*math.cos(math.sqrt(2)*math.pi/n); c3=-a1*a1; c2=b1; c1=1-c2-c3
    out=[]; 
    for i in range(len(x)):
        p1=out[i-1] if i>=1 else x[i-1] if i>=1 else x[0]
        p2=out[i-2] if i>=2 else (x[i-2] if i>=2 else x[0])
        if i<2: out.append(x[i]); continue
        out.append(c1*(x[i]+x[i-1])/2*0+c1*x[i]+c2*out[i-1]+c3*out[i-2]) if False else out.append(c1*(x[i]+x[i-1])/2+c2*out[i-1]+c3*out[i-2])
    return out
def laguerre(x,g):
    L0=L1=L2=L3=None; out=[]
    for v in x:
        if L0 is None: L0=L1=L2=L3=v
        l0=(1-g)*v+g*L0; l1=-g*l0+L0+g*L1; l2=-g*l1+L1+g*L2; l3=-g*l2+L2+g*L3
        L0,L1,L2,L3=l0,l1,l2,l3; out.append((l0+2*l1+2*l2+l3)/6)
    return out
def jma(x,n,phase=0,power=2):
    pr = 0.5 if phase<-100 else 2.5 if phase>100 else phase/100+1.5
    beta=0.45*(n-1)/(0.45*(n-1)+2); alpha=beta**power
    e0=e1=e2=j=0.0; out=[]
    for v in x:
        e0=(1-alpha)*v+alpha*e0
        e1=(v-e0)*(1-beta)+beta*e1
        e2=(e0+pr*e1-j)*(1-alpha)**2+alpha*alpha*e2
        j=e2+j; out.append(j)
    return out
def vwma(x,v,n):
    out=[None]*len(x)
    for i in range(n-1,len(x)):
        sv=sum(v[i-n+1:i+1]); out[i]=sum(x[k]*v[k] for k in range(i-n+1,i+1))/sv if sv else None
    return out
