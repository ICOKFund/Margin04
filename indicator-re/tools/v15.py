import sys, datetime as dt; sys.path.insert(0, sys.argv[1])
import yh, bn
from srv2 import sr_levels
ix = yh.cut(yh.load_daily(sys.argv[2]), dt.date(2023,5,10), last=(12286.66,12324.01,12211.58,12240.73))
bd = bn.cut(bn.load(sys.argv[3]), bn.ms(2023,5,7), last=(28837.9,29137.0,28691.2,28746.8))
cases = {"IXIC 1D @2023-05-10": (ix, 0.01, [12407.91, 11660.27, 11133.06, 10773.97, 10175.88]),
         "BTC 1D @2023-05-07":  (bd, 0.1,  [24490.7, 20986.8, 18208.9, 15452.9])}
for name,(b,tick,target) in cases.items():
    O=[x[1] for x in b]; H=[x[2] for x in b]; L=[x[3] for x in b]; C=[x[4] for x in b]; end=len(b)-1
    print("=====", name, " target:", sorted(target, reverse=True))
    for variant in (1,2):
        last, mids, stg, cw = sr_levels(H,L,end,variant=variant,tick=tick)
        got=sorted(mids, reverse=True)
        hit=[m for m in got if any(abs(m-t)<tick/2+1e-9 for t in target)]
        lab = b[last][0] if not isinstance(b[last][0], int) else bn.ts(b[last][0])
        print("  variant %d: last recalculation bar %s, channel width %.2f" % (variant, lab, cw))
        print("     levels %s  strengths %s" % (got, stg))
        print("     rate%%: %s" % ["%.2f" % (100*(m-C[-1])/C[-1]) for m in got])
        print("     matched %d / %d" % (len(hit), len(target)))
