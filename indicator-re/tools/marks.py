import sys
from PIL import Image
import numpy as np
# detect '+' markers of a given colour inside a box; prints (x, y) centres in original image coords
src=sys.argv[1]; x0,y0,x1,y1=[int(v) for v in sys.argv[2:6]]; col=sys.argv[6]
im=np.asarray(Image.open(src).convert("RGB")).astype(int)[y0:y1, x0:x1]
R,G,B=im[...,0],im[...,1],im[...,2]
if col=="orange": m=(R>235)&(G>130)&(G<175)&(B<40)
elif col=="cyan": m=(R<40)&(G>170)&(G<200)&(B>195)&(B<225)
elif col=="purple": m=(R>140)&(R<175)&(G<60)&(B>160)&(B<200)
H,W=m.shape; seen=np.zeros_like(m,bool); out=[]
for y,x in zip(*np.nonzero(m)):
    if seen[y,x]: continue
    st=[(y,x)]; seen[y,x]=True; pts=[]
    while st:
        cy,cx=st.pop(); pts.append((cy,cx))
        for dy in (-1,0,1):
            for dx in (-1,0,1):
                ny,nx=cy+dy,cx+dx
                if 0<=ny<H and 0<=nx<W and m[ny,nx] and not seen[ny,nx]: seen[ny,nx]=True; st.append((ny,nx))
    a=np.array(pts); w=a[:,1].max()-a[:,1].min()+1; h=a[:,0].max()-a[:,0].min()+1
    if 4<=len(pts)<=40 and 3<=w<=9 and 3<=h<=9: out.append((a[:,1].mean()+x0, a[:,0].mean()+y0))
rows={}
for x,y in sorted(out, key=lambda p:(round(p[1]),p[0])):
    k=next((k for k in rows if abs(k-y)<=2), None)
    if k is None: k=y; rows[k]=[]
    rows[k].append(x)
for k in sorted(rows): 
    xs=sorted(rows[k]); print("y=%.1f n=%d first_x=%.1f last_x=%.1f step=%.2f" % (k,len(xs),xs[0],xs[-1],(xs[-1]-xs[0])/max(1,len(xs)-1)))
