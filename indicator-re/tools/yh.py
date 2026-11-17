import csv, datetime as dt
def load_daily(path, nd=2):
    out=[]
    for r in csv.DictReader(open(path)):
        d=dt.datetime.fromtimestamp(int(r["time"]), dt.timezone.utc).date()
        out.append((d, round(float(r["open"]),nd), round(float(r["high"]),nd), round(float(r["low"]),nd), round(float(r["close"]),nd), int(r["volume"])))
    return out
def to_weekly(daily):
    wk={}; order=[]
    for (d,o,h,l,c,v) in daily:
        key=d-dt.timedelta(days=d.weekday())           # Monday of that week
        if key not in wk: wk[key]=[key,o,h,l,c,v]; order.append(key)
        else:
            w=wk[key]; w[2]=max(w[2],h); w[3]=min(w[3],l); w[4]=c; w[5]+=v
    return [tuple(wk[k]) for k in order]
def cut(bars, last_date, last=None):
    b=[x for x in bars if x[0]<=last_date]
    if last is not None: b[-1]=(b[-1][0], last[0], last[1], last[2], last[3], b[-1][5])
    return b
