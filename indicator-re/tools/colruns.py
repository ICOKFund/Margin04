import sys
from PIL import Image
import numpy as np
src=sys.argv[1]; x=int(sys.argv[2]); y0=int(sys.argv[3]); y1=int(sys.argv[4])
im=np.asarray(Image.open(src).convert("RGB")).astype(int)
col=im[y0:y1, x]
bg=np.array([241,243,246])
runs=[]; cur=None
for k,p in enumerate(col):
    y=y0+k; t=tuple(int(v) for v in p)
    isbg = abs(t[0]-t[1])<10 and abs(t[1]-t[2])<10 and t[0]>225
    if isbg:
        if cur: runs.append(cur); cur=None
        continue
    if cur and abs(np.array(t)-np.array(cur[2])).sum()<60: cur[1]=y
    else:
        if cur: runs.append(cur)
        cur=[y,y,t]
if cur: runs.append(cur)
for a,b,t in runs: print("x=%d y %4d-%4d rgb%s" % (x,a,b,t))
