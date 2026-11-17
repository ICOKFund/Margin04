# common dataset bundle: returns dict name -> (O,H,L,C,V, tick, targets)
import sys, datetime as dt
import yh, bn
def bundle(ixp, sxp, bdp, b4p):
    ix = yh.cut(yh.load_daily(ixp), dt.date(2023,5,10), last=(12286.66,12324.01,12211.58,12240.73))
    sx = yh.cut(yh.to_weekly(yh.load_daily(sxp)), dt.date(2023,4,17), last=(15.10,16.36,14.48,14.67))
    bd = bn.cut(bn.load(bdp), bn.ms(2023,4,17), last=(30286.6,30307.4,29714.1,29835.3))
    b4 = bn.cut(bn.load(b4p), bn.ms(2023,4,17,8), last=(29831.2,29913.6,29781.6,29835.1))
    def cols(b): return ([x[1] for x in b],[x[2] for x in b],[x[3] for x in b],[x[4] for x in b],[x[5] for x in b],[x[0] for x in b])
    return {"IXIC_1D": cols(ix)+(0.01, dict(TLLJ=12061.70, d=385.50)),
            "SOXL_1W": cols(sx)+(0.01, dict(TLLJ=13.06, d=2.73)),
            "BTC_1D":  cols(bd)+(0.1,  dict(TLLJ=27974.5, d=2755.0)),
            "BTC_4H":  cols(b4)+(0.1,  dict(TLLJ=30413.7, d=644.9))}
