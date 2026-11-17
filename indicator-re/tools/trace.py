import sys, json
from PIL import Image
import numpy as np
# trace a thin line of a given RGB (tolerance) between x0..x1 in a pane (y0..y1); output median y per column
src=sys.argv[1]; x0,x1,y0,y1=[int(v) for v in sys.argv[2:6]]; rgb=tuple(int(v) for v in sys.argv[6].split(",")); tol=int(sys.argv[7])
im=np.asarray(Image.open(src).convert("RGB")).astype(int)
out={}
for x in range(x0,x1+1):
    col=im[y0:y1,x]; d=np.abs(col-np.array(rgb)).sum(axis=1)
    ys=np.nonzero(d<=tol)[0]
    if len(ys): out[x]=float(np.median(ys))+y0
json.dump(out, open(sys.argv[8],"w")); print("columns traced:", len(out), "of", x1-x0+1)
