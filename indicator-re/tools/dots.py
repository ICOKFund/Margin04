import sys
from PIL import Image
import numpy as np
src=sys.argv[1]; y0=int(sys.argv[2]); y1=int(sys.argv[3]); x1=int(sys.argv[4])
im=np.asarray(Image.open(src).convert("RGB")).astype(int)
print("size", im.shape)
sub=im[y0:y1,:x1]
R,G,B=sub[...,0],sub[...,1],sub[...,2]
def blobs(mask, minpix=6):
    H,W=mask.shape; seen=np.zeros_like(mask,bool); out=[]
    ys,xs=np.nonzero(mask)
    for y,x in zip(ys,xs):
        if seen[y,x]: continue
        st=[(y,x)]; seen[y,x]=True; pts=[]
        while st:
            cy,cx=st.pop(); pts.append((cy,cx))
            for dy in (-1,0,1):
                for dx in (-1,0,1):
                    ny,nx=cy+dy,cx+dx
                    if 0<=ny<H and 0<=nx<W and mask[ny,nx] and not seen[ny,nx]:
                        seen[ny,nx]=True; st.append((ny,nx))
        if len(pts)>=minpix:
            a=np.array(pts); out.append((a[:,1].mean(), a[:,0].mean()+y0, len(pts), a[:,1].min(), a[:,1].max()))
    return out
dark=(R<70)&(G>75)&(G<140)&(B<90)&(G-R>35)          # dark green dot centres
db=sorted(blobs(dark,8))
print("dark-green dots:", len(db))
# group dots into rows by y
rows={}
for x,y,n,xa,xb in db:
    key=None
    for k in rows:
        if abs(k-y)<=2.0: key=k; break
    if key is None: key=y; rows[key]=[]
    rows[key].append(x)
for k in sorted(rows):
    xs=sorted(rows[k]); print("  y=%.1f  n=%d  x: %s" % (k, len(xs), " ".join("%.0f"%v for v in xs)))
# purple / cyan line rows at right edge columns
def colrows(cond, xa, xb):
    m=cond[:, xa:xb].sum(axis=1); return [(y0+i, int(v)) for i,v in enumerate(m) if v>=(xb-xa)*0.6]
purple=(R>130)&(R<190)&(G<70)&(B>140)
cyan=(R<60)&(G>170)&(B>190)
xs_right=int(sys.argv[5]); 
print("purple rows near x=%d:"%xs_right, colrows(purple, xs_right-12, xs_right))
print("cyan rows near x=%d:"%xs_right, colrows(cyan, xs_right-12, xs_right))
