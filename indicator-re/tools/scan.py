import sys
from PIL import Image
import numpy as np
# usage: scan.py src x0 x1 y0 y1  -> for each row band in [y0,y1], report dominant non-background colour clusters within columns [x0,x1]
src = sys.argv[1]; x0,x1,y0,y1 = [int(v) for v in sys.argv[2:6]]
im = np.asarray(Image.open(src).convert("RGB")).astype(int)
sub = im[y0:y1, x0:x1]
bg = np.array([241,243,246])
def name(c):
    r,g,b = c
    if abs(r-g)<18 and abs(g-b)<18:
        if r>225: return None
        return "black" if r<90 else "gray"
    if b>200 and r<110 and g>120: return "blue_line"
    if b>180 and g>170 and r<60: return "cyan"
    if r>130 and b>140 and g<90: return "purple"
    if r>230 and 120<g<190 and b<60: return "orange"
    if g>150 and r<120 and b<140: return "green"
    if g>90 and r<60 and b<110: return "darkgreen"
    if r>200 and g<120 and b<130: return "red"
    return "other(%d,%d,%d)"%(r,g,b)
rows=[]
for yy in range(sub.shape[0]):
    cnt={}
    for xx in range(sub.shape[1]):
        n=name(sub[yy,xx])
        if n: cnt[n]=cnt.get(n,0)+1
    if cnt:
        top=sorted(cnt.items(), key=lambda kv:-kv[1])[:3]
        rows.append((y0+yy, top))
# compress consecutive rows with same leading colour
out=[]; prev=None
for y,top in rows:
    lead=top[0][0]
    if prev and prev[2]==lead and y-prev[1]<=1:
        prev[1]=y; prev[3]=max(prev[3], top[0][1])
    else:
        prev=[y,y,lead,top[0][1]]; out.append(prev)
for a,b,lead,n in out:
    print("y %4d-%4d  %-22s maxcount=%d"%(a,b,lead,n))
